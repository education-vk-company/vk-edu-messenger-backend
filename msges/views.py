from rest_framework import generics, filters
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import IsAuthenticated

from django.utils import timezone
from .tasks import publish_message
from chats.models import Chat
from .models import Message
from application.pagination import Pagination
from .serializers import MessageCreateSerializer, MessageSerializer
from .permissions import IsChatMember, IsMessageChatMember, IsMessageSender


class MessageListCreateView(generics.ListCreateAPIView):
    pagination_class = Pagination
    serializer_class = MessageCreateSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [filters.SearchFilter]
    search_fields = [
        "text",
        "sender__username",
        "sender__first_name",
        "sender__last_name",
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

        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)

        created_at = serializer.data.get("created_at")
        chat.updated_at = created_at
        chat.save()

        publish_message(
            message=serializer.data, members=chat.members.all(), event="create"
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MessageDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def get_object(self):
        message_id = self.kwargs["id"]
        return generics.get_object_or_404(Message, id=message_id)

    def get_permissions(self):
        if self.request.method == "GET":
            permissions = [IsAuthenticated, IsMessageChatMember]

        if self.request.method in {"DELETE", "PATCH"}:
            permissions = [IsAuthenticated, IsMessageChatMember, IsMessageSender]

        return [permission() for permission in permissions]

    def patch(self, request, *args, **kwargs):
        message = self.get_object()
        serializer = self.get_serializer(message, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        text = message.text
        self.perform_update(serializer)

        if text != serializer.data.get("text"):
            message.updated_at = timezone.now()
            message.save()

            chat = generics.get_object_or_404(Chat, id=message.chat.id)
            publish_message(
                message=serializer.data, members=chat.members.all(), event="update"
            )

        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        message = MessageSerializer(instance).data
        chat = generics.get_object_or_404(Chat, id=instance.chat.id)

        publish_message(message=message, members=chat.members.all(), event="update")
        return super().perform_destroy(instance)

    def put(self, request, *args, **kwargs):
        raise MethodNotAllowed("PUT method is not allowed")
