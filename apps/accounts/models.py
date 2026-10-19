
from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("شماره موبایل الزامی است.")

        user = self.model(
            phone_number=phone_number,
            **extra_fields,
        )

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser باید is_staff=True داشته باشد.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser باید is_superuser=True داشته باشد.")

        if not password:
            raise ValueError("رمز عبور مدیر الزامی است.")

        return self.create_user(phone_number, password, **extra_fields)


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "admin", "مدیر"
        ATHLETE = "athlete", "ورزشکار"
        COACH = "coach", "مربی"

    username = None

    phone_number = models.CharField(
        max_length=15,
        unique=True,
        verbose_name="شماره موبایل",
    )
    first_name = models.CharField(max_length=150, verbose_name="نام")
    last_name = models.CharField(max_length=150, verbose_name="نام خانوادگی")

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.ATHLETE,
        verbose_name="نقش کاربر",
    )
    
    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = UserManager()

    def __str__(self):
        return self.phone_number

    class Meta:
        verbose_name = "کاربر"
        verbose_name_plural = "کاربران"

class UserProfile(models.Model):
    class Gender(models.TextChoices):
        MALE = "male", "مرد"
        FEMALE = "female", "زن"
        OTHER = "other", "سایر"
        NOT_SPECIFIED = "not_specified", "ترجیح می‌دهم نگویم"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="کاربر",
    )
    gender = models.CharField(
        max_length=20,
        choices=Gender.choices,
        default=Gender.NOT_SPECIFIED,
        verbose_name="جنسیت",
    )
    national_code = models.CharField(
        max_length=10,
        unique=True,
        null=True,
        blank=True,
        verbose_name="کد ملی",
    )
    birth_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="تاریخ تولد",
    )

    def __str__(self):
        return f"پروفایل {self.user.phone_number}"

    class Meta:
        verbose_name = "پروفایل کاربر"
        verbose_name_plural = "پروفایل کاربران"


class PendingRegistration(models.Model):
    phone_number = models.CharField(
        max_length=15,
        unique=True,
        verbose_name="شماره موبایل",
    )
    first_name = models.CharField(max_length=150, verbose_name="نام")
    last_name = models.CharField(max_length=150, verbose_name="نام خانوادگی")
    password_hash = models.CharField(max_length=128)

    
    last_otp_sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="زمان آخرین ارسال کد",
    )

    otp_resend_count = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="تعداد ارسال مجدد کد",
    )


    otp_hash = models.CharField(max_length=128)
    expires_at = models.DateTimeField()
    attempts = models.PositiveSmallIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.phone_number

    class Meta:
        verbose_name = "ثبت‌نام در انتظار تأیید"
        verbose_name_plural = "ثبت‌نام‌های در انتظار تأیید"
