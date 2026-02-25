"""Commande de management pour générer des événements fictifs."""

import random
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from accounts.models import User
from events.models import Event, Sector

fake = Faker("fr_FR")


class Command(BaseCommand):
    """Génère des événements fictifs pour le développement."""

    help = "Génère des événements fictifs avec dates entre le 01/02/2025 et 01/05/2026"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=15,
            help="Nombre d'événements à créer (défaut: 15)",
        )
        parser.add_argument(
            "--user",
            type=str,
            help="Email de l'utilisateur créateur (défaut: premier utilisateur)",
        )

    def handle(self, *args, **options):
        count = options["count"]
        user_email = options["user"]

        # Récupérer ou créer l'utilisateur
        if user_email:
            try:
                user = User.objects.get(email=user_email)
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"Utilisateur {user_email} non trouvé")
                )
                return
        else:
            user = User.objects.first()
            if not user:
                self.stdout.write(
                    self.style.ERROR(
                        "Aucun utilisateur trouvé. Créez un utilisateur d'abord."
                    )
                )
                return

        # Récupérer tous les secteurs
        sectors = list(Sector.objects.all())
        if not sectors:
            self.stdout.write(
                self.style.WARNING(
                    "Aucun secteur trouvé. Exécutez 'python manage.py load_sectors' d'abord."
                )
            )
            return

        # Dates de référence (2025 et 2026)
        start_date = datetime(2025, 2, 1, tzinfo=timezone.get_current_timezone())
        end_date = datetime(2026, 5, 1, tzinfo=timezone.get_current_timezone())
        date_range_days = (end_date - start_date).days

        created_count = 0
        events_data = []

        # Générer les données des événements
        for i in range(count):
            # Date aléatoire dans la plage
            random_days = random.randint(0, date_range_days)
            random_hours = random.randint(8, 18)  # Entre 8h et 18h
            event_start = start_date + timedelta(days=random_days, hours=random_hours)

            # Durée aléatoire entre 1 et 8 heures
            duration_hours = random.randint(1, 8)
            event_end = event_start + timedelta(hours=duration_hours)

            events_data.append(
                {
                    "title": fake.catch_phrase(),
                    "description": fake.text(max_nb_chars=500),
                    "location": fake.street_address(),
                    "city": fake.city(),
                    "start_datetime": event_start,
                    "end_datetime": event_end,
                    "created_by": user,
                    "is_active": True,
                    "comm_before": random.choice([True, False]),
                    "comm_during": random.choice([True, False]),
                    "comm_after": random.choice([True, False]),
                    "needs_filming": random.choice([True, False]),
                    "needs_poster": random.choice([True, False]),
                }
            )

        # Créer 1-2 paires d'événements qui se chevauchent
        num_overlapping_pairs = random.randint(1, 2)

        for pair_idx in range(num_overlapping_pairs):
            # Choisir une date aléatoire pour le chevauchement
            random_days = random.randint(0, date_range_days)
            base_hour = random.randint(9, 15)  # Entre 9h et 15h pour avoir de la marge

            base_date = start_date + timedelta(days=random_days)

            # Premier événement : 14h-16h
            event1_start = base_date.replace(hour=14, minute=0)
            event1_end = base_date.replace(hour=16, minute=0)

            # Deuxième événement : 15h-17h (chevauchement de 1h)
            event2_start = base_date.replace(hour=15, minute=0)
            event2_end = base_date.replace(hour=17, minute=0)

            # Remplacer 2 événements existants par ces événements qui se chevauchent
            replace_indices = random.sample(range(len(events_data)), 2)

            events_data[replace_indices[0]].update(
                {
                    "title": f"{fake.catch_phrase()} - Session A",
                    "start_datetime": event1_start,
                    "end_datetime": event1_end,
                    "description": fake.text(max_nb_chars=300)
                    + "\n\n(Cet événement se chevauche avec un autre)",
                }
            )

            events_data[replace_indices[1]].update(
                {
                    "title": f"{fake.catch_phrase()} - Session B",
                    "start_datetime": event2_start,
                    "end_datetime": event2_end,
                    "description": fake.text(max_nb_chars=300)
                    + "\n\n(Cet événement se chevauche avec un autre)",
                }
            )

            self.stdout.write(
                self.style.WARNING(
                    f"Création d'événements chevauchants le {base_date.strftime('%d/%m/%Y')}"
                )
            )

        # Créer les événements dans la base de données
        for event_data in events_data:
            # Extraire les secteurs avant la création
            num_sectors = random.randint(1, min(3, len(sectors)))
            selected_sectors = random.sample(sectors, num_sectors)

            # Créer l'événement
            event = Event.objects.create(**event_data)

            # Assigner les secteurs
            event.sectors.set(selected_sectors)

            created_count += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f"Événement créé: {event.title} ({event.start_datetime.strftime('%d/%m/%Y %H:%M')} - {event.end_datetime.strftime('%H:%M')})"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(f"\n{created_count} événement(s) créé(s) avec succès")
        )

        if num_overlapping_pairs > 0:
            self.stdout.write(
                self.style.WARNING(
                    f"Dont {num_overlapping_pairs * 2} événements avec chevauchement temporel"
                )
            )
