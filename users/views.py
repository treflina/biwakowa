from django.contrib.auth import authenticate, login, logout

from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.views.generic import View
from django.views.generic.edit import FormView

from .forms import LoginForm


class LoginUser(FormView):
    """User login page"""

    template_name = "users/login.html"
    form_class = LoginForm
    success_url = reverse_lazy("bookings_app:bookings")

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