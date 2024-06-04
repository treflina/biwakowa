from calendar import monthrange
from datetime import date
from django.db import models
from django.db.models import Q


class BookingManager(models.Manager):
    """Search manager for Apartment Model"""

    def bookings_per_month(self, apartment, year, month):
        num_days = monthrange(year, month)[1]
        result = self.filter(
            Q(apartment__name=apartment)
            & (
            (Q(date_to__gte=date(year,month, 1)) & Q(date_to__lte=date(year,month, num_days)))
            | (Q(date_from__gte=date(year,month,1)) & Q(date_from__lte=date(year,month, num_days)))
            )
        )
        return result

    def bookings_periods(self, apartment, arrival, departure):
        result = self.filter(
            Q(apartment__id=apartment.id)
            &Q(date_from__lt=departure)
            &Q(date_to__gt=arrival)
            )
        return result

