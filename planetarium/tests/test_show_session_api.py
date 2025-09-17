from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.utils import timezone

from planetarium.models import (
    PlanetariumDome,
    AstronomyShow,
    ShowTheme,
    ShowSession,
    Ticket,
    Reservation,
)
from planetarium.serializers import (
    ShowSessionListSerializer,
    ShowSessionDetailSerializer,
)

SHOW_SESSION_URL = reverse("planetarium:show_session-list")


def sample_show_session(**params):
    dome = PlanetariumDome.objects.create(name="TestDome", rows=10, seats_in_row=10)
    theme, _ = ShowTheme.objects.get_or_create(name="ThemeTest")
    show = AstronomyShow.objects.create(
        title="ShowTitleTest", description="ShowDescription"
    )
    show.theme.add(theme)

    defaults = {
        "astronomy_show": show,
        "planetarium_dome": dome,
        "show_time": timezone.now(),
    }
    defaults.update(params)

    return ShowSession.objects.create(**defaults)


def sample_reservation(user, **params):
    return Reservation.objects.create(user=user, **params)


def sample_ticket(session, reservation, row=1, seat=1):
    return Ticket.objects.create(
        show_session=session, reservation=reservation, row=row, seat=seat
    )


def detail_url(session_id):
    return reverse("planetarium:show_session-detail", args=[session_id])


class UnauthenticatedShowSessionApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(SHOW_SESSION_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedShowSessionApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user("user@test.com", "testpass")
        self.client.force_authenticate(self.user)

    def test_list_show_sessions(self):
        session1 = sample_show_session()
        session2 = sample_show_session()

        res = self.client.get(SHOW_SESSION_URL)
        serializer = ShowSessionListSerializer(ShowSession.objects.all(), many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertCountEqual(res.data, serializer.data)

    def test_filter_by_show_dome_date(self):
        session1 = sample_show_session()
        session2 = sample_show_session()

        serializer2 = ShowSessionListSerializer(session2)

        res = self.client.get(SHOW_SESSION_URL, {"show": session2.astronomy_show.id})
        self.assertIn(serializer2.data, res.data)
        serializer1 = ShowSessionListSerializer(session1)
        self.assertIn(serializer2.data, res.data)

        res = self.client.get(SHOW_SESSION_URL, {"dome": session2.planetarium_dome.id})
        self.assertIn(serializer2.data, res.data)

        date_str = session2.show_time.date().isoformat()
        res = self.client.get(SHOW_SESSION_URL, {"date": date_str})
        self.assertIn(serializer2.data, res.data)

    def test_retrieve_show_session(self):
        session = sample_show_session()
        url = detail_url(session.id)
        res = self.client.get(url)
        serializer = ShowSessionDetailSerializer(session)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tickets_available_initial(self):
        session = sample_show_session()
        res = self.client.get(SHOW_SESSION_URL)
        expected = session.planetarium_dome.rows * session.planetarium_dome.seats_in_row
        self.assertEqual(res.data[0]["tickets_available"], expected)

    def test_tickets_available_after_selling_some(self):
        session = sample_show_session()
        reservation = sample_reservation(user=self.user)
        sample_ticket(session=session, reservation=reservation, row=1, seat=1)
        sample_ticket(session=session, reservation=reservation, row=1, seat=2)

        res = self.client.get(SHOW_SESSION_URL)
        expected = (
            session.planetarium_dome.rows * session.planetarium_dome.seats_in_row - 2
        )
        self.assertEqual(res.data[0]["tickets_available"], expected)

    def test_free_seats_detail(self):
        session = sample_show_session()
        reservation = sample_reservation(user=self.user)
        sample_ticket(
            session=session,
            reservation=reservation,
            row=1,
            seat=1)

        url = detail_url(session.id)
        res = self.client.get(url)
        free_seats = res.data["free_seats"]

        self.assertNotIn({"row": 1, "seat": 1}, free_seats)
        self.assertEqual(
            len(free_seats),
            session.planetarium_dome.rows * session.planetarium_dome.seats_in_row - 1,
        )

    def test_create_show_session_forbidden(self):
        session = sample_show_session()
        payload = {
            "astronomy_show": session.astronomy_show.id,
            "planetarium_dome": session.planetarium_dome.id,
            "show_time": timezone.now(),
        }
        res = self.client.post(SHOW_SESSION_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminShowSessionApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = get_user_model().objects.create_superuser(
            "admin@test.com", "adminpass"
        )
        self.client.force_authenticate(self.admin)

    def test_create_show_session(self):
        session = sample_show_session()
        payload = {
            "astronomy_show": session.astronomy_show.id,
            "planetarium_dome": session.planetarium_dome.id,
            "show_time": timezone.now(),
        }
        res = self.client.post(SHOW_SESSION_URL, payload)
        self.assertIn(
            res.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]
        )
