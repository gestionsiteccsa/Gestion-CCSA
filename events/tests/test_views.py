"""Tests pour les vues de l'app events."""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from events.models import Event, EventComment, Sector

User = get_user_model()


class EventListViewTest(TestCase):
    """Tests pour la vue EventListView."""

    def setUp(self):
        """Créer les objets nécessaires pour les tests."""
        self.client = Client()
        self.user = User.objects.create_user(
            email="test@cc-sudavesnois.fr",
            password="testpass123",
        )
        self.sector = Sector.objects.create(name="Santé", color_code="#b4c7e7")
        self.event = Event.objects.create(
            title="Test Event",
            description="Test description",
            location="Salle polyvalente",
            city="Saint-Quentin",
            start_datetime=timezone.now() + timedelta(days=1),
            end_datetime=timezone.now() + timedelta(days=1, hours=3),
            created_by=self.user,
        )
        self.event.sectors.add(self.sector)

    def test_list_view_status_code(self):
        """Test que la vue retourne 200."""
        response = self.client.get(reverse("events:event_list"))
        self.assertEqual(response.status_code, 200)

    def test_list_view_template(self):
        """Test que le bon template est utilisé."""
        response = self.client.get(reverse("events:event_list"))
        self.assertTemplateUsed(response, "events/event_list.html")

    def test_list_view_context(self):
        """Test que les événements sont dans le contexte."""
        response = self.client.get(reverse("events:event_list"))
        self.assertIn("events", response.context)
        self.assertEqual(len(response.context["events"]), 1)

    def test_list_view_filter_by_sector(self):
        """Test le filtrage par secteur."""
        sector2 = Sector.objects.create(name="Mobilité", color_code="#ff0000")
        event2 = Event.objects.create(
            title="Autre event",
            description="Test",
            location="Test",
            city="Test",
            start_datetime=timezone.now() + timedelta(days=2),
            end_datetime=timezone.now() + timedelta(days=2, hours=3),
            created_by=self.user,
        )
        event2.sectors.add(sector2)
        response = self.client.get(reverse("events:event_list"), {"sector": self.sector.pk})
        self.assertEqual(len(response.context["events"]), 1)
        self.assertIn(self.sector, response.context["events"][0].sectors.all())

    def test_list_view_filter_by_city(self):
        """Test le filtrage par ville."""
        response = self.client.get(reverse("events:event_list"), {"city": "Saint-Quentin"})
        self.assertEqual(len(response.context["events"]), 1)

    def test_list_view_pagination(self):
        """Test la pagination."""
        # Créer 15 événements supplémentaires
        for i in range(15):
            event = Event.objects.create(
                title=f"Event {i}",
                description="Test",
                location="Test",
                city="Test",
                start_datetime=timezone.now() + timedelta(days=i + 2),
                end_datetime=timezone.now() + timedelta(days=i + 2, hours=3),
                created_by=self.user,
            )
            event.sectors.add(self.sector)
        response = self.client.get(reverse("events:event_list"))
        self.assertEqual(len(response.context["events"]), 12)  # 12 par page


class EventCalendarViewTest(TestCase):
    """Tests pour la vue EventCalendarView."""

    def setUp(self):
        """Créer les objets nécessaires pour les tests."""
        self.client = Client()
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

    def test_calendar_view_status_code(self):
        """Test que la vue retourne 200."""
        response = self.client.get(reverse("events:event_calendar"))
        self.assertEqual(response.status_code, 200)

    def test_calendar_view_template(self):
        """Test que le bon template est utilisé."""
        response = self.client.get(reverse("events:event_calendar"))
        self.assertTemplateUsed(response, "events/event_calendar.html")

    def test_calendar_view_with_year_month(self):
        """Test la vue avec année et mois spécifiques."""
        now = timezone.now()
        response = self.client.get(
            reverse("events:event_calendar_month", kwargs={"year": now.year, "month": now.month})
        )
        self.assertEqual(response.status_code, 200)

    def test_calendar_view_context(self):
        """Test que les données du calendrier sont dans le contexte."""
        response = self.client.get(reverse("events:event_calendar"))
        self.assertIn("events", response.context)
        self.assertIn("current_month", response.context)
        self.assertIn("prev_month", response.context)
        self.assertIn("next_month", response.context)


