from django.contrib import admin

from .models import Message


@admin.register(Message)
class AdminUser(admin.ModelAdmin):
    list_display = (
        "id",
        "chat__id",
        "sender__username",
        "created_at",
    )
