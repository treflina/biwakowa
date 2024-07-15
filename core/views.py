from django.contrib.staticfiles.storage import staticfiles_storage
from django.http import HttpResponseRedirect
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_GET


@require_GET
@cache_control(max_age=60 * 60 * 24, immutable=True, public=True)  # one day
def favicon_file(request):
    """Serve site's icons"""
    name = "favicon" + str(request.path)
    url = staticfiles_storage.url(name)
    return HttpResponseRedirect(url)
