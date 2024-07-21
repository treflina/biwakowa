from django.db import models
from django.db.models import Q


class BookingManager(models.Manager):
    """Search manager for Booking Model"""

    #
    def bookings_per_month(self, apartment, year, month):
        result = self.filter(
            Q(apartment__id=apartment.id)
            & (
                Q(date_from__year=year) & Q(date_from__month=month)
                | Q(date_to__year=year) & Q(date_to__month=month)
            )
        )
        return result

    def bookings_periods(self, apartment, arrival, departure):
        result = self.filter(
            Q(apartment__id=apartment.id)
            & Q(date_from__lt=departure)
            & Q(date_to__gt=arrival)
        )
        return result
