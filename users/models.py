import uuid

from django.db import models
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    id = models.UUIDField(
        editable=False,
        primary_key=True,
        default=uuid.uuid4,
    )

    bio = models.CharField(
        null=True,
        blank=True,
        max_length=450,
    )

    avatar = models.ImageField(
        null=True,
        blank=True,
        upload_to="users/avatars/",
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png"])],
    )

    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)

    REQUIRED_FIELDS = ["first_name", "last_name"]
