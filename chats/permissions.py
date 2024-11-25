from rest_framework.generics import get_object_or_404
from rest_framework.permissions import BasePermission

from .models import Chat


class IsChatMember(BasePermission):
    def has_permission(self, request, view):
        chat_id = view.kwargs.get("id")
        chat = get_object_or_404(Chat, id=chat_id)
        return chat.members.filter(id=request.user.id).exists()


class IsChatCreator(BasePermission):
    def has_permission(self, request, view):
        chat_id = view.kwargs.get("id")
        chat = get_object_or_404(Chat, id=chat_id)

        if chat.is_private:
            return chat.is_private

        return chat.creator and chat.creator.id == request.user.id
