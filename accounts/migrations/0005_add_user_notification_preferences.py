# Generated manually

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0004_alter_notification_notification_type"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserNotificationPreference",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "notification_type",
                    models.CharField(
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
                        verbose_name="type de notification",
                    ),
                ),
                (
                    "in_app_enabled",
                    models.BooleanField(default=True, verbose_name="notification in-app activée"),
                ),
                (
                    "email_enabled",
                    models.BooleanField(default=False, verbose_name="notification email activée"),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="créée le")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="modifiée le")),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notification_preferences",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="utilisateur",
                    ),
                ),
            ],
            options={
                "verbose_name": "préférence de notification",
                "verbose_name_plural": "préférences de notifications",
                "ordering": ["notification_type"],
                "unique_together": {("user", "notification_type")},
            },
        ),
    ]
