"""Tests pour les vues de l'app pointage."""

from datetime import date, timedelta

from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import Role, User, UserRole
from pointage.models import DailyTracking, SectionType


class AccueilRequiredMixinTests(TestCase):
    """Tests pour le mixin de vérification du rôle Accueil."""

    def setUp(self):
        """Créer les données de test."""
        self.client = Client()
        self.user_without_role = User.objects.create_user(
            email="user@example.com",
            first_name="User",
            last_name="Test",
            password="testpass123",
        )
        self.user_with_accueil = User.objects.create_user(
            email="accueil@example.com",
            first_name="Accueil",
            last_name="Test",
            password="testpass123",
        )
        self.role_accueil = Role.objects.create(
            name="Accueil",
            description="Rôle accueil",
        )
        UserRole.objects.create(user=self.user_with_accueil, role=self.role_accueil, is_active=True)

    def test_access_denied_without_role(self):
        """Teste que l'accès est refusé sans le rôle."""
        self.client.login(email="user@example.com", password="testpass123")
        response = self.client.get(reverse("pointage:daily_tracking"))

        self.assertEqual(response.status_code, 403)

    def test_access_granted_with_role_lowercase(self):
        """Teste que l'accès est accordé avec le rôle 'accueil' (minuscule)."""
        self.client.login(email="accueil@example.com", password="testpass123")
        response = self.client.get(reverse("pointage:daily_tracking"))

        self.assertEqual(response.status_code, 200)

    def test_access_granted_with_role_uppercase(self):
        """Teste que l'accès est accordé avec le rôle 'Accueil' (majuscule)."""
        # Créer un nouveau rôle avec majuscule
        role_upper = Role.objects.create(
            name="ACCUEIL",
            description="Rôle ACCUEIL",
        )
        user_upper = User.objects.create_user(
            email="upper@example.com",
            first_name="Upper",
            last_name="Test",
            password="testpass123",
        )
        user_upper.roles.add(role_upper)

        self.client.login(email="upper@example.com", password="testpass123")
        response = self.client.get(reverse("pointage:daily_tracking"))

        self.assertEqual(response.status_code, 200)


