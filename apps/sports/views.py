from rest_framework import generics

from .models import Sport
from .serializers import SportSerializer


class SportListAPIView(generics.ListAPIView):
    serializer_class = SportSerializer

    def get_queryset(self):
        return Sport.objects.filter(is_active=True)