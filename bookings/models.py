from datetime import timedelta

from django.utils.translation import gettext_lazy as _
from django.db import models
from django.db.models import Q

from .managers import BookingManager
from bookings.utils import get_base_price



class Booking(models.Model):

    TRANSACTION_STATUS = [
        ("unpaid", _("unpaid")),
        ("success", _("success"),),
        ("failed", _("failed")),
        ("pending",_("pending"))
    ]

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    # TODO remove null True
    apartment = models.ForeignKey("apartments.Apartment", on_delete=models.PROTECT)
    date_from = models.DateField(_("date from"))
    date_to = models.DateField(_("date to"))
    guest = models.CharField(_("guest's name"), max_length=255, blank=True, null=True)
    phone = models.CharField(_("phone number"),  max_length=255, blank=True, null=True)
    email = models.EmailField(_("email"),blank=True, null=True)
    total_price = models.DecimalField(_("total price"), decimal_places=2, max_digits=7, null=True, blank=True)
    paid = models.BooleanField(_("paid"), default=False)
    notes = models.TextField(_("additional information"), null=True, blank=True)
    stripe_checkout_id = models.TextField(_("stripe transaction id"), null=True, blank=True)
    stripe_transaction_status = models.CharField(_("transaction status"), max_length=255, default="unpaid", choices=TRANSACTION_STATUS)
    objects = BookingManager()


    def daterange(self, start_date, end_date):
        for n in range(int((end_date - start_date).days)):
            yield start_date + timedelta(n)


    @property
    def calculated_price(self):
        price_list = []
        for date in self.daterange(self.date_from, self.date_to):
            price_per_day = get_base_price(self.apartment, date)
            price_list.append(price_per_day)

        return sum(price_list)


    def __str__(self):
        return f"{self.apartment.name}: {self.date_from} - {self.date_to}"


    @property
    def nights_num(self):
        return (self.date_to - self.date_from).days
