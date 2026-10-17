
from django.contrib.auth.models import Group
from django.db import transaction
from django.utils import timezone

from .models import Coach
from .services.status_service import validate_coach_approval


@transaction.atomic
def approve_coach(coach_id: int) -> Coach:
    coach = Coach.objects.select_for_update().get(pk=coach_id)

    validate_coach_approval(coach)

    # Create the coach group if it does not exist.
    coach_group, _ = Group.objects.get_or_create(name="مربی")

    # Add the coach role without removing existing roles.
    coach.user.groups.add(coach_group)

    # Approve the coach application.
    coach.status = Coach.Status.APPROVED
    coach.reviewed_at = timezone.now()
    coach.save(update_fields=["status", "reviewed_at"])

    return coach
