# Generated by Django 4.2.13 on 2024-05-17 19:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("apartments", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Apartment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=50, verbose_name="nazwa")),
                (
                    "apartment_type",
                    models.CharField(
                        choices=[("midi", "midi"), ("maxi", "maxi")],
                        max_length=50,
                        verbose_name="apartment's type",
                    ),
                ),
            ],
        ),
    ]
