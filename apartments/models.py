import calendar
from collections import Counter
from datetime import date, timedelta

from django.db import models
from django.shortcuts import render
from django.utils.translation import gettext as _

from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.models import Page
from wagtail.contrib.routable_page.models import RoutablePageMixin, path, re_path

from bookings.models import Booking
from .forms import OnlineBookingForm
from .utils import booking_dates_assignment


APARTMENT_TYPES = [
    ("midi", "midi"),
    ("maxi", "maxi"),
]

class Apartment(models.Model):

    name = models.CharField(_("nazwa"), max_length=50)
    apartment_type = models.CharField(
        _("apartment's type"),
        max_length=50,
        choices=APARTMENT_TYPES
        )

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


    # def serve(self, request, *args, **kwargs):

    #     if request.method == "POST":
    #         form = OnlineBookingForm(request.POST)
    #         if form.is_valid():
    #             booking = form.save()
    #             print(booking)
    #     else:
    #         form = OnlineBookingForm()
    #     return render(request, 'apartments/apartment.html', {
    #         'page': self,
    #         'form': form,
    #     })


    @path('')
    @path('calendar/')
    @path('calendar/<int:year>/<int:month>/')
    def calendar(self, request, year=None, month=None):

        if request.method == "POST":
            print(request)
            form = OnlineBookingForm(request.POST)
            if form.is_valid():
                print("yes")
            else:
                print(form.errors)

        else:
            form = OnlineBookingForm()

        if month is None:
            month = date.today().month
        if year is None:
            year = date.today().year
        cal = calendar.monthrange(year, month)

        previous_year = year
        previous_month = month - 1
        if previous_month == 0:
            previous_year = year - 1
            previous_month = 12
        next_year = year
        next_month = month + 1
        if next_month == 13:
            next_year = year + 1
            next_month = 1

#TODO: filter by name defined in choicefield, add name to context
        ap1_bookings_list = (
            Booking.objects.bookings_per_month(
                self.apartment1, year, month, next_month
                ))

        ap2_bookings_list = (
           Booking.objects.bookings_per_month(
                self.apartment2, year, month, next_month
                ))

        ap1_dates, ap1_arr_dates, ap1_dep_dates = booking_dates_assignment(ap1_bookings_list, year, month)
        ap2_dates, ap2_arr_dates, ap2_dep_dates = booking_dates_assignment(ap2_bookings_list, year, month)


        if request.htmx and not request.htmx.history_restore_request:
            templ = "apartments/fragments/booking-calendar.html"
        else:
            templ= "apartments/apartment.html"

        return self.render(request, template=templ, context_overrides={
            'year': year,
            'month': month,
            'displayed_month': date(year,month,1),
            'previous_year': previous_year,
            'previous_month': previous_month,
            'next_month': next_month,
            'next_year': next_year,
            'num_days': range(1,cal[1]+1),
            'first_day': cal[0],
            'b1_dates': ap1_dates,
            'b1_arrival_dates': ap1_arr_dates,
            'b1_departure_dates': ap1_dep_dates,
            'b2_dates': ap2_dates,
            'b2_arrival_dates': ap2_arr_dates,
            'b2_departure_dates': ap2_dep_dates,
            'b1_name': self.apartment1.name,
            'b2_name': self.apartment2.name,
            'form': form
        })





