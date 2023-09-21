from django.urls import path, include
from rest_framework import routers

from airport.views import AirplaneTypeViewSet, AirplaneViewSet, AirportViewSet, RouteViewSet, CrewViewSet, FlightViewSet

router = routers.DefaultRouter()
router.register("airplane_types", AirplaneTypeViewSet)
router.register("airplanes", AirplaneViewSet)
router.register("airports", AirportViewSet)
router.register("routes", RouteViewSet)
router.register("crew", CrewViewSet)
router.register("flights", FlightViewSet)


urlpatterns = [
    path("", include(router.urls))
]

app_name = "airport"
