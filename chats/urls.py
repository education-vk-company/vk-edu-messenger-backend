from django.urls import path
from .views import ChatListCreateView, ChatDetail

urlpatterns = [
    path("chats/", ChatListCreateView.as_view(), name="chat-list-create"),
    path("chat/<uuid:id>/", ChatDetail.as_view(), name="chat-detail"),
]
