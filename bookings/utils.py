import calendar
import logging
from datetime import timedelta

from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models import Q
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.templatetags.static import static
from django.utils.html import strip_tags
from django.urls import reverse
from webpush import send_user_notification

from home.models import AdminEmail, PhoneSnippet

logger = logging.getLogger("django")


def daterange(start_date, end_date, end_include=0):
    """Iterate over dates in a given period."""
    for n in range(int((end_date - start_date).days) + end_include):
        yield start_date + timedelta(n)


def get_price(apartment, date):
    """Get apartment price for a given date"""
    Apartment = apps.get_model("apartments", "Apartment")
    Price = apps.get_model("apartments", "Price")

    price_obj = (
        Price.objects.order_by("start_date")
        .filter(
            Q(apartment_type=apartment.apartment_type)
            & (
                Q(start_date__lte=date) & Q(end_date__gte=date)
                | Q(start_date__lte=date) & Q(end_date=None)
            )
        )
        .last()
    )
    if price_obj:
        price_per_day = price_obj.amount
    else:
        price_per_day = Apartment.objects.get(id=apartment.id).base_price

    return price_per_day


def calculated_price(apartment, arrival, departure):
    """Calculate apartment total price for a given booking period."""
    price_list = [
        get_price(apartment, date) for date in daterange(arrival, departure)
    ]
    return sum(price_list)


def booking_dates_assignment(apartment, year, month):
    """Assign booking dates as a first, in the middle or last day of stay.
    Necessary for display purposes in calendars."""

    Booking = apps.get_model("bookings", "Booking")
    bookings_list = Booking.objects.bookings_per_month(apartment, year, month)

    cal = calendar.Calendar()
    month_dates = [
        date for date in cal.itermonthdates(year, month) if date.month == month
    ]

    dates = []
    arrival_dates = []
    departure_dates = []

    for d in month_dates:
        for booking in bookings_list:
            if d > booking.date_from and d < booking.date_to:
                dates.append(d.day)
            elif d == booking.date_from:
                arrival_dates.append(d.day)
            elif d == booking.date_to:
                departure_dates.append(d.day)

    dates.extend(list(set(arrival_dates) & set(departure_dates)))
    dates = sorted(set(dates))
    arrival_dates_list = sorted(
        set([day for day in arrival_dates if day not in dates])
    )
    departure_dates_list = sorted(
        set([day for day in departure_dates if day not in dates])
    )
    bookings_dates_dict = {
        "apartment": apartment,
        "dates": dates,
        "arr_dates": arrival_dates_list,
        "dep_dates": departure_dates_list,
    }
    return bookings_dates_dict


def get_next_prev_month(year, month):
    previous_year = year
    previous_month = month - 1
    if previous_month == 0:
        previous_year = year - 1
        previous_month = 12
    next_year = year
    next_month = month + 1
    if next_month == 13:
        next_year = year + 1
        next_month = 1
    calendar_months = {
        "previous_year": previous_year,
        "next_year": next_year,
        "previous_month": previous_month,
        "next_month": next_month,
    }
    return calendar_months


def handle_error_notification(err_subj, err_msg):
    """Send error messages to admin."""

    logger.error(f"{err_subj}: {err_msg}")
    # webpush notification
    payload = {"head": err_subj, "body": err_msg}
    try:
        admin_email = settings.ADMIN_EMAIL
        admin = User.objects.filter(email=admin_email).first()
        send_user_notification(user=admin, payload=payload, ttl=1000)
    except User.DoesNotExist:
        admin = None
        logger.error("Notification not sent. User doesn't exist.")
    except Exception as e:
        logger.error(f"{e}")
    # email notification
    send_mail(
        subject=err_subj,
        message=err_msg,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[settings.ADMIN_EMAIL],
        fail_silently=True,
    )


def send_email_about_booking_to_hotel(
    request, booking, from_email, hotel_email
):
    subject = f"Rezerwacja Ap. nr {booking.apartment.name} \
                od {booking.date_from}"
    url = str(
        request.build_absolute_uri(
            reverse("bookings_app:booking", kwargs={"pk": booking.id})
        )
    )
    notes = booking.notes if booking.notes else "-"
    msg = f"""Nowa rezerwacja: #{booking.id} \n
    Apartament nr {booking.apartment.name} \n
    od {booking.date_from} do {booking.date_to} \n
    Gość: {booking.guest} \n
    Uwagi gościa: {notes} \n
    utworzona: {booking.created_at} \n
    Zobacz: {url}"""

    try:
        send_mail(subject, msg, from_email, [hotel_email])
    except Exception as e:
        error_subj = "Confirmation email not sent for booking"
        error_msg = f"Confirmation email not sent for booking num \
            {booking.id}. {repr(e)}"
        handle_error_notification(error_subj, error_msg)


def send_webpush_notification_to_hotel(request, booking, hotel_email):
    hotel = User.objects.filter(email=hotel_email).last()
    subject = f"Rezerwacja Ap. nr {booking.apartment.name} \
                od {booking.date_from}"
    url = str(
        request.build_absolute_uri(
            reverse("bookings_app:booking", kwargs={"pk": booking.id})
        )
    )
    try:
        payload = {
            "head": subject,
            "body": f"Nowa rezerwacja: #{booking.id}",
            "url": url,
            "icon": static("favicon/android-chrome-96x96.png"),
        }
        send_user_notification(user=hotel, payload=payload, ttl=1000)
    except User.DoesNotExist:
        hotel = None
        logger.error("Notification not sent. User doesn't exist.")
    except Exception as e:
        handle_error_notification(
            "Error while sending webpush confirmation to hotel",
            repr(e),
        )


def send_confirmation_email(booking, from_email):
    try:
        hotel_phone = PhoneSnippet.objects.last()
        subject = "Potwierdzenie rezerwacji B4B"
        html_message = render_to_string(
            "bookings/confirmation-email.html",
            {"booking": booking, "phone": hotel_phone},
        )
        plain_message = strip_tags(html_message)
        to = booking.email
        send_mail(
            subject,
            plain_message,
            from_email,
            [to],
            html_message=html_message,
        )
    except Exception as e:
        error_subj = "Sending confirmation email failed"
        error_msg = f"Confirmation email not sent for {booking}. {repr(e)}"
        handle_error_notification(error_subj, error_msg)


def handle_sending_notifications_about_new_booking(booking, request=None):
    from_email = settings.EMAIL_HOST_USER
    hotel_email = AdminEmail.objects.last()

    if hotel_email:
        send_email_about_booking_to_hotel(
            request=request,
            booking=booking,
            from_email=from_email,
            hotel_email=hotel_email,
        )

        send_webpush_notification_to_hotel(
            request=request, booking=booking, hotel_email=hotel_email
        )
    send_confirmation_email(booking, from_email)


class WebhookResponse(HttpResponse):

    def __init__(self, request, booking, **kwargs):
        super().__init__(**kwargs)
        self.request = request
        self.booking = booking

    def close(self):
        super().close()
        handle_sending_notifications_about_new_booking(
            request=self.request, booking=self.booking
        )
