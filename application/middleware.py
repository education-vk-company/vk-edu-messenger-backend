from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework_simplejwt.authentication import JWTAuthentication

User = get_user_model()


class UserOnlineMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        try:
            request.user = JWTAuthentication().authenticate(request)[0]
            request.user.is_online = True
            request.user.last_online_at = timezone.now()
            request.user.save()
        except:
            pass
