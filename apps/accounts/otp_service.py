
import hashlib
import hmac
import re
import secrets
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from .constants import (
    OTP_LENGTH,
    OTP_EXPIRY_MINUTES,
    OTP_MAX_ATTEMPTS,
)


def generate_otp():
    """Generate a cryptographically secure OTP."""
    return f"{secrets.randbelow(10**OTP_LENGTH):0{OTP_LENGTH}d}"


def hash_otp(code):
    """Hash an OTP using a server-side secret."""
    secret = settings.SECRET_KEY.encode("utf-8")
    return hmac.new(
        secret,
        code.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def verify_otp(pending_registration, submitted_code):
    """
    Verify OTP expiry, attempt limit, and hash.

    The caller must execute this function inside a transaction
    and lock the pending registration row with select_for_update().
    """
    now = timezone.now()

    if now >= pending_registration.expires_at:
        return False, "کد تأیید منقضی شده است."

    if pending_registration.attempts >= OTP_MAX_ATTEMPTS:
        return False, "تعداد تلاش‌های مجاز تمام شده است."

    if not isinstance(submitted_code, str):
        return False, "کد تأیید نامعتبر است."

    if not re.fullmatch(rf"\d{{{OTP_LENGTH}}}", submitted_code):
        return False, f"کد تأیید باید دقیقاً {OTP_LENGTH} رقم باشد."

    # Count each well-formed verification attempt, whether correct or not.
    pending_registration.attempts += 1
    pending_registration.save(update_fields=["attempts"])

    submitted_hash = hash_otp(submitted_code)

    if not hmac.compare_digest(
        pending_registration.otp_hash,
        submitted_hash,
    ):
        return False, "کد تأیید اشتباه است."

    return True, "کد تأیید معتبر است."


def otp_expiry_time():
    return timezone.now() + timedelta(minutes=OTP_EXPIRY_MINUTES)
