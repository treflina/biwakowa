import django_filters
from django.forms.widgets import DateInput, Select

from apartments.models import Apartment

from .models import Booking


class BookingsFilter(django_filters.FilterSet):
    apartment = django_filters.ChoiceFilter(
        choices=[],
        field_name="apartment__name",
        lookup_expr="iexact",
        label="Apartament",
        widget=Select(
            attrs={
                "class": "rounded-md border-gray-300",
            },
        ),
    )
    arrival = django_filters.DateFilter(
        field_name="date_from",
        lookup_expr="gte",
        label="Od:",
        widget=DateInput(
            format="%d.%m.%y",
            attrs={
                "class": "rounded-md border-gray-300",
                "type": "date",
            },
        ),
    )
    departure = django_filters.DateFilter(
        field_name="date_to",
        lookup_expr="lte",
        label="Do:",
        widget=DateInput(
            format="%d.%m.%y",
            attrs={
                "class": "rounded-md border-gray-300",
                "type": "date",
            },
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters["apartment"].extra["choices"] = [
            (name, name)
            for name in Apartment.objects.values_list("name", flat=True)
        ]

    class Meta:
        model = Booking
        fields = ["arrival", "departure"]
