"""Commande de management pour charger les secteurs par défaut."""

from django.core.management.base import BaseCommand

from events.fixtures.sectors import DEFAULT_SECTORS
from events.models import Sector


class Command(BaseCommand):
    """Charge les secteurs par défaut dans la base de données."""

    help = "Charge les secteurs par défaut"

    def handle(self, *args, **options):
        """Exécute la commande."""
        count = 0
        for sector_data in DEFAULT_SECTORS:
            sector, created = Sector.objects.get_or_create(
                name=sector_data["name"],
                defaults={
                    "color_code": sector_data["color_code"],
                    "description": sector_data["description"],
                    "order": sector_data["order"],
                },
            )
            if created:
                count += 1
                self.stdout.write(self.style.SUCCESS(f"Secteur créé: {sector.name}"))
            else:
                self.stdout.write(f"Secteur existant: {sector.name}")

        self.stdout.write(self.style.SUCCESS(f"\n{count} secteur(s) créé(s)"))
