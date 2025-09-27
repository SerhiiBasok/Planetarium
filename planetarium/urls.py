from django.urls import path, include
from rest_framework import routers
from planetarium.views import (
    PlanetariumDomeViewSet,
    AstronomyShowViewSet,
    ShowSessionViewSet,
    ShowThemeViewSet,
    ReservationViewSet,
)

app_name = "planetarium"

router = routers.DefaultRouter()
router.register("domes", PlanetariumDomeViewSet)
router.register("astronomy_shows", AstronomyShowViewSet, basename="astronomy-show")
router.register("show_sessions", ShowSessionViewSet, basename="show_session")
router.register("show_themes", ShowThemeViewSet)
router.register("reservations", ReservationViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
