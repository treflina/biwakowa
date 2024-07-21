from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel,
)
from wagtail.models import Orderable, Page
from wagtail.snippets.models import register_snippet
from wagtailmetadata.models import MetadataPageMixin


@register_snippet
class BankAccountNumberSnippet(models.Model):
    bank_account = models.CharField(_("bank account number"), max_length=42)

    def __str__(self):
        return self.bank_account

    class Meta:
        verbose_name = _("bank account")
        verbose_name_plural = _("bank accounts")


@register_snippet
class PhoneSnippet(models.Model):
    phone = models.CharField(_("phone"), max_length=30)

    def __str__(self):
        return self.phone

    class Meta:
        verbose_name = _("phone")
        verbose_name_plural = _("phones")


@register_snippet
class AdminEmail(models.Model):
    email = models.EmailField()

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = _("email")
        verbose_name_plural = _("email")


class HomePage(MetadataPageMixin, Page):
    template = "home/home_page.html"
    max_count = 1

    subtitle = models.CharField(
        _("subtitle"), max_length=50, null=True, blank=True
    )
    paragraph1 = models.TextField(_("paragraph 1"), null=True, blank=True)
    paragraph2 = models.TextField(_("paragraph 2"), null=True, blank=True)
    signature1 = models.CharField(
        _("signature 1"),
        max_length=40,
        null=True,
        blank=True,
        help_text=_("in bold"),
    )
    signature2 = models.CharField(
        _("signature 2"), max_length=40, null=True, blank=True
    )
    image1 = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="image",
    )
    image1_alt = models.CharField(
        _("alternative text"), max_length=255, blank=True, null=True
    )
    heading_ap1 = models.CharField(
        _("heading"), max_length=60, null=True, blank=True
    )
    image_ap1 = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="image",
        related_name="image_ap1",
    )
    image_ap1_alt = models.CharField(
        _("alternative text"), max_length=255, blank=True, null=True
    )
    page_ap1 = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("link to page"),
    )
    description_ap1 = models.TextField(_("description"), null=True, blank=True)
    heading_ap2 = models.CharField(
        _("heading"), max_length=60, null=True, blank=True
    )
    image_ap2 = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="image",
        related_name="image_ap2",
    )
    image_ap2_alt = models.CharField(
        _("alternative text"), max_length=255, blank=True, null=True
    )
    description_ap2 = models.TextField(_("description"), null=True, blank=True)
    page_ap2 = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("link to page"),
    )

    class Meta:
        verbose_name = _("Home Page")

    content_panels = Page.content_panels + [
        FieldPanel("subtitle"),
        MultiFieldPanel(
            [
                InlinePanel(
                    "header_images", max_num=3, min_num=3, label=_("Image")
                )
            ],
            heading=_("Header images"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("paragraph1"),
                FieldPanel("paragraph2"),
                FieldPanel("signature1"),
                FieldPanel("signature2"),
                FieldPanel("image1"),
                FieldPanel("image1_alt"),
            ],
            heading=_("About us"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("heading_ap1"),
                FieldPanel("description_ap1"),
                PageChooserPanel("page_ap1", "apartments.ApartmentPage"),
                FieldPanel("image_ap1"),
                FieldPanel("image_ap1_alt"),
            ],
            heading=_("Apartment 1"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("heading_ap2"),
                FieldPanel("description_ap2"),
                PageChooserPanel("page_ap2", "apartments.ApartmentPage"),
                FieldPanel("image_ap2"),
                FieldPanel("image_ap2_alt"),
            ],
            heading=_("Apartment 2"),
        ),
        MultiFieldPanel(
            [
                InlinePanel(
                    "lake_images", max_num=3, min_num=3, label=_("Image")
                )
            ],
            heading=_("Lake images"),
        ),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["header_imgs"] = self.header_images.all()
        context["lake_imgs"] = self.lake_images.all()
        return context


class HeaderImage(Orderable):
    page = ParentalKey(
        HomePage, on_delete=models.CASCADE, related_name="header_images"
    )
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="",
    )
    alt_attr = models.CharField(_("alternative text"), max_length=255)

    panels = [
        FieldPanel("image"),
        FieldPanel("alt_attr"),
    ]


class LakeImage(Orderable):
    page = ParentalKey(
        HomePage, on_delete=models.CASCADE, related_name="lake_images"
    )
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="",
    )
    alt_attr = models.CharField(_("alternative text"), max_length=255)

    panels = [
        FieldPanel("image"),
        FieldPanel("alt_attr"),
    ]
