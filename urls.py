from django.urls import path, re_path

from . import views

app_name = "open"

contentpatterns = [
    path("mondai", views.mondai, name="mondai"),
] # yapf: disable
