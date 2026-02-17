# Generated manually on 2026-02-10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_add_notification_model"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notification",
            name="notification_type",
            field=models.CharField(
                choices=[
                    ("video_refused", "Refus de tournage vidéo"),
                    ("video_confirmed", "Confirmation de tournage vidéo"),
                    ("event_created", "Nouvel événement créé"),
                    ("event_updated", "Événement modifié"),
                    ("event_deleted", "Événement supprimé"),
                    ("event_commented", "Nouveau commentaire"),
                    ("event_validated", "Événement validé"),
                    ("event_rejected", "Événement rejeté"),
                    ("video_request_sent", "Demande de tournage envoyée"),
                ],
                max_length=50,
                verbose_name="type",
            ),
        ),
    ]
