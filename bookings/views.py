import calendar
import logging
import time
from datetime import date

import after_response
import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.timezone import datetime
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, DetailView, UpdateView
from django_filters import views

from apartments.models import Apartment
from bookings.utils import booking_dates_assignment, get_next_prev_month
from home.models import PhoneSnippet

from .filters import BookingsFilter
from .forms import (
    BookingForm, BookingUpdateForm, OnlineBookingDetailsForm,
    OnlineBookingForm,
)
from .models import Booking
from .utils import (
    WebhookResponse, calculated_price, fulfill_order, get_available_apartments,
    handle_error_notification, handle_sending_notifications_about_new_booking,
)

logger = logging.getLogger("django")
stripe.api_key = settings.STRIPE_SECRET_KEY


class BookingsListView(LoginRequiredMixin, views.FilterView):
    """Bookings listing page."""

    model = Booking
    context_object_name = "bookings"
    template_name = "bookings/bookings.html"
    login_url = reverse_lazy("login")
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
            arrival = datetime.strptime(
                request.GET.get("arrival"), "%d.%m.%Y"
            ).date()
            departure = datetime.strptime(
                request.GET.get("departure"), "%d.%m.%Y"
            ).date()
            session_email = request.session.get("email", None)

            available_apartments = get_available_apartments(
                session_email, arrival, departure
            )

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

    all_apartments = Apartment.objects.all().order_by("name")
    apartments_booking_dates = {}
    for num, apartment in enumerate(all_apartments):
        apartments_booking_dates[
            "ap{0}_dates".format(num + 1)
        ] = booking_dates_assignment(apartment, year, month)

    context = {
        **apartments_booking_dates,
        "year": year,
        "month": month,
        "displayed_month": date(year, month, 1),
        "previous_year": cal_months["previous_year"],
        "previous_month": cal_months["previous_month"],
        "next_month": cal_months["next_month"],
        "next_year": cal_months["next_year"],
        "num_days": range(1, num_days + 1),
        "first_day": first_day,
    }

    return render(
        request, "bookings/fragments/booking-calendar.html", context=context
    )


class UpcomingBookingsListView(LoginRequiredMixin, views.FilterView):
    """Upcoming bookings listing page."""

    today = datetime.today()
    queryset = Booking.objects.filter(date_from__gte=today)
    context_object_name = "bookings"
    template_name = "bookings/bookings.html"
    login_url = reverse_lazy("login")
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
    login_url = reverse_lazy("login")


class BookingCreateView(LoginRequiredMixin, CreateView):
    """Booking registration form."""

    template_name = "bookings/add-booking.html"
    model = Booking
    form_class = BookingForm
    success_url = reverse_lazy("bookings_app:bookings")
    login_url = reverse_lazy("login")


class BookingUpdateView(LoginRequiredMixin, UpdateView):
    """Booking update form."""

    model = Booking
    form_class = BookingUpdateForm
    template_name = "bookings/add-booking.html"
    success_url = reverse_lazy("bookings_app:bookings")
    login_url = reverse_lazy("login")

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
            Booking.objects.filter(
                apartment__id=self.get_object().apartment.id
            )
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


@login_required(login_url="login")
def delete_booking(request, pk):
    """Delete booking."""

    if request.method == "POST":
        booking_to_delete = get_object_or_404(Booking, id=pk)
        booking_to_delete.delete()
    return HttpResponseRedirect(reverse("bookings_app:bookings"))

def onlinebooking_without_payment(request, arrival=None, departure=None, pk=None):
    form = OnlineBookingDetailsForm(request=request)

    date_from = datetime.strptime(arrival, "%Y-%m-%d").date()
    date_to = datetime.strptime(departure, "%Y-%m-%d").date()

    context = {}
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
        return render(
            request, "bookings/onlinebookingdetails.html", context=context
        )

    total_price = calculated_price(ap_to_book, date_from, date_to)
    context["price"] = total_price

    if request.method == "POST":
        form = OnlineBookingDetailsForm(request.POST, request=request)

        if form.is_valid():
            guest = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            guest_phone = form.cleaned_data["phone"]
            arrival = form.cleaned_data["arrival"]
            departure = form.cleaned_data["departure"]
            guest_notes = form.cleaned_data["guest_notes"]
            guest_notes = f"{guest_notes}" if guest_notes != "" else None

            new_booking = Booking(
                date_from=arrival,
                date_to=departure,
                apartment=ap_to_book,
                total_price=total_price,
                guest=guest,
                phone=guest_phone,
                email=email,
                notes=guest_notes,
            )
            new_booking.save()
            request.session["booking_id"] = new_booking.id
            request.session["email"] = email
            handle_sending_notifications_about_new_booking.after_response(new_booking)
            return redirect('bookings_app:success_without_payment')

        else:
            context["form"] = form
    return render(
        request, "bookings/onlinebookingdetails2.html", context=context
    )

def success_without_payment(request):
    booking_id = request.session.get("booking_id", None)
    if booking_id is not None:
        booking = Booking.objects.filter(id=booking_id).first()
    if booking:
        return render(
        request, "bookings/success_without_payment.html", context={"booking": booking}
        )
    else:
        logger.error(f"Błąd po dokonaniu wstępnej rezerwacji.")
        return redirect("bookings_app:bookings")


