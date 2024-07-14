from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import View
from django.views.generic.edit import FormView

from .forms import LoginForm


class LoginUser(FormView):
    """User login page"""

    template_name = "users/login.html"
    form_class = LoginForm

    def get_success_url(self):
        next_url = self.request.GET.get(
            "next", reverse("bookings_app:bookings")
        )
        return f"{self.request.build_absolute_uri(next_url)}"

    def form_valid(self, form):
        user = authenticate(
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password"],
        )
        login(self.request, user)
        return super(LoginUser, self).form_valid(form)


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return HttpResponseRedirect(reverse("users_app:user-login"))
