from django.db.models import F, Count
from rest_framework import viewsets

from airport.models import AirplaneType, Airplane, Airport, Route, Crew, Flight
from airport.serializers import AirplaneTypeSerializer, AirplaneSerializer, AirportSerializer, RouteSerializer, \
    CrewSerializer, FlightSerializer, FlightListSerializer, RouteDetailSerializer, FlightDetailSerializer


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer

    def get_serializer_class(self):
        if self.action == "retrieve":
            return RouteDetailSerializer
        return RouteSerializer


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action == "list":
            queryset = (
                queryset
                .prefetch_related("tickets")
                .annotate(
                    tickets_available=F(
                        "airplane__rows") * F("airplane__seats_in_row")
                    - Count("tickets")
                )
            )

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        if self.action == "retrieve":
            return FlightDetailSerializer
        return FlightSerializer
