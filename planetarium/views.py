from rest_framework import viewsets

from planetarium.base.mixins import BaseViewSetMethodMixin
from planetarium.models import (PlanetariumDome,
                                AstronomyShow,
                                ShowSession,
                                ShowTheme,
                                Reservation,
                                )
from planetarium.serializers import (PlanetariumDomeSerializer,
                                     AstronomyShowListSerializer,
                                     ShowSessionListSerializer,
                                     ShowThemeSerializer,
                                     ReservationSerializer,
                                     PlanetariumDomeDetailSerializer,
                                     PlanetariumDomeListSerializer,
                                     AstronomyShowDetailSerializer,
                                     ShowSessionDetailSerializer,
                                     ShowSessionSerializer,
                                     ReservationListSerializer,
                                     )


class PlanetariumDomeViewSet(BaseViewSetMethodMixin, viewsets.ModelViewSet):
    queryset = PlanetariumDome.objects.all()
    serializer_class = PlanetariumDomeSerializer

    action_serializers = {
        "list": PlanetariumDomeListSerializer,
        "retrieve": PlanetariumDomeDetailSerializer
    }


class AstronomyShowViewSet(BaseViewSetMethodMixin, viewsets.ModelViewSet):
    queryset = AstronomyShow.objects.all()
    serializer_class = AstronomyShowDetailSerializer

    action_serializers = {
        "list": AstronomyShowListSerializer
    }


class ShowSessionViewSet(BaseViewSetMethodMixin, viewsets.ModelViewSet):
    queryset = ShowSession.objects.all()
    serializer_class = ShowSessionSerializer

    action_serializers = {
        "list": ShowSessionListSerializer,
        "retrieve": ShowSessionDetailSerializer
    }


class ShowThemeViewSet(BaseViewSetMethodMixin, viewsets.ModelViewSet):
    queryset = ShowTheme.objects.all()
    serializer_class = ShowThemeSerializer


class ReservationViewSet(BaseViewSetMethodMixin, viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

    action_serializers = {
        "list": ReservationListSerializer
    }

    # def get_queryset(self):
    #     return self.queryset.filter(user=self.request.user)
    #
    # def perform_create(self, serializer):
    #     serializer.save(user=self.request.user)
