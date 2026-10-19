from django.urls import path

from .views import SportListAPIView

urlpatterns = [
    path(
        "",
        SportListAPIView.as_view(),
        name="sport-list",
    ),
]