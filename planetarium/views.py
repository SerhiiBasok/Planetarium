from django.db.models import F, Count
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from planetarium.base.mixins import BaseViewSetMethodMixin
from planetarium.base.pagination import PlanetariumPagination
from planetarium.base.permissions import IsAdminOrIfAuthenticatedReadOnly
from planetarium.base.swagger_schemas import theme_schema
from planetarium.models import (
    PlanetariumDome,
    AstronomyShow,
    ShowSession,
    ShowTheme,
    Reservation,
)
from planetarium.serializers import (
    PlanetariumDomeSerializer,
    AstronomyShowListSerializer,
    ShowSessionListSerializer,
    ReservationSerializer,
    PlanetariumDomeDetailSerializer,
    PlanetariumDomeListSerializer,
    AstronomyShowDetailSerializer,
    ShowSessionDetailSerializer,
    ShowSessionSerializer,
    ReservationListSerializer,
    ShowThemeSerializer,
    AstronomyShowSerializer,
    AstronomyShowImageSerializer,
)


class PlanetariumDomeViewSet(BaseViewSetMethodMixin, viewsets.ModelViewSet):
    queryset = PlanetariumDome.objects.all()
    serializer_class = PlanetariumDomeSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    action_serializers = {
        "list": PlanetariumDomeListSerializer,
        "retrieve": PlanetariumDomeDetailSerializer,
    }


class AstronomyShowViewSet(BaseViewSetMethodMixin, viewsets.ModelViewSet):
    queryset = AstronomyShow.objects.all().prefetch_related("theme")
    serializer_class = AstronomyShowSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    action_serializers = {
        "list": AstronomyShowListSerializer,
        "retrieve": AstronomyShowDetailSerializer,
    }

    @staticmethod
    def _params_to_ints(query_string):
        """Converts a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in query_string.split(",")]

    def get_queryset(self):
        queryset = self.queryset.prefetch_related("theme")
        theme = self.request.query_params.get("theme")

        if theme:
            theme = self._params_to_ints(theme)
            queryset = queryset.filter(theme__id__in=theme)

        title = self.request.query_params.get("title")

        if title:
            queryset = queryset.filter(title__icontains=title)

        return queryset.distinct()

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        serializer_class=AstronomyShowImageSerializer,
        permission_classes=[IsAdminOrIfAuthenticatedReadOnly],
    )

    def upload_image(self, request, pk=None):
        show = self.get_object()
        serializer = self.get_serializer(show, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(**theme_schema)
    def list(self, request, *args, **kwargs):
        """Get list of planetarium"""
        return super().list(request, *args, **kwargs)


class ShowSessionViewSet(BaseViewSetMethodMixin, viewsets.ModelViewSet):
    queryset = (
        ShowSession.objects.select_related("astronomy_show", "planetarium_dome")
        .annotate(tickets_sold=Count("tickets"))
        .annotate(
            tickets_available=F("planetarium_dome__rows")
            * F("planetarium_dome__seats_in_row")
            - F("tickets_sold")
        )
    )
    serializer_class = ShowSessionSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        queryset = self.queryset

        show_id_str = self.request.query_params.get("show")
        dome_id_str = self.request.query_params.get("dome")
        date_str = self.request.query_params.get("date")

        if show_id_str:
            queryset = queryset.filter(astronomy_show_id=int(show_id_str))
        if dome_id_str:
            queryset = queryset.filter(planetarium_dome_id=int(dome_id_str))
        if date_str:
            queryset = queryset.filter(show_time__date=date_str)

        return queryset

    action_serializers = {
        "list": ShowSessionListSerializer,
        "retrieve": ShowSessionDetailSerializer,
    }


class ShowThemeViewSet(BaseViewSetMethodMixin, viewsets.ModelViewSet):
    queryset = ShowTheme.objects.all()
    serializer_class = ShowThemeSerializer


class ReservationViewSet(BaseViewSetMethodMixin, viewsets.ModelViewSet):
    queryset = Reservation.objects.prefetch_related(
        "tickets__show_session__astronomy_show",
        "tickets__show_session__planetarium_dome",
    )
    serializer_class = ReservationSerializer
    pagination_class = PlanetariumPagination

    action_serializers = {"list": ReservationListSerializer}

    action_permissions = {
        "list": [IsAuthenticated],
        "retrieve": [IsAuthenticated],
        "create": [IsAuthenticated],
        "destroy": [IsAdminOrIfAuthenticatedReadOnly],
    }

    def get_queryset(self):
        """All reservations if admin and personal reservations for user"""
        if self.request.user.is_staff:
            return self.queryset
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
