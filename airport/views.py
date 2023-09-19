from rest_framework import viewsets

from airport.models import AirplaneType, Airplane, Airport
from airport.serializers import AirplaneTypeSerializer, AirplaneSerializer, AirportSerializer


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer