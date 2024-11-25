from django.db import transaction
from django.utils import timezone
from rest_framework import filters, generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import MethodNotAllowed, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from application.pagination import Pagination
from application.settings import PRODUCTION
from chats.models import Chat

from .models import Message
from .permissions import (
    IsChatMember,
    IsMessageChatMember,
    IsMessageSender,
    IsNotMessageSender,
)
from .serializers import MessageCreateSerializer, MessageSerializer
from .tasks import (
    start_publishing_message,
    start_reading_chat_messages,
    start_updating_messages_limits_for_user,
)


class MessageListCreateView(generics.ListCreateAPIView):
    pagination_class = Pagination
    serializer_class = MessageCreateSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [filters.SearchFilter]
    search_fields = [
        "$text",
        "$sender__username",
        "$sender__first_name",
        "$sender__last_name",
    ]

    def get_queryset(self):
        chat_id = self.request.GET.get("chat")
        if chat_id:
            chat = generics.get_object_or_404(Chat, id=chat_id)
            return chat.messages.all()
        return Message.objects.none()

    def get_permissions(self):
        if self.request.method == "GET":
            permissions = [IsAuthenticated, IsChatMember]
        else:
            permissions = [IsAuthenticated]

        return [permission() for permission in permissions]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return MessageSerializer

        if self.request.method == "POST":
            return MessageCreateSerializer

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        chat_id = request.data.get("chat")
        chat = generics.get_object_or_404(Chat, id=chat_id)

        if PRODUCTION:
            start_updating_messages_limits_for_user.delay(
                chat_id=chat.id,
                user_id=request.user.id,
            )

        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            message = serializer.save()

            message.updated_at = message.created_at
            message.save()

            chat.updated_at = message.created_at
            chat.save()

        start_publishing_message.delay(
            event="create",
            message=MessageSerializer(
                message, context={"request": request}
            ).data,
            members=chat.get_members_ids_list(),
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MessageDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    http_method_names = ["get", "patch", "delete"]

    def get_object(self):
        message_id = self.kwargs["id"]
        return generics.get_object_or_404(Message, id=message_id)

    def get_permissions(self):
        if self.request.method == "GET":
            permissions = [IsAuthenticated, IsMessageChatMember]

        if self.request.method in {"DELETE", "PATCH"}:
            permissions = [
                IsAuthenticated,
                IsMessageChatMember,
                IsMessageSender,
            ]

        return [permission() for permission in permissions]

    def patch(self, request, *args, **kwargs):
        message = self.get_object()
        serializer = self.get_serializer(
            message,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(raise_exception=True)
        message_text = message.text

        if message_text != message.text:
            with transaction.atomic():
                message = serializer.save()

                message.updated_at = timezone.now()
                message.save()

                chat = generics.get_object_or_404(Chat, id=message.chat.id)

            start_publishing_message.delay(
                event="update",
                message=serializer.data,
                members=chat.get_members_ids_list(),
            )

        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        chat = generics.get_object_or_404(Chat, id=instance.chat.id)

        start_publishing_message.delay(
            event="delete",
            message=MessageSerializer(instance).data,
            members=chat.get_members_ids_list(),
        )

        return super().perform_destroy(instance)

    def put(self, request, *args, **kwargs):
        raise MethodNotAllowed()


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsMessageChatMember, IsNotMessageSender])
def read_message(request, id):
    message = generics.get_object_or_404(Message, id=id)
    message.was_read_by.add(request.user)

    publish_data = MessageSerializer(
        message,
        context={"request": request},
    ).data

    start_publishing_message.delay(
        event="read",
        message=publish_data,
        members=message.chat.get_members_ids_list(),
    )

    return Response(publish_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def read_all_messages(request):
    chat_id = request.query_params.get("chat")

    if not chat_id:
        return Response(
            {"detail": "Chat UUID is required in url"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    chat = generics.get_object_or_404(Chat, id=chat_id)

    if not chat.members.filter(id=request.user.id).exists():
        raise PermissionDenied()

    start_reading_chat_messages.delay(
        chat_id=chat.id,
        user_id=request.user.id,
    )

    return Response({"deatil": "Job is running"}, status=status.HTTP_200_OK)
