import re

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from application.settings import Constants
from chats.models import Chat
from users.anonymization import get_bot_username, get_deleted_user

User = get_user_model()


def get_default_fields(*args):
    return [
        "id",
        "username",
        "first_name",
        "last_name",
        "bio",
        "avatar",
        "is_online",
        "last_online_at",
        *args,
    ]


def get_default_readonly_fields(*args):
    return [
        "id",
        "is_online",
        "last_online_at",
        *args,
    ]


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
    )

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        user.set_password(validated_data["password"])
        user.save()

        try:
            chat = Chat.objects.get(
                is_private=False,
                title="VK Education",
                creator__username=get_bot_username(),
            )
            chat.members.add(user)
        except:
            pass

        return user

    def validate_first_name(self, value):
        if not re.match(r"^[A-Za-zА-Яа-яЁё]+$", value):
            raise serializers.ValidationError(
                "First Name can only contain Latin or Cyrillic letters"
            )

        return value

    def validate_last_name(self, value):
        if not re.match(r"^[A-Za-zА-Яа-яЁё]+$", value):
            raise serializers.ValidationError(
                "Last Name can only contain Latin or Cyrillic letters"
            )

        return value

    def validate_username(self, value):
        if value[0].isdigit():
            raise serializers.ValidationError(
                "Username can't start with a number"
            )

        if len(value) > Constants.MAX_USERNAME_LENGTH:
            raise serializers.ValidationError(
                f"Username can't be longer than {Constants.MAX_USERNAME_LENGTH} characters"
            )

        if not re.match(r"^[a-zA-Z0-9]*$", value):
            raise serializers.ValidationError(
                "Username can only contain Latin letters and numbers"
            )

        return value

    class Meta:
        model = User
        fields = get_default_fields("password")
        read_only_fields = get_default_readonly_fields()


class UserSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        if instance is None:
            return get_deleted_user()

        return super().to_representation(instance)

    class Meta:
        model = User
        fields = get_default_fields()
        read_only_fields = get_default_readonly_fields()
