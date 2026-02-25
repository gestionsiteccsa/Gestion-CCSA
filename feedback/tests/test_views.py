"""Tests pour les vues de l'app feedback."""

import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse

from accounts.models import Role, UserRole
from feedback.models import FeedbackComment, FeedbackSettings, FeedbackTicket

User = get_user_model()


@pytest.fixture
def user(db):
    """Fixture pour créer un utilisateur de test."""
    return User.objects.create_user(
        email="test@example.com", first_name="Test", last_name="User", password="testpass123"
    )


@pytest.fixture
def support_user(db):
    """Fixture pour créer un utilisateur support de test."""
    user = User.objects.create_user(
        email="support@example.com", first_name="Support", last_name="User", password="testpass123"
    )
    # Créer le rôle Support
    support_role, _ = Role.objects.get_or_create(
        name="Support",
        defaults={"description": "Rôle pour la gestion des tickets de support", "color": "#3B82F6"},
    )
    # Assigner le rôle à l'utilisateur
    UserRole.objects.create(user=user, role=support_role)
    return user


@pytest.fixture
def ticket(db, user):
    """Fixture pour créer un ticket de test."""
    return FeedbackTicket.objects.create(
        title="Test Ticket",
        description="Description du test",
        ticket_type="bug",
        priority="medium",
        created_by=user,
    )


@pytest.fixture
def settings_obj(db):
    """Fixture pour créer les paramètres de test."""
    settings = FeedbackSettings.get_settings()
    settings.from_email = "support@example.com"
    settings.save()
    return settings


@pytest.mark.django_db
class TestFeedbackListView:
    """Tests de la vue FeedbackListView."""

    def test_list_view_requires_login(self, client):
        """Test que la vue nécessite une connexion."""
        url = reverse("feedback:ticket_list")
        response = client.get(url)
        assert response.status_code == 302
        assert "/accounts/login/" in response.url

    def test_list_view_shows_user_tickets(self, client, user, ticket):
        """Test que la vue affiche les tickets de l'utilisateur."""
        client.force_login(user)
        url = reverse("feedback:ticket_list")
        response = client.get(url)
        assert response.status_code == 200
        assert "tickets" in response.context
        assert ticket in response.context["tickets"]

    def test_list_view_pagination(self, client, user):
        """Test la pagination de la liste."""
        # Créer 15 tickets
        for i in range(15):
            FeedbackTicket.objects.create(
                title=f"Ticket {i}", description=f"Desc {i}", created_by=user
            )
        client.force_login(user)
        url = reverse("feedback:ticket_list")
        response = client.get(url)
        assert response.status_code == 200
        assert len(response.context["tickets"]) <= 10  # paginate_by

    def test_list_view_filters_by_status(self, client, user):
        """Test le filtre par statut."""
        ticket_new = FeedbackTicket.objects.create(
            title="Nouveau", description="Desc", status="new", created_by=user
        )
        ticket_resolved = FeedbackTicket.objects.create(
            title="Résolu", description="Desc", status="resolved", created_by=user
        )
        client.force_login(user)
        url = reverse("feedback:ticket_list")
        response = client.get(url, {"status": "new"})
        assert response.status_code == 200
        assert ticket_new in response.context["tickets"]
        assert ticket_resolved not in response.context["tickets"]

    def test_list_view_only_shows_own_tickets(self, client, user):
        """Test que seuls les tickets de l'utilisateur sont affichés."""
        other_user = User.objects.create_user(
            email="other@example.com", first_name="Other", last_name="User", password="testpass123"
        )
        own_ticket = FeedbackTicket.objects.create(
            title="Mon ticket", description="Desc", created_by=user
        )
        other_ticket = FeedbackTicket.objects.create(
            title="Autre ticket", description="Desc", created_by=other_user
        )
        client.force_login(user)
        url = reverse("feedback:ticket_list")
        response = client.get(url)
        assert response.status_code == 200
        assert own_ticket in response.context["tickets"]
        assert other_ticket not in response.context["tickets"]