class DailyTrackingViewTests(TestCase):
    """Tests pour la vue de pointage journalier."""

    def setUp(self):
        """Créer les données de test."""
        self.client = Client()
        self.user = User.objects.create_user(
            email="accueil@example.com",
            first_name="Accueil",
            last_name="Test",
            password="testpass123",
        )
        self.role = Role.objects.create(name="Accueil")
        UserRole.objects.create(user=self.user, role=self.role, is_active=True)
        self.section = SectionType.objects.create(name="Accueil", order=1)

        self.client.login(email="accueil@example.com", password="testpass123")

    def test_daily_tracking_page_loads(self):
        """Teste que la page de pointage charge correctement."""
        response = self.client.get(reverse("pointage:daily_tracking"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pointage/daily_tracking.html")

    def test_daily_tracking_context(self):
        """Teste le contexte passé au template."""
        response = self.client.get(reverse("pointage:daily_tracking"))

        self.assertIn("sections", response.context)
        self.assertIn("selected_date", response.context)
        self.assertIn("tracking_data", response.context)

    def test_daily_tracking_with_specific_date(self):
        """Teste le pointage pour une date spécifique."""
        yesterday = date.today() - timedelta(days=1)
        response = self.client.get(
            reverse("pointage:daily_tracking_date", kwargs={"date": yesterday.isoformat()})
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["selected_date"], yesterday)

    def test_daily_tracking_retroactive_limit(self):
        """Teste la limite de rétroactivité (30 jours)."""
        too_old = date.today() - timedelta(days=31)
        response = self.client.get(
            reverse("pointage:daily_tracking_date", kwargs={"date": too_old.isoformat()})
        )

        self.assertEqual(response.status_code, 403)

    def test_update_tracking_ajax(self):
        """Teste la mise à jour du pointage via AJAX."""
        tracking = DailyTracking.objects.create(
            date=date.today(),
            section=self.section,
            count=5,
            created_by=self.user,
            updated_by=self.user,
        )

        response = self.client.post(
            reverse("pointage:update_tracking", kwargs={"pk": tracking.pk}),
            {"delta": 2},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 200)
        tracking.refresh_from_db()
        self.assertEqual(tracking.count, 7)

    def test_update_tracking_invalid_delta(self):
        """Teste la mise à jour avec un delta invalide."""
        tracking = DailyTracking.objects.create(
            date=date.today(),
            section=self.section,
            count=5,
            created_by=self.user,
            updated_by=self.user,
        )

        response = self.client.post(
            reverse("pointage:update_tracking", kwargs={"pk": tracking.pk}),
            {"delta": 10},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 400)

    def test_update_tracking_negative_delta(self):
        """Teste la mise à jour avec un delta négatif."""
        tracking = DailyTracking.objects.create(
            date=date.today(),
            section=self.section,
            count=5,
            created_by=self.user,
            updated_by=self.user,
        )

        response = self.client.post(
            reverse("pointage:update_tracking", kwargs={"pk": tracking.pk}),
            {"delta": -3},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 200)
        tracking.refresh_from_db()
        self.assertEqual(tracking.count, 2)

    def test_update_tracking_prevents_negative_count(self):
        """Teste que le compteur ne peut pas devenir négatif."""
        tracking = DailyTracking.objects.create(
            date=date.today(),
            section=self.section,
            count=2,
            created_by=self.user,
            updated_by=self.user,
        )

        response = self.client.post(
            reverse("pointage:update_tracking", kwargs={"pk": tracking.pk}),
            {"delta": -5},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 400)
        tracking.refresh_from_db()
        self.assertEqual(tracking.count, 2)


class SectionManagementViewTests(TestCase):
    """Tests pour la gestion des sections."""

    def setUp(self):
        """Créer les données de test."""
        self.client = Client()
        self.user = User.objects.create_user(
            email="accueil@example.com",
            first_name="Accueil",
            last_name="Test",
            password="testpass123",
        )
        self.role = Role.objects.create(name="Accueil")
        UserRole.objects.create(user=self.user, role=self.role, is_active=True)

        self.client.login(email="accueil@example.com", password="testpass123")

    def test_section_list(self):
        """Teste la liste des sections."""
        SectionType.objects.create(name="Section 1", order=1)
        SectionType.objects.create(name="Section 2", order=2)

        response = self.client.get(reverse("pointage:section_list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["sections"]), 2)

    def test_create_section(self):
        """Teste la création d'une section."""
        response = self.client.post(
            reverse("pointage:section_create"),
            {
                "name": "Nouvelle Section",
                "description": "Description test",
                "color": "#ff0000",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(SectionType.objects.filter(name="Nouvelle Section").exists())

    def test_update_section(self):
        """Teste la modification d'une section."""
        section = SectionType.objects.create(name="Old Name", order=1)

        response = self.client.post(
            reverse("pointage:section_update", kwargs={"pk": section.pk}),
            {
                "name": "New Name",
                "description": "New description",
                "color": "#00ff00",
            },
        )

        self.assertEqual(response.status_code, 302)
        section.refresh_from_db()
        self.assertEqual(section.name, "New Name")

    def test_toggle_section(self):
        """Teste l'activation/désactivation d'une section."""
        section = SectionType.objects.create(name="Test", is_active=True)

        response = self.client.post(reverse("pointage:section_toggle", kwargs={"pk": section.pk}))

        self.assertEqual(response.status_code, 302)
        section.refresh_from_db()
        self.assertFalse(section.is_active)


class StatsViewTests(TestCase):
    """Tests pour les vues de statistiques."""

    def setUp(self):
        """Créer les données de test."""
        self.client = Client()
        self.user = User.objects.create_user(
            email="accueil@example.com",
            first_name="Accueil",
            last_name="Test",
            password="testpass123",
        )
        self.role = Role.objects.create(name="Accueil")
        UserRole.objects.create(user=self.user, role=self.role, is_active=True)
        self.section = SectionType.objects.create(name="Accueil", order=1)

        self.client.login(email="accueil@example.com", password="testpass123")

    def test_stats_dashboard_loads(self):
        """Teste que le dashboard de stats charge."""
        response = self.client.get(reverse("pointage:stats_dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pointage/stats_dashboard.html")

    def test_stats_data_api(self):
        """Teste l'API de données statistiques."""
        today = date.today()
        DailyTracking.objects.create(
            date=today,
            section=self.section,
            count=10,
            created_by=self.user,
            updated_by=self.user,
        )

        response = self.client.get(
            reverse("pointage:stats_data"),
            {"period": "day", "date": today.isoformat()},
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("labels", data)
        self.assertIn("datasets", data)

    def test_stats_invalid_period(self):
        """Teste avec une période invalide."""
        response = self.client.get(
            reverse("pointage:stats_data"),
            {"period": "invalid"},
        )

        self.assertEqual(response.status_code, 400)
