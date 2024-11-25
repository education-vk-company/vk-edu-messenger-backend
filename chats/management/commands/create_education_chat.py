import os

from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.management.base import BaseCommand

from application.settings import BASE_DIR
from chats.models import Chat
from msges.models import Message
from users.anonymization import get_bot_user

User = get_user_model()


class Command(BaseCommand):
    def handle(self, *args, **options):
        user, _ = User.objects.get_or_create(**get_bot_user())

        bot_avatar_path = os.path.join(BASE_DIR, "assets", "bot_avatar.png")

        with open(bot_avatar_path, "rb") as f:
            user.avatar.save("bot_avatar.png", File(f), save=True)

        chat, _ = Chat.objects.get_or_create(
            creator=user,
            is_private=False,
            title="VK Education",
        )

        chat_avatar_path = os.path.join(BASE_DIR, "assets", "vk_logo.png")

        with open(chat_avatar_path, "rb") as f:
            chat.avatar.save("vk_logo.png", File(f), save=True)

        Message.objects.get_or_create(
            chat=chat,
            sender=user,
            text="Добро пожаловать в общий чат VK Образования! Вы были добавлены сюда автоматически. Начинайте общение здесь)",
        )
