from django.contrib import admin

from .models import Chat


@admin.register(Chat)
class AdminUser(admin.ModelAdmin):
    list_display = [
        "id",
        "stitle",
        "is_private",
        "creator__username",
    ]

    list_filter = [
        "is_private",
        "creator",
        "created_at",
        "updated_at",
    ]

    search_fields = [
        "id",
        "title",
        "creator__id",
        "creator__username",
        "creator__first_name",
        "creator__last_name",
    ]

    ordering = ["-created_at"]

    def stitle(self, obj):
        return obj.title if obj.title else "Private"

    stitle.short_description = "Title"
