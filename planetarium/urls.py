from django.urls import path, include
from rest_framework import routers
from planetarium.views import (PlanetariumDomeViewSet,
                               AstronomyShowViewSet,
                               ShowSessionViewSet,
                               ShowThemeViewSet, ReservationViewSet, TicketViewSet)

app_name = "planetarium"

router = routers.DefaultRouter()
router.register("dome", PlanetariumDomeViewSet)
router.register("astronomy_show", AstronomyShowViewSet)
router.register("show_session", ShowSessionViewSet)
router.register("show_theme", ShowThemeViewSet)
router.register("reservation", ReservationViewSet)
router.register("ticket", TicketViewSet)

urlpatterns = [
    path("", include(router.urls)),
]