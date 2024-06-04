from django.contrib import admin

from .models import Apartment, ApartmentType, Price

admin.site.register(Apartment)
admin.site.register(ApartmentType)
admin.site.register(Price)
