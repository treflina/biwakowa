from datetime import date
from django.db import models
from django.db.models import Q


class BookingManager(models.Manager):
    """Search manager for Apartment Model"""

    def bookings_per_month(self, apartment, year, month, next_month):
        result = self.filter(
            Q(apartment__name=apartment)
            & Q(date_to__gt=date(year,month,1))
            & Q(date_to__lt=date(year,next_month,1))
        )
        # .exclude(
        #     Q(stripe_checkout_id__isnull=False)
        #           &(Q(stripe_transaction_status="unpaid")
        #             |Q(stripe_transaction_status="failed"))
        # )
        return result

    def bookings_periods(self, apartment, arrival, departure):
        result = self.filter(
            Q(apartment__id=apartment.id)
            &Q(date_from__lt=departure)
            &Q(date_to__gt=arrival)
            )
        # .exclude(
        #     Q(stripe_checkout_id__isnull=False)
        #           &(Q(stripe_transaction_status="unpaid")
        #             |Q(stripe_transaction_status="failed"))
        # )
        return result

