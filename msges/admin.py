from django.contrib import admin

from .models import Message, MessageFile


class MessageFileInline(admin.TabularInline):
    model = MessageFile
    fields = ["item"]


@admin.register(Message)
class AdminUser(admin.ModelAdmin):
    list_display = [
        "id",
        "chat",
        "sender__username",
        "text",
        "created_at",
        "updated_at",
    ]

    list_filter = [
        "created_at",
        "updated_at",
    ]

    search_fields = [
        "id",
        "text",
        "chat__id",
        "chat__title",
        "sender__id",
        "sender__username",
        "sender__first_name",
        "sender__last_name",
    ]

    ordering = ["-created_at"]

    inlines = [MessageFileInline]
