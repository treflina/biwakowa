from django.conf import settings

from home.models import PhoneSnippet


def biwakowa_phone(request):
    phone = PhoneSnippet.objects.last()
    return {
        "phone": phone,
    }