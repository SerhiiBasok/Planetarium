from django.db import transaction
from rest_framework.exceptions import ValidationError
from rest_framework import serializers

from planetarium.models import (
    PlanetariumDome,
    AstronomyShow,
    ShowSession,
    ShowTheme,
    Reservation,
    Ticket,
)


class PlanetariumDomeSerializer(serializers.ModelSerializer):

    class Meta:
        model = PlanetariumDome
        fields = "__all__"


class PlanetariumDomeListSerializer(serializers.ModelSerializer):

    class Meta:
        model = PlanetariumDome
        fields = ("id", "name", "capacity")


class PlanetariumDomeDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = PlanetariumDome
        fields = ("id", "name", "rows", "seats_in_row", "capacity")


class ShowThemeSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShowTheme
        fields = ("id", "name")


class AstronomyShowSerializer(serializers.ModelSerializer):

    class Meta:
        model = AstronomyShow
        fields = ("id", "title", "theme", "description", "image")


class AstronomyShowListSerializer(serializers.ModelSerializer):
    theme = serializers.SlugRelatedField(
        many=True, slug_field="name", queryset=ShowTheme.objects.all()
    )

    class Meta:
        model = AstronomyShow
        fields = ("id", "title", "theme", "description", "image")


class AstronomyShowDetailSerializer(AstronomyShowListSerializer):

    class Meta:
        model = AstronomyShow
        fields = ("id", "title", "theme", "description", "image")


class AstronomyShowImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AstronomyShow
        fields = ("id", "image")


class ShowSessionSerializer(serializers.ModelSerializer):
    astronomy_show = serializers.SlugRelatedField(
        queryset=AstronomyShow.objects.all(), slug_field="title"
    )
    planetarium_dome = serializers.SlugRelatedField(
        queryset=PlanetariumDome.objects.all(), slug_field="name"
    )
    tickets_available = serializers.SerializerMethodField()

    class Meta:
        model = ShowSession
        fields = (
            "id",
            "show_time",
            "astronomy_show",
            "planetarium_dome",
            "tickets_available",
        )

    def get_tickets_available(self, obj):
        return obj.planetarium_dome.capacity - obj.tickets.count()


class ShowSessionListSerializer(ShowSessionSerializer):

    class Meta:
        model = ShowSession
        fields = (
            "id",
            "show_time",
            "astronomy_show",
            "planetarium_dome",
            "tickets_available",
        )


class ShowSessionDetailSerializer(ShowSessionSerializer):
    astronomy_show = AstronomyShowDetailSerializer(read_only=False)
    planetarium_dome = PlanetariumDomeDetailSerializer(read_only=False)
    free_seats = serializers.SerializerMethodField()

    class Meta(ShowSessionSerializer.Meta):
        fields = ShowSessionSerializer.Meta.fields + (
            "astronomy_show",
            "planetarium_dome",
            "free_seats",
        )

    def get_free_seats(self, obj):
        sold_tickets = obj.tickets.values_list("row", "seat")
        sold_set = set(sold_tickets)

        free = []
        for row in range(1, obj.planetarium_dome.rows + 1):
            for seat in range(1, obj.planetarium_dome.seats_in_row + 1):
                if (row, seat) not in sold_set:
                    free.append({"row": row, "seat": seat})

        return free


class TicketSerializer(serializers.ModelSerializer):

    def validate(self, attrs):
        show_session = attrs.get("show_session")
        row = attrs.get("row")
        seat = attrs.get("seat")

        if Ticket.objects.filter(
            show_session=show_session, row=row, seat=seat
        ).exists():
            raise ValidationError(
                f"Row {row}, seat {seat} is already taken for this session."
            )

        dome = show_session.planetarium_dome
        if row > dome.rows or seat > dome.seats_in_row:
            raise ValidationError(
                f"Row {row}, seat {seat} exceeds the dome's capacity."
            )
        return attrs

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "show_session")


class TicketListSerializer(TicketSerializer):
    show_session = ShowSessionListSerializer(many=False, read_only=False)


class TicketSeatsSerializer(TicketSerializer):
    class Meta:
        model = Ticket
        fields = ("row", "seat")


class ReservationSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, allow_empty=False)

    class Meta:
        model = Reservation
        fields = ("id", "tickets", "created_at")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            reservation = Reservation.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(reservation=reservation, **ticket_data)
            return reservation


class ReservationListSerializer(ReservationSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)

    class Meta:
        model = Reservation
        fields = ("id", "created_at", "tickets")