class EventDetailViewTest(TestCase):
    """Tests pour la vue EventDetailView."""

    def setUp(self):
        """Créer les objets nécessaires pour les tests."""
        self.client = Client()
        self.user = User.objects.create_user(
            email="test@cc-sudavesnois.fr",
            password="testpass123",
        )
        self.sector = Sector.objects.create(name="Santé", color_code="#b4c7e7")
        self.event = Event.objects.create(
            title="Test Event",
            description="Test description",
            location="Salle polyvalente",
            city="Saint-Quentin",
            start_datetime=timezone.now() + timedelta(days=1),
            end_datetime=timezone.now() + timedelta(days=1, hours=3),
            created_by=self.user,
        )
        self.event.sectors.add(self.sector)

    def test_detail_view_status_code(self):
        """Test que la vue retourne 200."""
        response = self.client.get(reverse("events:event_detail", kwargs={"slug": self.event.slug}))
        self.assertEqual(response.status_code, 200)

    def test_detail_view_template(self):
        """Test que le bon template est utilisé."""
        response = self.client.get(reverse("events:event_detail", kwargs={"slug": self.event.slug}))
        self.assertTemplateUsed(response, "events/event_detail.html")

    def test_detail_view_context(self):
        """Test que l'événement est dans le contexte."""
        response = self.client.get(reverse("events:event_detail", kwargs={"slug": self.event.slug}))
        self.assertIn("event", response.context)
        self.assertEqual(response.context["event"], self.event)

    def test_detail_view_404(self):
        """Test que la vue retourne 404 pour un slug inexistant."""
        response = self.client.get(
            reverse("events:event_detail", kwargs={"slug": "inexistant-2024-01-01"})
        )
        self.assertEqual(response.status_code, 404)


