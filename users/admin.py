from django.contrib import admin

from .models import User


@admin.register(User)
class AdminUser(admin.ModelAdmin):
    list_display = [
        "id",
        "username",
        "first_name",
        "last_name",
        "is_online",
        "last_online_at",
    ]

    list_filter = [
        "is_online",
        "date_joined",
        "last_online_at",
    ]

    search_fields = [
        "id",
        "username",
        "first_name",
        "last_name",
    ]

    ordering = ["username"]
