"""Commande pour créer 60 événements de test entre mars et mai 2026."""

import random
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import User
from events.models import Event, Sector


class Command(BaseCommand):
    """Crée 60 événements de test entre mars et mai 2026."""

    help = "Crée 60 événements de test avec chevauchements entre mars et mai 2026"

    def handle(self, *args, **options):
        user = User.objects.first()
        sectors = list(Sector.objects.all())

        if not user:
            self.stdout.write(self.style.ERROR("Aucun utilisateur trouvé"))
            return

        if not sectors:
            self.stdout.write(self.style.ERROR("Aucun secteur trouvé"))
            return

        # Configuration
        start_date = timezone.make_aware(datetime(2026, 3, 1))
        end_date = timezone.make_aware(datetime(2026, 5, 31))
        date_range_days = (end_date - start_date).days

        # Liste de titres
        titles = [
            "Réunion CCSA",
            "Atelier Communication",
            "Formation vidéo",
            "Conférence de presse",
            "Réunion sectorielle",
            "Comité de direction",
            "Présentation projet",
            "Réunion partenaires",
            "Séminaire interne",
            "Formation collaborateurs",
            "Réunion technique",
            "Point d'étape",
            "Réunion projet",
            "Conférence",
            "Table ronde",
            "Atelier créatif",
            "Brainstorming",
            "Présentation stratégie",
            "Réunion mensuelle",
            "Conseil d'administration",
            "AG CCSA",
            "Réunion équipe",
            "Formation interne",
            "Séminaire externe",
            "Journée portes ouvertes",
            "Réunion client",
            "Négociation contrat",
            "Réunion prestataire",
            "Validation projet",
            "Lancement produit",
            "Réunion bilan",
            "Planification stratégique",
            "Réunion crise",
            "Point projet",
            "Réunion fournisseur",
            "Audit interne",
            "Réunion plénière",
            "Commission permanente",
            "Réunion de travail",
            "Atelier prospective",
            "Diagnostic territoire",
            "Réunion mobilité",
            "Commission tourisme",
            "Réunion habitat",
            "Commission environnement",
            "Réunion économie",
            "Commission communication",
            "Réunion jeunesse",
            "Commission culture",
        ]

        cities = [
            "Paris",
            "Lyon",
            "Marseille",
            "Bordeaux",
            "Toulouse",
            "Nantes",
            "Strasbourg",
            "Lille",
        ]

        # Créer les événements
        created = 0
        same_day_count = 0
        same_hour_count = 0

        for i in range(60):
            # Date aléatoire entre mars et mai 2026
            random_days = random.randint(0, date_range_days)
            event_date = start_date + timedelta(days=random_days)
            base_date = event_date.replace(hour=0, minute=0, second=0, microsecond=0)

            # 40% de chance d'avoir plusieurs événements le même jour
            if random.random() < 0.4 and i < 55:
                # Créer 2-3 événements le même jour
                num_same_day = random.randint(2, 3)
                same_day_count += num_same_day

                first_hour = None
                first_minute = None
                for j in range(num_same_day):
                    # 50% de chance d'avoir la même heure
                    if j > 0 and first_hour is not None and random.random() < 0.5:
                        # Même heure que le premier
                        hour = first_hour
                        minute = first_minute
                        same_hour_count += 1
                    else:
                        hour = random.choice([9, 10, 11, 14, 15, 16, 17])
                        minute = random.choice([0, 15, 30, 45])
                        if j == 0:
                            first_hour = hour
                            first_minute = minute

                    event_start = base_date.replace(hour=hour, minute=minute)
                    duration = random.randint(1, 4)
                    event_end = event_start + timedelta(hours=duration)

                    event = Event.objects.create(
                        title=f"{random.choice(titles)} {i+1}.{j+1}",
                        description=f"Description de l'événement {i+1}.{j+1} avec des détails sur l'activité prévue.",
                        location=(
                            f"{random.randint(1, 50)} rue "
                            f"{random.choice(['Principale', 'Centrale', 'de Paris', 'des Champs', 'de la Mairie'])}"
                        ),
                        city=random.choice(cities),
                        start_datetime=event_start,
                        end_datetime=event_end,
                        created_by=user,
                        is_active=True,
                        comm_before=random.choice([True, False]),
                        comm_during=random.choice([True, False]),
                        comm_after=random.choice([True, False]),
                        needs_filming=random.choice([True, False]),
                        needs_poster=random.choice([True, False]),
                    )

                    # Assigner 1-2 secteurs
                    num_sectors = random.randint(1, min(2, len(sectors)))
                    event.sectors.set(random.sample(sectors, num_sectors))

                    created += 1
                    self.stdout.write(
                        f"  {event.title} - {event.start_datetime.strftime('%d/%m/%Y %H:%M')}"
                    )

                # Sauter les indices utilisés
                i += num_same_day - 1
            else:
                # Événement unique
                hour = random.choice([8, 9, 10, 11, 14, 15, 16, 17])
                minute = random.choice([0, 15, 30, 45])
                event_start = base_date.replace(hour=hour, minute=minute)
                duration = random.randint(1, 5)
                event_end = event_start + timedelta(hours=duration)

                event = Event.objects.create(
                    title=f"{random.choice(titles)} {i+1}",
                    description=f"Description de l'événement {i+1} avec des détails sur l'activité prévue.",
                    location=(
                        f"{random.randint(1, 50)} rue "
                        f"{random.choice(['Principale', 'Centrale', 'de Paris', 'des Champs', 'de la Mairie'])}"
                    ),
                    city=random.choice(cities),
                    start_datetime=event_start,
                    end_datetime=event_end,
                    created_by=user,
                    is_active=True,
                    comm_before=random.choice([True, False]),
                    comm_during=random.choice([True, False]),
                    comm_after=random.choice([True, False]),
                    needs_filming=random.choice([True, False]),
                    needs_poster=random.choice([True, False]),
                )

                # Assigner 1-2 secteurs
                num_sectors = random.randint(1, min(2, len(sectors)))
                event.sectors.set(random.sample(sectors, num_sectors))

                created += 1
                self.stdout.write(
                    f"  {event.title} - {event.start_datetime.strftime('%d/%m/%Y %H:%M')}"
                )

        self.stdout.write(
            self.style.SUCCESS(f"\n[OK] {created} événements créés avec succès !")
        )
        self.stdout.write(
            f"  - {same_day_count} événements partagent leur jour avec d'autres"
        )
        self.stdout.write(
            f"  - {same_hour_count} événements ont la même heure (chevauchement)"
        )
