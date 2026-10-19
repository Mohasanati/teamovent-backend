
import re

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import PendingRegistration

User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        max_length=128,
        trim_whitespace=False,
        style={"input_type": "password"},
    )

    class Meta:
        model = PendingRegistration
        fields = [
            "phone_number",
            "first_name",
            "last_name",
            "password",
        ]

    def validate_phone_number(self, value):
        if not re.fullmatch(r"09\d{9}", value):
            raise serializers.ValidationError(
                "شماره موبایل باید با 09 شروع شود و دقیقاً 11 رقم باشد."
            )

        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError(
                "این شماره موبایل قبلاً ثبت‌نام کرده است."
            )

        return value

    def validate_password(self, value):
        if not value.strip():
            raise serializers.ValidationError(
                "رمز عبور نمی‌تواند خالی باشد."
            )
        return value


class VerifyRegistrationSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    code = serializers.RegexField(
        regex=r"^\d{6}$",
        error_messages={
            "invalid": "کد تأیید باید دقیقاً ۶ رقم باشد."
        },
    )

    def validate_phone_number(self, value):
        if not re.fullmatch(r"09\d{9}", value):
            raise serializers.ValidationError(
                "شماره موبایل باید با 09 شروع شود و دقیقاً 11 رقم باشد."
            )
        return value


class ResendRegistrationOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        max_length=15,
        required=True,
    )

    def validate_phone_number(self, value):
        import re

        if not re.fullmatch(r"09\d{9}", value):
            raise serializers.ValidationError(
                "شماره موبایل باید با 09 شروع شود و 11 رقم داشته باشد."
            )

        return value
