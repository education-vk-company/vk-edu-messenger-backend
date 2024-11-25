from django.db import transaction
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import MethodNotAllowed, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from application.pagination import Pagination
from application.settings import PRODUCTION, Constants
from users.anonymization import get_bot_username

from .filters import SearchFilter
from .models import Chat
from .permissions import IsChatCreator, IsChatMember
from .serializers import (
    ChatSerializer,
    GroupChatPatchSerializer,
    GroupChatSerializer,
    IsPrivateSerializer,
    PrivateChatSerializer,
)


class ChatListCreateView(generics.ListCreateAPIView):
    pagination_class = Pagination
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]

    def get_queryset(self):
        return self.request.user.chats.all()

    def post(self, request, *args, **kwargs):
        is_private = IsPrivateSerializer(data=request.data)
        is_private.is_valid(raise_exception=True)
        is_private = is_private.validated_data.get("is_private")

        if (
            is_private
            and PRODUCTION
            and request.user.creator.filter(is_private=True).count()
            >= Constants.MAX_PRIVATE_CHATS_PER_USER
        ):
            return Response(
                {
                    "detail": f"You can't create more than {Constants.MAX_PRIVATE_CHATS_PER_USER} private chats"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (
            not is_private
            and PRODUCTION
            and request.user.creator.filter(is_private=False).count()
            >= Constants.MAX_GROUP_CHATS_PER_USER
        ):
            return Response(
                {
                    "detail": f"You can't create more than {Constants.MAX_GROUP_CHATS_PER_USER} group chats"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if is_private:
            is_fallback = self.request.GET.get("fallback") == "on"

            serializer = PrivateChatSerializer(
                data=request.data,
                context={"request": request, "is_fallback": is_fallback},
            )
        else:
            serializer = GroupChatSerializer(
                data=request.data, context={"request": request}
            )

        if serializer.is_valid():
            with transaction.atomic():
                chat = serializer.save()
                chat.updated_at = chat.created_at
                chat.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChatDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Chat.objects.all()
    http_method_names = ["get", "patch", "delete"]

    def get_queryset(self):
        return self.request.user.chats.all()

    def get_object(self):
        chat_id = self.kwargs["id"]
        return generics.get_object_or_404(Chat, id=chat_id)

    def get_permissions(self):
        if self.request.method == "GET":
            permissions = [IsAuthenticated, IsChatMember]
        else:
            permissions = [IsAuthenticated, IsChatMember, IsChatCreator]

        return [permission() for permission in permissions]

    def get_serializer_class(self):
        if self.request.method in {"GET", "DELETE"}:
            return ChatSerializer

        return GroupChatPatchSerializer

    def perform_update(self, serializer):
        if self.get_object().is_private:
            raise MethodNotAllowed("PATCH for private chats")

        with transaction.atomic():
            chat = serializer.save()
            chat.updated_at = timezone.now()
            chat.save()

    def put(self, request, *args, **kwargs):
        raise MethodNotAllowed()


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsChatMember])
def leave_chat(request, id):
    chat = generics.get_object_or_404(Chat, id=id)

    if chat.is_private:
        return Response(
            {"detail": "Chat must not be private"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if chat.creator.username == get_bot_username():
        raise PermissionDenied()

    if request.user == chat.creator:
        return Response(
            {"detail": "Creator can't leave the chat"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    with transaction.atomic():
        chat.members.remove(request.user)

        if chat.members.count() == 0:
            chat.delete()

    return Response(
        {"detail": "You leave the chat"}, status=status.HTTP_200_OK
    )
