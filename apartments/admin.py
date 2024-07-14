from django.contrib import admin

from .models import Apartment, ApartmentType, Price


class ApartmentTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "type_name")


admin.site.register(Apartment)
admin.site.register(ApartmentType, ApartmentTypeAdmin)
admin.site.register(Price)
