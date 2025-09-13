from rest_framework import serializers

from planetarium.models import PlanetariumDome, AstronomyShow, ShowSession, ShowTheme, Reservation, Ticket


class PlanetariumDomeSerializer(serializers.ModelSerializer):

    class Meta:
        model = PlanetariumDome
        fields = ("name", "rows", "seats_in_row")

class AstronomyShowSerializer(serializers.ModelSerializer):

    class Meta:
        model = AstronomyShow
        fields = ("title", "description")

class ShowSessionSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShowSession
        fields = ("astronomy_show", "planetarium_dome", "show_time")

class ShowThemeSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShowTheme
        fields = ("name", "show")

class ReservationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Reservation
        fields = ("created_at", "user",)

class TicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = ("row", "seat", "show_session", "reservation")