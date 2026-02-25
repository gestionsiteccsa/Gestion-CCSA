"""Tests pour les formulaires de l'app feedback."""

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from feedback.forms import FeedbackCommentForm, FeedbackSettingsForm, FeedbackTicketForm
from feedback.models import FeedbackSettings, FeedbackTicket

User = get_user_model()


@pytest.fixture
def user(db):
    """Fixture pour créer un utilisateur de test."""
    return User.objects.create_user(
        email="test@example.com", first_name="Test", last_name="User", password="testpass123"
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


@pytest.mark.django_db
class TestFeedbackTicketForm:
    """Tests du formulaire FeedbackTicketForm."""

    def test_form_valid_with_all_fields(self, user):
        """Test qu'un formulaire avec tous les champs est valide."""
        data = {
            "title": "Ticket de test",
            "description": "Description détaillée",
            "ticket_type": "bug",
            "priority": "high",
        }
        form = FeedbackTicketForm(data=data)
        assert form.is_valid()

    def test_form_valid_without_screenshot(self, user):
        """Test qu'un formulaire sans capture d'écran est valide."""
        data = {
            "title": "Ticket sans image",
            "description": "Description",
            "ticket_type": "feature",
            "priority": "low",
        }
        form = FeedbackTicketForm(data=data)
        assert form.is_valid()

    def test_form_invalid_empty_title(self, user):
        """Test qu'un titre vide rend le formulaire invalide."""
        data = {
            "title": "",
            "description": "Description",
            "ticket_type": "bug",
            "priority": "medium",
        }
        form = FeedbackTicketForm(data=data)
        assert not form.is_valid()
        assert "title" in form.errors

    def test_form_invalid_empty_description(self, user):
        """Test qu'une description vide rend le formulaire invalide."""
        data = {
            "title": "Titre",
            "description": "",
            "ticket_type": "bug",
            "priority": "medium",
        }
        form = FeedbackTicketForm(data=data)
        assert not form.is_valid()
        assert "description" in form.errors

    def test_form_screenshot_validation_size(self, user):
        """Test que l'upload d'une image trop grande échoue."""
        # Créer un fichier de plus de 2MB
        large_image = SimpleUploadedFile(
            "large.png", b"x" * (3 * 1024 * 1024), content_type="image/png"  # 3MB
        )
        data = {
            "title": "Ticket",
            "description": "Desc",
            "ticket_type": "bug",
            "priority": "medium",
        }
        files = {"screenshot": large_image}
        form = FeedbackTicketForm(data=data, files=files)
        assert not form.is_valid()
        assert "screenshot" in form.errors

    def test_form_screenshot_validation_extension(self, user):
        """Test que seuls les formats JPG/PNG sont acceptés."""
        invalid_file = SimpleUploadedFile(
            "test.pdf", b"file_content", content_type="application/pdf"
        )
        data = {
            "title": "Ticket",
            "description": "Desc",
            "ticket_type": "bug",
            "priority": "medium",
        }
        files = {"screenshot": invalid_file}
        form = FeedbackTicketForm(data=data, files=files)
        assert not form.is_valid()
        assert "screenshot" in form.errors

    def test_form_without_screenshot_is_valid(self, user):
        """Test qu'un formulaire sans screenshot est valide."""
        data = {
            "title": "Ticket",
            "description": "Desc",
            "ticket_type": "bug",
            "priority": "medium",
        }
        form = FeedbackTicketForm(data=data)
        assert form.is_valid()

    def test_form_save_sets_created_by(self, user):
        """Test que le formulaire sauvegarde avec created_by."""
        data = {
            "title": "Ticket",
            "description": "Desc",
            "ticket_type": "bug",
            "priority": "medium",
        }
        form = FeedbackTicketForm(data=data)
        assert form.is_valid()
        ticket = form.save(commit=False)
        ticket.created_by = user
        ticket.save()
        assert ticket.created_by == user


@pytest.mark.django_db
class TestFeedbackCommentForm:
    """Tests du formulaire FeedbackCommentForm."""

    def test_form_valid_comment(self, ticket):
        """Test qu'un commentaire valide est accepté."""
        data = {
            "content": "Ceci est un commentaire valide",
        }
        form = FeedbackCommentForm(data=data)
        assert form.is_valid()

    def test_form_invalid_empty_content(self, ticket):
        """Test qu'un contenu vide rend le formulaire invalide."""
        data = {
            "content": "",
        }
        form = FeedbackCommentForm(data=data)
        assert not form.is_valid()
        assert "content" in form.errors

    def test_form_save_sets_ticket_and_author(self, ticket, user):
        """Test que le formulaire sauvegarde avec ticket et author."""
        data = {
            "content": "Commentaire test",
        }
        form = FeedbackCommentForm(data=data)
        assert form.is_valid()
        comment = form.save(commit=False)
        comment.ticket = ticket
        comment.author = user
        comment.save()
        assert comment.ticket == ticket
        assert comment.author == user


@pytest.mark.django_db
class TestFeedbackSettingsForm:
    """Tests du formulaire FeedbackSettingsForm."""

    def test_form_valid_settings(self):
        """Test que le formulaire de paramètres est valide."""
        data = {
            "notify_on_new_ticket": True,
            "notify_on_status_change": True,
            "from_email": "support@example.com",
        }
        form = FeedbackSettingsForm(data=data)
        assert form.is_valid()

    def test_form_email_recipients(self, user):
        """Test que les destinataires email peuvent être sélectionnés."""
        settings_obj = FeedbackSettings.get_settings()
        data = {
            "email_recipients": [user.id],
            "notify_on_new_ticket": True,
            "notify_on_status_change": False,
            "from_email": "support@example.com",
        }
        form = FeedbackSettingsForm(data=data, instance=settings_obj)
        assert form.is_valid()
        form.save()
        assert user in settings_obj.email_recipients.all()

    def test_form_invalid_email_format(self):
        """Test qu'un email invalide est rejeté."""
        data = {
            "notify_on_new_ticket": True,
            "notify_on_status_change": True,
            "from_email": "invalid-email",
        }
        form = FeedbackSettingsForm(data=data)
        assert not form.is_valid()
        assert "from_email" in form.errors

    def test_form_optional_from_email(self):
        """Test que l'email d'expédition est optionnel."""
        data = {
            "notify_on_new_ticket": True,
            "notify_on_status_change": True,
            "from_email": "",
        }
        form = FeedbackSettingsForm(data=data)
        assert form.is_valid()
