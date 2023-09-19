from django.urls import path, include
from rest_framework import routers

from airport.views import AirplaneTypeViewSet, AirplaneViewSet, AirportViewSet

router = routers.DefaultRouter()
router.register("airplane_types", AirplaneTypeViewSet)
router.register("airplanes", AirplaneViewSet)
router.register("airports", AirportViewSet)


urlpatterns = [
    path("", include(router.urls))
]

app_name = "airport"
