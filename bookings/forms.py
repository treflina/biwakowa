import datetime as dt

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db.models import Q
from django.forms import (
    CheckboxInput, DateInput, EmailInput, NumberInput, Select, Textarea,
    TextInput,
)
from django.utils.translation import gettext_lazy as _

from apartments.models import Apartment
from home.models import PhoneSnippet

from .models import Booking


def get_today():
    return dt.date.today()


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


class BookingBaseForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [
            "apartment",
            "date_from",
            "date_to",
            "guest",
            "phone",
            "email",
            "total_price",
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
            "total_price": NumberInput(
                attrs={
                    "class": "rounded-md",
                }
            ),
            "paid": CheckboxInput(
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


class BookingForm(BookingBaseForm):
    def clean(self):
        super().clean()
        date_from = self.cleaned_data.get("date_from")
        date_to = self.cleaned_data.get("date_to")
        apartment = self.cleaned_data.get("apartment")
        if date_from >= date_to:
            raise ValidationError(
                _("Start date cannot be later or the same as end date")
            )
        qs = Booking.objects.filter(
            Q(apartment__id=apartment.id)
            & Q(date_to__gt=date_from)
            & Q(date_from__lt=date_to)
        ).exists()
        if qs:
            raise ValidationError(
                _("There is already a booking in the given date range.")
            )


class BookingUpdateForm(BookingBaseForm):
    def clean(self):
        super().clean()
        date_from = self.cleaned_data.get("date_from")
        date_to = self.cleaned_data.get("date_to")
        if date_from >= date_to:
            raise ValidationError(
                _("Start date cannot be later or the same as end date")
            )


class OnlineBookingForm(forms.Form):
    arrival = forms.DateField()
    departure = forms.DateField()

    def clean(self):
        cleaned_data = super().clean()
        arrival = cleaned_data.get("arrival")
        departure = cleaned_data.get("departure")

        today = get_today()
        if not arrival or not departure:
            raise ValidationError(_("Please provide both dates."))
        else:
            if arrival >= departure:
                raise ValidationError(
                    _("Start date cannot be later or the same as end date")
                )
            if arrival < today or departure < today:
                raise ValidationError(
                    "Wybrana data nie może być wcześniejsza od dzisiaj."
                )
            if arrival.month in [7, 8] and departure.month in [7, 8]:
                if (departure - arrival).days < 7 and (
                    (arrival - today).days > 7
                ):
                    raise ValidationError(error_msg("MIN_7_NIGHTS"))
                if (arrival - today).days > 7 and arrival.weekday() != 6:
                    raise ValidationError(error_msg("FIRST_DAY_SUNDAY"))
            if (departure - arrival).days < 3:
                raise ValidationError(
                    "Minimalna długość pobytu wynosi 3 doby."
                )


class OnlineBookingDetailsForm(forms.Form):
    input_class = """basis-3/5 flex-grow w-full xsm:max-w-[350px]
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

    def clean_email(self):
        email = self.cleaned_data.get("email")
        try:
            validate_email(email)
        except ValidationError:
            raise ValidationError(_("Invalid email has been provided."))
        return email

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if len(name) < 5:
            raise ValidationError(_("Invalid name has been provided."))
        return name

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if len(phone) < 7:
            raise ValidationError(_("Invalid phone number has been provided."))
        return phone

    def clean(self):
        super().clean()
        arrival = self.cleaned_data.get("arrival")
        departure = self.cleaned_data.get("departure")
        email = self.cleaned_data.get("email")
        id = self.cleaned_data.get("pk")

        today = dt.date.today()

        if not arrival or not departure:
            raise ValidationError(_("Please provide both dates."))
        else:
            if arrival >= departure:
                raise ValidationError(
                    _("Start date cannot be later or the same as end date")
                )
            if arrival < today or departure < today:
                raise ValidationError(
                    "Wybrana data nie może być wcześniejsza od dzisiaj."
                )
            if arrival.month in [7, 8] and departure.month in [7, 8]:
                if (departure - arrival).days < 7 and (
                    (arrival - today).days > 7
                ):
                    raise ValidationError(error_msg("MIN_7_NIGHTS"))
                if (arrival - today).days > 7 and arrival.weekday() != 6:
                    raise ValidationError(error_msg("FIRST_DAY_SUNDAY"))
            if (departure - arrival).days < 3:
                raise ValidationError(
                    "Minimalna długość pobytu wynosi 3 doby."
                )

        if self.session:
            session_email = self.session.get("email", None)

        qs = Booking.objects.filter(
            Q(apartment__id=id)
            & Q(date_to__gt=arrival)
            & Q(date_from__lt=departure)
        )
        if session_email is not None:
            qs_check = qs.exclude(
                Q(email=email) | Q(email=session_email)
            ).exists()
        else:
            qs_check = qs.exclude(Q(email=email)).exists()

        if qs_check:
            raise ValidationError(
                _("There is already a booking in the given date range.")
            )
