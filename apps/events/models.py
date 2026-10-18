
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Event(models.Model):
    class EventType(models.TextChoices):
        EVENT = "event", "رویداد"
        COURSE = "course", "دوره آموزشی"

    class LocationType(models.TextChoices):
        FIXED = "fixed", "محل ثابت"
        ROUTE = "route", "مسیر با مبدأ و مقصد"

    class GenderType(models.TextChoices):
        ALL = "all", "آقایان و بانوان"
        MALE = "male", "فقط آقایان"
        FEMALE = "female", "فقط بانوان"

    class Status(models.TextChoices):
        DRAFT = "draft", "پیش‌نویس"
        PENDING = "pending", "در انتظار تأیید"
        PUBLISHED = "published", "منتشرشده"
        REJECTED = "rejected", "ردشده"
        CANCELLED = "cancelled", "لغوشده"

    coach = models.ForeignKey(
    "coaches.Coach",
    on_delete=models.PROTECT,
    related_name="events",
    verbose_name="مربی برگزارکننده",
    )
    
    title = models.CharField(max_length=200, verbose_name="عنوان")
    description = models.TextField(verbose_name="توضیحات")

    event_type = models.CharField(
        max_length=10,
        choices=EventType.choices,
        default=EventType.EVENT,
        verbose_name="نوع",
    )
    sport = models.ForeignKey(
        "sports.Sport",
        on_delete=models.PROTECT,
        related_name="events",
        verbose_name="رشته ورزشی",
    )

    city = models.ForeignKey(
        "locations.City",
        on_delete=models.PROTECT,
        related_name="events",
        verbose_name="شهر",
    )

    location_type = models.CharField(
        max_length=10,
        choices=LocationType.choices,
        default=LocationType.FIXED,
        verbose_name="نوع مکان",
    )

    start_address = models.CharField(
        max_length=255,
        verbose_name="آدرس نقطه شروع",
    )
    start_latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
        verbose_name="عرض جغرافیایی شروع",
    )
    start_longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
        verbose_name="طول جغرافیایی شروع",
    )

    end_address = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="آدرس نقطه پایان",
    )
    end_latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
        verbose_name="عرض جغرافیایی پایان",
    )
    end_longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
        verbose_name="طول جغرافیایی پایان",
    )

    gender_type = models.CharField(
        max_length=10,
        choices=GenderType.choices,
        default=GenderType.ALL,
        verbose_name="جنسیت مجاز شرکت‌کنندگان",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name="وضعیت انتشار",
    )

    starts_at = models.DateTimeField(verbose_name="زمان شروع")
    ends_at = models.DateTimeField(verbose_name="زمان پایان")

    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="قیمت",
    )
    capacity = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        verbose_name="ظرفیت",
    )
    
    session_count = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name="تعداد جلسات",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="زمان ایجاد",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین به‌روزرسانی",
    )

    
    
    def clean(self):
        from django.core.exceptions import ValidationError

        super().clean()
        errors = {}

        if self.coach_id and self.coach.status != "approved":
            errors["coach"] = "فقط مربی تأییدشده می‌تواند رویداد برگزار کند."

        if self.location_type == self.LocationType.ROUTE:
            if not self.end_address:
                errors["end_address"] = "آدرس مقصد الزامی است."
            if self.end_latitude is None:
                errors["end_latitude"] = "عرض جغرافیایی مقصد الزامی است."
            if self.end_longitude is None:
                errors["end_longitude"] = "طول جغرافیایی مقصد الزامی است."

        elif self.location_type == self.LocationType.FIXED:
            self.end_address = ""
            self.end_latitude = None
            self.end_longitude = None

        if self.starts_at and self.ends_at and self.ends_at <= self.starts_at:
            errors["ends_at"] = "زمان پایان باید بعد از زمان شروع باشد."

        if not 1 <= self.session_count <= 10:
            errors["session_count"] = "تعداد جلسات باید بین ۱ تا ۱۰ باشد."

        if self.price is not None and self.price < 0:
            errors["price"] = "قیمت نمی‌تواند منفی باشد."

        if errors:
            raise ValidationError(errors)



    class Meta:
        ordering = ["starts_at"]
        verbose_name = "رویداد یا دوره"
        verbose_name_plural = "رویدادها و دوره‌ها"

    def __str__(self):
        return self.title
