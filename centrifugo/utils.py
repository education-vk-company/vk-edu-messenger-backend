import time
import jwt
import json
import requests

from django.core.serializers.json import DjangoJSONEncoder
from application.settings import (
    CENTRIFUGO_API_KEY,
    CENTRIFUGO_TOKEN_HMAC_SECRET_KEY,
    CENTRIFUGO_TOKEN_TIME,
    CENTRIFUGO_PORT,
)


def generate_connection_token(client):
    claims = {"sub": f"{client}", "exp": int(time.time()) + CENTRIFUGO_TOKEN_TIME}
    return jwt.encode(claims, CENTRIFUGO_TOKEN_HMAC_SECRET_KEY, algorithm="HS256")


def generate_subscription_token(client, channel):
    claims = {
        "sub": f"{client}",
        "channel": f"{channel}",
        "exp": int(time.time()) + CENTRIFUGO_TOKEN_TIME,
    }
    return jwt.encode(claims, CENTRIFUGO_TOKEN_HMAC_SECRET_KEY, algorithm="HS256")


def publish_data(data, channel):
    command = {"channel": channel, "data": data}

    data = json.dumps(command, cls=DjangoJSONEncoder)

    headers = {
        "Content-type": "application/json",
        "X-API-Key": CENTRIFUGO_API_KEY,
    }

    requests.post(
        f"http://localhost:{CENTRIFUGO_PORT}/api/publish", data=data, headers=headers
    )
