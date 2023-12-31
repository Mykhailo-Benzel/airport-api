from django.db import transaction
from rest_framework import serializers

from airport.models import (
    AirplaneType,
    Airplane,
    Airport,
    Route,
    Crew,
    Flight,
    Ticket,
    Order
)


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name")


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = (
            "id", "name", "rows", "seats_in_row", "airplane_type", "capacity", "image"
        )


class AirplaneImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ("id", "image")


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "name", "closest_big_city")


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class RouteListSerializer(RouteSerializer):
    source = serializers.CharField(source="source.name", read_only=True)
    destination = serializers.CharField(
        source="destination.name",
        read_only=True
    )


class RouteDetailSerializer(RouteSerializer):
    source = AirportSerializer(many=False, read_only=True)
    destination = AirportSerializer(many=False, read_only=True)


class CrewSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="__str__", read_only=True)

    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name", "full_name")


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = (
            "id", "route", "airplane", "departure_time", "arrival_time", "crew"
        )


class FlightListSerializer(FlightSerializer):
    route = serializers.CharField(read_only=True)
    airplane = serializers.CharField(read_only=True)
    airplane_capacity = serializers.IntegerField(
        source="airplane.capacity",
        read_only=True
    )
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "airplane_capacity",
            "tickets_available",
            "departure_time",
            "arrival_time"
        )


class TicketListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = ("row", "seat")


class FlightDetailSerializer(serializers.ModelSerializer):
    route = serializers.CharField(read_only=True)
    crew = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="full_name"
    )
    airplane = AirplaneSerializer(many=False, read_only=True)
    taken_places = TicketListSerializer(
        source="tickets",
        many=True,
        read_only=True
    )

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "crew",
            "departure_time",
            "arrival_time",
            "airplane",
            "taken_places"
        )


class TicketSerializer(serializers.ModelSerializer):
    flight = FlightListSerializer(many=False, read_only=True)

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight")


class TicketCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("row", "seat", "flight")


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketCreateSerializer(
        many=True,
        read_only=False,
        allow_empty=False
    )

    class Meta:
        model = Order
        fields = ("id", "tickets", "created_at",)

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketSerializer(
        many=True,
        read_only=False,
        allow_empty=False
    )
