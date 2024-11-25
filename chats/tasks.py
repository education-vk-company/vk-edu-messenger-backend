from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from application.celery import app
from users.anonymization import get_bot_username

from .models import Chat


def remove_old_chats():
    with transaction.atomic():
        time_threshold = timezone.now() - timedelta(weeks=2)

        Chat.objects.exclude(creator__username=get_bot_username()).filter(
            updated_at__lt=time_threshold
        ).delete()


@app.task
def start_removing_old_chats():
    remove_old_chats()
