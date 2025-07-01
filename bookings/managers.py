from calendar import monthrange
from datetime import date
from django.db import models
from django.db.models import Q


class BookingManager(models.Manager):
    """Search manager for Booking Model"""

    def bookings_per_month(self, apartment, year, month):
        month_start = date(year, month, 1)
        last_day = monthrange(year, month)[1]
        month_end = date(year, month, last_day)

        return self.filter(
            apartment__id=apartment.id,
            date_from__lte=month_end,
            date_to__gte=month_start
            ).exclude(status='cancelled')

    def bookings_periods(self, apartment, arrival, departure):
        result = self.filter(
            Q(apartment__id=apartment.id)
            & Q(date_from__lt=departure)
            & Q(date_to__gt=arrival)
            ).exclude(status='cancelled')

        return result
