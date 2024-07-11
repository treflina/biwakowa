from django import template
from django.utils.safestring import mark_safe
from django.urls import reverse

register = template.Library()


@register.simple_tag(takes_context=True)
def param_replace(context, **kwargs):
    """
    Return encoded URL parameters that are the same as the current
    request's parameters, only with the specified GET parameters added or changed.
    """
    d = context["request"].GET.copy()
    for k, v in kwargs.items():
        d[k] = v
    for k in [k for k, v in d.items() if not v]:
        del d[k]
    return d.urlencode()


@register.simple_tag(takes_context=True)
def robots(context):
    """
    Create meta tags for robots.
    """
    page = context.get('self', None)
    if page or (reverse("bookings_app:booking-search") in repr(context["request"])):
            return mark_safe(
                '<meta name="robots" content="index, follow, archive, \
                imageindex, noodp, noydir, snippet, \
                translate, max-snippet:-1, max-image-preview:large, \
                max-video-preview:-1">'
                )
    return mark_safe('<meta name="robots" content="noindex">')
