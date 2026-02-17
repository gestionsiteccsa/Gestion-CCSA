"""Tests pour les fonctionnalités de tournage vidéo."""

import pytest
from django.test import Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch, MagicMock

from accounts.models import User, Role, UserRole
from events.models import Event, VideoRequestLog


@pytest.mark.django_db
class TestVideoRequest:
    """Tests pour les demandes de tournage vidéo."""

    def test_send_video_request_success(self, client):
        """Test envoi réussi de demande de tournage."""
        # Créer un utilisateur avec rôle Communication
        user = User.objects.create_user(
            email="comm@cc-sudavesnois.fr",
            password="testpass123",
        )
        role = Role.objects.create(name="Communication")
        UserRole.objects.create(user=user, role=role)
        
        # Créer un événement
        event = Event.objects.create(
            title="Test Event",
            description="Description",
            location="Test Location",
            start_datetime=timezone.now() + timedelta(days=1),
            created_by=user,
        )
        
        client.force_login(user)
        
        with patch("events.views.send_mail") as mock_send_mail:
            mock_send_mail.return_value = 1
            response = client.post(
                reverse("events:send_video_request", kwargs={"slug": event.slug}),
                {"recipient_email": "cameraman@test.com"},
            )
            
            assert response.status_code == 302
            mock_send_mail.assert_called_once()
            
            # Vérifier que le log a été créé
            assert VideoRequestLog.objects.filter(event=event).exists()

    def test_send_video_request_unauthorized(self, client):
        """Test que seuls les users Communication peuvent envoyer des demandes."""
        user = User.objects.create_user(
            email="user@cc-sudavesnois.fr",
            password="testpass123",
        )
        # Pas de rôle Communication
        
        event = Event.objects.create(
            title="Test Event",
            description="Description",
            location="Test Location",
            start_datetime=timezone.now() + timedelta(days=1),
            created_by=user,
        )
        
        client.force_login(user)
        
        response = client.post(
            reverse("events:send_video_request", kwargs={"slug": event.slug}),
            {"recipient_email": "cameraman@test.com"},
        )
        
        # Devrait être interdit (403)
        assert response.status_code == 403


@pytest.mark.django_db
class TestVideoConfirmation:
    """Tests pour la confirmation/refus du caméraman."""

    def test_confirm_video_request(self, client):
        """Test confirmation par le caméraman."""
        user = User.objects.create_user(
            email="comm@cc-sudavesnois.fr",
            password="testpass123",
        )
        role = Role.objects.create(name="Communication")
        UserRole.objects.create(user=user, role=role)
        
        event = Event.objects.create(
            title="Test Event",
            description="Description",
            location="Test Location",
            start_datetime=timezone.now() + timedelta(days=1),
            needs_filming=True,
            created_by=user,
        )
        
        # Créer un log de demande
        import uuid
        token = uuid.uuid4()
        log = VideoRequestLog.objects.create(
            event=event,
            recipient_email="cameraman@test.com",
            sent_by=user,
            confirmation_token=token,
        )
        
        response = client.get(
            reverse("events:confirm_video_request", kwargs={
                "token": str(token),
            })
        )
        
        assert response.status_code == 200
        
        # Vérifier que le log a été mis à jour
        log.refresh_from_db()
        assert log.confirmed is True

    def test_refuse_video_request(self, client):
        """Test refus par le caméraman."""
        user = User.objects.create_user(
            email="comm@cc-sudavesnois.fr",
            password="testpass123",
        )
        role = Role.objects.create(name="Communication")
        UserRole.objects.create(user=user, role=role)
        
        event = Event.objects.create(
            title="Test Event",
            description="Description",
            location="Test Location",
            start_datetime=timezone.now() + timedelta(days=1),
            needs_filming=True,
            created_by=user,
        )
        
        import uuid
        token = uuid.uuid4()
        log = VideoRequestLog.objects.create(
            event=event,
            recipient_email="cameraman@test.com",
            sent_by=user,
            confirmation_token=token,
        )
        
        response = client.get(
            reverse("events:refuse_video_request", kwargs={
                "token": str(token),
            })
        )
        
        assert response.status_code == 200
        
        # Vérifier que le log a été mis à jour
        log.refresh_from_db()
        assert log.refused is True

    def test_invalid_token(self, client):
        """Test token invalide."""
        user = User.objects.create_user(
            email="comm@cc-sudavesnois.fr",
            password="testpass123",
        )
        
        event = Event.objects.create(
            title="Test Event",
            description="Description",
            location="Test Location",
            start_datetime=timezone.now() + timedelta(days=1),
            needs_filming=True,
            created_by=user,
        )
        
        response = client.get(
            reverse("events:confirm_video_request", kwargs={
                "token": "invalid-token",
            })
        )
        
        # Devrait retourner une erreur
        assert response.status_code == 400
