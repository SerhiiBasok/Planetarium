from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from PIL import Image
import tempfile
from rest_framework.test import APIClient
from planetarium.models import AstronomyShow, ShowTheme
from planetarium.serializers import AstronomyShowSerializer

ASTRONOMY_SHOW_URL = reverse("planetarium:astronomy-show-list")


def astronomy_show(**params):
    defaults = {
        "title": "Test Show",
        "description": "Some description",
    }
    defaults.update(params)
    return AstronomyShow.objects.create(**defaults)


def sample_theme(**params):
    defaults = {
        "name": "Space",
    }
    defaults.update(params)

    return ShowTheme.objects.create(**defaults)


def detail_url(show_id):
    return reverse("planetarium:astronomy-show-detail", args=[show_id])


def create_theme(name="Space"):
    return ShowTheme.objects.create(name=name)


class UnauthenticatedPlayApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(ASTRONOMY_SHOW_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAstronomyShowApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpassword",
        )
        self.client.force_authenticate(self.user)

    def test_filter_byTitle(self):
        show1 = astronomy_show(title="Show1")
        show2 = astronomy_show(title="Show2")

        res = self.client.get(ASTRONOMY_SHOW_URL, {"title": f"{show1.title}"})

        serializer1 = AstronomyShowSerializer(show1)
        serializer2 = AstronomyShowSerializer(show2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_filter_show_by_theme(self):
        show1 = astronomy_show(title="Show1")
        show2 = astronomy_show(title="Show2")

        theme1 = ShowTheme.objects.create(name="space1")
        theme2 = ShowTheme.objects.create(name="space2")

        show1.theme.add(theme1)
        show2.theme.add(theme2)

        show_with_out_theme = astronomy_show(title="Show With Out Theme")

        res = self.client.get(ASTRONOMY_SHOW_URL, {"theme": f"{theme1.id},{theme2.id}"})

        show_titles_in_res = [show["title"] for show in res.data]
        self.assertIn(show1.title, show_titles_in_res)
        self.assertIn(show2.title, show_titles_in_res)
        self.assertNotIn(show_with_out_theme.title, show_titles_in_res)

    def test_retrieve_astronomy_show(self):
        show = astronomy_show()
        theme = sample_theme(name="Space")
        show.theme.add(theme)

        url = detail_url(show.id)
        res = self.client.get(url)

        serializer = AstronomyShowSerializer(show)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        res_theme_names = [t for t in res.data["theme"]]
        self.assertIn("Space", res_theme_names)


class AdminAstronomyShowImageUploadTests(TestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_superuser(
            "admin@test.com", "adminpass"
        )
        self.user = get_user_model().objects.create_user("user@test.com", "userpass")
        self.client = APIClient()

    def _make_image_file(self):
        tmp = tempfile.NamedTemporaryFile(suffix=".jpg")
        Image.new("RGB", (200, 200)).save(tmp, format="JPEG")
        tmp.seek(0)
        return tmp

    def test_admin_can_upload_image(self):
        show = astronomy_show(title="With Image")
        url = reverse("planetarium:astronomy-show-upload-image", args=[show.id])
        self.client.force_authenticate(user=self.admin)
        with self._make_image_file() as img:
            res = self.client.post(url, {"image": img}, format="multipart")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_non_admin_cannot_upload_image(self):
        show = astronomy_show(title="No Image")
        url = reverse("planetarium:astronomy-show-upload-image", args=[show.id])
        self.client.force_authenticate(user=self.user)
        with self._make_image_file() as img:
            res = self.client.post(url, {"image": img}, format="multipart")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    class AdminAstronomyShowApiTests(TestCase):
        def setUp(self):
            self.admin = get_user_model().objects.create_superuser(
                "admin@test.com", "adminpass"
            )
            self.client = APIClient()
            self.client.force_authenticate(user=self.admin)
            self.theme = create_theme()

        def test_create_show(self):
            payload = {
                "title": "Test Show",
                "description": "Some description",
                "theme": [self.theme.id],
            }

            res = self.client.post(ASTRONOMY_SHOW_URL, payload, format="json")
            self.assertEqual(res.status_code, status.HTTP_201_CREATED)

            show = AstronomyShow.objects.get(id=res.data["id"])
            self.assertEqual(show.title, payload["title"])
            self.assertEqual(show.description, payload["description"])
            self.assertIn(self.theme, show.theme.all())

        def test_put_show(self):
            payload = {
                "title": "changed title",
                "description": "changed description",
            }

            show = astronomy_show()
            url = detail_url(show.id)

            res = self.client.put(url, payload)

            self.assertEqual(res.status_code, status.HTTP_200_OK)

        def test_delete_play(self):
            show = astronomy_show()
            url = detail_url(show.id)
            res = self.client.delete(url)

            self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