@pytest.mark.django_db
class TestFeedbackCreateView:
    """Tests de la vue FeedbackCreateView."""

    def test_create_view_requires_login(self, client):
        """Test que la création nécessite une connexion."""
        url = reverse("feedback:ticket_create")
        response = client.get(url)
        assert response.status_code == 302
        assert "/accounts/login/" in response.url

    def test_create_view_get_request(self, client, user):
        """Test l'affichage du formulaire de création."""
        client.force_login(user)
        url = reverse("feedback:ticket_create")
        response = client.get(url)
        assert response.status_code == 200
        assert "form" in response.context

    def test_create_view_post_valid_data(self, client, user):
        """Test la création d'un ticket avec données valides."""
        client.force_login(user)
        url = reverse("feedback:ticket_create")
        data = {
            "title": "Nouveau ticket",
            "description": "Description détaillée",
            "ticket_type": "bug",
            "priority": "high",
        }
        response = client.post(url, data)
        assert response.status_code == 302
        assert FeedbackTicket.objects.filter(title="Nouveau ticket").exists()

    def test_create_view_redirect_after_success(self, client, user):
        """Test la redirection après création réussie."""
        client.force_login(user)
        url = reverse("feedback:ticket_create")
        data = {
            "title": "Ticket",
            "description": "Desc",
            "ticket_type": "bug",
            "priority": "medium",
        }
        response = client.post(url, data)
        assert response.status_code == 302
        assert response.url == reverse("feedback:ticket_list")

    def test_create_view_sends_email_notification(self, client, user, settings_obj):
        """Test l'envoi d'email après création."""
        # Ajouter un destinataire
        settings_obj.email_recipients.add(user)
        settings_obj.notify_on_new_ticket = True
        settings_obj.save()

        client.force_login(user)
        url = reverse("feedback:ticket_create")
        data = {
            "title": "Ticket avec email",
            "description": "Desc",
            "ticket_type": "bug",
            "priority": "high",
        }
        response = client.post(url, data)
        assert response.status_code == 302
        assert len(mail.outbox) == 1
        assert "Nouveau ticket" in mail.outbox[0].subject

    def test_create_view_creates_notification_for_support(self, client, user, support_user):
        """Test la création d'une notification pour le support."""
        client.force_login(user)
        url = reverse("feedback:ticket_create")
        data = {
            "title": "Ticket pour support",
            "description": "Desc",
            "ticket_type": "bug",
            "priority": "high",
        }
        response = client.post(url, data)
        assert response.status_code == 302
        # Vérifier qu'une notification a été créée pour le support
        from accounts.models import Notification

        notification = Notification.objects.filter(
            user=support_user, notification_type="feedback_new_ticket"
        ).first()
        assert notification is not None


@pytest.mark.django_db
class TestFeedbackDetailView:
    """Tests de la vue FeedbackDetailView."""

    def test_detail_view_requires_login(self, client, ticket):
        """Test que le détail nécessite une connexion."""
        url = reverse("feedback:ticket_detail", kwargs={"pk": ticket.pk})
        response = client.get(url)
        assert response.status_code == 302

    def test_detail_view_shows_ticket(self, client, user, ticket):
        """Test que la vue affiche le ticket."""
        client.force_login(user)
        url = reverse("feedback:ticket_detail", kwargs={"pk": ticket.pk})
        response = client.get(url)
        assert response.status_code == 200
        assert response.context["ticket"] == ticket

    def test_detail_view_shows_comments(self, client, user, ticket):
        """Test que la vue affiche les commentaires."""
        comment = FeedbackComment.objects.create(
            ticket=ticket, author=user, content="Commentaire test"
        )
        client.force_login(user)
        url = reverse("feedback:ticket_detail", kwargs={"pk": ticket.pk})
        response = client.get(url)
        assert response.status_code == 200
        assert comment in response.context["comments"]

    def test_detail_view_add_comment(self, client, user, ticket):
        """Test l'ajout d'un commentaire."""
        client.force_login(user)
        url = reverse("feedback:ticket_detail", kwargs={"pk": ticket.pk})
        data = {
            "content": "Nouveau commentaire",
        }
        response = client.post(url, data)
        assert response.status_code == 302
        assert FeedbackComment.objects.filter(content="Nouveau commentaire").exists()

    def test_detail_view_403_if_not_owner_or_support(self, client, user, ticket):
        """Test le refus d'accès si pas propriétaire ni support."""
        other_user = User.objects.create_user(
            email="other@example.com", first_name="Other", last_name="User", password="testpass123"
        )
        client.force_login(other_user)
        url = reverse("feedback:ticket_detail", kwargs={"pk": ticket.pk})
        response = client.get(url)
        assert response.status_code == 403

    def test_detail_view_support_can_access_all_tickets(self, client, support_user, ticket):
        """Test que le support peut accéder à tous les tickets."""
        client.force_login(support_user)
        url = reverse("feedback:ticket_detail", kwargs={"pk": ticket.pk})
        response = client.get(url)
        assert response.status_code == 200


