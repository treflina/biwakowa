import calendar
import logging
import stripe
import time
from datetime import date, datetime
from django_filters import views

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy, reverse
from django.utils.timezone import datetime
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, UpdateView, DetailView
from django.views.decorators.csrf import csrf_exempt

from apartments.models import Apartment
from bookings.utils import get_next_prev_month, booking_dates_assignment
from .filters import BookingsFilter
from .forms import (
    BookingForm,
    BookingUpdateForm,
    OnlineBookingForm,
    OnlineBookingDetailsForm,
)
from .models import Booking
from .utils import calculated_price

logger = logging.getLogger("django")
stripe.api_key = settings.STRIPE_SECRET_KEY


class BookingsListView(LoginRequiredMixin, views.FilterView):
    """Bookings listing page."""

    model = Booking
    context_object_name = "bookings"
    template_name = "bookings/bookings.html"
    login_url = reverse_lazy("users_app:user-login")
    filterset_class = BookingsFilter
    paginate_by = 20
    ordering = ["-date_from"]

    def get_template_names(self):
        if self.request.htmx and not self.request.htmx.history_restore_request:
            return "bookings/fragments/booking-table.html"
        return "bookings/bookings.html"


def booking_search(request, year=None, month=None):
    """Search and display available apartments."""

    context = {"form": OnlineBookingForm()}

    if "submit" in request.GET:
        form = OnlineBookingForm(request.GET)
        if form.is_valid():
            arrival = datetime.strptime(request.GET.get("arrival"), "%d.%m.%Y").date()
            departure = datetime.strptime(
                request.GET.get("departure"), "%d.%m.%Y"
            ).date()

            available_apartments = []
            apartments = Apartment.objects.all().order_by("name")

            session_email = request.session.get("email", None)

            for apartment in apartments:
                if session_email:
                    qs = Booking.objects.bookings_periods(
                        apartment, arrival, departure
                    ).exclude(email=session_email)
                else:
                    qs = Booking.objects.bookings_periods(apartment, arrival, departure)
                if not qs.exists():
                    price = calculated_price(apartment, arrival, departure)
                    apartment.price = price
                    available_apartments.append(apartment)

            context["available_apartments"] = available_apartments
            context["arrival"] = arrival
            context["departure"] = departure
            context["results"] = True
            context["num_nights"] = (departure - arrival).days
        else:
            context["form"] = form
        return render(
            request,
            template_name="bookings/fragments/search-results.html",
            context=context,
        )

    return render(
        request, template_name="bookings/bookings-search.html", context=context
    )


def calendars(request, year=None, month=None):
    """Display apartment's availability calendars"""

    if month is None:
        month = date.today().month
    if year is None:
        year = date.today().year

    year = int(year)
    month = int(month)

    first_day = calendar.monthrange(year, month)[0]
    num_days = calendar.monthrange(year, month)[1]

    cal_months = get_next_prev_month(year, month)

    ap1 = Apartment.objects.get(name="1")
    ap2 = Apartment.objects.get(name="2")
    ap3 = Apartment.objects.get(name="3")
    ap4 = Apartment.objects.get(name="4")

    ap1_bookings_dict = booking_dates_assignment(ap1, year, month)
    ap2_bookings_dict = booking_dates_assignment(ap2, year, month)
    ap3_bookings_dict = booking_dates_assignment(ap3, year, month)
    ap4_bookings_dict = booking_dates_assignment(ap4, year, month)

    context = {
        "year": year,
        "month": month,
        "displayed_month": date(year, month, 1),
        "previous_year": cal_months["previous_year"],
        "previous_month": cal_months["previous_month"],
        "next_month": cal_months["next_month"],
        "next_year": cal_months["next_year"],
        "num_days": range(1, num_days + 1),
        "first_day": first_day,
        "ap1_dates": ap1_bookings_dict,
        "ap2_dates": ap2_bookings_dict,
        "ap3_dates": ap3_bookings_dict,
        "ap4_dates": ap4_bookings_dict,
    }

    return render(request, "bookings/fragments/booking-calendar.html", context=context)


class UpcomingBookingsListView(LoginRequiredMixin, views.FilterView):
    """Upcoming bookings listing page."""

    today = datetime.today()
    queryset = Booking.objects.filter(date_from__gte=today)
    context_object_name = "bookings"
    template_name = "bookings/bookings.html"
    login_url = reverse_lazy("users_app:user-login")
    filterset_class = BookingsFilter
    paginate_by = 20
    ordering = ["date_from"]

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
        initials["date_from"] = booking_obj.date_from.strftime("%Y-%m-%d")
        initials["date_to"] = booking_obj.date_to.strftime("%Y-%m-%d")
        return initials

    def get_object(self, *args, **kwargs):
        booking = get_object_or_404(Booking, pk=self.kwargs["pk"])
        return booking

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["updating"] = True
        return context

    def form_valid(self, form):
        start = form.cleaned_data["date_from"]
        end = form.cleaned_data["date_to"]
        qs = (
            Booking.objects.filter(apartment__id=self.get_object().apartment.id)
            .filter(Q(date_to__gt=start) & Q(date_from__lt=end))
            .exclude(Q(id=self.get_object().id))
            .exists()
        )
        if qs:
            form.add_error(
                None, _("There is already a booking in the given date range.")
            )
            return self.form_invalid(form)
        return super().form_valid(form)


