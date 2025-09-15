from django.template.defaulttags import querystring
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

    def _params_to_ints(self, query_string):
        """Converts a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in query_string.split(",")]

    def get_queryset(self):
        queryset = self.queryset
        theme = self.request.query_params.get("theme")

        if theme:
            theme = self._params_to_ints(theme)
            queryset = queryset.filter(theme__id__in=theme)

        title = self.request.query_params.get("title")
        if title:
            queryset = queryset.filter(title__icontains=title)

        return queryset.distinct()


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
    queryset = Reservation.objects.prefetch_related("tickets")
    serializer_class = ReservationSerializer

    action_serializers = {
        "list": ReservationListSerializer
    }

    # def get_queryset(self):
    #     return self.queryset.filter(user=self.request.user)
    #
    # def perform_create(self, serializer):
    #     serializer.save(user=self.request.user)
