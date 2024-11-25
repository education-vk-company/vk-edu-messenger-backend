import uuid

from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone

from application.settings import Constants


class User(AbstractUser):
    id = models.UUIDField(
        editable=False,
        primary_key=True,
        default=uuid.uuid4,
    )

    bio = models.CharField(
        null=True,
        blank=True,
        max_length=150,
    )

    avatar = models.ImageField(
        null=True,
        blank=True,
        upload_to="users/avatars/",
        validators=[
            FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png"])
        ],
    )

    first_name = models.CharField(
        max_length=Constants.MAX_FIRST_NAME_LENGTH,
        db_index=True,
    )

    last_name = models.CharField(
        max_length=Constants.MAX_LAST_NAME_LENGTH,
        db_index=True,
    )

    is_online = models.BooleanField(
        default=False,
    )

    last_online_at = models.DateTimeField(
        db_index=True,
        default=timezone.now,
    )

    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return f"{self.username}"

    class Meta:
        ordering = ["first_name", "last_name"]


class UserIP(models.Model):
    id = models.UUIDField(
        editable=False,
        primary_key=True,
        default=uuid.uuid4,
    )

    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        related_name="ip_addresses",
        on_delete=models.CASCADE,
    )

    ip_address = models.GenericIPAddressField(
        db_index=True,
    )

    def __str__(self):
        return f"{self.user}:{self.ip_address}"
