from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import UserCreate, UserDetail, UserList, set_online

urlpatterns = [
    path("auth/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("register/", UserCreate.as_view(), name="user-register"),
    path("user/<uuid:id>/", UserDetail.as_view(), name="user-detail"),
    path("user/current/", UserDetail.as_view(), name="user-detail"),
    path("users/", UserList.as_view(), name="user-list"),
    path("user/online/", set_online, name="user-online"),
]
