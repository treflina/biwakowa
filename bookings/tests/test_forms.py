from datetime import date

import pytest
from django.core.exceptions import NON_FIELD_ERRORS

from ..forms import (
    BookingForm, BookingUpdateForm, OnlineBookingDetailsForm,
    OnlineBookingForm,
)
from .base import faker


@pytest.mark.parametrize(
    "date_from, date_to, validity",
    [
        (date(2024, 7, 1), date(2024, 7, 8), True),
        (date(2024, 7, 9), date(2024, 7, 8), False),
        (date(2024, 7, 16), date(2024, 7, 23), False),
    ],
)
@pytest.mark.django_db
def test_booking_form(
    apartment, booking_factory, date_from, date_to, validity
):
    booking_factory(
        date_from=date(2024, 7, 10),
        date_to=date(2024, 7, 17),
        apartment=apartment,
    )
    form = BookingForm(
        data={
            "apartment": apartment,
            "date_from": date_from,
            "date_to": date_to,
        }
    )

    assert form.is_valid() is validity


@pytest.mark.parametrize(
    "date_from, date_to, validity",
    [
        (date(2024, 7, 1), date(2024, 7, 8), True),
        (date(2024, 7, 9), date(2024, 7, 8), False),
        (date(2024, 7, 16), date(2024, 7, 23), True),
    ],
)
@pytest.mark.django_db
def test_booking_update_form(
    apartment, booking_factory, date_from, date_to, validity
):
    booking_factory(
        apartment=apartment,
        date_from=date(2024, 7, 10),
        date_to=date(2024, 7, 17),
    )
    form = BookingUpdateForm(
        data={
            "apartment": apartment,
            "date_from": date_from,
            "date_to": date_to,
        }
    )

    assert form.is_valid() is validity


@pytest.mark.django_db
class TestOnlineBookingForm:

    future_date = faker.future_date()
    past_date = faker.past_date()

    # fmt: off
    @pytest.mark.parametrize(
        "arrival, departure, validity",
        [
            (past_date, future_date, False),
            (date(2044, 7, 1), date(2044, 6, 24), False),  # arrival date after departure
            # (date(2044, 7, 3), date(2044, 7, 6), False),  # min. 7-nights in July
            (date(2044, 9, 3), date(2044, 9, 5), False),  # min. 3-nights stay
            # (date(2044, 7, 4), date(2044, 7, 11), False),  # Sunday not the first day of stay in July
            (date(2044, 9, 3), date(2044, 9, 6), True),
        ],
    )
    # fmt: on
    def test_online_booking_form_wrong_data_throws_err(
        self, arrival, departure, validity
    ):

        form = OnlineBookingForm(
            data={
                "arrival": arrival,
                "departure": departure,
            }
        )

        assert form.is_valid() is validity

    def test_online_booking_form_missing_data_throws_err(self):
        form = OnlineBookingForm(
            data={
                "arrival": None,
                "departure": date(2024, 7, 1),
            }
        )

        assert form.has_error(NON_FIELD_ERRORS)
        assert "To pole jest wymagane." in form.errors["arrival"]


@pytest.mark.django_db
class TestOnlineBookingDetailsForm:

    future_date = faker.future_date()
    past_date = faker.past_date()

    def test_correct_data_form_is_valid(self, booking_data):
        form = OnlineBookingDetailsForm(booking_data)
        assert form.is_valid()

    def test__incorrect_email_field_raises_err(self, booking_data):
        booking_data["email"] = "invalid@"

        form = OnlineBookingDetailsForm(booking_data)
        assert form.is_valid() is False

    @pytest.mark.parametrize(
        "phone, validity",
        [
            ("tel. +48/609 000 000", True),
            ("774212000 wewn.605", True),
            ("", False),
            ("774212", False),
            ("609000000a", False),
        ],
    )
    def test__phone_field_validation(self, booking_data, phone, validity):
        booking_data["phone"] = phone
        form = OnlineBookingDetailsForm(booking_data)

        assert form.has_error("phone") is not validity
        assert form.is_valid() is validity

    def test__name_validation(self, booking_data):
        booking_data["name"] = "Abcd"
        form = OnlineBookingDetailsForm(booking_data)

        assert form.has_error("name") is True
        assert form.is_valid() is False

    def test_invalid_apartment_pk_raises_err(self, booking_data):
        booking_data["pk"] = 3
        form = OnlineBookingDetailsForm(booking_data)

        assert form.has_error("pk") is True
        assert form.is_valid() is False

    def test_no_consent_raises_err(self, booking_data):
        booking_data["consent"] = False
        form = OnlineBookingDetailsForm(booking_data)

        assert form.has_error("consent") is True
        assert form.is_valid() is False

    # fmt: off
    @pytest.mark.parametrize(
        "arrival, departure, validity",
        [
            (past_date, future_date, False),
            (date(2044, 7, 1), date(2044, 6, 24), False),  # arrival date after departure
            # (date(2044, 7, 3), date(2044, 7, 6), False),  # min. 7-nights in July
            (date(2044, 9, 3), date(2044, 9, 5), False),  # min. 3-nights stay
            # (date(2044, 7, 4), date(2044, 7, 11), False),  # Sunday not the first day of stay in July
            (date(2044, 9, 3), date(2044, 9, 6), True),
        ],
    )
    # fmt: on
    def test_arrival_departure_dates(
        self, booking_data, arrival, departure, validity
    ):
        booking_data["arrival"] = arrival
        booking_data["departure"] = departure
        form = OnlineBookingDetailsForm(booking_data)

        assert form.is_valid() is validity
        assert form.has_error(NON_FIELD_ERRORS) is not validity

    # fmt: off
    @pytest.mark.parametrize(
        "arrival, departure, email, session_email, validity",
        [
            (date(2044, 9, 6), date(2044, 9, 15), "test4@example.com", None, True),
            # the same email as in overlapping booking
            (date(2044, 9, 4), date(2044, 9, 7), "test1@example.com", None, True),
            # different email as in overlapping booking
            (date(2044, 9, 4), date(2044, 9, 7), "test3@example.com", None, False),
            # the same email but overlapping booking status unpaid
            (date(2044, 9, 15), date(2044, 9, 25), "test2@example.com", None, False),
            # session email the same as in overlapping booking
            (date(2044, 9, 4), date(2044, 9, 7), "test3@example.com", "test1@example.com", True),
            # session email is different than in overlapping booking
            (date(2044, 9, 4), date(2044, 9, 7), "test3@example.com", "test5@example.com", False),
        ],
    )
    # fmt: on
    def test_apartments_availability(
        self,
        apartment,
        booking_data,
        booking_factory,
        arrival,
        departure,
        email,
        session_email,
        validity,
    ):
        booking_data["arrival"] = arrival
        booking_data["departure"] = departure
        booking_data["email"] = email
        booking_data["pk"] = apartment.id

        booking_factory(
            date_from=date(2044, 9, 3),
            date_to=date(2044, 9, 6),
            apartment=apartment,
            email="test1@example.com",
            stripe_transaction_status="pending",
        )
        booking_factory(
            date_from=date(2044, 9, 15),
            date_to=date(2044, 9, 20),
            apartment=apartment,
            email="test2@example.com",
        )

        form = OnlineBookingDetailsForm(booking_data)
        form.session = {}
        form.session["email"] = session_email
        assert form.is_valid() is validity
