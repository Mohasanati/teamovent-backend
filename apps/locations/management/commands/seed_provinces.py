
from django.core.management.base import BaseCommand
from apps.locations.models import Province, City


PROVINCES = [
    ("آذربایجان شرقی", "east-azerbaijan"),
    ("آذربایجان غربی", "west-azerbaijan"),
    ("اردبیل", "ardabil"),
    ("اصفهان", "isfahan"),
    ("البرز", "alborz"),
    ("ایلام", "ilam"),
    ("بوشهر", "bushehr"),
    ("تهران", "tehran"),
    ("چهارمحال و بختیاری", "chaharmahal-and-bakhtiari"),
    ("خراسان جنوبی", "south-khorasan"),
    ("خراسان رضوی", "razavi-khorasan"),
    ("خراسان شمالی", "north-khorasan"),
    ("خوزستان", "khuzestan"),
    ("زنجان", "zanjan"),
    ("سمنان", "semnan"),
    ("سیستان و بلوچستان", "sistan-and-baluchestan"),
    ("فارس", "fars"),
    ("قزوین", "qazvin"),
    ("قم", "qom"),
    ("کردستان", "kurdistan"),
    ("کرمان", "kerman"),
    ("کرمانشاه", "kermanshah"),
    ("کهگیلویه و بویراحمد", "kohgiluyeh-and-boyer-ahmad"),
    ("گلستان", "golestan"),
    ("گیلان", "gilan"),
    ("لرستان", "lorestan"),
    ("مازندران", "mazandaran"),
    ("مرکزی", "markazi"),
    ("هرمزگان", "hormozgan"),
    ("همدان", "hamedan"),
    ("یزد", "yazd"),
]


class Command(BaseCommand):
    help = "ثبت استان‌های ایران و استانداردسازی اسلاگ اصفهان"

    def handle(self, *args, **options):
        for name, slug in PROVINCES:
            conflict = Province.objects.filter(slug=slug).exclude(name=name)
            if conflict.exists():
                self.stdout.write(
                    self.style.ERROR(
                        f"اسلاگ {slug} قبلاً برای استان دیگری استفاده شده است."
                    )
                )
                return

            Province.objects.update_or_create(
                name=name,
                defaults={"slug": slug, "is_active": True},
            )

        isfahan = Province.objects.get(slug="isfahan")
        City.objects.filter(
            province=isfahan,
            name="اصفهان",
        ).update(slug="isfahan")

        self.stdout.write(
            self.style.SUCCESS(
                f"تعداد استان‌های ثبت‌شده: {Province.objects.count()}"
            )
        )
