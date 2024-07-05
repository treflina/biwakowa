from django.db import models
from django.utils.translation import gettext_lazy as _

from modelcluster.fields import ParentalKey
from wagtail.models import Orderable, Page
from wagtail.snippets.models import register_snippet
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel


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
        verbose_name_plural = _("emails")


class HomePage(Page):
    template = "home/home_page.html"
    max_count = 1

    subtitle = models.CharField(_("subtitle"), max_length=50, null=True, blank=True)
    paragraph1 = models.TextField(_("paragraph 1"), null=True, blank=True)
    paragraph2 = models.TextField(_("paragraph 2"), null=True, blank=True)
    signature1 = models.CharField(_("signature 1"), max_length=40, null=True, blank=True, help_text=_("in bold"))
    signature2 = models.CharField(_("signature 2"), max_length=40, null=True, blank=True)


    class Meta:
        verbose_name = _("Home Page")


    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [InlinePanel('header_images', max_num=3, min_num=3, label=_("Image"))],
            heading=_("Header images")
            ),
        MultiFieldPanel(
            [
            FieldPanel("paragraph1"),
            FieldPanel("paragraph2"),
            FieldPanel("signature1"),
            FieldPanel("signature2")
            ], heading=_("About us")
        ),
        MultiFieldPanel(
            [InlinePanel('lake_images', max_num=3, min_num=3, label=_("Image"))],
            heading=_("Lake images")
            ),
    ]


class HeaderImage(Orderable):
    page = ParentalKey(HomePage, on_delete=models.CASCADE, related_name='header_images')
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    alt_attr = models.CharField(_("alternative text"), max_length=255)

    panels = [
        FieldPanel('image'),
        FieldPanel('alt_attr'),
    ]


class LakeImage(Orderable):
    page = ParentalKey(HomePage, on_delete=models.CASCADE, related_name='lake_images')
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    alt_attr = models.CharField(_("alternative text"), max_length=255)

    panels = [
        FieldPanel('image'),
        FieldPanel('alt_attr'),
    ]
