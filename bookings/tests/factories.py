from datetime import date, timedelta

import factory
from django.contrib.auth import get_user_model
from django.utils.timezone import datetime as dt

from apartments.models import Apartment, ApartmentType, Price
from home.models import PhoneSnippet

from ..models import Booking
from .base import faker


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = "Test User"
    password = "somepass1234"


class ApartmentTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ApartmentType

    type_name = "2-osobowy"


class ApartmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Apartment

    name = factory.Sequence(lambda n: "ap%d" % n)
    apartment_type = factory.SubFactory(ApartmentTypeFactory)
    stripe_product_id = "stripe_id_1513"
    base_price = 400
    floor = "0"


class PriceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Price

    amount = 500
    apartment_type = factory.SubFactory(ApartmentTypeFactory)
    start_date = date(2024, 7, 1)
    end_date = None


class BookingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Booking

    created_at = factory.LazyFunction(dt.now)
    apartment = factory.SubFactory(ApartmentFactory)
    guest = factory.LazyAttribute(lambda _: faker.name())
    email = factory.LazyAttribute(lambda _: faker.unique.email())
    phone = "+48/000-000-000"
    date_from = date(2024, 7, 1)
    date_to = factory.LazyAttribute(lambda o: o.date_from + o.duration)
    total_price = 0
    paid = False
    address = factory.LazyAttribute(lambda _: faker.address())
    notes = ""
    stripe_checkout_id = None
    stripe_transaction_status = "unpaid"

    class Params:
        duration = timedelta(days=3)


class PhoneFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PhoneSnippet

    phone = "000-000-001"
