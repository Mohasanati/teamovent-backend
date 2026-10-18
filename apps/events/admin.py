
from django.contrib import admin
from django.utils.html import format_html

from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "coach",
        "sport",
        "event_type",
        "location_type",
        "get_province",
        "city",
        "starts_at",
        "session_count",
        "gender_type",
        "status",
    )

    list_filter = (
        "status",
        "event_type",
        "location_type",
        "gender_type",
        "city__province",
        "city",
        "sport",
    )

    search_fields = (
        "title",
        "coach__user__first_name",
        "coach__user__last_name",
        "city__name",
        "city__province__name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "cover_image_preview",
    )

    fields = (
        "title",
        "description",
        "coach",
        "sport",
        "event_type",
        "location_type",
        "city",
        "start_address",
        "start_latitude",
        "start_longitude",
        "end_address",
        "end_latitude",
        "end_longitude",
        "gender_type",
        "starts_at",
        "ends_at",
        "session_count",
        "price",
        "capacity",
        "cover_image",
        "cover_image_preview",
        "video_url",
        "status",
        "created_at",
        "updated_at",
    )

    ordering = ("-created_at",)
    list_per_page = 25

    @admin.display(
        description="استان",
        ordering="city__province__name",
    )
    def get_province(self, obj):
        return obj.city.province.name

    @admin.display(description="پیش‌نمایش تصویر")
    def cover_image_preview(self, obj):
        if obj and obj.cover_image:
            return format_html(
                '<img src="{}" style="max-height: 180px; '
                'max-width: 320px; object-fit: contain;" />',
                obj.cover_image.url,
            )
        return "تصویری بارگذاری نشده است."

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "coach":
            from apps.coaches.models import Coach

            kwargs["queryset"] = Coach.objects.filter(
                status=Coach.Status.APPROVED,
                user__is_active=True,
            ).select_related("user")

        return super().formfield_for_foreignkey(
            db_field, request, **kwargs
        )
