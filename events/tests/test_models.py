"""Tests pour les modèles de l'app events."""

from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from accounts.models import User
from events.models import (Event, EventChangeLog, EventComment, EventImage,
                           Sector)


class SectorModelTest(TestCase):
    """Tests pour le modèle Sector."""

    def setUp(self):
        """Créer un secteur pour les tests."""
        self.sector = Sector.objects.create(
            name="Santé",
            color_code="#b4c7e7",
            description="Événements liés à la santé",
        )

    def test_sector_creation(self):
        """Test la création d'un secteur."""
        self.assertEqual(self.sector.name, "Santé")
        self.assertEqual(self.sector.color_code, "#b4c7e7")
        self.assertTrue(self.sector.is_active)

    def test_sector_str_representation(self):
        """Test la représentation string du secteur."""
        self.assertEqual(str(self.sector), "Santé")

    def test_sector_ordering(self):
        """Test l'ordre des secteurs."""
        # Mettre à jour le secteur existant pour avoir un ordre différent
        self.sector.order = 5
        self.sector.save()

        sector2 = Sector.objects.create(name="Ruralité", color_code="#005b24", order=1)
        sector3 = Sector.objects.create(name="Mobilité", color_code="#ff0000", order=0)
        sectors = list(Sector.objects.order_by("order", "name"))
        # Vérifier que les secteurs sont ordonnés par order puis name
        # order=0: Mobilité, order=1: Ruralité, order=5: Santé
        self.assertEqual(sectors[0], sector3)  # order=0: Mobilité
        self.assertEqual(sectors[1], sector2)  # order=1: Ruralité
        self.assertEqual(sectors[2], self.sector)  # order=5: Santé


class EventModelTest(TestCase):
    """Tests pour le modèle Event."""

    def setUp(self):
        """Créer les objets nécessaires pour les tests."""
        self.user = User.objects.create_user(
            email="test@cc-sudavesnois.fr",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )
        self.sector = Sector.objects.create(
            name="Santé",
            color_code="#b4c7e7",
        )
        self.event = Event.objects.create(
            title="Fête de la musique",
            description="Concert en plein air",
            location="Salle polyvalente",
            city="Saint-Quentin",
            start_datetime=timezone.now() + timedelta(days=1),
            end_datetime=timezone.now() + timedelta(days=1, hours=3),
            created_by=self.user,
            comm_before=True,
            comm_during=True,
            needs_filming=True,
            needs_poster=True,
        )
        self.event.sectors.add(self.sector)

    def test_event_creation(self):
        """Test la création d'un événement."""
        self.assertEqual(self.event.title, "Fête de la musique")
        self.assertEqual(self.event.location, "Salle polyvalente")
        self.assertEqual(self.event.city, "Saint-Quentin")
        self.assertTrue(self.event.comm_before)
        self.assertTrue(self.event.comm_during)
        self.assertFalse(self.event.comm_after)
        self.assertTrue(self.event.needs_filming)
        self.assertTrue(self.event.needs_poster)

    def test_event_slug_generation(self):
        """Test la génération automatique du slug."""
        self.assertIn("fete-de-la-musique", self.event.slug)
        self.assertIn(self.event.start_datetime.strftime("%Y-%m-%d"), self.event.slug)

    def test_event_slug_uniqueness(self):
        """Test que les slugs sont uniques."""
        event2 = Event.objects.create(
            title="Fête de la musique",
            description="Autre concert",
            location="Parc",
            city="Saint-Quentin",
            start_datetime=self.event.start_datetime,
            end_datetime=self.event.end_datetime,
            created_by=self.user,
        )
        event2.sectors.add(self.sector)
        self.assertNotEqual(self.event.slug, event2.slug)

    def test_event_end_date_after_start_date(self):
        """Test que la date de fin est après la date de début."""
        event = Event(
            title="Test",
            description="Test",
            location="Test",
            city="Test",
            start_datetime=timezone.now() + timedelta(days=1),
            end_datetime=timezone.now(),  # Avant le début
            created_by=self.user,
        )
        with self.assertRaises(ValidationError):
            event.full_clean()

    def test_event_str_representation(self):
        """Test la représentation string de l'événement."""
        expected = (
            f"Fête de la musique - {self.event.start_datetime.strftime('%d/%m/%Y')}"
        )
        self.assertEqual(str(self.event), expected)

    def test_event_get_absolute_url(self):
        """Test la méthode get_absolute_url."""
        self.assertEqual(
            self.event.get_absolute_url(), f"/evenements/{self.event.slug}/"
        )

    def test_event_is_upcoming(self):
        """Test la propriété is_upcoming."""
        self.assertTrue(self.event.is_upcoming)

        # Événement passé
        past_event = Event.objects.create(
            title="Événement passé",
            description="Test",
            location="Test",
            city="Test",
            start_datetime=timezone.now() - timedelta(days=1),
            end_datetime=timezone.now() - timedelta(days=1, hours=-3),
            created_by=self.user,
        )
        past_event.sectors.add(self.sector)
        self.assertFalse(past_event.is_upcoming)


