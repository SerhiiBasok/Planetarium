from rest_framework import serializers

from planetarium.models import PlanetariumDome, AstronomyShow, ShowSession, ShowTheme, Reservation, Ticket


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

class AstronomyShowSerializer(serializers.ModelSerializer):

    class Meta:
        model = AstronomyShow
        fields = ("title", "description")

class ShowSessionSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShowSession
        fields = ("id", "astronomy_show", "planetarium_dome", "show_time")
#
# class ShowSessionListSerializer(ShowSessionSerializer):
#     show_title = serializers.CharField(source="show_session.title", read_only=True)
#     astronomy_show = serializers.StringRelatedField()
#     planetarium_dome = serializers.StringRelatedField()



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