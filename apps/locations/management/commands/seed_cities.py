
import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.locations.models import City, Province


class Command(BaseCommand):
    help = "Import Iranian cities from JSON data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Validate and preview without saving changes",
        )

    def handle(self, *args, **options):
        data_dir = Path("data")
        provinces_file = data_dir / "provinces.json"
        cities_file = data_dir / "cities-filtered.json"

        for file_path in (provinces_file, cities_file):
            if not file_path.is_file():
                raise CommandError(f"File not found: {file_path}")

        try:
            with provinces_file.open(encoding="utf-8") as file:
                source_provinces = json.load(file)

            with cities_file.open(encoding="utf-8") as file:
                source_cities = json.load(file)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise CommandError(f"Invalid JSON data: {exc}") from exc

        if not isinstance(source_provinces, list):
            raise CommandError("Province data must be a JSON list.")
        if not isinstance(source_cities, list):
            raise CommandError("City data must be a JSON list.")

        provinces_by_source_id = {}
        for item in source_provinces:
            province = Province.objects.filter(
                name=item["name"]
            ).first()
            if province is None:
                raise CommandError(
                    f"Province not found in database: {item['name']}"
                )
            provinces_by_source_id[item["id"]] = province

        seen = set()
        to_create = 0
        already_exists = 0
        pending_cities = []

        for item in source_cities:
            province = provinces_by_source_id.get(item["province_id"])
            if province is None:
                raise CommandError(
                    f"Unknown province_id: {item['province_id']}"
                )

            name = item["name"].strip()
            if not name:
                raise CommandError(
                    f"Empty city name for source ID {item['id']}"
                )

            key = (province.pk, name)
            if key in seen:
                continue
            seen.add(key)

            exists = City.objects.filter(
                province=province,
                name=name,
            ).exists()

            if exists:
                already_exists += 1
            else:
                to_create += 1
                pending_cities.append(
                    City(
                        province=province,
                        name=name,
                        slug=f"city-{item['id']}",
                        is_active=True,
                    )
                )

        self.stdout.write(f"Cities in source: {len(source_cities)}")
        self.stdout.write(f"New cities: {to_create}")
        self.stdout.write(f"Existing cities preserved: {already_exists}")

        if options["dry_run"]:
            self.stdout.write(
                self.style.SUCCESS(
                    "Dry run completed; no changes saved."
                )
            )
            self.stdout.write(
                f"Cities currently in database: {City.objects.count()}"
            )
            return

        with transaction.atomic():
            City.objects.bulk_create(pending_cities, batch_size=500)

        self.stdout.write(
            self.style.SUCCESS("City import completed.")
        )
        self.stdout.write(
            f"Cities now in database: {City.objects.count()}"
        )