def onlinebooking(request, arrival=None, departure=None, pk=None):
    form = OnlineBookingDetailsForm(request=request)

    date_from = datetime.strptime(arrival, "%Y-%m-%d").date()
    date_to = datetime.strptime(departure, "%Y-%m-%d").date()

    context = {}
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
        return render(
            request, "bookings/onlinebookingdetails.html", context=context
        )

    total_price = calculated_price(ap_to_book, date_from, date_to)
    context["price"] = total_price

    if request.method == "POST":
        form = OnlineBookingDetailsForm(request.POST, request=request)

        if form.is_valid():
            guest = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            guest_phone = form.cleaned_data["phone"]
            arrival = form.cleaned_data["arrival"]
            departure = form.cleaned_data["departure"]
            guest_notes = form.cleaned_data["guest_notes"]
            guest_notes = f"{guest_notes}" if guest_notes != "" else None

            # check if stripe product id is specified for apartment instance
            product_id = ap_to_book.stripe_product_id
            if not product_id:
                messages.error(
                    request, _("Booking this apartment is not possible now.")
                )
                err_subject = "Error. No stripe product_id"
                err_msg = (
                    f"No stripe id for apartment {ap_to_book.name}. "
                    f"Booking details: {guest} {guest_phone} {email} "
                    f"from {arrival} to {departure} "
                    f"notes: {guest_notes}"
                )
                handle_error_notification(err_subject, err_msg)

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
                    phone=guest_phone,
                    email=email,
                    notes=guest_notes,
                    stripe_checkout_id=checkout_session.id,
                    stripe_transaction_status="pending",
                )
                new_booking.save()
                request.session["email"] = email
                return redirect(checkout_session.url, code=303)

            except stripe._error.APIConnectionError as e:
                logger.error(f"Błąd podczas próby płatności: {repr(e)}.")
                phone = PhoneSnippet.objects.last()

                messages.error(
                    request,
                    (
                        f"Bardzo nam przykro, ale wystąpił problem "
                        f"z połączeniem internetowym podczas "
                        f"próby utworzenia płatności. \n "
                        f"Spróbuj ponownie lub zarezerwuj "
                        f"telefonicznie pod nr {phone}."
                    ),
                )
                return redirect("bookings_app:booking-search")

            except Exception as ex:
                logger.error(f"Błąd podczas próby płatności: {repr(ex)}.")
                phone = PhoneSnippet.objects.last()

                messages.error(
                    request,
                    (
                        f"Bardzo nam przykro, ale wystąpił problem "
                        f"podczas próby utworzenia płatności. \n"
                        f"Spróbuj ponownie lub zarezerwuj "
                        f"telefonicznie pod nr {phone}."
                    ),
                )
                err_subject = (
                    "Error while creating checkout session or db saving"
                )
                err_msg = (
                    f"{repr(ex)} while booking apartment "
                    f"{ap_to_book.name}. "
                    f"Booking details: {guest} {guest_phone} {email} "
                    f"from {arrival} to {departure} "
                    f"notes: {guest_notes}"
                )
                handle_error_notification(err_subject, err_msg)
                return redirect("bookings_app:booking-search")

        else:
            context["form"] = form
    return render(
        request, "bookings/onlinebookingdetails.html", context=context
    )


def success(request):
    for key in list(request.session.keys()):
        if key == "email":  # skip keys set by the django system
            del request.session[key]

    stripe.api_key = settings.STRIPE_SECRET_KEY
    checkout_session_id = request.GET.get("session_id", None)

    if checkout_session_id is not None:
        new_booking = fulfill_order(checkout_session_id)
        if new_booking:
            handle_sending_notifications_about_new_booking(new_booking)

    return render(request, "bookings/success.html")


def cancel(request):
    checkout_session_id = request.GET.get("session_id", None)
    session = stripe.checkout.Session.retrieve(checkout_session_id)
    phone = PhoneSnippet.objects.last()
    context = {"session_url": session.url, "phone": phone}
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
        logger.error(f"Stripe-webhook error: {repr(e)}")
        return HttpResponse(status=400)
    except Exception as e:
        err_subj = "Webhook error"
        err_msg = f"{repr(e)}"
        handle_error_notification(err_subj, err_msg)
        return HttpResponse(status=400)

    try:
        session = event["data"]["object"]
        session_id = session.get("id", None)
    except KeyError:
        err_subj = "Webhook sent, but event['data']['object'] not found"
        err_msg = err_subj + "in it's content."
        handle_error_notification(err_subj, err_msg)

    if event["type"] == "checkout.session.completed":
        new_booking = fulfill_order(session_id)
        if new_booking:
            return WebhookResponse(booking=new_booking, status=200)

    elif event["type"] == "checkout.session.expired":
        try:
            booking = Booking.objects.get(stripe_checkout_id=session_id)
            booking.delete()
        except Booking.DoesNotExist:
            logger.error(
                f"Session expired (session id: {session_id}) "
                f"webhook was sent, but related booking was "
                f"not found in the database."
            )

    else:
        error_subj = "Webhook with unexpected event type received."
        error_msg = (
            "Wehook was sent, but contains unexpected event type: "
            f"{event['type']}. Session id: {session_id}"
        )
        handle_error_notification(error_subj, error_msg)

    return HttpResponse(status=200)
