import calendar
from collections import Counter
from datetime import date, datetime, timedelta

from django.contrib import messages
from django.db import models
from django.db.models import Q
from django.shortcuts import render, redirect
from django.utils.translation import gettext as _

from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.models import Page
from wagtail.contrib.routable_page.models import RoutablePageMixin, path
from wagtail.snippets.models import register_snippet

from bookings.utils import booking_dates_assignment, get_next_prev_month


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


class ApartmentPage(RoutablePageMixin, Page):

    template = "apartments/apartment.html"
    content_panels = Page.content_panels + []
    ajax_template = "apartments/fragments/booking-calendar.html"

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

    @path('')
    @path('calendar/')
    @path('calendar/<int:year>/<int:month>/')
    def calendar(self, request, year=None, month=None):

        if month is None:
            month = date.today().month
        if year is None:
            year = date.today().year

        first_day = calendar.monthrange(year, month)[0]
        num_days = calendar.monthrange(year, month)[1]

        cal_months = get_next_prev_month(year, month)

        ap1_bookings_dict = booking_dates_assignment(self.apartment1, year, month)
        ap2_bookings_dict = booking_dates_assignment(self.apartment2, year, month)

        if request.htmx and not request.htmx.history_restore_request:
            templ = "apartments/fragments/booking-calendar.html"
        else:
            templ= "apartments/apartment.html"

        context_overrides = {
            'year': year,
            'month': month,
            'displayed_month': date(year,month,1),
            'previous_year': cal_months["previous_year"],
            'previous_month': cal_months["previous_month"],
            'next_month': cal_months["next_month"],
            'next_year': cal_months["next_year"],
            'num_days': range(1,num_days+1),
            'first_day': first_day,
            'ap1_dates': ap1_bookings_dict,
            'ap2_dates': ap2_bookings_dict,
            'b1_name': self.apartment1.name,
            'b2_name': self.apartment2.name,
        }



        return self.render(request, template=templ, context_overrides=context_overrides)