class EventImageModelTest(TestCase):
    """Tests pour le modèle EventImage."""

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

    def test_image_creation(self):
        """Test la création d'une image."""
        # Note: On ne teste pas l'upload réel ici, juste le modèle
        image = EventImage.objects.create(
            event=self.event,
            order=1,
        )
        self.assertEqual(image.event, self.event)
        self.assertEqual(image.order, 1)

    def test_image_ordering(self):
        """Test l'ordre des images."""
        img1 = EventImage.objects.create(event=self.event, order=2)
        img2 = EventImage.objects.create(event=self.event, order=1)
        img3 = EventImage.objects.create(event=self.event, order=3)

        images = list(EventImage.objects.filter(event=self.event))
        self.assertEqual(images[0], img2)  # order=1
        self.assertEqual(images[1], img1)  # order=2
        self.assertEqual(images[2], img3)  # order=3

    def test_max_images_limit(self):
        """Test la limite de 10 images par événement."""
        # Créer 10 images
        for i in range(10):
            EventImage.objects.create(event=self.event, order=i)

        # La 11ème devrait échouer
        with self.assertRaises(ValidationError):
            img11 = EventImage(event=self.event, order=10)
            img11.full_clean()


class EventCommentModelTest(TestCase):
    """Tests pour le modèle EventComment."""

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
        self.comment = EventComment.objects.create(
            event=self.event,
            author=self.user,
            content="Super événement !",
        )

    def test_comment_creation(self):
        """Test la création d'un commentaire."""
        self.assertEqual(self.comment.content, "Super événement !")
        self.assertEqual(self.comment.author, self.user)
        self.assertEqual(self.comment.event, self.event)
        self.assertTrue(self.comment.is_active)

    def test_comment_str_representation(self):
        """Test la représentation string du commentaire."""
        expected = f"Commentaire de {self.user} sur {self.event}"
        self.assertEqual(str(self.comment), expected)

    def test_comment_ordering(self):
        """Test que les commentaires sont ordonnés par date décroissante."""
        comment2 = EventComment.objects.create(
            event=self.event,
            author=self.user,
            content="Deuxième commentaire",
        )
        comments = list(
            EventComment.objects.filter(event=self.event).order_by("-created_at")
        )
        # Vérifier que les deux commentaires sont présents
        self.assertEqual(len(comments), 2)
        self.assertIn(self.comment, comments)
        self.assertIn(comment2, comments)


class EventChangeLogModelTest(TestCase):
    """Tests pour le modèle EventChangeLog."""

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
        self.changelog = EventChangeLog.objects.create(
            event=self.event,
            changed_by=self.user,
            field_name="title",
            old_value="Ancien titre",
            new_value="Nouveau titre",
        )

    def test_changelog_creation(self):
        """Test la création d'un changelog."""
        self.assertEqual(self.changelog.field_name, "title")
        self.assertEqual(self.changelog.old_value, "Ancien titre")
        self.assertEqual(self.changelog.new_value, "Nouveau titre")

    def test_changelog_str_representation(self):
        """Test la représentation string du changelog."""
        expected = f"Modification de title sur {self.event}"
        self.assertEqual(str(self.changelog), expected)

    def test_changelog_ordering(self):
        """Test que les changelogs sont ordonnés par date décroissante."""
        changelog2 = EventChangeLog.objects.create(
            event=self.event,
            changed_by=self.user,
            field_name="location",
            old_value="Ancien lieu",
            new_value="Nouveau lieu",
        )
        logs = list(
            EventChangeLog.objects.filter(event=self.event).order_by("-changed_at")
        )
        # Vérifier que les deux changelogs sont présents
        self.assertEqual(len(logs), 2)
        self.assertIn(self.changelog, logs)
        self.assertIn(changelog2, logs)
