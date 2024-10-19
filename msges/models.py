import uuid

from django.db import models
from django.core.validators import FileExtensionValidator
from django.contrib.auth import get_user_model
from chats.models import Chat

User = get_user_model()


class Message(models.Model):
    id = models.UUIDField(
        editable=False,
        primary_key=True,
        default=uuid.uuid4,
    )

    text = models.TextField(null=True, blank=True)

    voice = models.FileField(
        null=True,
        blank=True,
        upload_to="messages/voices/",
        validators=[FileExtensionValidator(allowed_extensions=["mp3", "wav", "ogg"])],
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    sender = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="messages"
    )

    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")

    class Meta:
        ordering = ["-created_at"]


class MessageFile(models.Model):
    id = models.UUIDField(
        editable=False,
        primary_key=True,
        default=uuid.uuid4,
    )

    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="files")

    item = models.FileField(
        null=True,
        blank=True,
        upload_to="messages/files/",
    )
