from rest_framework import generics
from rest_framework.exceptions import ValidationError

from .models import Province, City
from .serializers import ProvinceSerializer, CitySerializer


class ProvinceListAPIView(generics.ListAPIView):
    serializer_class = ProvinceSerializer

    def get_queryset(self):
        return Province.objects.filter(is_active=True)


class CityListAPIView(generics.ListAPIView):
    serializer_class = CitySerializer

    def get_queryset(self):
        province_id = self.request.query_params.get("province")

        if not province_id:
            raise ValidationError({
                "province": "شناسه استان را مشخص کنید."
            })

        return City.objects.filter(
            province_id=province_id,
            province__is_active=True,
            is_active=True,
        ).select_related("province")