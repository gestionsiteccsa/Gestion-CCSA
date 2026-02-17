# Generated manually for removing email defaults

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0012_alter_videorequestlog_confirmation_token_and_more"),
    ]

    operations = [
        # Remove default from video_notification_email and make it nullable
        migrations.AlterField(
            model_name="eventsettings",
            name="video_notification_email",
            field=models.EmailField(
                blank=True,
                help_text="Adresse email qui recevra les demandes de tournage vidéo. Doit être configuré pour pouvoir envoyer des demandes.",
                max_length=254,
                null=True,
                verbose_name="Email de notification vidéo",
            ),
        ),
        # Remove default from default_from_email and make it nullable
        migrations.AlterField(
            model_name="eventsettings",
            name="default_from_email",
            field=models.EmailField(
                blank=True,
                help_text="Adresse email utilisée pour envoyer les notifications (optionnel)",
                max_length=254,
                null=True,
                verbose_name="Email d'expédition",
            ),
        ),
    ]
