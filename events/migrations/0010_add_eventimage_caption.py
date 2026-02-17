# Generated manually on 2026-02-11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0009_videorequestlog_refused_videorequestlog_refused_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="eventimage",
            name="caption",
            field=models.CharField(
                blank=True,
                help_text="Description ou légende de l'image (optionnel)",
                max_length=255,
                verbose_name="Légende",
            ),
        ),
    ]
