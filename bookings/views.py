import calendar
import logging
import stripe
import time
from datetime import date, datetime
from django_filters import views
from webpush import send_user_notification

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.utils.html import strip_tags
from django.utils.timezone import datetime
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, UpdateView, DetailView
from django.views.decorators.csrf import csrf_exempt

from apartments.models import Apartment
from home.models import PhoneSnippet, AdminEmail
from bookings.utils import get_next_prev_month, booking_dates_assignment
from .filters import BookingsFilter
from .forms import (
    BookingForm,
    BookingUpdateForm,
    OnlineBookingForm,
    OnlineBookingDetailsForm,
)
from .models import Booking
from .utils import calculated_price, handle_error_notification

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
        # TODO REMOVE
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
        return render(request, "bookings/onlinebookingdetails.html", context=context)

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
                err_subject = _("Error. No stripe product_id")
                err_msg = f"No stripe id for apartment {ap_to_book.name}. \
                    Booking details: {guest} {guest_phone} {email} \
                    from {arrival} to {departure} \
                    notes: {guest_notes}"
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
                logger.error(f"Błąd podczas próby płatności: {e}.")
                phone = PhoneSnippet.objects.last()

                messages.error(
                    request,
                    f"Bardzo nam przykro, ale wystąpił problem \
                            z połączeniem internetowym podczas \
                            próby utworzenia płatności. \n \
                            Spróbuj ponownie lub zarezerwuj telefonicznie pod nr {phone}.",
                )
                return redirect("bookings_app:booking-search")

            except Exception as ex:
                logger.error(f"Błąd podczas próby płatności: {ex}.")
                phone = PhoneSnippet.objects.last()

                messages.error(
                    request,
                    f"Bardzo nam przykro, ale wystąpił problem podczas próby utworzenia \
                            płatności. \n \
                            Spróbuj ponownie lub zarezerwuj telefonicznie pod nr {phone}.",
                )
                err_subject = "Error while creating checkout session or db saving"
                err_msg = f"{ex} while booking apartment {ap_to_book.name}. \
                    Booking details: {guest} {guest_phone} {email} \
                    from {arrival} to {departure} \
                    notes: {guest_notes}"
                handle_error_notification(err_subject, err_msg)
                return redirect("bookings_app:booking-search")

        else:
            context["form"] = form
    return render(request, "bookings/onlinebookingdetails.html", context=context)


def success(request):
    for key in list(request.session.keys()):
        if not key.startswith("_"): # skip keys set by the django system
            del request.session[key]
    # stripe.api_key = settings.STRIPE_SECRET_KEY
    # checkout_session_id = request.GET.get('session_id', None)
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
        logger.error(f"Stripe-webhook error: {e}")
        return HttpResponse(status=400)
    except Exception as e:
        error_subj = "Webhook error"
        error_msg = f"{e}"
        handle_error_notification(error_subj, error_msg)
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        session_id = session.get("id", None)

        try:
            booking = Booking.objects.get(stripe_checkout_id=session_id)
        except Booking.DoesNotExist:
            booking = None
            error_subj = _("Session completed, booking not found")
            error_msg = f"""Session completed (session id: {session_id})
                webhook was sent, but related booking was not found
                in the database.
                """
            handle_error_notification(error_subj, error_msg)

        if booking and session.payment_status == "paid":
            booking.stripe_transaction_status = "success"
            booking.paid = True
            booking.save()

            from_email = settings.EMAIL_HOST_USER
            hotel_email = AdminEmail.objects.last()
            subject = (
                f"Rezerwacja Ap. nr {booking.apartment.name} od {booking.date_from}"
            )
            notes = booking.notes if booking.notes else "-"
            url = f"{reverse('bookings:booking', kwargs={'pk': booking.id})}"
            msg = f"""Nowa rezerwacja: #{booking.id} \n
    Apartament nr {booking.apartment.name} \n
    od {booking.date_from} do {booking.date_to} \n
    Gość: {booking.guest} \n
    Uwagi gościa: {notes} \n
    utworzona: {booking.created_at} \n
    Zobacz: {url}"""

            # send email to hotel
            try:
                send_mail(subject, msg, from_email, [hotel_email])
            except Exception as e:
                error_subj = "Confirmation email not sent for booking"
                error_msg = (
                    f"Confirmation email not sent for booking num {booking.id}. {e}"
                )
                handle_error_notification(error_subj, error_msg)

            # send webpush notification to hotel
            try:
                hotel = User.objects.filter(email=hotel_email).last()
                payload = {
                    "head": subject,
                    "body": f"Nowa rezerwacja: #{booking.id}",
                    "url":url
                    }
                send_user_notification(user=hotel, payload=payload, ttl=1000)
            except User.DoesNotExist:
                hotel = None
                logger.error("Notification not sent. User doesn't exist.")
            except Exception as e:
                logger.error(f"{e}")

            # send email to guest
            try:
                hotel_phone = PhoneSnippet.objects.last()
                subject = "Potwierdzenie rezerwacji B4B"
                html_message = render_to_string(
                    "bookings/confirmation-email.html",
                    {"booking": booking, "phone": hotel_phone},
                )
                plain_message = strip_tags(html_message)
                to = booking.email
                send_mail(
                    subject, plain_message, from_email, [to], html_message=html_message
                )
            except Exception as e:
                error_subj = "Sending confirmation email failed"
                error_msg = f"Confirmation email not sent for {booking}. {e}"
                handle_error_notification(error_subj, error_msg)

    elif event["type"] == "checkout.session.expired":
        session = event["data"]["object"]
        session_id = session.get("id", None)
        try:
            booking = Booking.objects.get(stripe_checkout_id=session_id)
            booking.delete()
        except Booking.DoesNotExist:
            logger.error(
                f"""Session expired (session id: {session_id}) webhook was sent,
                but related booking was not found in the database.
                """
            )
    return HttpResponse(status=200)
