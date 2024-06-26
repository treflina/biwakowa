from django.db import models
from django.utils.translation import gettext_lazy as _

# from modelcluster.fields import ParentalKey

from wagtail.models import Page
from wagtail.snippets.models import register_snippet
# from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel


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


#     header_heading = models.CharField(_("heading"), max_length=50)
#     header_subheading = models.CharField(_("subheading"), max_length=50)

#     content_panels = Page.content_panels + [
#         MultiFieldPanel(
#             [
#                 FieldPanel("header_heading"),
#                 FieldPanel("header_subheading"),
#                 InlinePanel(
#                     "header_images",
#                     heading="_(Header images)",
#                     label="_(Header images)",
#                     min_num=3,
#                     max_num=3
#                     ),
#             ],
#             heading="_(Header)",
#         ),
#     ]

# class HeaderImage(Orderable):
#     page = ParentalKey(HomePage, on_delete=models.CASCADE, related_name='header_images')
#     image = models.ForeignKey(
#         'wagtailimages.Image',
#         null=True,
#         blank=True,
#         on_delete=models.SET_NULL,
#         related_name='+'
#     )
#     alt_attr = models.CharField(_("alternative text"), max_length=255)

#     panels = [
#         FieldPanel('image'),
#         FieldPanel('alt_attr'),
#     ]
