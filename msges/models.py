import uuid

from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone

from application.settings import Constants
from chats.models import Chat

User = get_user_model()


class Message(models.Model):
    id = models.UUIDField(
        editable=False,
        primary_key=True,
        default=uuid.uuid4,
    )

    text = models.TextField(
        null=True,
        blank=True,
        max_length=Constants.MAX_MESSAGE_TEXT_LENGTH,
    )

    voice = models.FileField(
        null=True,
        blank=True,
        upload_to="messages/voices/",
        validators=[
            FileExtensionValidator(allowed_extensions=["mp3", "wav", "ogg"])
        ],
    )

    created_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
    )

    updated_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
    )

    sender = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="messages",
    )

    chat = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE,
        related_name="messages",
    )

    was_read_by = models.ManyToManyField(
        User,
        blank=True,
        related_name="reader",
    )

    def __str__(self):
        return f"{self.id}"

    class Meta:
        ordering = ["-created_at"]


class MessageFile(models.Model):
    id = models.UUIDField(
        editable=False,
        primary_key=True,
        default=uuid.uuid4,
    )

    message = models.ForeignKey(
        Message,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="files",
    )

    item = models.FileField(
        null=True,
        blank=True,
        upload_to="messages/files/",
    )

    def __str__(self):
        return f"{self.message}:{self.id}"
