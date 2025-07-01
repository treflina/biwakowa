import logging
from datetime import date
from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings
from django.core import mail
from webpush import send_user_notification

from ..utils import (
    WebhookResponse, booking_dates_assignment, calculated_price, daterange,
    get_available_apartments, get_next_prev_month, get_price,
    send_confirmation_email, send_email_about_booking_to_hotel,
    send_webpush_notification_to_hotel,
)

logger = logging.getLogger("django")


@pytest.fixture
def prices(apartment, price_factory):
    return [
        price_factory(
            amount=600,
            start_date=date(2024, 6, 30),
            apartment_type=apartment.apartment_type,
        ),
        price_factory(
            amount=500,
            start_date=date(2024, 7, 1),
            end_date=date(2024, 7, 4),
            apartment_type=apartment.apartment_type,
        ),
        price_factory(
            amount=800,
            start_date=date(2024, 7, 3),
            end_date=date(2024, 7, 5),
            apartment_type=apartment.apartment_type,
        ),
    ]


@pytest.mark.django_db
def test_daterange(booking_factory):
    booking = booking_factory(
        date_from=date(2024, 7, 1), date_to=date(2024, 7, 5)
    )
    num_dates = len(list(daterange(date(2024, 7, 1), date(2024, 7, 5))))
    assert num_dates == booking.nights_num


@pytest.mark.django_db
def test_get_price(apartment, prices):

    assert get_price(apartment, date(2024, 6, 29)) == 400
    assert get_price(apartment, date(2024, 6, 30)) == 600
    assert get_price(apartment, date(2024, 7, 1)) == 500
    assert get_price(apartment, date(2024, 7, 2)) == 500
    assert get_price(apartment, date(2024, 7, 3)) == 800
    assert get_price(apartment, date(2024, 7, 4)) == 800
    assert get_price(apartment, date(2024, 7, 5)) == 800
    assert get_price(apartment, date(2024, 7, 6)) == 600


@pytest.mark.django_db
def test_calculated_price(apartment, prices):

    total = calculated_price(apartment, date(2024, 6, 29), date(2024, 7, 7))
    assert total == 5000


@pytest.mark.django_db
def test_booking_dates_assignment(
    apartment, apartment_factory, booking_factory
):

    apartment_2 = apartment_factory(name="2")
    booking_factory(
        apartment=apartment,
        date_from=date(2024, 6, 28),
        date_to=date(2024, 7, 4),
    )
    booking_factory(
        apartment=apartment,
        date_from=date(2024, 7, 4),
        date_to=date(2024, 7, 6),
    )
    booking_factory(
        apartment=apartment,
        date_from=date(2024, 7, 30),
        date_to=date(2024, 8, 2),
    )
    booking_factory(
        apartment=apartment_2,
        date_from=date(2024, 7, 20),
        date_to=date(2024, 7, 23),
    )
    booking_factory(
        apartment=apartment,
        date_from=date(2024, 7, 3),
        date_to=date(2024, 7, 6),
    )

    booking_dates_dict = booking_dates_assignment(apartment, 2024, 7)

    assert booking_dates_dict["dates"] == [1, 2, 3, 4, 5, 31]
    assert booking_dates_dict["arr_dates"] == [30]
    assert booking_dates_dict["dep_dates"] == [6]


def test_get_next_prev_month():
    res_2023_12 = {
        "previous_year": 2023,
        "next_year": 2024,
        "previous_month": 11,
        "next_month": 1,
    }
    res_2024_1 = {
        "previous_year": 2023,
        "next_year": 2024,
        "previous_month": 12,
        "next_month": 2,
    }

    assert get_next_prev_month(2023, 12) == res_2023_12
    assert get_next_prev_month(2024, 1) == res_2024_1


@pytest.mark.django_db
def test_webhookhttp_response(booking):
    mock_handle_sending_notifications_about_new_booking = MagicMock()
    with patch(
        "bookings.utils.handle_sending_notifications_about_new_booking",
        mock_handle_sending_notifications_about_new_booking,
    ):
        resp = WebhookResponse(booking=booking)
        resp.close()

        assert resp.status_code == 200
        mock_handle_sending_notifications_about_new_booking.assert_called()


@pytest.mark.django_db
def test_send_confirmation_email(booking_factory):
    booking = booking_factory(email="guest@example.com")
    from_email = "test@example.com"

    send_confirmation_email(booking, from_email)
    assert len(mail.outbox) == 1
    assert mail.outbox[0].from_email == "test@example.com"
    assert mail.outbox[0].to == ["guest@example.com"]
    assert mail.outbox[0].subject == "Potwierdzenie wstępnej rezerwacji B4B"


@pytest.mark.parametrize(
    "s_email, arrival, departure, validity, count",
    [
        ("test@example.com", date(2044, 7, 8), date(2044, 7, 18), True, 3),
        ("test@example.com", date(2044, 7, 8), date(2044, 7, 19), False, 2),
        ("test@example.com", date(2044, 7, 7), date(2044, 7, 18), True, 3),
        (None, date(2044, 7, 7), date(2044, 7, 18), False, 2),
    ],
)
@pytest.mark.django_db
def test_get_available_apartments(
    apartment_factory,
    booking_factory,
    s_email,
    arrival,
    departure,
    validity,
    count,
):
    ap1 = apartment_factory(name=1)
    ap2 = apartment_factory(name=2)
    ap3 = apartment_factory(name=3)

    b1 = booking_factory(
        apartment=ap1,
        date_from=date(2044, 7, 1),
        date_to=date(2044, 7, 8),
        email="test@example.com",
        stripe_transaction_status="pending",
    )
    booking_factory(
        apartment=ap1,
        date_from=date(2044, 7, 18),
        date_to=date(2044, 7, 25),
        email="test2@example.com",
    )

    available_aparts = get_available_apartments(s_email, arrival, departure)
    assert (ap1 in available_aparts) is validity
    assert len(available_aparts) == count


@pytest.mark.django_db
def test_send_email_about_booking_to_hotel(booking):
    from_email = settings.EMAIL_HOST_USER
    hotel_email = "hotel@example.com"
    send_email_about_booking_to_hotel(booking, from_email, hotel_email)

    assert len(mail.outbox) > 0
    assert booking.apartment.name in mail.outbox[0].subject
    assert booking.guest in mail.outbox[0].body


@pytest.mark.django_db
def test_send_webpush_notification_to_hotel(booking, user_factory):
    user_factory(email="hotel@email.com")

    with patch(
        "bookings.utils.send_user_notification", MagicMock()
    ) as mock_func:
        send_webpush_notification_to_hotel(booking, "hotel@email.com")
        mock_func.assert_called()
