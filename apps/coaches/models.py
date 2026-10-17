
from django.conf import settings
from django.db import models


class Coach(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "در انتظار بررسی"
        APPROVED = "approved", "تأیید شده"
        REJECTED = "rejected", "رد شده"
        SUSPENDED = "suspended", "تعلیق شده"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="coach_record",
        verbose_name="کاربر",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="وضعیت درخواست",
    )
    application_note = models.TextField(
        blank=True,
        verbose_name="توضیحات درخواست",
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="زمان بررسی",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="زمان ثبت درخواست",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین به‌روزرسانی",
    )

    def __str__(self):
        return f"{self.user.phone_number} - {self.get_status_display()}"

    class Meta:
        verbose_name = "پرونده مربی"
        verbose_name_plural = "پرونده‌های مربیان"
        ordering = ["-created_at"]


class CoachSport(models.Model):
    class Grade(models.IntegerChoices):
        GRADE_0 = 0, "international grade"
        GRADE_1 = 1, "گرید ۱"
        GRADE_2 = 2, "گرید ۲"
        GRADE_3 = 3, "گرید ۳"

    coach = models.ForeignKey(
        Coach,
        on_delete=models.CASCADE,
        related_name="sports",
        verbose_name="مربی",
    )
    sport = models.ForeignKey(
        "sports.Sport",
        on_delete=models.PROTECT,
        related_name="coach_assignments",
        verbose_name="رشته ورزشی",
    )
    grade = models.PositiveSmallIntegerField(
        choices=Grade.choices,
        verbose_name="درجه مربی",
    )

    class Meta:
        verbose_name = "رشته و درجه مربی"
        verbose_name_plural = "رشته‌ها و درجه‌های مربیان"
        constraints = [
            models.UniqueConstraint(
                fields=["coach", "sport"],
                name="unique_coach_sport",
            ),
        ]

    def __str__(self):
        return (
            f"{self.coach.user.phone_number} - "
            f"{self.sport.name} - {self.get_grade_display()}"
        )
