# Generated manually on 2026-02-11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0010_add_eventimage_caption"),
    ]

    operations = [
        migrations.CreateModel(
            name="EventSettings",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "video_notification_email",
                    models.EmailField(
                        default="communication@cc-sudavesnois.fr",
                        help_text="Adresse email qui recevra les demandes de tournage vidéo",
                        verbose_name="Email de notification vidéo",
                    ),
                ),
                (
                    "max_events_per_user",
                    models.PositiveIntegerField(
                        default=50,
                        help_text="Limite le nombre d'événements qu'un utilisateur peut créer",
                        verbose_name="Nombre maximum d'événements par utilisateur",
                    ),
                ),
                (
                    "max_images_per_event",
                    models.PositiveIntegerField(
                        default=10,
                        help_text="Limite le nombre d'images qu'un événement peut contenir",
                        verbose_name="Nombre maximum d'images par événement",
                    ),
                ),
                (
                    "auto_validate_events",
                    models.BooleanField(
                        default=False,
                        help_text="Si activé, les événements seront automatiquement validés sans passer par la file d'attente",
                        verbose_name="Validation automatique",
                    ),
                ),
                (
                    "default_from_email",
                    models.EmailField(
                        default="communication@cc-sudavesnois.fr",
                        help_text="Adresse email utilisée pour envoyer les notifications",
                        verbose_name="Email d'expédition",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Modifié le"),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.SET_NULL,
                        related_name="event_settings_updates",
                        to="accounts.user",
                        verbose_name="Modifié par",
                    ),
                ),
            ],
            options={
                "verbose_name": "Paramètres des événements",
                "verbose_name_plural": "Paramètres des événements",
            },
        ),
    ]
