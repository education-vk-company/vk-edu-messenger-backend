import uuid

from django.db import models
from django.core.validators import FileExtensionValidator
from django.contrib.auth import get_user_model

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
        max_length=150,
    )

    avatar = models.ImageField(
        null=True,
        blank=True,
        upload_to="chats/avatars/",
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png"])],
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

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-updated_at"]
