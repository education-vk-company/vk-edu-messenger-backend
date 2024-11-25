from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from application.celery import app
from application.decorators import throttle
from application.settings import Constants
from centrifugo.utils import publish_data
from chats.models import Chat
from users.anonymization import get_bot_username

from .models import Message

User = get_user_model()


def publish_message(message, members, event):
    data = {
        "event": event,
        "message": message,
    }
    publish_data(data=data, channels=members)


@app.task
def start_publishing_message(message, members, event):
    publish_message(message, members, event)


def remove_old_messages():
    with transaction.atomic():
        time_threshold = timezone.now() - timedelta(weeks=1)

        Message.objects.exclude(sender__username=get_bot_username()).filter(
            created_at__lt=time_threshold
        ).delete()


@app.task
def start_removing_old_messages():
    remove_old_messages()


def update_messages_limits_for_user(user_id, chat_id):
    with transaction.atomic():
        chat = Chat.objects.get(id=chat_id)

        messages = chat.messages.exclude(
            sender__username=get_bot_username()
        ).filter(sender__id=user_id)

        messages_count = messages.count()

        if messages_count < Constants.MAX_CHAT_MESSSAGES_PER_USER:
            return

        limit = (
            messages_count
            - Constants.MAX_CHAT_MESSSAGES_PER_USER
            + Constants.MESSAGES_AMOUNT_TO_DELETE_ON_LIMIT
        )

        messages.order_by("created_at")[:limit].delete()


@app.task
@throttle(interval=10, timeout=20)
def start_updating_messages_limits_for_user(user_id, chat_id):
    update_messages_limits_for_user(user_id, chat_id)


def read_chat_messages(user_id, chat_id):
    with transaction.atomic():
        chat = Chat.objects.get(id=chat_id)
        user = User.objects.get(id=user_id)

        if not chat.members.filter(id=user_id).exists():
            return

        messages = chat.messages.exclude(was_read_by=user)

        def worker(message):
            message.was_read_by.add(user)
            return message.id

        result = [worker(message) for message in messages]

        if not result:
            return

        return [
            {
                "user": user.id,
                "chat": chat.id,
                "messages": result,
            },
            chat.get_members_ids_list(),
        ]


@app.task
def start_reading_chat_messages(user_id, chat_id):
    result = read_chat_messages(user_id, chat_id)

    if result:
        message, members = result
        publish_message(message, members, "read_all")