@pytest.mark.django_db
class TestFeedbackAdminListView:
    """Tests de la vue FeedbackAdminListView (pour support)."""

    def test_admin_list_view_requires_login(self, client):
        """Test que la vue admin nécessite une connexion."""
        url = reverse("feedback:admin_list")
        response = client.get(url)
        assert response.status_code == 302

    def test_admin_list_view_requires_support_role(self, client, user):
        """Test que la vue admin nécessite le rôle Support."""
        client.force_login(user)
        url = reverse("feedback:admin_list")
        response = client.get(url)
        assert response.status_code == 403

    def test_admin_list_view_shows_all_tickets(self, client, support_user, user):
        """Test que la vue admin affiche tous les tickets."""
        ticket1 = FeedbackTicket.objects.create(
            title="Ticket 1", description="Desc", created_by=user
        )
        ticket2 = FeedbackTicket.objects.create(
            title="Ticket 2", description="Desc", created_by=support_user
        )
        client.force_login(support_user)
        url = reverse("feedback:admin_list")
        response = client.get(url)
        assert response.status_code == 200
        assert ticket1 in response.context["tickets"]
        assert ticket2 in response.context["tickets"]

    def test_admin_list_view_filters(self, client, support_user, user):
        """Test les filtres de la vue admin."""
        ticket_bug = FeedbackTicket.objects.create(
            title="Bug", description="Desc", ticket_type="bug", created_by=user
        )
        ticket_feature = FeedbackTicket.objects.create(
            title="Feature", description="Desc", ticket_type="feature", created_by=user
        )
        client.force_login(support_user)
        url = reverse("feedback:admin_list")
        response = client.get(url, {"ticket_type": "bug"})
        assert response.status_code == 200
        assert ticket_bug in response.context["tickets"]
        assert ticket_feature not in response.context["tickets"]

    def test_admin_list_view_status_update(self, client, support_user, ticket):
        """Test la mise à jour du statut."""
        client.force_login(support_user)
        url = reverse("feedback:ticket_update_status", kwargs={"pk": ticket.pk})
        data = {"status": "in_progress"}
        response = client.post(url, data)
        assert response.status_code == 302
        ticket.refresh_from_db()
        assert ticket.status == "in_progress"

    def test_admin_list_view_sends_notification_on_status_change(
        self, client, support_user, ticket, settings_obj, user
    ):
        """Test l'envoi de notification sur changement de statut."""
        settings_obj.notify_on_status_change = True
        settings_obj.save()

        client.force_login(support_user)
        url = reverse("feedback:ticket_update_status", kwargs={"pk": ticket.pk})
        data = {"status": "resolved"}
        response = client.post(url, data)
        assert response.status_code == 302
        # Vérifier qu'une notification a été créée pour le créateur
        from accounts.models import Notification

        notification = Notification.objects.filter(
            user=user, notification_type="feedback_status_changed"
        ).first()
        assert notification is not None


@pytest.mark.django_db
class TestFeedbackSettingsView:
    """Tests de la vue FeedbackSettingsView."""

    def test_settings_view_requires_superuser(self, client, user):
        """Test que la vue paramètres nécessite un superuser."""
        client.force_login(user)
        url = reverse("feedback:settings")
        response = client.get(url)
        assert response.status_code == 403

    def test_settings_view_requires_superuser_post(self, client, user):
        """Test que le POST nécessite un superuser."""
        client.force_login(user)
        url = reverse("feedback:settings")
        response = client.post(url, {})
        assert response.status_code == 403

    def test_settings_view_update_email_recipients(self, client, user):
        """Test la mise à jour des destinataires email."""
        user.is_superuser = True
        user.save()
        client.force_login(user)
        url = reverse("feedback:settings")
        data = {
            "email_recipients": [user.id],
            "notify_on_new_ticket": True,
            "notify_on_status_change": False,
            "from_email": "support@newdomain.com",
        }
        response = client.post(url, data)
        assert response.status_code == 302
        settings_obj = FeedbackSettings.get_settings()
        assert user in settings_obj.email_recipients.all()
        assert settings_obj.from_email == "support@newdomain.com"
