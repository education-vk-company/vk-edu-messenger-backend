from django.contrib.auth import get_user_model

from rest_framework import generics, filters
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import AllowAny, IsAuthenticated

from application.pagination import Pagination
from .serializers import UserSerializer, UserCreateSerializer

User = get_user_model()


class UserCreate(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user_id = self.kwargs["id"]
        user = generics.get_object_or_404(User, id=user_id)
        return user

    def perform_update(self, serializer):
        if self.request.user != self.get_object():
            self.permission_denied(self.request)
        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user != instance:
            self.permission_denied(self.request)
        instance.delete()

    def put(self, request, *args, **kwargs):
        raise MethodNotAllowed("PUT method is not allowed")


class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    pagination_class = Pagination
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ["username", "first_name", "last_name"]
