from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, ListView, UpdateView

from .forms import BookingForm
from .models import Booking


class BookingListView(LoginRequiredMixin, ListView):
    """Bookings listing page."""

    # filterset_class = SickleavesFilter
    queryset = Booking.objects.all()
    context_object_name = "bookings"
    template_name = "bookings/bookings.html"
    login_url = reverse_lazy("users_app:user-login")
    paginate_by = 20



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
    template_name = "bookings/update-booking.html"
    fields = "__all__"
    success_url = reverse_lazy("bookings_app:bookings")
    login_url = reverse_lazy("users_app:user-login")


@login_required(login_url="users_app:user-login")
def delete_booking(request, pk):
    """Deletes booking."""
    Booking.objects.get(id=pk).delete()
    return HttpResponseRedirect(reverse("bookings_app:bookings"))
