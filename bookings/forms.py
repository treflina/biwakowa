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
            apartment__id=apartment.id
        ).filter(date_to__gte=date_from, date_from__lte=date_to
                 ).exists()
        if qs:
        # if any(set(x.booking_dates_list)&set(self.booking_dates_list) for x in qs):
            raise ValidationError(_("There is already a booking in the given date range."))


class BookingUpdateForm(BookingBaseForm):

    def clean(self):
        super().clean()
        date_from = self.cleaned_data.get("date_from")
        date_to = self.cleaned_data.get("date_to")
        # apartment = self.cleaned_data.get("apartment")
        if date_from >= date_to:
            raise ValidationError(_("Start date cannot be later or the same as end date"))





