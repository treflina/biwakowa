from django.urls import path

from .views import (
    BookingCreateView,
    BookingDetailView,
    BookingsListView,
    BookingUpdateView,
    UpcomingBookingsListView,
    calendars,
    delete_booking,
    onlinebooking,
    success,
    cancel,
    stripe_webhook,
    booking_search,
)

app_name = "bookings_app"

urlpatterns = [
    path("rezerwacje/", BookingsListView.as_view(), name="bookings"),
    path(
        "rezerwacje/nadchodzace/",
        UpcomingBookingsListView.as_view(),
        name="upcoming-bookings",
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
    path("rezerwacja/<arrival>/<departure>/<pk>/", onlinebooking, name="onlinebooking"),
    path("success/", success, name="success"),
    path("cancel/", cancel, name="cancel"),
    path("stripe-webhook/", stripe_webhook, name="webhook"),
    path("calendars/<year>/<month>/", calendars, name="calendars"),
    path("calendars/", calendars, name="calendars"),
    path("wyszukaj/", booking_search, name="booking-search"),
]
