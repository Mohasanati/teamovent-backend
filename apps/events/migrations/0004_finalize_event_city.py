
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0003_remove_event_province_alter_event_city"),
        ("locations", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="event",
            name="province",
        ),
        migrations.RemoveField(
            model_name="event",
            name="city",
        ),
        migrations.RenameField(
            model_name="event",
            old_name="city_new",
            new_name="city",
        ),
        migrations.AlterField(
            model_name="event",
            name="city",
            field=models.ForeignKey(
                to="locations.city",
                on_delete=django.db.models.deletion.PROTECT,
                related_name="events",
                verbose_name="شهر",
            ),
        ),
    ]
