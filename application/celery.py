import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "application.settings")

app = Celery("application")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.conf.broker_url = "redis://redis:6379/0"
app.conf.result_backend = "redis://redis:6379/0"

app.autodiscover_tasks()

app.conf.broker_connection_retry_on_startup = True
app.conf.timezone = "Europe/Moscow"

app.conf.beat_schedule = {
    "setting-users-offline": {
        "task": "users.tasks.start_setting_users_offline",
        "schedule": 5 * 60,
    }
}
