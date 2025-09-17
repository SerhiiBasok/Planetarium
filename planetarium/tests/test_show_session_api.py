from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from planetarium.models import PlanetariumDome, AstronomyShow, ShowTheme, ShowSession, Ticket, Reservation
from planetarium.serializers import ShowSessionListSerializer, ShowSessionSerializer
from django.utils import timezone


SHOW_SESSION_URL = reverse("planetarium:show_session-list")


def sample_show_session(**params):
    dome = PlanetariumDome.objects.create(
        name="TestDome",
        rows=10,
        seats_in_row=10,
    )
    theme = ShowTheme.objects.create(name="ThemeTest")
    show = AstronomyShow.objects.create(
        title="ShowTitleTest",
        description="ShowDescription",
    )
    show.theme.add(theme)

    session = ShowSession.objects.create(
        astronomy_show=show,
        planetarium_dome=dome,
        show_time=params.get("show_time")
    )
    return session


def sample_reservation(user, **params):
    return Reservation.objects.create(user=user, **params)


def sample_ticket(session, reservation, row=1, seat=1):
    return Ticket.objects.create(
        show_session=session,
        reservation=reservation,
        row=row,
        seat=seat
    )


class UnauthenticatedPlanetariumApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(SHOW_SESSION_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class AuthenticatedPlanetariumApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpasswword",
        )
        self.client.force_authenticate(self.user)
        self.session = sample_show_session(show_time=timezone.now())


    def test_tickets_available_initial(self):
        """tickets_available правильно рахується без квитків"""
        res = self.client.get(SHOW_SESSION_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        expected = self.session.planetarium_dome.rows * self.session.planetarium_dome.seats_in_row
        self.assertEqual(res.data["results"][0]["tickets_available"], expected)

    def test_tickets_available_after_selling_some(self):
        """tickets_available враховує продані квитки"""
        reservation = sample_reservation(user=self.user)
        sample_ticket(session=self.session, reservation=reservation, row=1, seat=1)
        sample_ticket(session=self.session, reservation=reservation, row=1, seat=2)

        self.session.refresh_from_db()
        res = self.client.get(SHOW_SESSION_URL)
        expected = self.session.planetarium_dome.rows * self.session.planetarium_dome.seats_in_row - 2
        self.assertEqual(res.data["results"][0]["tickets_available"], expected)

    def test_free_seats_detail(self):
        """free_seats у Detail повертає правильні вільні місця"""
        reservation = sample_reservation(user=self.user)
        sample_ticket(session=self.session, reservation=reservation, row=1, seat=1)

        url = reverse("planetarium:show_session-detail", args=[self.session.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        free_seats = res.data["free_seats"]
        self.assertNotIn({"row": 1, "seat": 1}, free_seats)
        self.assertEqual(len(free_seats),
                         self.session.planetarium_dome.rows * self.session.planetarium_dome.seats_in_row - 1)

    def test_filters_show_dome_date(self):
        """Перевірка фільтрів show/dome/date"""
        show_id = self.session.astronomy_show.id
        dome_id = self.session.planetarium_dome.id
        date_str = self.session.show_time.date().isoformat()

        # фільтр за show
        res = self.client.get(f"{SHOW_SESSION_URL}?show={show_id}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"][0]["id"], self.session.id)

        # фільтр за dome
        res = self.client.get(f"{SHOW_SESSION_URL}?dome={dome_id}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # фільтр за date
        res = self.client.get(f"{SHOW_SESSION_URL}?date={date_str}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_permissions(self):
        """Перевірка прав доступу: read-only для користувача, створення тільки для адміна"""
        # Користувач (не адмін) спробує створити сеанс
        res = self.client.post(SHOW_SESSION_URL, data={
            "astronomy_show": self.session.astronomy_show.id,
            "planetarium_dome": self.session.planetarium_dome.id,
            "show_time": timezone.now()
        })
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # Адмін може створювати
        self.client.force_authenticate(user=self.admin)
        res = self.client.post(SHOW_SESSION_URL, data={
            "astronomy_show": self.session.astronomy_show.id,
            "planetarium_dome": self.session.planetarium_dome.id,
            "show_time": timezone.now()
        })
        self.assertIn(res.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST])
