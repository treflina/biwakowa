import django_filters
from django_filters.views import FilterView

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms.widgets import DateInput, Select
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils.timezone import datetime
from django.views.generic import CreateView, UpdateView, DetailView
import django_filters.views

from apartments.models import Apartment
from .forms import BookingForm, BookingUpdateForm
from .models import Booking


class BookingsFilter(django_filters.FilterSet):
    apartment = django_filters.ChoiceFilter(
        choices=[],
        field_name="apartment__name",
        lookup_expr="iexact",
        label="Apartament",
        widget=Select(
            attrs={
                "class": "rounded-md border-gray-100",
            },
        ),
    )
    arrival = django_filters.DateFilter(
        field_name="date_from",
        lookup_expr="gte",
        label="Od:",
        widget=DateInput(
            format="%d.%m.%y",
            attrs={
                "class": "rounded-md border-gray-100",
                "type": "date",
            },
        ),
    )
    departure = django_filters.DateFilter(
        field_name="date_to",
        lookup_expr="lte",
        label="Do:",
        widget=DateInput(
            format="%d.%m.%y",
            attrs={
                "class": "rounded-md border-amber-300",
                "type": "date",
            },
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['apartment'].extra['choices'] = [
            (name, name)
            for name in Apartment.objects.values_list('name', flat=True)
        ]

    class Meta:
        model = Booking
        fields = ['arrival', 'departure']


class BookingsListView(LoginRequiredMixin, FilterView):
    """Bookings listing page."""

    model = Booking
    context_object_name = "bookings"
    template_name = "bookings/bookings.html"
    login_url = reverse_lazy("users_app:user-login")
    filterset_class = BookingsFilter
    paginate_by = 20
    ordering = ['-date_from']

    def get_template_names(self):
        if self.request.htmx and not self.request.htmx.history_restore_request:
            return "bookings/fragments/booking-table.html"
        return "bookings/bookings.html"


class UpcomingBookingsListView(LoginRequiredMixin, FilterView):
    """Upcoming bookings listing page."""
    today = datetime.today()
    queryset = Booking.objects.filter(date_from__gte=today)
    context_object_name = "bookings"
    template_name = "bookings/bookings.html"
    login_url = reverse_lazy("users_app:user-login")
    filterset_class = BookingsFilter
    paginate_by = 20
    ordering = ['date_from']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["upcoming"] = True
        return context

    def get_template_names(self):
        if self.request.htmx and not self.request.htmx.history_restore_request:
            return "bookings/fragments/booking-table.html"
        return "bookings/bookings.html"


class BookingDetailView(LoginRequiredMixin, DetailView):
    model = Booking
    login_url = reverse_lazy("users_app:user-login")


class BookingCreateView(LoginRequiredMixin, CreateView):
    """Booking registration form."""

    template_name = "bookings/add-booking.html"
    model = Booking
    form_class = BookingForm
    success_url = reverse_lazy("bookings_app:bookings")
    login_url = reverse_lazy("users_app:user-login")


class BookingUpdateView(LoginRequiredMixin, UpdateView):
    """Booking update form."""

    model = Booking
    form_class = BookingUpdateForm
    template_name = "bookings/add-booking.html"
    success_url = reverse_lazy("bookings_app:bookings")
    login_url = reverse_lazy("users_app:user-login")


    def get_initial(self):
        initials = super(BookingUpdateView, self).get_initial()
        booking_obj = self.get_object()
        initials["date_from"] = booking_obj.date_from.strftime('%Y-%m-%d')
        initials["date_to"] = booking_obj.date_to.strftime('%Y-%m-%d')
        return initials

    def get_object(self, *args, **kwargs):
        booking = get_object_or_404(Booking, pk=self.kwargs['pk'])
        return booking

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["updating"] = True
        return context

    def form_valid(self, form):
        start = form.cleaned_data["date_from"]
        end = form.cleaned_data["date_to"]
        qs = Booking.objects.filter(
            apartment__id=self.get_object().apartment.id
        ).filter(
            date_to__gte=start, date_from__lte=end
                 ).exclude(id=self.get_object().id).exists()
        if qs:
            form.add_error(None, _("There is already a booking in the given date range."))
            return self.form_invalid(form)
        return super().form_valid(form)


@login_required(login_url="users_app:user-login")
def delete_booking(request, pk):
    """Deletes booking."""
    Booking.objects.get(id=pk).delete()
    return HttpResponseRedirect(reverse("bookings_app:bookings"))
