
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.utils import timezone
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from .otp_service import (
    generate_otp,
    hash_otp,
    otp_expiry_time,
    verify_otp,
)

from .constants import (
    OTP_MAX_RESENDS,
    OTP_RESEND_COOLDOWN_SECONDS,
)
from .models import PendingRegistration
from .otp_service import generate_otp, hash_otp, otp_expiry_time


User = get_user_model()



@transaction.atomic
def create_pending_registration(
    *,
    phone_number,
    first_name,
    last_name,
    password,
):
    if User.objects.filter(phone_number=phone_number).exists():
        raise ValueError("این شماره موبایل قبلاً ثبت‌نام کرده است.")

    now = timezone.now()

    pending = (
        PendingRegistration.objects
        .select_for_update()
        .filter(phone_number=phone_number)
        .first()
    )

    if pending and pending.expires_at > now:
        raise ValueError(
            "کد قبلی هنوز منقضی نشده است. لطفاً پس از انقضا دوباره درخواست دهید."
        )

    code = generate_otp()

    defaults = {
        "first_name": first_name,
        "last_name": last_name,
        "password_hash": make_password(password),
        "otp_hash": hash_otp(code),
        "expires_at": otp_expiry_time(),
        "attempts": 0,
        "last_otp_sent_at": timezone.now(),
        "otp_resend_count": 0,
    }

    if pending:
        for field, value in defaults.items():
            setattr(pending, field, value)
        pending.save()
    else:
        pending = PendingRegistration.objects.create(
            phone_number=phone_number,
            **defaults,
        )

    return pending, code


@transaction.atomic
def verify_pending_registration(*, phone_number, code):
    pending = (
        PendingRegistration.objects
        .select_for_update()
        .filter(phone_number=phone_number)
        .first()
    )

    if pending is None:
        raise ValueError(
            "ثبت‌نام موقتی برای این شماره پیدا نشد یا منقضی شده است."
        )

    
    if User.objects.filter(phone_number=phone_number).exists():
        raise ValueError("این شماره موبایل قبلاً ثبت‌نام کرده است.")


    is_valid, message = verify_otp(pending, code)

    if not is_valid:
        # خروج عادی از تراکنش باعث ذخیره‌شدن شمارنده تلاش‌ها می‌شود.
        # خطای اعتبارسنجی را پس از پایان تراکنش به فراخواننده برمی‌گردانیم.
        return None, message

    user = User(
        phone_number=pending.phone_number,
        first_name=pending.first_name,
        last_name=pending.last_name,
        is_active=True,
    )

    # رمز عبور قبلاً با Django hash شده است؛ دوباره hash نمی‌کنیم.
    user.password = pending.password_hash
    user.save()

    pending.delete()

    return user, None

@transaction.atomic
def resend_pending_registration_otp(*, phone_number):
    pending = (
        PendingRegistration.objects
        .select_for_update()
        .filter(phone_number=phone_number)
        .first()
    )

    if pending is None:
        raise ValueError(
            "ثبت‌نام موقتی برای این شماره پیدا نشد."
        )

    now = timezone.now()

    if pending.last_otp_sent_at:
        cooldown_end = (
            pending.last_otp_sent_at
            + timedelta(seconds=OTP_RESEND_COOLDOWN_SECONDS)
        )

        if now < cooldown_end:
            remaining = int(
                (cooldown_end - now).total_seconds()
            ) + 1

            raise ValueError(
                f"برای درخواست کد جدید، {remaining} ثانیه صبر کنید."
            )

    if pending.otp_resend_count >= OTP_MAX_RESENDS:
        raise ValueError(
            "حداکثر تعداد ارسال مجدد کد تمام شده است. "
            "لطفاً ثبت‌نام را بعداً دوباره شروع کنید."
        )

    code = generate_otp()

    pending.otp_hash = hash_otp(code)
    pending.expires_at = otp_expiry_time()
    pending.attempts = 0
    pending.last_otp_sent_at = now
    pending.otp_resend_count += 1

    pending.save(
        update_fields=[
            "otp_hash",
            "expires_at",
            "attempts",
            "last_otp_sent_at",
            "otp_resend_count",
            "updated_at",
        ]
    )
    
    return pending, code