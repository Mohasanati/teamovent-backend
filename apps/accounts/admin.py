
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, UserProfile


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    ordering = ("phone_number",)

    list_display = (
        "phone_number",
        "first_name",
        "last_name",
        "role",
        "is_active",
    )

    list_filter = ("role", "is_active")
    search_fields = ("phone_number", "first_name", "last_name")

    fieldsets = (
        (None, {"fields": ("phone_number", "password")}),
        (
            "اطلاعات شخصی",
            {"fields": ("first_name", "last_name", "email")},
        ),
        (
            "نقش و وضعیت حساب",
            {"fields": ("role", "is_active")},
        ),
        (
            "دسترسی‌های مدیریتی جنگو",
            {"fields": ("is_superuser", "groups", "user_permissions")},
        ),
        ("تاریخ‌ها", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "phone_number",
                    "first_name",
                    "last_name",
                    "role",
                    "password1",
                    "password2",
                    "is_active",
                ),
            },
        ),
    )

    filter_horizontal = ("groups", "user_permissions")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "gender", "national_code", "birth_date")
    search_fields = ("user__phone_number", "national_code")
    list_filter = ("gender",)
