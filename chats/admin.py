from django.contrib import admin

from .models import Chat


@admin.register(Chat)
class AdminUser(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "creator__id",
        "is_private",
    )
