from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
    )

    def create(self, validated_data):
        user = User.objects.create(
            bio=validated_data.get("bio"),
            username=validated_data["username"],
            last_name=validated_data["last_name"],
            first_name=validated_data["first_name"],
        )

        user.set_password(validated_data["password"])
        user.save()

        return user

    class Meta:
        model = User
        read_only_fields = ["id"]
        fields = (
            "id",
            "username",
            "password",
            "first_name",
            "last_name",
            "bio",
            "avatar",
        )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "bio", "avatar")
