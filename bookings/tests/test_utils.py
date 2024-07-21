from datetime import date

import pytest

from ..utils import (
    booking_dates_assignment,
    calculated_price,
    daterange,
    get_next_prev_month,
    get_price,
)


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
