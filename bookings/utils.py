from calendar import Calendar
import logging
import requests
import time
from datetime import timedelta

import after_response
import stripe
from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models import Q
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.templatetags.static import static
from django.urls import reverse
from django.utils.html import strip_tags
from webpush import send_user_notification

from apartments.models import Apartment
from home.models import AdminEmail, BankAccountNumberSnippet, PhoneSnippet

from .models import Booking

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


def get_available_apartments(session_email, arrival, departure):
    """
    List apartments with corresponding prices
    that are available in the given period of time.
    """
    available_apartments = []
    apartments = Apartment.objects.all().order_by("name")

    for apartment in apartments:
        if session_email:
            qs = Booking.objects.bookings_periods(
                apartment, arrival, departure
            ).exclude(
                Q(email=session_email) & Q(stripe_transaction_status="pending")
            )
        else:
            qs = Booking.objects.bookings_periods(
                apartment, arrival, departure
            )
        if not qs.exists():
            price = calculated_price(apartment, arrival, departure)
            apartment.price = price
            available_apartments.append(apartment)

    return available_apartments

def booking_dates_assignment(apartment, year, month):
    """
    Assign booking dates into categories for calendar display:
    - 'dates': days that are in the middle of a booking
    - 'arr_dates': arrival days (start of a booking)
    - 'dep_dates': departure days (end of a booking)
    """

    Booking = apps.get_model("bookings", "Booking")
    bookings = Booking.objects.bookings_per_month(apartment, year, month)

    cal = Calendar()
    month_days = [d for d in cal.itermonthdates(year, month) if d.month == month]

    middle_days = set()
    arrival_days = set()
    departure_days = set()

    for booking in bookings:
        start = booking.date_from
        end = booking.date_to

        for day in month_days:
            if start < day < end:
                middle_days.add(day.day)
            elif day == start:
                arrival_days.add(day.day)
            elif day == end:
                departure_days.add(day.day)

    # Handle overlap: if a day is both arrival and departure, treat it as a middle day
    overlapping_days = arrival_days & departure_days
    middle_days.update(overlapping_days)

    # Remove overlaps from arrival and departure sets
    arrival_days.difference_update(middle_days)
    departure_days.difference_update(middle_days)

    return {
        "apartment": apartment,
        "dates": sorted(middle_days),
        "arr_dates": sorted(arrival_days),
        "dep_dates": sorted(departure_days),
    }


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


def handle_error_notification(err_subj, err_msg, email=True, push=True):
    """Send error messages to admin."""

    logger.error(f"{err_subj}: {err_msg}")
    # webpush notification
    payload = {"head": err_subj, "body": err_msg}
    try:
        admin_email = settings.ADMIN_EMAIL
        admin = User.objects.filter(email=admin_email).first()
        if email:
            send_mail(
                subject=err_subj,
                message=err_msg,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[settings.ADMIN_EMAIL],
                fail_silently=True,
        )
        if push:
            send_user_notification(user=admin, payload=payload, ttl=1000)

    except Exception as e:
        logger.error(f"{e}")


