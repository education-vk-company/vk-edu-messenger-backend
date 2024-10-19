from rest_framework import serializers
from .models import Message, MessageFile
from users.serializers import UserSerializer


class MessageFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageFile
        fields = ["item"]


class MessageCreateSerializer(serializers.ModelSerializer):
    files = MessageFileSerializer(many=True, required=False)
    sender = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Message
        read_only_fields = ["id", "updated_at", "created_at", "sender"]
        fields = [
            "id",
            "text",
            "voice",
            "sender",
            "chat",
            "files",
            "updated_at",
            "created_at",
        ]

    def validate(self, attrs):
        text = attrs.get("text")
        voice = attrs.get("voice")

        request = self.context.get("request")
        files = request.FILES.getlist("files")

        if not voice and not files and not text:
            raise serializers.ValidationError("NoVoiceMessage must contain text")

        if voice:
            if text or files:
                raise serializers.ValidationError(
                    "If 'voice' is provided, 'text' and 'files' must not be present"
                )

        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        files_data = request.FILES.getlist("files")

        message = Message.objects.create(**validated_data)

        if files_data:
            if len(files_data) > 5:
                raise serializers.ValidationError("Max files count == 5")

            for file_data in files_data:
                MessageFile.objects.create(message=message, item=file_data)

        return message


class MessageSerializer(serializers.ModelSerializer):
    files = MessageFileSerializer(many=True)
    sender = UserSerializer()

    class Meta:
        model = Message
        read_only_fields = [
            "id",
            "voice",
            "sender",
            "chat",
            "files",
            "updated_at",
            "created_at",
        ]
        fields = [
            "id",
            "text",
            "voice",
            "sender",
            "chat",
            "files",
            "updated_at",
            "created_at",
        ]
