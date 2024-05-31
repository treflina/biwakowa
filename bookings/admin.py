from django.contrib import admin

from .models import Booking, SearchedBooking

admin.site.register(Booking)
admin.site.register(SearchedBooking)
