from datetime import date
from django.db import models
from django.db.models import Q


class BookingManager(models.Manager):
    """Search manager for Apartment Model"""

    def bookings_per_month(self, apartment, year, month, next_month):
        result = self.filter(
            Q(apartment__name=apartment)
            & Q(date_to__gte=date(year,month,1))
            & Q(date_to__lt=date(year,next_month,1))
        )
        return result

