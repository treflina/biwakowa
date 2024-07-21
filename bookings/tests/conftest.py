from datetime import date

import pytest
from pytest_factoryboy import register
from unittest.mock import patch

from .base import faker
from .factories import (
    ApartmentFactory,
    ApartmentTypeFactory,
    BookingFactory,
    PriceFactory,
    UserFactory,
)

register(ApartmentFactory)
register(ApartmentTypeFactory)
register(BookingFactory)
register(PriceFactory)
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
