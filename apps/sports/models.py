
from django.db import models
from django.core.validators import RegexValidator

class Sport(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="نام رشته ورزشی",
    )
    slug = models.SlugField(
    max_length=120,
    unique=True,
    validators=[
        RegexValidator(
            regex=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
            message="اسلاگ باید فقط شامل حروف انگلیسی کوچک، عدد و خط تیره باشد.",
        )
    ],
    verbose_name="اسلاگ انگلیسی",
    )
    description = models.TextField(
        blank=True,
        verbose_name="توضیحات",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "رشته ورزشی"
        verbose_name_plural = "رشته‌های ورزشی"
        ordering = ["name"]
