import uuid

from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone

from application.settings import Constants

User = get_user_model()


class Chat(models.Model):
    id = models.UUIDField(
        editable=False,
        primary_key=True,
        default=uuid.uuid4,
    )

    title = models.CharField(
        null=True,
        blank=True,
        max_length=Constants.MAX_CHAT_TITLE_LENGTH,
    )

    avatar = models.ImageField(
        null=True,
        blank=True,
        upload_to="chats/avatars/",
        validators=[
            FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png"])
        ],
    )

    creator = models.ForeignKey(
        User,
        null=True,
        blank=True,
        related_name="creator",
        on_delete=models.SET_NULL,
    )

    members = models.ManyToManyField(
        User,
        related_name="chats",
    )

    is_private = models.BooleanField()

    created_at = models.DateTimeField(db_index=True, default=timezone.now)

    updated_at = models.DateTimeField(db_index=True, default=timezone.now)

    def __str__(self):
        return f"{self.id}"

    def get_members_ids_list(self):
        queryset = self.members.all().values_list("id", flat=True)
        return list(queryset)

    class Meta:
        ordering = ["-updated_at"]


class ChatCounter(models.Model):
    id = models.UUIDField(
        editable=False,
        primary_key=True,
        default=uuid.uuid4,
    )

    chat = models.ForeignKey(
        Chat,
        null=True,
        blank=True,
        related_name="counters",
        on_delete=models.SET_NULL,
    )

    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        related_name="counters",
        on_delete=models.SET_NULL,
    )

    chats_count = models.PositiveIntegerField(default=0)
    messages_count = models.PositiveIntegerField(default=0)
    unread_messages_count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ["chat", "user"]

    def __str__(self):
        return f"{self.chat}:{self.user}"
