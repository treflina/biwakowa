import json
from datetime import date
from unittest.mock import patch

import pytest
import stripe
from pytest_factoryboy import register

from .base import faker
from .factories import (
    ApartmentFactory, ApartmentTypeFactory, BookingFactory, PhoneFactory,
    PriceFactory, UserFactory,
)

register(ApartmentFactory)
register(ApartmentTypeFactory)
register(BookingFactory)
register(PriceFactory)
register(PhoneFactory)
register(UserFactory)


@pytest.fixture(autouse=True)
def email_backend_setup(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"


@pytest.fixture
def req(request):
    return request.param


@pytest.fixture
def booking_data(apartment):
    return {
        "arrival": date(2044, 7, 3),
        "departure": date(2044, 7, 10),
        "pk": apartment.id,
        "name": "Test Guest",
        "email": faker.email(),
        "phone": "+48/609 000 000",
        "guest_notes": faker.text(max_nb_chars=10),
        "consent": True,
        "address": faker.address(),
    }


@pytest.fixture
def booking_to_update(booking_factory):
    return booking_factory(
        date_from=date(2024, 7, 1), date_to=date(2024, 7, 7)
    )


@pytest.fixture
def mock_stripe_verify_header():
    with patch("stripe.WebhookSignature.verify_header") as mock_verify:
        mock_verify.return_value = None
        yield mock_verify


@pytest.fixture
def mock_stripe_session_retrieve_paid():
    with patch("stripe.checkout.Session.retrieve") as mock_paid:
        mock_paid.return_value.payment_status = "paid"
        yield mock_paid


@pytest.fixture
def mock_stripe_session_retrieve_unpaid():
    with patch("stripe.checkout.Session.retrieve") as mock_unpaid:
        mock_unpaid.return_value.payment_status = "paid"
        yield mock_unpaid


@pytest.fixture
def mock_stripe_session_create_error():
    with patch("stripe.checkout.Session.create") as mock_create_error:
        mock_create_error.side_effect = stripe._error.InvalidRequestError(
            message="No such product: 'id_000'",
            param="line_items[0][price_data][product]",
            code="resource_missing",
            http_status=400,
        )
        yield mock_create_error


@pytest.fixture
def mock_stripe_connection_error():
    with patch("stripe.checkout.Session.create") as mock_conn_error:
        mock_conn_error.side_effect = stripe._error.APIConnectionError(
            message="connection error",
        )
        yield mock_conn_error
