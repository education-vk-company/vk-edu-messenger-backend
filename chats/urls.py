from django.urls import path

from .views import ChatDetail, ChatListCreateView, leave_chat

urlpatterns = [
    path("chats/", ChatListCreateView.as_view(), name="chat-list-create"),
    path("chat/<uuid:id>/", ChatDetail.as_view(), name="chat-detail"),
    path("chat/<uuid:id>/leave/", leave_chat, name="chat-leave"),
]
