import datetime

from django.core.exceptions import ValidationError
from django.forms import (
    Form,
    IntegerField,
    DateField,
    DateInput
    )

def get_nearest_sunday():
    today =  datetime.date.today()
    idx = (today.weekday() + 1) % 7
    sun = today + datetime.timedelta(7-idx)
    return sun

def get_today():
    return datetime.date.today()


class OnlineBookingForm(Form):
    arrival = DateField(

        widget=DateInput(attrs={
        'type': "date",
        "class": "rounded-md",
        "initial":get_nearest_sunday(),
    })
    )
    departure = DateField(
        initial=get_nearest_sunday() + datetime.timedelta(days=7),
        widget=DateInput(attrs={
        'type': "date",
        "class": "rounded-md",
    }))
    num_guests = IntegerField(min_value=1, max_value=5, initial=2)

    def clean_arrival(self):
        data = self.cleaned_data["arrival"]
        today = get_today()

        if data < today:
            raise ValidationError("Podana data zameldowania już minęła.")
        return data


    def clean_departure(self):
        data = self.cleaned_data["departure"]
        today = get_today()
        if data < today:
            raise ValidationError("Podana data wymeldowania już minęła.")
        return data


    def clean(self):
        cleaned_data = super().clean()
        arrival = cleaned_data.get("arrival")
        departure = cleaned_data.get("departure")

        today = get_today()
        add_days = 7 -  today.weekday()

        if arrival and departure:
            if arrival.month in [7,8] and departure.month in [7,8]:
                if (departure - arrival).days < 7 and (arrival - today).days > 7 + add_days:
                    raise ValidationError("Minimalna długość pobytu w okresie wakacyjnym wynosi 7 nocy. \
                        Jeśli nadal dysponujemy wolnymi apartamentami na tydzień przed \
                        planowanym pobytem, minimalna długość rezerwacji wynosi 3 doby.")
                if (arrival - today).days > 7 + add_days and arrival.weekday() != 6:
                    print(arrival.weekday())
                    raise ValidationError("Rezerwacja pobytu w okresie wakacyjnym \
                        jest możliwa jedynie na pełny tydzień od niedzieli do niedzieli. \
                        Jeśli nadal dysponujemy wolnymi apartamentami na tydzień przed \
                        planowanym pobytem, minimalna długość rezerwacji wynosi 3 doby.")
            if (departure - arrival).days < 3:
                raise ValidationError("Minimalna długość pobytu wynosi 3 doby.")

