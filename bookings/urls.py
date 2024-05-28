from django.urls import path

from .views import (
    BookingCreateView,
    BookingDetailView,
    BookingsListView,
    BookingUpdateView,
    UpcomingBookingsListView,
    delete_booking,
    # onlinebooking,
    success,
    cancel,
    stripe_webhook,
    create_checkout_session
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
    # path("rezerwacja/", onlinebooking, name="onlinebooking"),
    path("success/", success, name="success"),
    path("cancel/", cancel, name="cancel"),
    path("stripe-webhook/", stripe_webhook, name="webhook"),
    path("rezerwacja/platnosci/", create_checkout_session, name="checkout"),
]