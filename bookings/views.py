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
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy, reverse
from django.utils.timezone import datetime
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, UpdateView, DetailView
from django.views.decorators.csrf import csrf_exempt

from apartments.models import Apartment
from apartments.forms import OnlineBookingForm
from bookings.utils import get_next_prev_month, booking_dates_assignment
from .filters import BookingsFilter
from .forms import BookingForm, BookingUpdateForm, OnlineBookingDetailsForm
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
    ordering = ['-date_from']

    def get_template_names(self):
        if self.request.htmx and not self.request.htmx.history_restore_request:
            return "bookings/fragments/booking-table.html"
        return "bookings/bookings.html"


def booking_search(request, year=None, month=None):

    if request.htmx and not request.htmx.history_restore_request:
        templ = "apartments/fragments/booking-calendar.html"
    else:
        templ= "bookings/bookings-search.html"

    if month is None:
        month = date.today().month
    if year is None:
        year = date.today().year

    year=int(year)
    month=int(month)

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
        'ap3_dates': ap3_bookings_dict,
        'ap4_dates': ap4_bookings_dict,
        'form': OnlineBookingForm()
    }

    if 'submit' in request.GET:
        form = OnlineBookingForm(request.GET)
        if form.is_valid():
            arrival = datetime.strptime(request.GET.get("arrival"), '%Y-%m-%d').date()
            departure = datetime.strptime(request.GET.get("departure"), '%Y-%m-%d').date()

            available_apartments = []
            apartments = Apartment.objects.all()
            for apartment in apartments:
                if not Booking.objects.bookings_periods(apartment, arrival, departure).exists():
                    price = calculated_price(apartment, arrival, departure)
                    apartment.price = price
                    available_apartments.append(apartment)

            context['available_apartments'] = available_apartments
            context["arrival"] = arrival
            context["departure"] = departure
            context["results"] = True
            context["num_nights"] = (departure - arrival).days

        else:
            context['form'] = form

    return render(request, template_name=templ, context=context)


class UpcomingBookingsListView(LoginRequiredMixin, views.FilterView):
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
        ).filter(Q(date_to__gt=start)&Q(date_from__lt=end)
                 ).exclude(
                    Q(id=self.get_object().id)).exists()
        if qs:
            form.add_error(None, _("There is already a booking in the given date range."))
            return self.form_invalid(form)
        return super().form_valid(form)


@login_required(login_url="users_app:user-login")
def delete_booking(request, pk):
    """Deletes booking."""
    Booking.objects.get(id=pk).delete()
    return HttpResponseRedirect(reverse("bookings_app:bookings"))


def onlinebooking(request, arrival=None, departure=None, pk=None):

    form = OnlineBookingDetailsForm()
    context = {}
    context["arrival"] = arrival
    context["departure"] = departure
    context["form"] = form
    context['form'].fields['arrival'].initial = arrival
    context['form'].fields['departure'].initial = departure
    context['form'].fields['pk'].initial = pk

    if request.method == "POST":
        form = OnlineBookingDetailsForm(request.POST)

        if form.is_valid():
            guest = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            phone = form.cleaned_data["phone"]
            arrival = form.cleaned_data["arrival"]
            departure = form.cleaned_data["departure"]
            ap_id = int(form.cleaned_data["pk"])

            # check if the apartment exists
            try:
                ap_to_book = Apartment.objects.get(id=ap_id)
            except Apartment.DoesNotExist:
                messages.error(request, _(f"Apartment with id {pk} was not found"))
                return render(request, "bookings/onlinebookingdetails.html", context=context)

            # check if stripe product id is specified for apartment instance
            product_id = ap_to_book.stripe_product_id
            if not product_id:
                messages.error(request, _("Booking this apartment is not possible now."))
                #TODO SEND error email
                return redirect('bookings_app:booking-search')

            total_price = calculated_price(ap_to_book, arrival, departure)

            try:
                checkout_session = stripe.checkout.Session.create(
                    payment_method_types=['card', 'p24', 'blik'],
                    line_items=[
                        {
                            "price_data": {
                                "unit_amount_decimal": total_price,
                                "currency": "pln",
                                "product": product_id,
                                },
                            "quantity": 1,

                         }
                    ],
                    customer_email=email,
                    mode='payment',
                    expires_at=int(time.time() + 1800),
                    success_url=settings.BASE_URL + "/success?session_id={CHECKOUT_SESSION_ID}",
                    cancel_url=request.build_absolute_uri(reverse("bookings_app:cancel")),
                )
                new_booking = Booking(
                    date_from=arrival,
                    date_to=departure,
                    apartment=ap_to_book,
                    total_price=total_price,
                    guest=guest,
                    phone=phone,
                    email=email,
                    # checkout_url = checkout_session.url
                    stripe_checkout_id=checkout_session.id
                )
                new_booking.save()
                return redirect(checkout_session.url, code=303)

            except Exception as e:
                #TODO email about error
                return HttpResponse(f"<p>{str(e)}</p>")

        else:
            context["form"] = form
    return render(request, "bookings/onlinebookingdetails.html", context=context)


def success(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    checkout_session_id = request.GET.get('session_id', None)
    session = stripe.checkout.Session.retrieve(checkout_session_id)
    return render(request, "bookings/success.html")


def cancel(request):
    return render(request, "bookings/cancel.html")


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
        payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        # Retrieve the session.
        session = event['data']['object']
        session_id = session.get('id', None)
        time.sleep(15)
        #TODO make try except
        booking = Booking.objects.get(stripe_checkout_id=session_id)
        if session.payment_status == "paid":
            booking.stripe_transaction_status = "success"
            booking.paid = True
            booking.save()
    elif event['type'] == 'checkout.session.expired':
        session = event['data']['object']
        session_id = session.get('id', None)
        time.sleep(15)
        booking = Booking.objects.get(stripe_checkout_id=session_id)
        booking.delete()

    # Passed signature verification
    return HttpResponse(status=200)





