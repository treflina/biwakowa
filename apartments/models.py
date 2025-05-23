from datetime import datetime

from django.db import models
from django.utils.translation import gettext as _
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, MultipleChooserPanel
from wagtail.fields import RichTextField
from wagtail.models import Page, Orderable
from wagtail.snippets.models import register_snippet
from wagtailmetadata.models import MetadataPageMixin


@register_snippet
class ApartmentType(models.Model):
    type_name = models.CharField(
        _("apartment's type"),
        max_length=50,
    )

    class Meta:
        verbose_name = _("apartment's type")
        verbose_name_plural = _("apartments types")

    def __str__(self):
        return self.type_name


@register_snippet
class Price(models.Model):
    amount = models.DecimalField(_("price"), max_digits=6, decimal_places=2)
    apartment_type = models.ForeignKey(ApartmentType, on_delete=models.CASCADE)
    start_date = models.DateField(_("start date"))
    end_date = models.DateField(default=None, null=True, blank=True)

    panels = [
        FieldPanel("amount"),
        FieldPanel("apartment_type"),
        FieldPanel("start_date"),
        FieldPanel("end_date"),
    ]

    class Meta:
        verbose_name = _("price")
        verbose_name_plural = _("prices")

    def __str__(self):
        start = datetime.strftime(self.start_date, "%d.%m.%Y")
        if self.end_date:
            end = datetime.strftime(self.end_date, "%d.%m.%Y")
        else:
            end = "..."
        return f"{self.amount} ({start} - {end}) {self.apartment_type}"


@register_snippet
class Apartment(models.Model):
    name = models.CharField(_("apartment's name"), max_length=50, unique=True)
    apartment_type = models.ForeignKey(ApartmentType, on_delete=models.PROTECT)
    stripe_product_id = models.CharField(
        _("stripe product id"), max_length=255, null=True, blank=True
    )
    base_price = models.DecimalField(
        _("base price"), max_digits=7, decimal_places=2, default=0
    )
    floor = models.CharField(
        _("floor"),
        choices=(("0", _("ground floor")), ("1", _("first floor"))),
        default="0",
        max_length=10,
    )
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="image",
    )

    panels = [
        FieldPanel("name"),
        FieldPanel("apartment_type"),
        FieldPanel("floor"),
        FieldPanel("image"),
        FieldPanel("stripe_product_id"),
        FieldPanel("base_price"),
    ]

    class Meta:
        ordering = ["name"]
        verbose_name = _("apartment")
        verbose_name_plural = _("apartments")

    def __str__(self):
        return self.name


class ApartmentPage(MetadataPageMixin, Page):
    template = "apartments/apartment.html"
    subpage_types = []
    parent_page_types = ["home.HomePage"]
    max_count = 2

    apartment_type = models.ForeignKey(
        ApartmentType,
        on_delete=models.PROTECT,
        related_name="apartment_type",
        null=True,
        blank=True,
        verbose_name="apartaments' type",
    )
    # TODO  remove null=True

    heading = models.CharField(_("heading"), max_length=50, null=True)
    text_1 = RichTextField(_("text"), features=["bold"], default="")
    image_1 = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="image",
    )
    caption_1 = models.CharField(_("caption"), max_length=50, null=True)

    text_2 = RichTextField(_("text"), features=["bold"], default="")
    image_2 = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="image",
    )
    caption_2 = models.CharField(_("caption"), max_length=50, null=True)

    content_panels = Page.content_panels + [
        FieldPanel("apartment_type"),
        MultiFieldPanel(
            [
                FieldPanel("heading"),
                FieldPanel("text_1"),
                FieldPanel("image_1"),
                FieldPanel("caption_1"),
            ],
            heading=_("Description part I"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("text_2"),
                FieldPanel("image_2"),
                FieldPanel("caption_2"),
            ],
            heading=_("Description part II"),
        ),
        MultipleChooserPanel(
            'gallery_images1', label="Zdjęcia pierwszy apartament", chooser_field_name="image"
        ),
        MultipleChooserPanel(
            'gallery_images2', label="Zdjęcia drugi apartament", chooser_field_name="image"
        ),
    ]

    class Meta:
        verbose_name = _("Apartment Page")

    def get_context(self, request):
        context = super(ApartmentPage, self).get_context(request)
        apartments = Apartment.objects.filter(
            apartment_type=self.apartment_type
        )
        context["apartment1"] = apartments.first()
        context["apartment2"] = apartments.last()
        return context


class ApartmentPageGalleryImage1(Orderable):
    page = ParentalKey(ApartmentPage, on_delete=models.CASCADE, related_name='gallery_images1')
    image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.CASCADE, related_name='+'
    )

    panels = [
        FieldPanel('image'),
    ]


class ApartmentPageGalleryImage2(Orderable):
    page = ParentalKey(ApartmentPage, on_delete=models.CASCADE, related_name='gallery_images2')
    image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.CASCADE, related_name='+'
    )

    panels = [
        FieldPanel('image'),
    ]