from django.db.models import Count
from rest_framework import serializers

from msges.serializers import MessageSerializer
from users.anonymization import get_deleted_user, get_deleted_user_full_name
from users.serializers import UserSerializer

from .models import Chat


def get_default_fields(*args):
    return [
        "id",
        "title",
        "members",
        "creator",
        "avatar",
        "created_at",
        "updated_at",
        "is_private",
        "last_message",
        "unread_messages_count",
        *args,
    ]


def get_default_readonly_fields(*args):
    return [
        "id",
        "creator",
        "created_at",
        "updated_at",
        "last_message",
        "unread_messages_count",
        *args,
    ]


class ChatSerializer(serializers.ModelSerializer):
    creator = UserSerializer()
    title = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_messages_count = serializers.SerializerMethodField()

    def get_companion(self, instance):
        user = self.context.get("request").user
        return instance.members.exclude(id=user.id).first()

    def get_title(self, instance):
        if instance.is_private:
            companion = self.get_companion(instance)

            if companion:
                return companion.get_full_name()

            return get_deleted_user_full_name()

        return instance.title

    def get_avatar(self, instance):
        if instance.is_private:
            companion = self.get_companion(instance)

            if companion and companion.avatar:
                return self.context.get("request").build_absolute_uri(
                    companion.avatar.url
                )

        if instance.avatar:
            return self.context.get("request").build_absolute_uri(
                instance.avatar.url
            )

    def get_last_message(self, instance):
        message = instance.messages.first()

        if message:
            return MessageSerializer(message).data

    def get_unread_messages_count(self, instance):
        user = self.context.get("request").user
        return instance.messages.exclude(was_read_by=user).count()

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if instance.creator:
            representation["creator"] = UserSerializer(
                instance.creator,
                context=self.context,
            ).data

        if representation.get("creator") is None:
            representation["creator"] = get_deleted_user()

        representation["members"] = UserSerializer(
            instance.members,
            context=self.context,
            many=True,
        ).data

        representation["last_message"] = representation.get(
            "last_message", None
        )

        representation["unread_messages_count"] = representation.get(
            "unread_messages_count", 0
        )

        return representation

    class Meta:
        model = Chat
        fields = get_default_fields()
        read_only_fields = get_default_readonly_fields()


class PrivateChatSerializer(ChatSerializer):
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def validate_members(self, value):
        if len(value) != 1:
            raise serializers.ValidationError(
                "Private chat must contain only one companion"
            )

        user = self.context.get("request").user

        if value[0] == user:
            raise serializers.ValidationError("Can't append current user")

        if user not in value:
            value.append(user)

        return value

    def create(self, validated_data):
        request = self.context.get("request")
        is_fallback = self.context.get("is_fallback")

        members = validated_data["members"]

        chat = (
            request.user.chats.filter(is_private=True)
            .annotate(members_count=Count("members"))
            .filter(members__in=members)
            .distinct()
            .filter(members_count=len(members))
            .first()
        )

        if is_fallback and chat:
            return chat

        if not is_fallback and chat:
            raise serializers.ValidationError(
                "Private chat with these members already exists"
            )

        return super().create(validated_data)

    class Meta:
        model = Chat
        fields = get_default_fields()
        read_only_fields = get_default_readonly_fields("title", "avatar")


class GroupChatSerializer(ChatSerializer):
    title = serializers.CharField(
        required=True,
        max_length=150,
    )
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def validate_members(self, value):
        user = self.context.get("request").user

        if len(value) == 0:
            raise serializers.ValidationError("Chat must conatin companions")

        if len(value) == 1 and value[0] == user:
            raise serializers.ValidationError(
                "Chat must contain other members than current user"
            )

        if len(value) > 100:
            raise serializers.ValidationError(
                "Chat must not contain more than 100 members"
            )

        if user not in value:
            value.append(user)

        return value

    class Meta:
        model = Chat
        fields = get_default_fields()
        read_only_fields = get_default_readonly_fields()


class GroupChatPatchSerializer(GroupChatSerializer):
    class Meta:
        model = Chat
        fields = get_default_fields()
        read_only_fields = get_default_readonly_fields("is_private")


class IsPrivateSerializer(serializers.Serializer):
    is_private = serializers.BooleanField(required=True)
