from django.urls import path

from .views import (
    MessageDetail,
    MessageListCreateView,
    read_all_messages,
    read_message,
)

urlpatterns = [
    path(
        "messages/",
        MessageListCreateView.as_view(),
        name="message-list-create",
    ),
    path("messages/read_all/", read_all_messages, name="messages-read"),
    path("message/<uuid:id>/", MessageDetail.as_view(), name="message-detail"),
    path("message/<uuid:id>/read/", read_message, name="message-read"),
]
