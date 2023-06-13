from django.contrib import admin

from django.contrib.auth import get_user_model

User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["username", "last_login", "group_list"]
    ordering = ["username"]

    def group_list(self, obj):
        return ", ".join(obj.groups.values_list("name", flat=True))
