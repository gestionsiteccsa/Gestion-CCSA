"""Tests pour les modèles de l'app pointage."""

from datetime import date, timedelta

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from accounts.models import Role, User
from pointage.models import DailyTracking, SectionType, TrackingHistory


class SectionTypeModelTests(TestCase):
    """Tests pour le modèle SectionType."""

    def setUp(self):
        """Créer les données de test."""
        self.user = User.objects.create_user(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            password="testpass123",
        )

    def test_create_section_type(self):
        """Teste la création d'un type de section."""
        section = SectionType.objects.create(
            name="Accueil",
            description="Visites à l'accueil",
            color="#3b82f6",
            order=1,
        )

        self.assertEqual(section.name, "Accueil")
        self.assertEqual(section.description, "Visites à l'accueil")
        self.assertEqual(section.color, "#3b82f6")
        self.assertEqual(section.order, 1)
        self.assertTrue(section.is_active)

    def test_section_type_ordering(self):
        """Teste l'ordre des sections."""
        SectionType.objects.create(name="Section C", order=3)
        SectionType.objects.create(name="Section A", order=1)
        SectionType.objects.create(name="Section B", order=2)

        sections = list(SectionType.objects.all())
        self.assertEqual(sections[0].name, "Section A")
        self.assertEqual(sections[1].name, "Section B")
        self.assertEqual(sections[2].name, "Section C")

    def test_section_type_str(self):
        """Teste la représentation string du type de section."""
        section = SectionType.objects.create(name="Accueil")
        self.assertEqual(str(section), "Accueil")

    def test_default_values(self):
        """Teste les valeurs par défaut."""
        section = SectionType.objects.create(name="Test")
        self.assertEqual(section.color, "#64748b")
        self.assertEqual(section.order, 0)
        self.assertTrue(section.is_active)


class DailyTrackingModelTests(TestCase):
    """Tests pour le modèle DailyTracking."""

    def setUp(self):
        """Créer les données de test."""
        self.user = User.objects.create_user(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            password="testpass123",
        )
        self.section = SectionType.objects.create(
            name="Accueil",
            order=1,
        )

    def test_create_daily_tracking(self):
        """Teste la création d'un pointage journalier."""
        tracking = DailyTracking.objects.create(
            date=date.today(),
            section=self.section,
            count=5,
            created_by=self.user,
            updated_by=self.user,
        )

        self.assertEqual(tracking.date, date.today())
        self.assertEqual(tracking.section, self.section)
        self.assertEqual(tracking.count, 5)
        self.assertEqual(tracking.created_by, self.user)
        self.assertEqual(tracking.updated_by, self.user)

    def test_unique_constraint(self):
        """Teste la contrainte d'unicité date + section."""
        DailyTracking.objects.create(
            date=date.today(),
            section=self.section,
            count=5,
            created_by=self.user,
            updated_by=self.user,
        )

        with self.assertRaises(IntegrityError):
            DailyTracking.objects.create(
                date=date.today(),
                section=self.section,
                count=3,
                created_by=self.user,
                updated_by=self.user,
            )

    def test_update_count(self):
        """Teste la mise à jour du compteur."""
        tracking = DailyTracking.objects.create(
            date=date.today(),
            section=self.section,
            count=5,
            created_by=self.user,
            updated_by=self.user,
        )

        tracking.count = 10
        tracking.save()

        tracking.refresh_from_db()
        self.assertEqual(tracking.count, 10)

    def test_default_count(self):
        """Teste la valeur par défaut du compteur."""
        tracking = DailyTracking.objects.create(
            date=date.today(),
            section=self.section,
            created_by=self.user,
            updated_by=self.user,
        )
        self.assertEqual(tracking.count, 0)

    def test_count_cannot_be_negative(self):
        """Teste que le compteur ne peut pas être négatif."""
        tracking = DailyTracking(
            date=date.today(),
            section=self.section,
            count=-1,
            created_by=self.user,
            updated_by=self.user,
        )

        with self.assertRaises(ValidationError):
            tracking.full_clean()

    def test_str_representation(self):
        """Teste la représentation string."""
        tracking = DailyTracking.objects.create(
            date=date.today(),
            section=self.section,
            count=5,
            created_by=self.user,
            updated_by=self.user,
        )

        expected = f"Accueil - {date.today()} : 5"
        self.assertEqual(str(tracking), expected)


