from django.urls import path
from . import views

urlpatterns = [
    path("register", views.register_client, name="register"),
    path("register_master", views.register_master, name="register_master"),
    path("login", views.login, name="login"),
    path("logout", views.logout, name="logout"),
]
