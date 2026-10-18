
import hashlib

import django.db.models.deletion
from django.db import migrations, models


def transfer_old_locations(apps, schema_editor):
    Event = apps.get_model("events", "Event")
    Province = apps.get_model("locations", "Province")
    City = apps.get_model("locations", "City")

    for event in Event.objects.all().iterator():
        province_name = (event.province or "").strip() or "نامشخص"
        city_name = (event.city or "").strip() or "نامشخص"

        province_hash = hashlib.sha256(
            province_name.encode("utf-8")
        ).hexdigest()[:12]

        province, _ = Province.objects.get_or_create(
            name=province_name,
            defaults={
                "slug": f"province-{province_hash}",
                "is_active": True,
            },
        )

        city_hash = hashlib.sha256(
            f"{province.pk}:{city_name}".encode("utf-8")
        ).hexdigest()[:12]

        city, _ = City.objects.get_or_create(
            province=province,
            name=city_name,
            defaults={
                "slug": f"city-{city_hash}",
                "is_active": True,
            },
        )

        event.city_new_id = city.pk
        event.save(update_fields=["city_new"])


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0002_event_session_count"),
        ("locations", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="city_new",
            field=models.ForeignKey(
                to="locations.city",
                on_delete=django.db.models.deletion.PROTECT,
                null=True,
                blank=True,
                related_name="+",
                verbose_name="شهر جدید",
            ),
        ),
        migrations.RunPython(
            transfer_old_locations,
            migrations.RunPython.noop,
        ),
    ]
