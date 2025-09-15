from django.urls import path, include
from rest_framework import routers
from planetarium.views import (PlanetariumDomeViewSet,
                               AstronomyShowViewSet,
                               ShowSessionViewSet,
                               ShowThemeViewSet,
                               ReservationViewSet)

app_name = "planetarium"

router = routers.DefaultRouter()
router.register("domes", PlanetariumDomeViewSet)
router.register("astronomy_shows", AstronomyShowViewSet)
router.register("show_sessions", ShowSessionViewSet)
router.register("show_themes", ShowThemeViewSet)
router.register("reservations", ReservationViewSet)

urlpatterns = [
    path("", include(router.urls)),
]