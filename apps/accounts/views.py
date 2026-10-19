
import logging

from django.db import IntegrityError
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import PendingRegistration
from .serializers import RegistrationSerializer

from .registration_service import (
    create_pending_registration,
    verify_pending_registration,
    resend_pending_registration_otp,
)
from .serializers import (
    VerifyRegistrationSerializer,
    ResendRegistrationOTPSerializer,
)
from .otp_service import hash_otp
from .sms_service import send_otp

logger = logging.getLogger(__name__)


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            pending, code = create_pending_registration(
                phone_number=serializer.validated_data["phone_number"],
                first_name=serializer.validated_data["first_name"],
                last_name=serializer.validated_data["last_name"],
                password=serializer.validated_data["password"],
            )

        except ValueError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except IntegrityError:
            logger.warning(
                "Registration database conflict occurred."
            )
            return Response(
                {
                    "detail": (
                        "درخواست ثبت‌نام با تعارض مواجه شد. "
                        "لطفاً دوباره تلاش کنید."
                    )
                },
                status=status.HTTP_409_CONFLICT,
            )

        except Exception:
            logger.exception(
                "Unexpected error while creating pending registration."
            )
            return Response(
                {
                    "detail": (
                        "در حال حاضر امکان ثبت‌نام وجود ندارد. "
                        "لطفاً بعداً تلاش کنید."
                    )
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        try:
            send_otp(pending.phone_number, code)

        except Exception:
            logger.exception(
                "OTP delivery failed for pending registration."
            )

            # فقط رکورد مربوط به همین کد را حذف می‌کنیم.
            # اگر رکورد هم‌زمان تغییر کرده باشد، حذف نمی‌شود.
            PendingRegistration.objects.filter(
                phone_number=pending.phone_number,
                otp_hash=hash_otp(code),
            ).delete()

            return Response(
                {
                    "detail": (
                        "ارسال کد تأیید ناموفق بود. "
                        "لطفاً بعداً دوباره تلاش کنید."
                    )
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response(
            {
                "detail": (
                    "ثبت‌نام موقت ایجاد شد. "
                    "کد تأیید در محیط آزمایشی در ترمینال سرور "
                    "نمایش داده شده است."
                )
            },
            status=status.HTTP_200_OK,
        )

class VerifyRegistrationAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user, error_message = verify_pending_registration(
                phone_number=serializer.validated_data["phone_number"],
                code=serializer.validated_data["code"],
            )
            if error_message:
                return Response(
                {"detail": error_message},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ValueError as exc:
                return Response(
            {"detail": str(exc)},
            status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception:
            logger.exception("Registration OTP verification failed.")
            return Response(
            {"detail": "خطای داخلی هنگام تأیید ثبت‌نام رخ داد."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
        {
            "detail": "ثبت‌نام با موفقیت تأیید شد.",
            "user": {
                "phone_number": user.phone_number,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role,
                "role_display": user.get_role_display(),
            },
        },
        status=status.HTTP_201_CREATED,
    )



class ResendRegistrationOTPAPIView(APIView):
    permission_classes = [AllowAny]

    
    def post(self, request):
        serializer = ResendRegistrationOTPSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        phone_number = serializer.validated_data["phone_number"]

        try:
            pending, code = resend_pending_registration_otp(
                phone_number=phone_number
            )
        except ValueError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception:
            logger.exception("Failed to prepare OTP resend.")
            return Response(
                {"detail": "خطای داخلی هنگام ارسال مجدد کد رخ داد."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        try:
            send_otp(pending.phone_number, code)
        except Exception:
            logger.exception("Failed to send resent OTP.")
            return Response(
                {"detail": "ارسال کد تأیید ناموفق بود."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response(
            {
                "detail": (
                    "کد تأیید جدید در محیط آزمایشی "
                    "در ترمینال سرور نمایش داده شد."
                )
            },
            status=status.HTTP_200_OK,
        )

