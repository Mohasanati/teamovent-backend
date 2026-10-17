
from django.contrib import admin
from django.db import transaction

from .models import Coach, CoachSport
from .coach_service import approve_coach


class CoachSportInline(admin.TabularInline):
    model = CoachSport
    extra = 1


@admin.register(Coach)
class CoachAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "status",
        "created_at",
        "reviewed_at",
    )
    list_filter = ("status", "created_at")
    search_fields = (
        "user__phone_number",
        "user__first_name",
        "user__last_name",
    )
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)
    inlines = [CoachSportInline]

    def changeform_view(
        self, request, object_id=None, form_url="", extra_context=None
    ):
        with transaction.atomic():
            return super().changeform_view(
                request, object_id, form_url, extra_context
            )

    def save_model(self, request, obj, form, change):
        if change:
            obj._status_before_save = (
                Coach.objects.filter(pk=obj.pk)
                .values_list("status", flat=True)
                .first()
            )
        else:
            obj._status_before_save = None

        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)

        coach = form.instance
        old_status = getattr(coach, "_status_before_save", None)

        if (
            coach.status == Coach.Status.APPROVED
            and old_status != Coach.Status.APPROVED
        ):
            approve_coach(coach.pk)
            coach.refresh_from_db()


@admin.register(CoachSport)
class CoachSportAdmin(admin.ModelAdmin):
    list_display = ("coach", "sport", "grade")
    list_filter = ("grade", "sport")
    search_fields = (
        "coach__user__phone_number",
        "coach__user__first_name",
        "coach__user__last_name",
        "sport__name",
    )
