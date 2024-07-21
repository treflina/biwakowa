from datetime import date

import pytest
from django.db.utils import IntegrityError

from ..models import Booking


@pytest.mark.django_db
def test_str_booking(booking):
    model_str = (
        f"{booking.apartment.name}: {booking.date_from} - {booking.date_to}"
    )

    assert str(booking) == model_str


@pytest.mark.django_db
def test_date_from_field_raise_error_when_missing(booking_factory):

    with pytest.raises(IntegrityError):
        booking_factory(date_from=None, date_to=date(2024, 7, 1))


@pytest.mark.django_db
def test_date_to_field_raise_error_when_missing(booking_factory):

    with pytest.raises(IntegrityError):
        booking_factory(date_from=date(2024, 7, 1), date_to=None)


@pytest.mark.django_db
def test_nights_num_property(booking_factory):

    booking_1 = booking_factory(
        date_from=date(2024, 7, 1), date_to=date(2024, 7, 7)
    )
    assert booking_1.nights_num == 6


@pytest.mark.django_db
def test_bookings_periods_overlapping_manager(apartment, booking_factory):
    booking_factory(
        apartment=apartment,
        date_from=date(2024, 6, 28),
        date_to=date(2024, 7, 2),
    )
    booking_factory(
        apartment=apartment,
        date_from=date(2024, 7, 7),
        date_to=date(2024, 7, 14),
    )
    bookings_overlapping_should_not_exist = Booking.objects.bookings_periods(
        apartment, date(2024, 7, 2), date(2024, 7, 7)
    )
    bookings_overlapping_should_exist = Booking.objects.bookings_periods(
        apartment, date(2024, 7, 2), date(2024, 7, 8)
    )
    assert bookings_overlapping_should_not_exist.exists() is False
    assert bookings_overlapping_should_exist.exists() is True
