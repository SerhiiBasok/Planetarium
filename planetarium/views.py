from rest_framework import viewsets

from planetarium.models import (PlanetariumDome,
                                AstronomyShow,
                                ShowSession,
                                ShowTheme,
                                Reservation,
                                Ticket)
from planetarium.serializers import (PlanetariumDomeSerializer,
                                     AstronomyShowSerializer,
                                     ShowSessionSerializer,
                                     ShowThemeSerializer,
                                     ReservationSerializer,
                                     TicketSerializer,
                                     PlanetariumDomeDetailSerializer,
                                     PlanetariumDomeListSerializer
                                     )


class PlanetariumDomeViewSet(viewsets.ModelViewSet):
    queryset = PlanetariumDome.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return PlanetariumDomeListSerializer
        if self.action == "retrieve":
            return PlanetariumDomeDetailSerializer
        return PlanetariumDomeSerializer


class AstronomyShowViewSet(viewsets.ModelViewSet):
    queryset = AstronomyShow.objects.all()
    serializer_class = AstronomyShowSerializer


class ShowSessionViewSet(viewsets.ModelViewSet):
    queryset = ShowSession.objects.all()
    serializer_class = ShowSessionSerializer


class ShowThemeViewSet(viewsets.ModelViewSet):
    queryset = ShowTheme.objects.all()
    serializer_class = ShowThemeSerializer


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer