from django.db import models
from django.utils.translation import gettext_lazy as _


class Customer(models.Model):
    name = models.CharField(_("Customer's name"), max_length=255)
    phone = models.CharField(_("Phone"), max_length=20)
    email = models.EmailField()

    def __str__(self):
        return self.name
