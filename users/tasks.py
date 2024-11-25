from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from application.celery import app

User = get_user_model()


def set_users_offline():
    with transaction.atomic():
        time_threshold = timezone.now() - timedelta(minutes=5)

        User.objects.filter(
            last_online_at__lt=time_threshold, is_online=True
        ).update(is_online=False)


@app.task
def start_setting_users_offline():
    set_users_offline()
