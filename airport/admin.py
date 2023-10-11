from django.contrib import admin

from airport.models import (
    Route,
    Airport,
    AirplaneType,
    Airplane,
    Order,
    Crew,
    Flight,
    Ticket
)

admin.site.register(Route)
admin.site.register(Airport)
admin.site.register(AirplaneType)
admin.site.register(Airplane)
admin.site.register(Order)
admin.site.register(Crew)
admin.site.register(Flight)
admin.site.register(Ticket)
