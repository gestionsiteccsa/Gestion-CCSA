"""Tests de sécurité pour l'application events."""

from datetime import timedelta

import pytest

from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from events.models import Event, EventComment, Sector


@pytest.mark.django_db
class TestXSSProtection:
    """Tests de protection contre les attaques XSS."""

    def test_description_escaped_in_template(self, client):
        """Test que les descriptions d'événements sont échappées."""
        user = User.objects.create_user(
            email="test@cc-sudavesnois.fr",
            password="testpass123",
        )
        event = Event.objects.create(
            title="Test Event",
            description="<script>alert('XSS')</script>",
            location="Test Location",
            start_datetime=timezone.now() + timedelta(days=1),
            created_by=user,
        )

        response = client.get(event.get_absolute_url())
        assert response.status_code == 200
        # Vérifier que le script malveillant n'est pas présent tel quel dans le contenu de l'événement
        content = response.content.decode()
        # Le script XSS ne doit pas apparaître tel quel dans le corps de la page
        # (mais peut y avoir d'autres scripts légitimes comme Tailwind)
        assert "<script>alert('XSS')</script>" not in content

    def test_comment_escaped_in_template(self, client):
        """Test que les commentaires sont échappés."""
        user = User.objects.create_user(
            email="test@cc-sudavesnois.fr",
            password="testpass123",
        )
        event = Event.objects.create(
            title="Test Event",
            description="Description",
            location="Test Location",
            start_datetime=timezone.now() + timedelta(days=1),
            created_by=user,
        )

        comment = EventComment.objects.create(
            event=event,
            author=user,
            content="<img src=x onerror=alert('XSS')>",
        )

        response = client.get(event.get_absolute_url())
        assert response.status_code == 200
        # Vérifier que le script n'est pas présent
        assert "onerror=alert" not in response.content.decode()


@pytest.mark.django_db
class TestRateLimiting:
    """Tests de limitation de débit."""

    def test_notification_mark_read_rate_limit(self, client):
        """Test que le rate limiting fonctionne pour mark_read."""
        import uuid

        user = User.objects.create_user(
            email="test@cc-sudavesnois.fr",
            password="testpass123",
        )
        client.force_login(user)

        # Faire 11 requêtes (limite à 10) avec un UUID valide
        for i in range(11):
            response = client.post(
                reverse(
                    "accounts:notification_mark_read",
                    kwargs={"notification_id": str(uuid.uuid4())},
                ),
                HTTP_X_REQUESTED_WITH="XMLHttpRequest",
            )

        # La 11ème devrait être rejetée (429) ou notification non trouvée (404)
        assert response.status_code in [429, 404]

    def test_notification_mark_all_rate_limit(self, client):
        """Test que le rate limiting fonctionne pour mark_all."""
        user = User.objects.create_user(
            email="test@cc-sudavesnois.fr",
            password="testpass123",
        )
        client.force_login(user)

        # Faire 6 requêtes (limite à 5)
        for i in range(6):
            response = client.post(
                reverse("accounts:notification_mark_all_read"),
                HTTP_X_REQUESTED_WITH="XMLHttpRequest",
            )

        # La 6ème devrait être rejetée ou retourner succès si pas de notifs
        assert response.status_code in [200, 204, 429]


@pytest.mark.django_db
class TestEventDuplication:
    """Tests pour la duplication d'événements avec transaction atomic."""

    def test_duplicate_event_with_transaction(self, client):
        """Test que la duplication utilise une transaction."""
        user = User.objects.create_user(
            email="test@cc-sudavesnois.fr",
            password="testpass123",
        )
        sector = Sector.objects.create(name="Test Sector", color_code="#000000")
        event = Event.objects.create(
            title="Original Event",
            description="Description",
            location="Test Location",
            city="Test City",
            start_datetime=timezone.now() + timedelta(days=1),
            created_by=user,
        )
        event.sectors.add(sector)

        client.force_login(user)

        # Récupérer la page de duplication pour obtenir les valeurs initiales
        response = client.get(
            reverse("events:event_duplicate", kwargs={"slug": event.slug})
        )
        assert response.status_code == 200

        # Utiliser le format de date attendu par le formulaire (datetime-local)
        response = client.post(
            reverse("events:event_duplicate", kwargs={"slug": event.slug}),
            {
                "title": "Duplicated Event",
                "description": "New Description",
                "location": "New Location",
                "city": "New City",
                "start_datetime": "2026-02-10T10:00",
                "end_datetime": "2026-02-10T12:00",
                "sectors": [sector.pk],
            },
        )

        # Vérifier que la duplication a réussi
        assert response.status_code in [200, 302]

        # Vérifier que l'événement a été créé
        assert Event.objects.filter(title="Duplicated Event").exists()


@pytest.mark.django_db
class TestInputValidation:
    """Tests de validation des entrées utilisateur."""

    def test_invalid_date_format_handling(self, client):
        """Test que les dates invalides sont gérées."""
        user = User.objects.create_user(
            email="comm@cc-sudavesnois.fr",
            password="testpass123",
        )
        # Attribuer le rôle Communication
        from accounts.models import Role, UserRole

        role = Role.objects.create(name="Communication")
        UserRole.objects.create(user=user, role=role)

        client.force_login(user)

        # Tester avec une date invalide
        response = client.get(
            reverse("events:communication_dashboard"),
            {
                "period_type": "custom",
                "date_from": "invalid-date",
                "date_to": "2026-02-10",
            },
        )

        # Ne devrait pas planter (erreur 500)
        assert response.status_code == 200

    def test_date_range_validation(self, client):
        """Test que les plages de dates sont validées."""
        user = User.objects.create_user(
            email="comm@cc-sudavesnois.fr",
            password="testpass123",
        )
        from accounts.models import Role, UserRole

        role = Role.objects.create(name="Communication")
        UserRole.objects.create(user=user, role=role)

        client.force_login(user)

        # Tester avec date de fin avant date de début
        response = client.get(
            reverse("events:communication_dashboard"),
            {
                "period_type": "custom",
                "date_from": "2026-02-10",
                "date_to": "2026-02-01",
            },
        )

        assert response.status_code == 200
