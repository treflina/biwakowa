from calendar import Calendar

def booking_dates_assignment(bookings_list, year, month):
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
        dates.append(*dep_arr_dates)
    return dates, arrival_dates, departure_dates