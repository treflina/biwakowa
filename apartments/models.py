from datetime import datetime

from django.db import models
from django.utils.translation import gettext as _

from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.models import Page
from wagtail.snippets.models import register_snippet


class ApartmentType(models.Model):
    type_name = models.CharField(
        _("apartment's type"),
        max_length=50,
        )

    def __str__(self):
        return self.type_name


@register_snippet
class Price(models.Model):
    amount = models.DecimalField(_("price"), max_digits=6, decimal_places=2)
    apartment_type = models.ForeignKey(
        ApartmentType, on_delete=models.CASCADE
        )
    start_date = models.DateField(_("start date"))
    end_date = models.DateField(default=None, null=True, blank=True)

    panels = [
        FieldPanel("amount"),
        FieldPanel("apartment_type"),
        FieldPanel("start_date"),
        FieldPanel("end_date"),
    ]


    def __str__(self):
        start = datetime.strftime(self.start_date, '%d.%m.%Y')
        if self.end_date:
            end = datetime.strftime(self.end_date, '%d.%m.%Y')
        else:
            end = "..."
        return f"{self.amount} ({start} - {end}) {self.apartment_type}"


@register_snippet
class Apartment(models.Model):

    name = models.CharField(_("apartment's name"), max_length=50, unique=True)
    apartment_type = models.ForeignKey(
        ApartmentType, on_delete=models.PROTECT
        )
    stripe_product_id = models.CharField(_("stripe product id"), max_length=255, null=True, blank=True)
    base_price = models.DecimalField(_("base price"), max_digits=7, decimal_places=2, default=0)

    panels = [
        FieldPanel("name",  read_only=True),
        FieldPanel("apartment_type", read_only=True),
        FieldPanel("stripe_product_id"),
        FieldPanel("base_price"),
    ]


    def __str__(self):
        return self.name


class ApartmentPage(Page):

    template = "apartments/apartment.html"
    content_panels = Page.content_panels + []

    apartment1 = models.ForeignKey(
        Apartment,
        on_delete=models.PROTECT,
        related_name="apartment1",
        null=True,
        blank=True
        )
    apartment2 = models.ForeignKey(
        Apartment,
        on_delete=models.PROTECT,
        related_name="apartment2",
        null=True,
        blank=True
        )

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("apartment1"),
                FieldPanel("apartment2"),
            ],
            heading="Apartamenty",
        ),
    ]




