from django.urls import path

from .views import index, feedView

urlpatterns = [
    path("", index),
    path("feed/", feedView),
]
