import datetime as dt
import re

from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.forms import (
    CheckboxInput, DateInput, EmailInput, NumberInput, Select, Textarea,
    TextInput,
)
from django.utils.translation import gettext_lazy as _

from apartments.models import Apartment
from home.models import PhoneSnippet

from .models import Booking


def error_msg(msg):
    phone = PhoneSnippet.objects.last()
    err_msg_dict = {
        "MIN_7_NIGHTS": (
            f"Minimalna długość pobytu w okresie wakacyjnym wynosi 7 nocy \
            przy rezerwacjach dokonywanych ponad tydzień \
            przed planowanym przyjazdem.\n \
            W razie wątpliwości zachęcamy do kontaktu pod nr tel. {phone}"
        ),
        "FIRST_DAY_SUNDAY": (
            f"Rezerwacja pobytu w okresie wakacyjnym \
            jest możliwa jedynie na pełny tydzień od niedzieli do niedzieli \
            (przy rezerwacjach dokonywanych ponad tydzień przed \
            planowanym przyjazdem).\n \
            W razie wątpliwości zachęcamy do kontaktu pod nr tel. {phone}"
        ),
    }
    return err_msg_dict.get(msg)


def validate_arrival_and_departure_dates(arrival, departure):
    today = dt.date.today()

    if not arrival or not departure:
        raise ValidationError(_("Please provide both dates."))
    else:
        if arrival >= departure:
            raise ValidationError(
                _("Start date cannot be later or the same as end date")
            )
        if arrival < today or departure < today:
            raise ValidationError(_("Selected date can't be a past date."))
        # if arrival.month in [7, 8] and departure.month in [7, 8]:
        #     if (departure - arrival).days < 7 and ((arrival - today).days > 7):
        #         raise ValidationError(error_msg("MIN_7_NIGHTS"))
        #     if (arrival - today).days > 7 and arrival.weekday() != 6:
        #         raise ValidationError(error_msg("FIRST_DAY_SUNDAY"))
        if (departure - arrival).days < 3:
            raise ValidationError(_("Minimum 3-nights stay required."))


