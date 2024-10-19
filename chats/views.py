from rest_framework import generics, filters
from rest_framework.response import Response
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import IsAuthenticated

from .models import Chat
from .permissions import IsChatMember, IsChatCreator
from .serializers import (
    ChatSerializer,
    GroupChatSerializer,
    PrivateChatSerializer,
    GroupChatPatchSerializer,
)

from application.pagination import Pagination


class ChatListCreateView(generics.ListCreateAPIView):
    pagination_class = Pagination
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [filters.SearchFilter]
    search_fields = ["title"]

    def get_queryset(self):
        return self.request.user.chats.all()

    def post(self, request, *args, **kwargs):
        is_private = request.data.get("is_private") == "true"

        if is_private:
            serializer = PrivateChatSerializer(
                data=request.data, context={"request": request}
            )
        else:
            serializer = GroupChatSerializer(
                data=request.data, context={"request": request}
            )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)


class ChatDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Chat.objects.all()

    def get_queryset(self):
        return self.request.user.chats.all()

    def get_object(self):
        chat_id = self.kwargs["id"]
        return generics.get_object_or_404(Chat, id=chat_id)

    def get_permissions(self):
        if self.request.method == "GET":
            permissions = [IsAuthenticated, IsChatMember]

        if self.request.method in {"DELETE", "PATCH"}:
            permissions = [IsAuthenticated, IsChatMember, IsChatCreator]

        return [permission() for permission in permissions]

    def get_serializer_class(self):
        if self.request.method in {"GET", "DELETE"}:
            return ChatSerializer

        return GroupChatPatchSerializer

    def perform_update(self, serializer):
        if self.get_object().is_private:
            raise MethodNotAllowed("PATCH method for private chats is not allowed")
        serializer.save()

    def put(self, request, *args, **kwargs):
        raise MethodNotAllowed("PUT method is not allowed")
