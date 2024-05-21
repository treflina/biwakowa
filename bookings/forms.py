from django.forms import (
    ModelForm,
    TextInput,
    EmailInput,
    DateInput,
    NumberInput,
    CheckboxInput,
    Select,
    Textarea
)
from django.utils.translation import gettext_lazy as _

from .models import Booking

class BookingForm(ModelForm):
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