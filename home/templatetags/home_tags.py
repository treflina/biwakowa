from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag(takes_context=True)
def robots(context):
    """
    Create meta tags for robots.
    """
    page = context.get("self", None)
    if page or (
        reverse("bookings_app:booking-search") in repr(context["request"])
    ):
        return mark_safe(
            '<meta name="robots" content="index, follow, archive, \
                imageindex, noodp, noydir, snippet, \
                translate, max-snippet:-1, max-image-preview:large, \
                max-video-preview:-1">'
        )
    return mark_safe('<meta name="robots" content="noindex">')
