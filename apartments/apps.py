from django.apps import AppConfig
from django.db.models.signals import post_migrate


def create_required_objects(sender, **kwargs):
    from apartments.models import ApartmentType, Apartment

    if not ApartmentType.objects.filter(type_name="2-osobowy").exists():
        at = ApartmentType.objects.create(type_name="2-osobowy")
        Apartment.objects.create(apartment_type=at, name="1")
        Apartment.objects.create(apartment_type=at, name="2")

    if not ApartmentType.objects.filter(type_name="4-osobowy").exists():
        at = ApartmentType.objects.create(type_name="4-osobowy")
        Apartment.objects.create(apartment_type=at, name="3")
        Apartment.objects.create(apartment_type=at, name="4")


class ApartmentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apartments"

    def ready(self):
        post_migrate.connect(create_required_objects, sender=self)
