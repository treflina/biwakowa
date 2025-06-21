from functools import wraps

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import resolve_url


def login_required_htmx(
    function=None, login_url="login", redirect_field_name=REDIRECT_FIELD_NAME
):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated and getattr(request, "htmx", False):
                resolved_login_url = resolve_url(login_url)
                return HttpResponse(status=204, headers={"HX-Redirect": resolved_login_url})

            return login_required(
                view_func, login_url=login_url, redirect_field_name=redirect_field_name
            )(request, *args, **kwargs)

        return _wrapped_view

    if function is None:
        return decorator
    else:
        return decorator(function)