def send_email_about_booking_to_hotel(booking, from_email, hotel_email):
    subject = (
        f"Rezerwacja Ap. nr {booking.apartment.name} od {booking.date_from}"
    )
    url = settings.BASE_URL + str(
        reverse("bookings_app:booking", kwargs={"pk": booking.id})
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
        handle_error_notification(error_subj, error_msg, email=False)


def send_webpush_notification_to_hotel(booking, hotel_email):
    hotel = User.objects.filter(email=hotel_email).first()
    subject = (
        f"Rezerwacja Ap. nr {booking.apartment.name} "
        f"od {booking.date_from}"
    )
    url = settings.BASE_URL + str(
        reverse("bookings_app:booking", kwargs={"pk": booking.id})
    )
    try:
        payload = {
            "head": subject,
            "body": f"Nowa rezerwacja: #{booking.id}",
            "url": url,
            "icon": static("favicon/android-chrome-96x96.png"),
        }
        send_user_notification(user=hotel, payload=payload, ttl=160000)
    except Exception as e:
        handle_error_notification(
            "Error while sending webpush confirmation to hotel",
            repr(e),
            push=False
        )

def send_confirmation_email(booking, from_email):
    try:
        hotel_phone = PhoneSnippet.objects.last()
        bank_account = BankAccountNumberSnippet.objects.last()
        subject = "Potwierdzenie wstępnej rezerwacji B4B"
        html_message = render_to_string(
            # "bookings/confirmation-email.html",
            "bookings/confirmation-email-no-payment.html",
            {
            "booking": booking,
            "phone": hotel_phone,
            "bank_account": bank_account,
            "url": settings.BASE_URL
            },
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
        handle_error_notification(error_subj, error_msg, email=False)


def send_final_confirmation_email(booking, action):
    hotel_email = AdminEmail.objects.last()
    hotel_phone = PhoneSnippet.objects.last()

    if not hotel_email or not booking.email:
        raise ValueError("Brakuje adresu e-mail nadawcy lub odbiorcy.")

    if action == "confirm":
        template = "bookings/confirmation-final-email.html"
        subject = "Rezerwacja w Apartamenty Biwakowa 4B"
    elif action == "cancel":
        template = "bookings/cancellation-email.html"
        subject = "Anulowanie rezerwacji w Apartamenty Biwakowa 4B"
    else:
        raise ValueError(f"Nieznane działanie: {action}")

    try:
        html_message = render_to_string(template,
            {
            "booking": booking,
            "phone": hotel_phone,
            "url": settings.BASE_URL
        },
        )
        plain_message = strip_tags(html_message)
        to = booking.email
        send_mail(
            subject,
            plain_message,
            hotel_email.email,
            [to],
            html_message=html_message,
        )
    except Exception as e:
        error_subj = "Sending final confirmation email failed"
        error_msg = f"Final Confirmation email not sent for {booking}. {repr(e)}"
        handle_error_notification(error_subj, error_msg, email=False)
        raise

@after_response.enable
def handle_sending_notifications_about_new_booking(booking):
    from_email = settings.DEFAULT_FROM_EMAIL
    hotel_email = AdminEmail.objects.last()
    url = settings.BASE_URL + str(
        reverse("bookings_app:booking", kwargs={"pk": booking.id})
    )
    msg = (
        f"Nowa rezerwacja apart. {booking.apartment.name} "
        f"od {booking.date_from} do {booking.date_to}.\n"
        f"Zobacz: {url}"
    )

    if hotel_email:
        send_email_about_booking_to_hotel(
            booking=booking,
            from_email=from_email,
            hotel_email=hotel_email.email,
        )

        send_webpush_notification_to_hotel(
            booking=booking, hotel_email=hotel_email.email
        )
    send_confirmation_email(booking, from_email)
    send_sms_with_retry(
        from_name="Biwakowa_4B",
        to_number=settings.HOTEL_PHONE_NUMBER,
        message=msg
    )


SMS_API_URL = "https://api2.smsplanet.pl/sms"
SMS_API_TOKEN = settings.SMS_TOKEN
MAX_DURATION_SECONDS = 600
INITIAL_WAIT = 5

@after_response.enable
def send_sms_with_retry(from_name, to_number, message):
    start_time = time.time()
    wait = INITIAL_WAIT

    while True:
        try:
            response = requests.post(
                SMS_API_URL,
                headers={
                    "Authorization": f"Bearer {SMS_API_TOKEN}",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                data={
                    "from": from_name,
                    "to": to_number,
                    "msg": message,
                },
                timeout=10,
            )

            if response.status_code == 200:
                try:
                    data = response.json()
                    if "messageId" in data:
                        break
                    else:
                        logger.error("Sending SMS failed: 200 OK but no messageId:", data)
                except ValueError:
                    logger.error("Invalid JSON in SMS API response.")
                    data = {}

            else:
                logger.error(f"Sending SMS failed: HTTP {response.status_code}:", response.text)

        except Exception as e:
            logger.error(f"Sending SMS failed: {e}")

        # Check if max time reached
        if time.time() - start_time > MAX_DURATION_SECONDS:
            logger.error("SMS sending failed. Gave up after 10 minutes.")
            break

        logger.info(f"SMS API: Retrying in {wait} seconds...")
        time.sleep(wait)

        wait = min(wait * 2, 60)


def fulfill_order(session_id):
    try:
        booking = Booking.objects.get(stripe_checkout_id=session_id)
    except Booking.DoesNotExist:
        booking = None
        err_subj = "Session completed, booking not found"
        err_msg = (
            f"Session completed (session id: {session_id}), "
            f"related booking was not found in the database."
        )
        handle_error_notification(err_subj, err_msg)
        return None

    if booking.stripe_transaction_status != "success":
        try:
            checkout_session = stripe.checkout.Session.retrieve(session_id)

            if checkout_session.payment_status == "paid":
                booking.stripe_transaction_status = "success"
                booking.paid = True
                booking.save()

                return booking

        except Exception as e:
            err_subj = "Error while retrieving session_id"
            err_msg = (
                f"{repr(e)}. Booking id:{booking.id}, session_id: {session_id}"
            )
            handle_error_notification(err_subj, err_msg)
    return None


class WebhookResponse(HttpResponse):
    """
    HttpResponse where additional function is called, after response
    has been sent to the client.
    """

    def __init__(self, booking, **kwargs):
        super().__init__(**kwargs)
        self.booking = booking

    def close(self):
        super().close()
        handle_sending_notifications_about_new_booking(booking=self.booking)
