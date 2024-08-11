from django.urls import path
from hans_ent.views import *




urlpatterns = [
    path("", index, name="hansent-home"),
]