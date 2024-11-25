def get_bot_user():
    return {
        "username": "bot",
        "first_name": "Bot",
        "last_name": "VK",
        "bio": "VK Bot",
    }


def get_bot_username():
    bot = get_bot_user()
    return bot.get("username")


def get_deleted_user():
    return {
        "id": "deleted",
        "username": "deleted",
        "first_name": "Удалённый",
        "last_name": "Пользователь",
        "bio": None,
        "avatar": None,
    }


def get_deleted_user_full_name():
    deleted_user = get_deleted_user()
    return f"{deleted_user.get('first_name')} {deleted_user.get('last_name')}"
