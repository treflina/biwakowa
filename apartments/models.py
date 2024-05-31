import calendar
from collections import Counter
from datetime import date, timedelta

from django.contrib import messages
from django.db import models
from django.db.models import Q
from django.shortcuts import render, redirect
from django.utils.translation import gettext as _

from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.models import Page
from wagtail.contrib.routable_page.models import RoutablePageMixin, path, re_path

from bookings.models import Booking, SearchedBooking

from .forms import OnlineBookingForm
from .utils import booking_dates_assignment, get_next_prev_month


APARTMENT_TYPES = [
    ("midi", "2-osobowy"),
    ("maxi", "4-osobowy"),
]

class Apartment(models.Model):

    name = models.CharField(_("apartment's name"), max_length=50)
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

    @path('')
    @path('calendar/')
    @path('calendar/<int:year>/<int:month>/')
    def calendar(self, request, year=None, month=None):

        form = OnlineBookingForm()

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
            'form': form
        }

        if request.method == "POST":
            form = OnlineBookingForm(request.POST)
            if form.is_valid():

                arrival = form.cleaned_data["arrival"]
                departure = form.cleaned_data["departure"]

                if not Booking.objects.bookings_periods(self.apartment1, arrival, departure).exists():
                    new_booking = SearchedBooking(apartment=self.apartment1, date_from=arrival, date_to=departure)
                    new_booking.save()
                    return render(request, 'bookings/onlinebooking.html', {"booking": new_booking})
                elif not Booking.objects.bookings_periods(self.apartment2, arrival, departure).exists():
                    new_booking = SearchedBooking(apartment=self.apartment2, date_from=arrival, date_to=departure)
                    new_booking.save()
                    return render(request, 'bookings/onlinebooking.html', {"booking": new_booking})

                else:
                    print("booked", Booking.objects.bookings_periods(self.apartment1, arrival, departure))
                    print(Booking.objects.bookings_periods(self.apartment1, arrival, departure))
                    messages.error(request, "Przykro nam, ale nie mamy wolnych apartamentów w podanym terminie.")
            else:
                self.render(request, template=templ, context_overrides=context_overrides.update({"form": form}))

        return self.render(request, template=templ, context_overrides=context_overrides)
