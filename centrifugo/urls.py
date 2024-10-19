from django.urls import path

from . import views

urlpatterns = [
    path("centrifugo/connect/", views.centrifugo_connect),
    path("centrifugo/subscribe/", views.centrifugo_subscribe),
]
