from rest_framework import serializers

from msges.serializers import MessageSerializer

from .models import Chat
from users.serializers import UserSerializer


class ChatSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    creator = UserSerializer()
    members = UserSerializer(many=True)

    def get_title(self, instance):
        if instance.is_private:
            user = self.context.get("request").user
            return instance.members.exclude(id=user.id).first().get_full_name()

        return instance.title

    def get_avatar(self, instance):
        if instance.is_private:
            user = self.context.get("request").user
            companion = instance.members.exclude(id=user.id).first()

            if companion and companion.avatar:
                return self.context.get("request").build_absolute_uri(
                    companion.avatar.url
                )

        if instance.avatar:
            return self.context.get("request").build_absolute_uri(instance.avatar.url)

    def get_last_message(self, instance):
        return MessageSerializer(instance.messages.first()).data

    class Meta:
        model = Chat
        fields = [
            "id",
            "title",
            "members",
            "creator",
            "avatar",
            "created_at",
            "updated_at",
            "is_private",
            "last_message",
        ]


class PrivateChatSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def get_title(self, instance):
        user = self.context.get("request").user
        return instance.members.exclude(id=user.id).first().get_full_name()

    def get_avatar(self, instance):
        user = self.context.get("request").user
        companion = instance.members.exclude(id=user.id).first()

        if companion and companion.avatar:
            return self.context.get("request").build_absolute_uri(companion.avatar.url)

    def validate_members(self, value):
        if len(value) != 1:
            raise serializers.ValidationError(
                "Private chat must contains only one companion"
            )

        user = self.context.get("request").user

        if value[0] == user.id:
            raise serializers.ValidationError("Can't append current user")

        if user not in value:
            value.append(user)

        isExists = (
            user.chats.filter(is_private=True, members__in=value).distinct().exists()
        )

        if isExists:
            raise serializers.ValidationError(
                "Private chat with these members already exists"
            )

        return value

    class Meta:
        model = Chat
        read_only_fields = ["id", "created_at", "updated_at", "creator"]
        fields = [
            "id",
            "title",
            "members",
            "avatar",
            "created_at",
            "updated_at",
            "is_private",
            "creator",
        ]


class GroupChatSerializerBase(serializers.ModelSerializer):
    title = serializers.CharField(
        required=True,
        max_length=150,
    )
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def validate_members(self, value):
        user = self.context.get("request").user

        if len(value) == 0:
            raise serializers.ValidationError("Chat must conatin companions")

        if len(value) == 1 and value[0] == user.id:
            raise serializers.ValidationError(
                "Chat must contain other members than current user"
            )

        if user not in value:
            value.append(user)

        return value


class GroupChatSerializer(GroupChatSerializerBase):
    class Meta:
        model = Chat
        read_only_fields = ["id", "created_at", "updated_at", "creator"]
        fields = [
            "id",
            "title",
            "members",
            "avatar",
            "created_at",
            "updated_at",
            "is_private",
            "creator",
        ]


class GroupChatPatchSerializer(GroupChatSerializerBase):
    class Meta:
        model = Chat
        read_only_fields = ["id", "created_at", "updated_at", "is_private", "creator"]
        fields = [
            "id",
            "title",
            "members",
            "avatar",
            "created_at",
            "updated_at",
            "is_private",
            "creator",
        ]
