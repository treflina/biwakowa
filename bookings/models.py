from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import BookingManager


class Booking(models.Model):
    TRANSACTION_STATUS = [
        ("unpaid", _("unpaid")),
        ("success",_("success"),),
        ("failed", _("failed")),
        ("pending", _("pending")),
    ]

    BOOKING_STATUS = [
        ("pending", "niepotwierdzono"),
        ("confirmed", "potwierdzono"),
        ("cancelled", "anulowano"),
    ]

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    # TODO remove null True,
    apartment = models.ForeignKey(
        "apartments.Apartment", on_delete=models.PROTECT
    )
    date_from = models.DateField(_("date from"))
    date_to = models.DateField(_("date to"))
    guest = models.CharField(
        _("guest's name"), max_length=255, blank=True, null=True
    )
    phone = models.CharField(
        _("phone number"), max_length=255, blank=True, null=True
    )
    email = models.EmailField(_("email"), blank=True, null=True)
    address = models.CharField(
        "Adres", max_length=255, blank=True, null=True
    )
    total_price = models.DecimalField(
        _("total price"), decimal_places=2, max_digits=7, null=True, blank=True
    )
    paid = models.BooleanField(_("paid"), default=False, blank=True)
    status = models.CharField(
        "status",
        max_length=255,
        default="pending",
        blank=True,
        choices=BOOKING_STATUS,
    )
    cancellation_email_sent = models.BooleanField(
        _("cancellation email sent"), default=False
        )
    confirmation_email_sent = models.BooleanField(
        _("confirmation email sent"), default=False
    )
    notes = models.TextField(
        _("additional information"), null=True, blank=True
    )
    stripe_checkout_id = models.TextField(
        _("stripe transaction id"), null=True, blank=True
    )
    stripe_transaction_status = models.CharField(
        _("transaction status"),
        max_length=255,
        default="unpaid",
        choices=TRANSACTION_STATUS,
    )

    objects = BookingManager()

    @property
    def nights_num(self):
        return (self.date_to - self.date_from).days

    def __str__(self):
        return f"{self.apartment.name}: {self.date_from} - {self.date_to}"

    def as_dict(self):
        excluded = ["stripe_checkout_id", "stripe_transaction_status"]
        return dict(
            (f.name, getattr(self, f.name))
            for f in self._meta.fields
            if f.name not in excluded
        )
