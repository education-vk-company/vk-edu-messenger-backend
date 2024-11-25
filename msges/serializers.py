from rest_framework import serializers

from application.settings import PRODUCTION, Constants
from users.anonymization import get_deleted_user
from users.serializers import UserSerializer

from .models import Message, MessageFile


def get_default_fields(*args):
    return [
        "id",
        "text",
        "voice",
        "sender",
        "chat",
        "files",
        "updated_at",
        "created_at",
        "was_read_by",
        *args,
    ]


def get_default_readonly_fields(*args):
    return [
        "id",
        "updated_at",
        "created_at",
        "sender",
        "was_read_by",
        *args,
    ]


class MessageFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageFile
        fields = ["item"]


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer()
    files = MessageFileSerializer(many=True)

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if instance.sender:
            representation["sender"] = UserSerializer(
                instance.sender,
                context=self.context,
            ).data

        if representation.get("sender") is None:
            representation["sender"] = get_deleted_user()

        representation["was_read_by"] = UserSerializer(
            instance.was_read_by,
            context=self.context,
            many=True,
        ).data

        return representation

    class Meta:
        model = Message
        fields = get_default_fields()
        read_only_fields = get_default_readonly_fields(
            "chat", "voice", "files"
        )


class MessageCreateSerializer(MessageSerializer):
    files = MessageFileSerializer(many=True, required=False)
    sender = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def validate(self, attrs):
        text = attrs.get("text")
        voice = attrs.get("voice")

        request = self.context.get("request")
        files = request.FILES.getlist("files")

        if not voice and not files and not text:
            raise serializers.ValidationError(
                "No voice message must contain text or files"
            )

        if voice:
            if text or files:
                raise serializers.ValidationError(
                    "If voice is provided, text and files must not be present"
                )

        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        files_data = request.FILES.getlist("files")

        validated_data.pop("files", [])
        message = Message.objects.create(**validated_data)

        if files_data:
            if (
                PRODUCTION
                and len(files_data) > Constants.MAX_MESSAGE_FILES_COUNT
            ):
                raise serializers.ValidationError(
                    f"Max files count is {Constants.MAX_MESSAGE_FILES_COUNT}"
                )

            for file_data in files_data:
                MessageFile.objects.create(message=message, item=file_data)

        return message

    class Meta:
        model = Message
        fields = get_default_fields()
        read_only_fields = get_default_readonly_fields()
