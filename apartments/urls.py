from django.urls import path

from .views import booking_calendar

app_name = "apartments_app"

urlpatterns = [
    path("booking/<year>/<month>/", booking_calendar, name="cal")
]
