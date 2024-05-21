from django.urls import path

from .views import (
    BookingListView,
    BookingCreateView,
    BookingUpdateView,
    delete_booking
)

app_name = "bookings_app"

urlpatterns = [
    path("rezerwacje/", BookingListView.as_view(), name="bookings"),
    path(
        "rezerwacje/dodaj/",
        BookingCreateView.as_view(),
        name="add-booking",
    ),
    path(
        "rezerwacje/usun/<pk>/",
        delete_booking,
        name="delete-booking",
    ),
    path(
        "sickleave-update/<pk>/",
        BookingUpdateView.as_view(),
        name="update-booking",
    ),
]