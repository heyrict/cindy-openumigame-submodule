from django.urls import path, re_path

from . import views

app_name = "open"

urlpatterns = [
    path("mondai", views.mondai, name="mondai"),
    path("mondai/show/<int:id>", views.mondai_show, name="mondai_show"),
    path("mondai/show/<int:id>/push_ques", views.mondai_show_push_ques, name="mondai_show_push_ques"),
    path("mondai/show/<int:id>/push_answ", views.mondai_show_push_answ, name="mondai_show_push_answ"),
    path("mondai/show/<int:id>/push_chatmessage", views.mondai_show_push_chatmessage, name="mondai_show_push_chatmessage"),
] # yapf: disable
