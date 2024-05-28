from django.utils.translation import gettext_lazy as _
from django.db import models

from .managers import BookingManager


class SearchedBooking(models.Model):

    apartment = models.ForeignKey("apartments.Apartment", on_delete=models.PROTECT)
    date_from = models.DateField()
    date_to = models.DateField()

    def __str__(self):
        return f"{self.apartment.name}: {self.date_from} - {self.date_to}"

    @property
    def nights_num(self):
        return (self.date_to - self.date_from).days


class Booking(models.Model):

    TRANSACTION_STATUS = [
        ("unpaid", _("unpaid")),
        ("pending", _("pending")),
        ("success", _("success"),),
        ("failed", _("failed"))
    ]

    apartment = models.ForeignKey("apartments.Apartment", on_delete=models.PROTECT)
    date_from = models.DateField()
    date_to = models.DateField()
    guest = models.CharField(_("guest's name"), max_length=255, blank=True, null=True)
    phone = models.CharField(_("phone number"),  max_length=255, blank=True, null=True)
    email = models.EmailField(_("email"),blank=True, null=True)
    total_price = models.DecimalField(_("total price"), decimal_places=2, max_digits=7, null=True, blank=True)
    paid = models.BooleanField(_("paid"), default=False)
    notes = models.TextField(_("additional information"), null=True, blank=True)
    stripe_checkout_id = models.TextField(_("stripe transaction id"), null=True, blank=True)
    stripe_transaction_status = models.CharField(_("transaction status"), max_length=255, default="unpaid", choices=TRANSACTION_STATUS)
    objects = BookingManager()

    def __str__(self):
        return f"{self.apartment.name}: {self.date_from} - {self.date_to}"

    @property
    def booking_dates_list(self):
        return pd.date_range(self.date_from, self.date_to, freq='d')


    @property
    def nights_num(self):
        return (self.date_to - self.date_from).days
