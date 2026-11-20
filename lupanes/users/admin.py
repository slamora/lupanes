from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["username", "email", "is_active", "last_login", "group_list"]
    ordering = ["username"]

    def group_list(self, obj):
        return ", ".join(obj.groups.values_list("name", flat=True))