class EventCreateViewTest(TestCase):
    """Tests pour la vue EventCreateView."""

    def setUp(self):
        """Créer les objets nécessaires pour les tests."""
        self.client = Client()
        self.user = User.objects.create_user(
            email="test@cc-sudavesnois.fr",
            password="testpass123",
        )
        self.sector = Sector.objects.create(name="Santé", color_code="#b4c7e7")
        self.valid_data = {
            "title": "Nouvel événement",
            "description": "Description",
            "location": "Salle polyvalente",
            "city": "Saint-Quentin",
            "start_datetime": (timezone.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M"),
            "end_datetime": (timezone.now() + timedelta(days=1, hours=3)).strftime(
                "%Y-%m-%dT%H:%M"
            ),
            "sectors": [self.sector.pk],
            "comm_before": True,
            "needs_filming": True,
        }

    def test_create_view_redirects_if_not_logged_in(self):
        """Test que la vue redirige si l'utilisateur n'est pas connecté."""
        response = self.client.get(reverse("events:event_create"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_create_view_get_logged_in(self):
        """Test que la vue retourne 200 si l'utilisateur est connecté."""
        self.client.login(email="test@cc-sudavesnois.fr", password="testpass123")
        response = self.client.get(reverse("events:event_create"))
        self.assertEqual(response.status_code, 200)

    def test_create_view_post_valid_data(self):
        """Test la création d'un événement avec des données valides."""
        self.client.login(email="test@cc-sudavesnois.fr", password="testpass123")
        response = self.client.post(reverse("events:event_create"), self.valid_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Event.objects.count(), 1)
        event = Event.objects.first()
        self.assertEqual(event.created_by, self.user)
        self.assertEqual(event.sectors.count(), 1)

    def test_create_view_post_invalid_data(self):
        """Test la création avec des données invalides."""
        self.client.login(email="test@cc-sudavesnois.fr", password="testpass123")
        invalid_data = self.valid_data.copy()
        invalid_data["title"] = ""
        response = self.client.post(reverse("events:event_create"), invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Event.objects.count(), 0)


class EventUpdateViewTest(TestCase):
    """Tests pour la vue EventUpdateView."""

    def setUp(self):
        """Créer les objets nécessaires pour les tests."""
        self.client = Client()
        self.user = User.objects.create_user(
            email="test@cc-sudavesnois.fr",
            password="testpass123",
        )
        self.other_user = User.objects.create_user(
            email="other@cc-sudavesnois.fr",
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

    def test_update_view_redirects_if_not_logged_in(self):
        """Test que la vue redirige si l'utilisateur n'est pas connecté."""
        response = self.client.get(reverse("events:event_update", kwargs={"slug": self.event.slug}))
        self.assertEqual(response.status_code, 302)

    def test_update_view_forbidden_if_not_creator(self):
        """Test que la vue retourne 403 si l'utilisateur n'est pas le créateur."""
        self.client.login(email="other@cc-sudavesnois.fr", password="testpass123")
        response = self.client.get(reverse("events:event_update", kwargs={"slug": self.event.slug}))
        self.assertEqual(response.status_code, 403)

    def test_update_view_get_creator(self):
        """Test que le créateur peut accéder à la vue."""
        self.client.login(email="test@cc-sudavesnois.fr", password="testpass123")
        response = self.client.get(reverse("events:event_update", kwargs={"slug": self.event.slug}))
        self.assertEqual(response.status_code, 200)

    def test_update_view_post_valid_data(self):
        """Test la mise à jour avec des données valides."""
        self.client.login(email="test@cc-sudavesnois.fr", password="testpass123")
        response = self.client.post(
            reverse("events:event_update", kwargs={"slug": self.event.slug}),
            {
                "title": "Titre modifié",
                "description": self.event.description,
                "location": self.event.location,
                "city": self.event.city,
                "start_datetime": self.event.start_datetime.strftime("%Y-%m-%dT%H:%M"),
                "end_datetime": self.event.end_datetime.strftime("%Y-%m-%dT%H:%M"),
                "sectors": [self.sector.pk],
            },
        )
        self.assertEqual(response.status_code, 302)
        self.event.refresh_from_db()
        self.assertEqual(self.event.title, "Titre modifié")


class EventDeleteViewTest(TestCase):
    """Tests pour la vue EventDeleteView."""

    def setUp(self):
        """Créer les objets nécessaires pour les tests."""
        self.client = Client()
        self.user = User.objects.create_user(
            email="test@cc-sudavesnois.fr",
            password="testpass123",
        )
        self.other_user = User.objects.create_user(
            email="other@cc-sudavesnois.fr",
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

    def test_delete_view_redirects_if_not_logged_in(self):
        """Test que la vue redirige si l'utilisateur n'est pas connecté."""
        response = self.client.get(reverse("events:event_delete", kwargs={"slug": self.event.slug}))
        self.assertEqual(response.status_code, 302)

    def test_delete_view_forbidden_if_not_creator(self):
        """Test que la vue retourne 403 si l'utilisateur n'est pas le créateur."""
        self.client.login(email="other@cc-sudavesnois.fr", password="testpass123")
        response = self.client.get(reverse("events:event_delete", kwargs={"slug": self.event.slug}))
        self.assertEqual(response.status_code, 403)

    def test_delete_view_post_creator(self):
        """Test que le créateur peut supprimer l'événement."""
        self.client.login(email="test@cc-sudavesnois.fr", password="testpass123")
        response = self.client.post(
            reverse("events:event_delete", kwargs={"slug": self.event.slug})
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Event.objects.count(), 0)


class EventCommentCreateViewTest(TestCase):
    """Tests pour la création de commentaires."""

    def setUp(self):
        """Créer les objets nécessaires pour les tests."""
        self.client = Client()
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

    def test_comment_create_redirects_if_not_logged_in(self):
        """Test que la création redirige si l'utilisateur n'est pas connecté."""
        response = self.client.post(
            reverse("events:event_detail", kwargs={"slug": self.event.slug}),
            {"content": "Test commentaire"},
        )
        self.assertEqual(response.status_code, 302)

    def test_comment_create_logged_in(self):
        """Test la création d'un commentaire connecté."""
        self.client.login(email="test@cc-sudavesnois.fr", password="testpass123")
        response = self.client.post(
            reverse("events:event_detail", kwargs={"slug": self.event.slug}),
            {"content": "Super événement !"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(EventComment.objects.count(), 1)
        comment = EventComment.objects.first()
        self.assertEqual(comment.content, "Super événement !")
        self.assertEqual(comment.author, self.user)
