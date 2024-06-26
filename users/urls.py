from django.urls import path
from . import views

app_name = "users_app"

urlpatterns = [
    path("logowanie/", views.LoginUser.as_view(), name="user-login"),
    path("wyloguj/", views.LogoutView.as_view(), name="logout"),
]
