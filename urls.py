from django.urls import path, re_path

from . import views

app_name = "open"

contentpatterns = [
    path("mondai", views.mondai, name="mondai"),
    path("mondai/show/<int:id>", views.mondai_show, name="mondai_show"),
] # yapf: disable
