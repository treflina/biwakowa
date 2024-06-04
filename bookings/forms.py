import datetime
from django.core.validators import validate_email

from django import forms
from django.core.exceptions import ValidationError

from django.forms import (
    TextInput,
    EmailInput,

    DateInput,
    NumberInput,
    CheckboxInput,
    Select,
    Textarea,
)
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import datetime

from .models import Booking
from apartments.models import Apartment



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
          "notes"
       ]

        # labels = {
        #     'name': _('Writer'),
        # }
       widgets = {
            'apartment': Select(attrs={
                'class': "rounded-md",
                'placeholder': _("Apartment")
                }),
            'date_from': DateInput(attrs={
                'class': "rounded-md",
                'placeholder': _("Date from"),
                'type': 'date'

                }),
            'date_to': DateInput(attrs={
                'class': "rounded-md",
                'placeholder': _("Date to"),
                'type': 'date'
                }),
            'guest': TextInput(attrs={
                'class': "rounded-md",
                'placeholder': _("Guest's name")
                }),
            'phone': TextInput(attrs={
                'class': "rounded-md",
                'placeholder': _("Phone")
                }),
            'email': EmailInput(attrs={
                'class': "rounded-md",
                'placeholder': 'Email',
                'type': 'email'
                }),
            'total_price': NumberInput(attrs={
                'class': "rounded-md",
                }),
            'paid': CheckboxInput(attrs={
                'class': "rounded-md",
                }),
            'notes': Textarea(attrs={
                'rows': 3,
                'class': "rounded-md w-full",
                'required': False
                }),

        }


class BookingForm(BookingBaseForm):

    def clean(self):
        super().clean()
        date_from = self.cleaned_data.get("date_from")
        date_to = self.cleaned_data.get("date_to")
        apartment = self.cleaned_data.get("apartment")
        if date_from >= date_to:
            raise ValidationError(_("Start date cannot be later or the same as end date"))
        qs = Booking.objects.filter(
            Q(apartment__id=apartment.id)
            &Q(date_to__gt=date_from)
            &Q(date_from__lt=date_to)
        ).exists()
        if qs:
            raise ValidationError(_("There is already a booking in the given date range."))


class BookingUpdateForm(BookingBaseForm):

    def clean(self):
        super().clean()
        date_from = self.cleaned_data.get("date_from")
        date_to = self.cleaned_data.get("date_to")
        # apartment = self.cleaned_data.get("apartment")
        if date_from >= date_to:
            raise ValidationError(_("Start date cannot be later or the same as end date"))


class OnlineBookingDetailsForm(forms.Form):

    arrival = forms.DateField(required=True, widget=forms.HiddenInput)
    departure = forms.DateField(required=True, widget=forms.HiddenInput)
    pk = forms.IntegerField(required=True, widget=forms.HiddenInput)
    name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(required=True)
    rodo_consent = forms.BooleanField(error_messages={'required': _('You must confirm rodo')},
            label=_("RODO"))
    rules_consent = forms.BooleanField(error_messages={'required': _('You must accept terms & conditions')},
            label=_("Terms&Conditions"))

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
        date_from = self.cleaned_data.get("arrival")
        date_to = self.cleaned_data.get("departure")
        id = self.cleaned_data.get("pk")
        if date_from >= date_to:
            raise ValidationError(_("Start date cannot be later or the same as end date"))
        qs = Booking.objects.filter(
            Q(apartment__id=id)
            &Q(date_to__gt=date_from)
            &Q(date_from__lt=date_to)
        ).exists()
        if qs:
            raise ValidationError(_("There is already a booking in the given date range."))










