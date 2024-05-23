from django.urls import path

from .views import (
    BookingCreateView,
    BookingDetailView,
    BookingsListView,
    BookingUpdateView,
    UpcomingBookingsListView,
    delete_booking
)

app_name = "bookings_app"

urlpatterns = [
    path("rezerwacje/", BookingsListView.as_view(), name="bookings"),
    path(
        "rezerwacje/nadchodzace/",
        UpcomingBookingsListView.as_view(),
        name="upcoming-bookings"
    ),
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
        "rezerwacje/edytuj/<pk>/",
        BookingUpdateView.as_view(),
        name="update-booking",
    ),
    path("rezerwacje/<pk>/", BookingDetailView.as_view(), name="booking"),
]