# Generated by Django 4.2.13 on 2024-05-21 08:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bookings", "0003_remove_booking_customer_booking_guest"),
    ]

    operations = [
        migrations.AlterField(
            model_name="booking",
            name="notes",
            field=models.TextField(
                blank=True, null=True, verbose_name="additional information"
            ),
        ),
    ]
