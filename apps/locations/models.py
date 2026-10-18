
from django.db import models
from django.core.validators import RegexValidator


slug_validator = RegexValidator(
    regex=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    message="اسلاگ باید انگلیسی و شامل حروف کوچک، عدد یا خط تیره باشد.",
)


class Province(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="نام استان",
    )
    slug = models.SlugField(
        max_length=120,
        unique=True,
        validators=[slug_validator],
        verbose_name="اسلاگ انگلیسی",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "استان"
        verbose_name_plural = "استان‌ها"

    def __str__(self):
        return self.name


class City(models.Model):
    province = models.ForeignKey(
        Province,
        on_delete=models.PROTECT,
        related_name="cities",
        verbose_name="استان",
    )
    name = models.CharField(
        max_length=100,
        verbose_name="نام شهر",
    )
    slug = models.SlugField(
        max_length=120,
        validators=[slug_validator],
        verbose_name="اسلاگ انگلیسی",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
    )

    class Meta:
        ordering = ["province__name", "name"]
        verbose_name = "شهر"
        verbose_name_plural = "شهرها"
        constraints = [
            models.UniqueConstraint(
                fields=["province", "name"],
                name="unique_city_per_province",
            ),
            models.UniqueConstraint(
                fields=["province", "slug"],
                name="unique_city_slug_per_province",
            ),
        ]

    def __str__(self):
        return f"{self.name} - {self.province.name}"
