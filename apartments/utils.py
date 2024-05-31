from calendar import Calendar

from bookings.models import Booking

def booking_dates_assignment(apartment, year, month):
    bookings_list = Booking.objects.bookings_per_month(
                apartment.name, year, month
                )

    c=Calendar()

    dates = []
    arrival_dates = []
    departure_dates = []

    for d in c.itermonthdates(year, month):
        for booking in bookings_list:
            if d.month==month and d > booking.date_from and d < booking.date_to:
                dates.append(d.day)
            elif d.month==month and d == booking.date_from:
                arrival_dates.append(d.day)
            elif d.month==month and d == booking.date_to:
                departure_dates.append(d.day)

    dep_arr_dates = list(set(arrival_dates)&set(departure_dates))
    if dep_arr_dates:
        dates.extend(dep_arr_dates)

    bookings_dates_dict = {
        "dates": dates,
        "arr_dates": arrival_dates,
        "dep_dates": departure_dates
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
        "next_month": next_month
    }
    return calendar_months