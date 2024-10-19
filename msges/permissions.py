from rest_framework import generics, serializers
from rest_framework.permissions import BasePermission

from .models import Message


class IsChatMember(BasePermission):
    def has_permission(self, request, view):
        if request.method == "GET":
            chat_id = request.GET.get("chat")

            if not chat_id:
                raise serializers.ValidationError(
                    "Provide chat field in request URL: ?chat=UUID"
                )

        return request.user.chats.filter(id=chat_id).exists()


class IsMessageChatMember(BasePermission):
    def has_permission(self, request, view):
        message_id = view.kwargs.get("id")
        message = generics.get_object_or_404(Message, id=message_id)
        return request.user.chats.filter(id=message.chat.id).exists()


class IsMessageSender(BasePermission):
    def has_permission(self, request, view):
        message_id = view.kwargs.get("id")
        return request.user.messages.filter(id=message_id).exists()
