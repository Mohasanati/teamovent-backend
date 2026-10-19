
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def send_otp(phone_number: str, code: str) -> None:
    """
    Send OTP through the configured SMS provider.
    In development, print the code to the server console only.
    """
    if settings.DEBUG:
        print(
            f"[DEV OTP] Phone: {phone_number} | Code: {code}",
            flush=True,
        )
        return

    raise ImproperlyConfigured(
        "سرویس ارسال پیامک در محیط عملیاتی پیکربندی نشده است."
    )
