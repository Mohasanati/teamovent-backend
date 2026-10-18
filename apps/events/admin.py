
from django.contrib import admin

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

    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)
    list_per_page = 25

    @admin.display(
        description="استان",
        ordering="city__province__name",
    )
    def get_province(self, obj):
        return obj.city.province.name

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