class BookingBaseForm(forms.ModelForm):

    YES_NO_CHOICES = (
        # ('none', '-----'),
        ('yes', 'Tak'),
        ('no', 'Nie'),
    )

    paid = forms.TypedChoiceField(
        required=False,
        coerce=lambda x: x =='True',
        choices=((False, 'Nie'), (True, 'Tak')), widget=Select(
        attrs={"class": "rounded-md"})
        )
    notification = forms.ChoiceField(
        choices=YES_NO_CHOICES,
        label='Wysłano powiadomienie',
        required=False,
        widget=Select(
            attrs={"class": "rounded-md"}
        )
    )

    class Meta:
        model = Booking
        fields = [
            "apartment",
            "date_from",
            "date_to",
            "guest",
            "phone",
            "email",
            "address",
            "total_price",
            "status",
            "notification",
            "paid",
            "notes",
        ]

        widgets = {
            "apartment": Select(
                attrs={"class": "rounded-md", "placeholder": _("Apartment")}
            ),
            "date_from": DateInput(
                attrs={
                    "class": "rounded-md",
                    "placeholder": _("Date from"),
                    "type": "date",
                }
            ),
            "date_to": DateInput(
                attrs={
                    "class": "rounded-md",
                    "placeholder": _("Date to"),
                    "type": "date",
                }
            ),
            "guest": TextInput(
                attrs={"class": "rounded-md", "placeholder": _("Guest's name")}
            ),
            "phone": TextInput(
                attrs={"class": "rounded-md", "placeholder": _("Phone")}
            ),
            "email": EmailInput(
                attrs={
                    "class": "rounded-md",
                    "placeholder": "Email",
                    "type": "email",
                }
            ),
            "address": TextInput(
                attrs={"class": "rounded-md", "placeholder": "Adres"}
            ),

            "total_price": NumberInput(
                attrs={
                    "class": "rounded-md",
                }
            ),
            "status": Select(
                attrs={
                    "class": "rounded-md",
                }
            ),
            "notes": Textarea(
                attrs={
                    "rows": 3,
                    "class": "rounded-md w-full",
                    "required": False,
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance:
            if instance.status == "confirmed":
                self.fields['notification'].choices = self.YES_NO_CHOICES
                if instance.confirmation_email_sent:
                    self.fields['notification'].initial = 'yes'
                else:
                    self.fields['notification'].initial = 'no'

            elif instance.status == "cancelled":
                self.fields['notification'].choices = self.YES_NO_CHOICES
                if instance.cancellation_email_sent:
                    self.fields['notification'].initial = 'yes'
                else:
                    self.fields['notification'].initial = 'no'
            else:
                self.fields['notification'].widget.attrs['style'] = "background-color: #f3f3f3;"
                self.fields['notification'].initial = 'no'
        else:
            self.fields['notification'].initial = 'no'
            self.fields['notification'].widget.attrs['disabled'] = True

    def save(self, commit=True):
        instance = super().save(commit=False)
        notification = self.cleaned_data.get('notification')

        if instance.status == "confirmed":
            instance.confirmation_email_sent = (notification == 'yes')
            instance.cancellation_email_sent = False
        elif instance.status == "cancelled":
            instance.cancellation_email_sent = (notification == 'yes')
            instance.confirmation_email_sent = False
        else:  # pending
            instance.confirmation_email_sent = False
            instance.cancellation_email_sent = False

        if commit:
            instance.save()
        return instance

    def clean(self):
        cleaned_data = super().clean()
        if self.fields['notification'].widget.attrs.get('disabled'):
            cleaned_data['notification'] = 'no'

        notification = cleaned_data.get('notification')
        if not notification:
            cleaned_data['notification'] = 'no'
        return cleaned_data

    #     status = cleaned_data.get("status")
    #     notification = cleaned_data.get("notification")

    #     if not status or not notification or notification == 'none':
    #         return cleaned_data

    #     if status == "confirmed" and notification == "cancellation":
    #         raise ValidationError(
    #             "Nie można zapisać powiadomienia o anulowaniu przy rezerwacji o statusie 'potwierdzone'"
    #             )

    #     if status == "cancelled" and notification == "confirmation":
    #         raise ValidationError(
    #             "Nie można zapisać powiadomienia o potwierdzeniu przy rezerwacji o statusie 'anulowane'"
    #             )

    #     if status == "pending" and (
    #         notification == "cancellation" or notification == "confirmation"
    #     ):
    #         raise ValidationError(
    #             "Nie można zapisać powiadomienia o potwierdzeniu ani anulowaniu przy rezerwacji o statusie 'oczekuje'."
    #         )


class BookingForm(BookingBaseForm):
    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get("date_from")
        date_to = cleaned_data.get("date_to")
        apartment = cleaned_data.get("apartment")
        if date_from and date_to:
            if date_from >= date_to:
                raise ValidationError(
                    _("Start date cannot be later or the same as end date")
                )
            qs = Booking.objects.bookings_periods(
                apartment, date_from, date_to
            )
            if qs.exists():
                raise ValidationError(
                    _("There is already a booking in the given date range.")
                )
            return cleaned_data


class BookingUpdateForm(BookingBaseForm):
    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get("date_from")
        date_to = cleaned_data.get("date_to")
        if date_from and date_to and date_from >= date_to:
            raise ValidationError(
                _("Start date cannot be later or the same as end date")
            )
        return cleaned_data


class OnlineBookingForm(forms.Form):
    arrival = forms.DateField()
    departure = forms.DateField()

    def clean(self):
        cleaned_data = super().clean()
        arrival = cleaned_data.get("arrival")
        departure = cleaned_data.get("departure")

        validate_arrival_and_departure_dates(arrival, departure)


class OnlineBookingDetailsForm(forms.Form):
    input_class = """xssm:basis-3/5 flex-grow w-full xssm:max-w-[350px]
        rounded-md border-2
        focus:outline-none border-2 border-blue-300 text-gray-900
        rounded-md focus:ring-amber-300 focus:border-amber-300
        block  p-2.5  dark:bg-gray-700 dark:border-gray-600
        dark:placeholder-gray-400
        dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"""

    error_css_class = "text-red-700 font-semibold mt-2 text-center"

    arrival = forms.DateField(required=True, widget=forms.HiddenInput)
    departure = forms.DateField(required=True, widget=forms.HiddenInput)
    pk = forms.IntegerField(required=True, widget=forms.HiddenInput)
    name = forms.CharField(
        required=True, widget=forms.TextInput(attrs={"class": input_class})
    )
    email = forms.EmailField(
        required=True, widget=forms.TextInput(attrs={"class": input_class})
    )
    phone = forms.CharField(
        required=True, widget=forms.TextInput(attrs={"class": input_class})
    )
    address = forms.CharField(
        required=True, widget=forms.TextInput(attrs={"class": input_class})
    )
    guest_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 2,
                "class": input_class,
            }
        ),
    )

    consent = forms.BooleanField(
        error_messages={"required": _("You must confirm rodo")},
        widget=forms.CheckboxInput(
            attrs={
                "class": "w-5 h-5 text-blue-600 bg-gray-100 \
                border-gray-300  rounded focus:ring-blue-500 focus:ring-2 mx-2"
            }
        ),
    )

    def __init__(self, *args, request=None, **kwargs):
        super(OnlineBookingDetailsForm, self).__init__(*args, **kwargs)
        self.request = request
        if request is not None:
            self.session = request.session

    def clean_pk(self):
        pk = self.cleaned_data.get("pk")
        try:
            Apartment.objects.get(id=pk)
        except Apartment.DoesNotExist:
            raise ValidationError(_(f"Apartment with id {pk} was not found"))
        return pk

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if len(name) < 5:
            raise ValidationError(_("Invalid name has been provided."))
        return name

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if not re.fullmatch(r"(^[\d +'\''/'-()eklonmtw.]*$)", phone):
            raise ValidationError(_("Invalid phone number has been provided."))
        if len(phone) < 7 or len(phone) > 25:
            raise ValidationError(_("Invalid phone number has been provided."))
        return phone

    def clean(self):
        super().clean()
        arrival = self.cleaned_data.get("arrival")
        departure = self.cleaned_data.get("departure")
        email = self.cleaned_data.get("email")
        apartment_id = self.cleaned_data.get("pk")

        validate_arrival_and_departure_dates(arrival, departure)

        def check_booked_periods(session_email=False):
            qs = Booking.objects.filter(
                Q(apartment__id=apartment_id)
                & Q(date_to__gt=arrival)
                & Q(date_from__lt=departure)
            ).exclude(status="cancelled")

            if session_email:
                qs_check = qs.exclude(
                    Q(stripe_transaction_status="pending")
                    & (Q(email=email) | Q(email=session_email))
                ).exists()
            else:
                qs_check = qs.exclude(
                    Q(stripe_transaction_status="pending") & Q(email=email)
                ).exists()
            if qs_check is True:
                raise ValidationError(
                    _("There is already a booking in the given date range.")
                )

        if hasattr(self, "session"):
            session_email = self.session.get("email", None)
            check_booked_periods(session_email)
        else:
            check_booked_periods()
