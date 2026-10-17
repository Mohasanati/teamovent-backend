
from django.core.exceptions import ValidationError

from apps.coaches.models import Coach, CoachSport


def validate_coach_approval(coach: Coach) -> None:
    """اعتبارسنجی شرایط لازم برای تأیید مربی."""

    if coach.status == Coach.Status.SUSPENDED:
        raise ValidationError(
            "مربی تعلیق‌شده امکان تأیید مجدد ندارد."
        )

    assignments = CoachSport.objects.filter(coach=coach)

    if not assignments.exists():
        raise ValidationError(
            "برای تأیید مربی، حداقل یک رشته ورزشی "
            "با گرید معتبر باید ثبت شده باشد."
        )
