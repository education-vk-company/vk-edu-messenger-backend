from rest_framework import generics, serializers
from rest_framework.permissions import BasePermission

from chats.models import Chat

from .models import Message


class IsChatMember(BasePermission):
    def has_permission(self, request, view):
        if request.method == "GET":
            chat_id = request.GET.get("chat")

            if not chat_id:
                raise serializers.ValidationError(
                    "Chat UUID is required in url"
                )

        chat = generics.get_object_or_404(Chat, id=chat_id)
        return chat.members.filter(id=request.user.id).exists()


class IsMessageChatMember(BasePermission):
    def has_permission(self, request, view):
        message_id = view.kwargs.get("id")
        message = generics.get_object_or_404(Message, id=message_id)
        return message.chat.members.filter(id=request.user.id).exists()


class IsMessageSender(BasePermission):
    def has_permission(self, request, view):
        message_id = view.kwargs.get("id")
        message = generics.get_object_or_404(Message, id=message_id)
        return message.sender and message.sender.id == request.user.id


class IsNotMessageSender(BasePermission):
    def has_permission(self, request, view):
        message_id = view.kwargs.get("id")
        message = generics.get_object_or_404(Message, id=message_id)
        return message.sender and message.sender.id != request.user.id
