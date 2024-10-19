from django.urls import path
from .views import MessageListCreateView, MessageDetail

urlpatterns = [
    path("messages/", MessageListCreateView.as_view(), name="message-list-create"),
    path("message/<uuid:id>/", MessageDetail.as_view(), name="message-detail"),
]
