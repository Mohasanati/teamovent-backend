
from django.contrib import admin
from .models import City, Province


@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "slug")
    ordering = ("name",)


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "province", "is_active")
    list_filter = ("province", "is_active")
    search_fields = ("name", "slug", "province__name")
    ordering = ("province__name", "name")
    list_per_page = 50
