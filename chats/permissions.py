from rest_framework.permissions import BasePermission
from rest_framework.generics import get_object_or_404

from .models import Chat


class IsChatMember(BasePermission):
    def has_permission(self, request, view):
        chat_id = view.kwargs.get("id")
        return request.user.chats.filter(id=chat_id).exists()


class IsChatCreator(BasePermission):
    def has_permission(self, request, view):
        chat_id = view.kwargs.get("id")
        chat = get_object_or_404(Chat, id=chat_id)

        if chat.is_private:
            return True

        return request.user.creator.filter(id=chat_id).exists()
