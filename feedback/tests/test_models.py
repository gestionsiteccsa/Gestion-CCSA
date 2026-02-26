"""Tests pour les modèles de l'app feedback."""

import pytest

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from feedback.models import FeedbackComment, FeedbackSettings, FeedbackTicket

User = get_user_model()


@pytest.fixture
def user(db):
    """Fixture pour créer un utilisateur de test."""
    return User.objects.create_user(
        email="test@example.com",
        first_name="Test",
        last_name="User",
        password="testpass123",
    )


@pytest.fixture
def support_user(db):
    """Fixture pour créer un utilisateur support de test."""
    return User.objects.create_user(
        email="support@example.com",
        first_name="Support",
        last_name="User",
        password="testpass123",
    )


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
    return FeedbackSettings.get_settings()


@pytest.mark.django_db
class TestFeedbackTicket:
    """Tests du modèle FeedbackTicket."""

    def test_create_ticket_with_valid_data(self, user):
        """Test la création d'un ticket avec des données valides."""
        ticket = FeedbackTicket.objects.create(
            title="Ticket de test",
            description="Description détaillée",
            ticket_type="bug",
            priority="high",
            created_by=user,
        )
        assert ticket.title == "Ticket de test"
        assert ticket.ticket_type == "bug"
        assert ticket.priority == "high"
        assert ticket.created_by == user

    def test_ticket_str_representation(self, ticket):
        """Test la représentation string du ticket."""
        expected = f"#{ticket.id} - Test Ticket"
        assert str(ticket) == expected

    def test_ticket_default_status_is_new(self, user):
        """Test que le statut par défaut est 'nouveau'."""
        ticket = FeedbackTicket.objects.create(
            title="Ticket", description="Desc", created_by=user
        )
        assert ticket.status == "new"

    def test_ticket_default_priority_is_medium(self, user):
        """Test que la priorité par défaut est 'moyenne'."""
        ticket = FeedbackTicket.objects.create(
            title="Ticket", description="Desc", created_by=user
        )
        assert ticket.priority == "medium"

    def test_ticket_status_choices(self):
        """Test que les choix de statut sont corrects."""
        choices = dict(FeedbackTicket.STATUS_CHOICES)
        assert "new" in choices
        assert "in_progress" in choices
        assert "resolved" in choices
        assert "closed" in choices

    def test_ticket_type_choices(self):
        """Test que les choix de type sont corrects."""
        choices = dict(FeedbackTicket.TICKET_TYPE_CHOICES)
        assert "bug" in choices
        assert "feature" in choices
        assert "question" in choices

    def test_ticket_priority_choices(self):
        """Test que les choix de priorité sont corrects."""
        choices = dict(FeedbackTicket.PRIORITY_CHOICES)
        assert "low" in choices
        assert "medium" in choices
        assert "high" in choices
        assert "critical" in choices

    def test_ticket_with_screenshot(self, user):
        """Test la création d'un ticket avec capture d'écran."""
        image = SimpleUploadedFile(
            "test_screenshot.png", b"file_content", content_type="image/png"
        )
        ticket = FeedbackTicket.objects.create(
            title="Ticket avec image",
            description="Desc",
            created_by=user,
            screenshot=image,
        )
        assert ticket.screenshot is not None
        assert "test_screenshot" in ticket.screenshot.name

    def test_ticket_ordering_by_created_at_desc(self, user):
        """Test que les tickets sont triés par date de création décroissante."""
        ticket1 = FeedbackTicket.objects.create(
            title="Premier", description="Desc1", created_by=user
        )
        ticket2 = FeedbackTicket.objects.create(
            title="Deuxième", description="Desc2", created_by=user
        )
        tickets = list(FeedbackTicket.objects.all())
        assert tickets[0] == ticket2
        assert tickets[1] == ticket1

    def test_ticket_assigned_to_support_user(self, user, support_user):
        """Test l'assignation d'un ticket à un utilisateur support."""
        ticket = FeedbackTicket.objects.create(
            title="Ticket assigné",
            description="Desc",
            created_by=user,
            assigned_to=support_user,
        )
        assert ticket.assigned_to == support_user

    def test_ticket_invalid_status_raises_error(self, user):
        """Test qu'un statut invalide lève une erreur."""
        ticket = FeedbackTicket(
            title="Test", description="Desc", created_by=user, status="invalid_status"
        )
        with pytest.raises(ValidationError):
            ticket.full_clean()


@pytest.mark.django_db
class TestFeedbackComment:
    """Tests du modèle FeedbackComment."""

    def test_create_comment(self, ticket, user):
        """Test la création d'un commentaire."""
        comment = FeedbackComment.objects.create(
            ticket=ticket, author=user, content="Ceci est un commentaire"
        )
        assert comment.ticket == ticket
        assert comment.author == user
        assert comment.content == "Ceci est un commentaire"

    def test_comment_str_representation(self, ticket, user):
        """Test la représentation string du commentaire."""
        comment = FeedbackComment.objects.create(
            ticket=ticket, author=user, content="Commentaire test"
        )
        expected = f"Commentaire de {user.email} sur #{ticket.id}"
        assert str(comment) == expected

    def test_comment_is_staff_response_default_false(self, ticket, user):
        """Test que is_staff_response est False par défaut."""
        comment = FeedbackComment.objects.create(
            ticket=ticket, author=user, content="Test"
        )
        assert comment.is_staff_response is False

    def test_comment_ordering_by_created_at_asc(self, ticket, user):
        """Test que les commentaires sont triés par date croissante."""
        comment1 = FeedbackComment.objects.create(
            ticket=ticket, author=user, content="Premier"
        )
        comment2 = FeedbackComment.objects.create(
            ticket=ticket, author=user, content="Deuxième"
        )
        comments = list(FeedbackComment.objects.all())
        assert comments[0] == comment1
        assert comments[1] == comment2


@pytest.mark.django_db
class TestFeedbackSettings:
    """Tests du modèle FeedbackSettings (Singleton)."""

    def test_settings_singleton_pattern(self):
        """Test que le pattern Singleton fonctionne."""
        settings1 = FeedbackSettings.get_settings()
        settings2 = FeedbackSettings.get_settings()
        assert settings1.id == settings2.id
        assert FeedbackSettings.objects.count() == 1

    def test_get_or_create_settings_creates_default(self):
        """Test que get_settings crée les paramètres par défaut."""
        settings = FeedbackSettings.get_settings()
        assert settings.notify_on_new_ticket is True
        assert settings.notify_on_status_change is True
        assert settings.from_email == ""

    def test_add_email_recipient(self, settings_obj, user):
        """Test l'ajout d'un destinataire email."""
        settings_obj.email_recipients.add(user)
        assert user in settings_obj.email_recipients.all()
        assert settings_obj.email_recipients.count() == 1

    def test_settings_str_representation(self):
        """Test la représentation string des paramètres."""
        settings = FeedbackSettings.get_settings()
        assert str(settings) == "Paramètres du feedback"

    def test_settings_save_prevents_multiple_instances(self):
        """Test qu'on ne peut pas créer plusieurs instances."""
        settings1 = FeedbackSettings.get_settings()
        settings2 = FeedbackSettings()
        settings2.save()
        assert FeedbackSettings.objects.count() == 1
        assert settings2.id == settings1.id
