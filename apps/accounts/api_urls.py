
from django.urls import path
from .views import (
    RegisterAPIView,
    VerifyRegistrationAPIView,
    ResendRegistrationOTPAPIView,
)

urlpatterns = [
    path("register/", RegisterAPIView.as_view(), name="register"),
    path("register/verify/", VerifyRegistrationAPIView.as_view(), name="register-verify"),
    path("register/resend/", ResendRegistrationOTPAPIView.as_view(), name="register-resend"),
]
