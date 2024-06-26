import calendar
from datetime import timedelta

from django.apps import apps
from django.db.models import Q


def daterange(start_date, end_date):
    """Iterate over dates in a given period."""
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def get_base_price(apartment, date):
    """Get apartment price for a given date"""
    Apartment = apps.get_model("apartments", "Apartment")
    Price = apps.get_model("apartments", "Price")

    price_obj = (
        Price.objects.order_by("-start_date")
        .filter(
            Q(apartment_type=apartment.apartment_type)
            & (
                Q(start_date__lte=date) & Q(end_date__gte=date)
                | Q(start_date__lte=date) & Q(end_date=None)
            )
        )
        .first()
    )
    if price_obj:
        price_per_day = price_obj.amount
    else:
        price_per_day = Apartment.objects.get(id=apartment.id).base_price

    return price_per_day


def calculated_price(apartment, arrival, departure):
    """Calculate apartment total price for a given booking period."""
    price_list = [
        get_base_price(apartment, date) for date in daterange(arrival, departure)
    ]
    return sum(price_list)


def booking_dates_assignment(apartment, year, month):
    """Assign booking dates as a first, in the middle or last day of stay.
    Necessary for display purposes in calendars."""

    Booking = apps.get_model("bookings", "Booking")
    bookings_list = Booking.objects.bookings_per_month(apartment.name, year, month)

    c = calendar.Calendar()

    dates = []
    arrival_dates = []
    departure_dates = []

    for d in c.itermonthdates(year, month):
        for booking in bookings_list:
            if d.month == month and d > booking.date_from and d < booking.date_to:
                dates.append(d.day)
            elif d.month == month and d == booking.date_from:
                arrival_dates.append(d.day)
            elif d.month == month and d == booking.date_to:
                departure_dates.append(d.day)

    dep_arr_dates = list(set(arrival_dates) & set(departure_dates))
    if dep_arr_dates:
        dates.extend(dep_arr_dates)

    bookings_dates_dict = {
        "apartment": apartment,
        "dates": dates,
        "arr_dates": arrival_dates,
        "dep_dates": departure_dates,
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
