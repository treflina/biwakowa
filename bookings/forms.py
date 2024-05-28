import datetime

from django.core.exceptions import ValidationError
from django.forms import (
    Form,
    ModelForm,
    TextInput,
    EmailInput,
    IntegerField,
    DateField,
    DateInput,
    NumberInput,
    CheckboxInput,
    Select,
    Textarea
)
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import datetime

from .models import Booking



class BookingBaseForm(ModelForm):
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





