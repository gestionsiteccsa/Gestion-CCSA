"""Tests pour les formulaires de l'app events."""

from datetime import timedelta
from io import BytesIO
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone
from PIL import Image

from accounts.models import User
from events.forms import EventCommentForm, EventForm, EventImageForm
from events.models import Event, Sector


class EventFormTest(TestCase):
    """Tests pour le formulaire EventForm."""

    def setUp(self):
        """Créer les objets nécessaires pour les tests."""
        self.user = User.objects.create_user(
            email="test@cc-sudavesnois.fr",
            password="testpass123",
        )
        self.sector = Sector.objects.create(
            name="Santé",
            color_code="#b4c7e7",
        )
        self.valid_data = {
            "title": "Fête de la musique",
            "description": "Concert en plein air",
            "location": "Salle polyvalente",
            "city": "Saint-Quentin",
            "start_datetime": (timezone.now() + timedelta(days=1)).strftime(
                "%Y-%m-%dT%H:%M"
            ),
            "end_datetime": (timezone.now() + timedelta(days=1, hours=3)).strftime(
                "%Y-%m-%dT%H:%M"
            ),
            "sectors": [self.sector.pk],
            "comm_before": True,
            "comm_during": True,
            "comm_after": False,
            "needs_filming": True,
            "needs_poster": False,
        }

    def test_form_valid_data(self):
        """Test avec des données valides."""
        form = EventForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_form_missing_required_fields(self):
        """Test avec champs requis manquants."""
        required_fields = ["title", "description", "location", "city"]
        for field in required_fields:
            data = self.valid_data.copy()
            data[field] = ""
            form = EventForm(data=data)
            self.assertFalse(form.is_valid())
            self.assertIn(field, form.errors)

        # Test spécifique pour sectors (ManyToMany)
        data = self.valid_data.copy()
        data["sectors"] = []
        form = EventForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("sectors", form.errors)

    def test_form_end_date_before_start_date(self):
        """Test validation date de fin avant date de début."""
        data = self.valid_data.copy()
        data["end_datetime"] = (timezone.now()).strftime("%Y-%m-%dT%H:%M")
        form = EventForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)

    def test_form_same_start_end_date(self):
        """Test validation date de fin égale à date de début."""
        data = self.valid_data.copy()
        data["end_datetime"] = data["start_datetime"]
        form = EventForm(data=data)
        self.assertFalse(form.is_valid())

    def test_form_widgets(self):
        """Test la configuration des widgets."""
        form = EventForm()
        # Vérifier que les widgets sont bien configurés
        self.assertIn(
            form.fields["start_datetime"].widget.__class__.__name__,
            ["DateTimeInput", "TextInput"],
        )
        self.assertIn(
            form.fields["end_datetime"].widget.__class__.__name__,
            ["DateTimeInput", "TextInput"],
        )
        self.assertIn(
            form.fields["description"].widget.__class__.__name__, ["Textarea"]
        )

    def test_form_save(self):
        """Test la sauvegarde du formulaire."""
        form = EventForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
        event = form.save(commit=False)
        event.created_by = self.user
        event.save()
        # Sauvegarder la relation ManyToMany
        form.save_m2m()
        self.assertEqual(event.title, "Fête de la musique")
        self.assertTrue(event.comm_before)
        self.assertTrue(event.comm_during)
        self.assertEqual(event.sectors.count(), 1)


class EventImageFormTest(TestCase):
    """Tests pour le formulaire EventImageForm."""

    def setUp(self):
        """Créer les objets nécessaires pour les tests."""
        self.user = User.objects.create_user(
            email="test@cc-sudavesnois.fr",
            password="testpass123",
        )
        self.sector = Sector.objects.create(name="Santé", color_code="#b4c7e7")
        self.event = Event.objects.create(
            title="Test Event",
            description="Test",
            location="Test",
            city="Test",
            start_datetime=timezone.now() + timedelta(days=1),
            end_datetime=timezone.now() + timedelta(days=1, hours=3),
            created_by=self.user,
        )
        self.event.sectors.add(self.sector)

    def create_test_image(self, extension="jpg", size=(100, 100)):
        """Créer une image de test."""
        image = Image.new("RGB", size, color="red")
        image_io = BytesIO()
        image.save(image_io, format="JPEG" if extension in ["jpg", "jpeg"] else "PNG")
        image_io.seek(0)
        return SimpleUploadedFile(
            name=f"test_image.{extension}",
            content=image_io.read(),
            content_type=f"image/{extension if extension != 'jpg' else 'jpeg'}",
        )

    def test_form_valid_image(self):
        """Test avec une image valide."""
        image = self.create_test_image("jpg")
        form = EventImageForm(files={"image": image})
        self.assertTrue(form.is_valid())

    def test_form_invalid_extension(self):
        """Test avec une extension invalide."""
        invalid_file = SimpleUploadedFile(
            name="test.pdf",
            content=b"test content",
            content_type="application/pdf",
        )
        form = EventImageForm(files={"image": invalid_file})
        self.assertFalse(form.is_valid())
        self.assertIn("image", form.errors)

    def test_form_image_too_large(self):
        """Test avec une image trop grande (>10Mo)."""
        # Créer un fichier qui simule une taille > 10Mo
        large_content = b"x" * (11 * 1024 * 1024)  # 11 Mo
        large_file = SimpleUploadedFile(
            name="large_image.jpg",
            content=large_content,
            content_type="image/jpeg",
        )
        form = EventImageForm(files={"image": large_file})
        self.assertFalse(form.is_valid())
        self.assertIn("image", form.errors)

    @patch("events.forms.EventImage.objects.filter")
    def test_form_max_images_limit(self, mock_filter):
        """Test la limite de 10 images."""
        # Simuler qu'il y a déjà 10 images
        mock_filter.return_value.count.return_value = 10
        image = self.create_test_image("jpg")
        form = EventImageForm(
            files={"image": image},
            event=self.event,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("image", form.errors)


class EventCommentFormTest(TestCase):
    """Tests pour le formulaire EventCommentForm."""

    def test_form_valid_data(self):
        """Test avec des données valides."""
        form = EventCommentForm(data={"content": "Super événement !"})
        self.assertTrue(form.is_valid())

    def test_form_empty_content(self):
        """Test avec un contenu vide."""
        form = EventCommentForm(data={"content": ""})
        self.assertFalse(form.is_valid())
        self.assertIn("content", form.errors)

    def test_form_whitespace_only(self):
        """Test avec uniquement des espaces."""
        form = EventCommentForm(data={"content": "   "})
        self.assertFalse(form.is_valid())

    def test_form_widget(self):
        """Test la configuration du widget."""
        form = EventCommentForm()
        self.assertEqual(form.fields["content"].widget.attrs.get("rows"), 3)
        self.assertEqual(
            form.fields["content"].widget.attrs.get("placeholder"),
            "Votre commentaire...",
        )
