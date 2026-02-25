"""
Commande pour nettoyer les notifications de plus de 15 jours.

À exécuter via cron une fois par jour.
"""

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import Notification


class Command(BaseCommand):
    """Commande pour nettoyer les anciennes notifications."""

    help = "Supprime les notifications de plus de 15 jours"

    def add_arguments(self, parser):
        """Ajoute les arguments de la commande."""
        parser.add_argument(
            "--days",
            type=int,
            default=15,
            help=(
                "Nombre de jours après lesquels les notifications "
                "sont supprimées (défaut: 15)"
            ),
        )

    def handle(self, *args, **options):
        """Exécute la commande."""
        days = options["days"]
        cutoff_date = timezone.now() - timedelta(days=days)

        # Supprimer les notifications anciennes
        deleted_count = Notification.objects.filter(
            created_at__lt=cutoff_date
        ).delete()[0]

        self.stdout.write(
            self.style.SUCCESS(
                f"{deleted_count} notification(s) de plus de {days} "
                "jours ont été supprimées."
            )
        )
