from django.db import models

from wagtail.models import Page
from wagtail.admin.panels import FieldPanel, MultiFieldPanel


class HomePage(Page):
    template = "home/home_page.html"

    banner_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    alt_attr = models.TextField(
        blank=False,
        null=True,
        verbose_name="Opis alternatywny",
        help_text="""Opisz co przedstawia zdjęcie główne.""",
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("banner_image"),
                FieldPanel("alt_attr"),
            ],
            heading="Zdjęcie główne",
        ),

    ]