class TrackingHistoryModelTests(TestCase):
    """Tests pour le modèle TrackingHistory."""

    def setUp(self):
        """Créer les données de test."""
        self.user = User.objects.create_user(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            password="testpass123",
        )
        self.section = SectionType.objects.create(
            name="Accueil",
            order=1,
        )
        self.tracking = DailyTracking.objects.create(
            date=date.today(),
            section=self.section,
            count=5,
            created_by=self.user,
            updated_by=self.user,
        )

    def test_create_history_entry(self):
        """Teste la création d'une entrée d'historique."""
        history = TrackingHistory.objects.create(
            tracking=self.tracking,
            previous_count=3,
            new_count=5,
            modified_by=self.user,
            reason="Correction après vérification",
        )

        self.assertEqual(history.tracking, self.tracking)
        self.assertEqual(history.previous_count, 3)
        self.assertEqual(history.new_count, 5)
        self.assertEqual(history.modified_by, self.user)
        self.assertEqual(history.reason, "Correction après vérification")
        self.assertIsNotNone(history.modified_at)

    def test_history_str(self):
        """Teste la représentation string de l'historique."""
        history = TrackingHistory.objects.create(
            tracking=self.tracking,
            previous_count=3,
            new_count=5,
            modified_by=self.user,
        )

        expected = f"Accueil - {date.today()} : 3 → 5"
        self.assertEqual(str(history), expected)

    def test_history_without_reason(self):
        """Teste la création d'historique sans raison."""
        history = TrackingHistory.objects.create(
            tracking=self.tracking,
            previous_count=0,
            new_count=1,
            modified_by=self.user,
        )

        self.assertIsNone(history.reason)
        self.assertEqual(history.previous_count, 0)
        self.assertEqual(history.new_count, 1)


class DailyTrackingManagerTests(TestCase):
    """Tests pour les méthodes du manager DailyTracking."""

    def setUp(self):
        """Créer les données de test."""
        self.user = User.objects.create_user(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            password="testpass123",
        )
        self.section1 = SectionType.objects.create(name="Accueil", order=1)
        self.section2 = SectionType.objects.create(name="Appels", order=2)

    def test_get_or_create_tracking(self):
        """Teste la méthode get_or_create_tracking."""
        tracking, created = DailyTracking.objects.get_or_create_tracking(
            date=date.today(),
            section=self.section1,
            defaults={"created_by": self.user, "updated_by": self.user},
        )

        self.assertTrue(created)
        self.assertEqual(tracking.count, 0)

        # Deuxième appel ne doit pas créer de doublon
        tracking2, created2 = DailyTracking.objects.get_or_create_tracking(
            date=date.today(),
            section=self.section1,
            defaults={"created_by": self.user, "updated_by": self.user},
        )

        self.assertFalse(created2)
        self.assertEqual(tracking.id, tracking2.id)

    def test_get_stats_for_date_range(self):
        """Teste la récupération des statistiques sur une période."""
        today = date.today()
        yesterday = today - timedelta(days=1)

        DailyTracking.objects.create(
            date=today,
            section=self.section1,
            count=10,
            created_by=self.user,
            updated_by=self.user,
        )
        DailyTracking.objects.create(
            date=yesterday,
            section=self.section1,
            count=5,
            created_by=self.user,
            updated_by=self.user,
        )

        stats = DailyTracking.objects.get_stats_for_date_range(
            start_date=yesterday,
            end_date=today,
        )

        self.assertEqual(len(stats), 2)
        self.assertEqual(stats[0]["total_count"], 5)
        self.assertEqual(stats[1]["total_count"], 10)


class SectionTypeActiveManagerTests(TestCase):
    """Tests pour le manager actif des sections."""

    def setUp(self):
        """Créer les données de test."""
        self.active_section = SectionType.objects.create(
            name="Active",
            is_active=True,
        )
        self.inactive_section = SectionType.objects.create(
            name="Inactive",
            is_active=False,
        )

    def test_active_manager(self):
        """Teste que seules les sections actives sont retournées."""
        active_sections = SectionType.objects.active()

        self.assertEqual(active_sections.count(), 1)
        self.assertIn(self.active_section, active_sections)
        self.assertNotIn(self.inactive_section, active_sections)
