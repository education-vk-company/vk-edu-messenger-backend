from rest_framework.decorators import api_view, renderer_classes, permission_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .utils import generate_connection_token, generate_subscription_token


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@renderer_classes([JSONRenderer])
def centrifugo_connect(request):
    return Response({"token": generate_connection_token(request.user.id)})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@renderer_classes([JSONRenderer])
def centrifugo_subscribe(request):
    return Response(
        {"token": generate_subscription_token(request.user.id, request.user.id)}
    )