@login_required(login_url="users_app:user-login")
def delete_booking(request, pk):
    """Delete booking."""
    booking_to_delete = get_object_or_404(Booking, id=pk)
    booking_to_delete.delete()
    return HttpResponseRedirect(reverse("bookings_app:bookings"))


def onlinebooking(request, arrival=None, departure=None, pk=None):
    form = OnlineBookingDetailsForm(request=request)
    context = {}

    date_from = datetime.strptime(arrival, "%Y-%m-%d").date()
    date_to = datetime.strptime(departure, "%Y-%m-%d").date()

    context["arrival"] = date_from
    context["departure"] = date_to
    context["form"] = form
    context["form"].fields["arrival"].initial = arrival
    context["form"].fields["departure"].initial = departure
    context["form"].fields["pk"].initial = pk

    try:
        ap_to_book = Apartment.objects.get(id=pk)
        context["apartment"] = ap_to_book
    except Apartment.DoesNotExist:
        messages.error(request, _(f"Apartment with id {pk} was not found"))
        return render(request, "bookings/onlinebookingdetails.html", context=context)

    total_price = calculated_price(ap_to_book, date_from, date_to)
    context["price"] = total_price

    if request.method == "POST":
        form = OnlineBookingDetailsForm(request.POST, request=request)

        if form.is_valid():
            guest = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            phone = form.cleaned_data["phone"]
            arrival = form.cleaned_data["arrival"]
            departure = form.cleaned_data["departure"]
            guest_notes = form.cleaned_data["guest_notes"]
            guest_notes = f"Uwagi gościa: {guest_notes}" if guest_notes != "" else None

            # check if stripe product id is specified for apartment instance
            product_id = ap_to_book.stripe_product_id
            if not product_id:
                messages.error(
                    request, _("Booking this apartment is not possible now.")
                )
                # TODO SEND error email
                return redirect("bookings_app:booking-search")

            try:
                checkout_session = stripe.checkout.Session.create(
                    payment_method_types=["card", "p24", "blik"],
                    line_items=[
                        {
                            "price_data": {
                                "unit_amount_decimal": total_price * 100,
                                "currency": "pln",
                                "product": product_id,
                            },
                            "quantity": 1,
                        }
                    ],
                    customer_email=email,
                    mode="payment",
                    expires_at=int(time.time() + 1800),
                    success_url=settings.BASE_URL
                    + "/success?session_id={CHECKOUT_SESSION_ID}",
                    cancel_url=settings.BASE_URL
                    + "/cancel?session_id={CHECKOUT_SESSION_ID}",
                )
                new_booking = Booking(
                    date_from=arrival,
                    date_to=departure,
                    apartment=ap_to_book,
                    total_price=total_price,
                    guest=guest,
                    phone=phone,
                    email=email,
                    notes=guest_notes,
                    stripe_checkout_id=checkout_session.id,
                    stripe_transaction_status="pending",
                )
                new_booking.save()
                request.session["email"] = email
                return redirect(checkout_session.url, code=303)

            except stripe._error.APIConnectionError as e:
                logger.error(f"Błąd podczas próby płatności: {e}.")

                messages.error(
                    request,
                    _(
                        "Bardzo nam przykro, ale wystąpił problem \
                                        z połączeniem internetowym podczas \
                                        próby utworzenia płatności. \n \
                                        Spróbuj ponownie lub zarezerwuj telefonicznie pod nr 609 000 000."
                    ),
                )
                # TODO SEND error email
                return redirect("bookings_app:booking-search")

            except Exception as ex:
                logger.error(f"Błąd podczas próby płatności: {ex}.")
                messages.error(
                    request,
                    _(
                        "Bardzo nam przykro, ale wystąpił problem podczas próby utworzenia \
                                        płatności. \n \
                                        Spróbuj ponownie lub zarezerwuj telefonicznie pod nr 609 000 000."
                    ),
                )
                # TODO SEND error email
                return redirect("bookings_app:booking-search")

        else:
            context["form"] = form
    return render(request, "bookings/onlinebookingdetails.html", context=context)


def success(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    # checkout_session_id = request.GET.get('session_id', None)
    # session = stripe.checkout.Session.retrieve(checkout_session_id)
    return render(request, "bookings/success.html")


def cancel(request):
    checkout_session_id = request.GET.get("session_id", None)
    session = stripe.checkout.Session.retrieve(checkout_session_id)
    context = {"session_url": session.url}
    return render(request, "bookings/cancel.html", context=context)


@csrf_exempt
def stripe_webhook(request):
    payload = request.body

    try:
        sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
    except KeyError:
        return HttpResponse(status=403)
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Stripe-webhook error: {e}")
        return HttpResponse(status=400)
    except Exception as e:
        logger.error(f"Stripe-webhook error: {e}")
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        # Retrieve the session.
        session = event["data"]["object"]
        session_id = session.get("id", None)
        # TODO make try except
        booking = Booking.objects.get(stripe_checkout_id=session_id)
        if session.payment_status == "paid":
            booking.stripe_transaction_status = "success"
            booking.paid = True
            booking.save()
    elif event["type"] == "checkout.session.expired":
        session = event["data"]["object"]
        session_id = session.get("id", None)
        booking = Booking.objects.get(stripe_checkout_id=session_id)
        booking.delete()

    # Passed signature verification
    return HttpResponse(status=200)
