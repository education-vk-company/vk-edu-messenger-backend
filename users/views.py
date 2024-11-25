from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import filters, generics, serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from application.pagination import Pagination
from application.settings import PRODUCTION, Constants
from users.models import UserIP

from .serializers import UserCreateSerializer, UserSerializer

User = get_user_model()


class UserCreate(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]

    def get_ip_address(self):
        x_forwarded_for = self.request.META.get("HTTP_X_FORWARDED_FOR")

        if x_forwarded_for:
            ip_address = x_forwarded_for.split(",")[0]
        else:
            ip_address = self.request.META.get("REMOTE_ADDR")

        return ip_address

    def perform_create(self, serializer):
        ip_address = self.get_ip_address()

        if PRODUCTION:
            if (
                UserIP.objects.filter(ip_address=ip_address).count()
                >= Constants.MAX_ACCOUNTS_PER_IP
            ):
                raise serializers.ValidationError(
                    f"You can create only {Constants.MAX_ACCOUNTS_PER_IP} accounts per IP on production"
                )

        with transaction.atomic():
            user = serializer.save()

            if PRODUCTION:
                UserIP.objects.create(
                    user=user,
                    ip_address=ip_address,
                )


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "patch", "delete"]

    def get_object(self):
        user_id = self.kwargs.get("id")

        if user_id:
            user = generics.get_object_or_404(User, id=user_id)
            return user

        return self.request.user

    def perform_update(self, serializer):
        if self.request.user != self.get_object():
            self.permission_denied(self.request)

        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user != instance:
            self.permission_denied(self.request)

        instance.delete()

    def put(self, request, *args, **kwargs):
        raise MethodNotAllowed()


class UserList(generics.ListAPIView):
    pagination_class = Pagination
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ["$username", "$first_name", "$last_name"]

    def get_queryset(self):
        return User.objects.exclude(id=self.request.user.id)


@api_view(["HEAD"])
@permission_classes([IsAuthenticated])
def set_online(request):
    return Response(status=status.HTTP_200_OK)
