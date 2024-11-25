from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .utils import generate_connection_token, generate_subscription_token


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def centrifugo_connect(request):
    return Response({"token": generate_connection_token(request.user.id)})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def centrifugo_subscribe(request):
    return Response(
        {
            "token": generate_subscription_token(
                request.user.id, request.user.id
            )
        }
    )
