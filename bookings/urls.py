from django.urls import path

from .views import (
    BookingCreateView, BookingDetailView, BookingsListView, BookingUpdateView,
    UpcomingBookingsListView, booking_search, calendars, cancel,
    delete_booking, onlinebooking, onlinebooking_without_payment, stripe_webhook, success,
    success_without_payment
)

app_name = "bookings_app"

urlpatterns = [
    path("rezerwacje/", BookingsListView.as_view(), name="bookings"),
    path(
        "rezerwacje/nadchodzace/",
        UpcomingBookingsListView.as_view(),
        name="upcoming_bookings",
    ),
    path(
        "rezerwacje/dodaj/",
        BookingCreateView.as_view(),
        name="add_booking",
    ),
    path(
        "rezerwacje/usun/<pk>/",
        delete_booking,
        name="delete_booking",
    ),
    path(
        "rezerwacje/edytuj/<pk>/",
        BookingUpdateView.as_view(),
        name="update_booking",
    ),
    path("rezerwacje/<pk>/", BookingDetailView.as_view(), name="booking"),
    path("calendars/<year>/<month>/", calendars, name="calendars"),
    path("calendars/", calendars, name="calendars"),
    path("wyszukaj/", booking_search, name="booking-search"),
    # views for online reservation without payment
    path(
        "rezerwacja/<arrival>/<departure>/<pk>/",
        onlinebooking_without_payment,
        name="onlinebooking_without_payment",
    ),
    path("sukces/", success_without_payment, name="success_without_payment"),
    # views for online payment
    # path(
    #     "rezerwacja/<arrival>/<departure>/<pk>/",
    #     onlinebooking,
    #     name="onlinebooking",
    # ),
    # path("success/", success, name="success"),
    # path("cancel/", cancel, name="cancel"),
    # path("stripe-webhook/", stripe_webhook, name="webhook"),
]
