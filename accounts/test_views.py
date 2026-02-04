"""Tests pour les vues de l'app accounts."""

from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import Client, TestCase, override_settings
from django.urls import reverse

User = get_user_model()


@override_settings(
    ACCOUNTS_RESTRICT_EMAIL_DOMAIN=True, ACCOUNTS_ALLOWED_EMAIL_DOMAIN="cc-sudavesnois.fr"
)
class RegistrationViewTests(TestCase):
    """Tests pour la vue d'inscription."""

    def setUp(self):
        """Configure les données initiales pour les tests."""
        self.client = Client()
        self.register_url = reverse("accounts:register")
        self.valid_data = {
            "email": "test@cc-sudavesnois.fr",
            "first_name": "Jean",
            "last_name": "Dupont",
            "password1": "TestPassword123!",
            "password2": "TestPassword123!",
            "accept_terms": True,
        }

    def test_register_view_get(self):
        """Teste l'affichage du formulaire d'inscription."""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/register.html")
        self.assertContains(response, "Inscription")

    def test_register_view_post_valid(self):
        """Teste une inscription valide."""
        response = self.client.post(self.register_url, self.valid_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("accounts:login"))

        # Vérifier que l'utilisateur a été créé
        self.assertTrue(User.objects.filter(email="test@cc-sudavesnois.fr").exists())

        # Vérifier le message de succès
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("succès" in str(m).lower() for m in messages))

    def test_register_view_post_invalid_email_domain(self):
        """Teste une inscription avec domaine email non autorisé."""
        data = self.valid_data.copy()
        data["email"] = "test@gmail.com"
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "cc-sudavesnois.fr")
        self.assertFalse(User.objects.filter(email="test@gmail.com").exists())

    def test_register_view_post_password_mismatch(self):
        """Teste une inscription avec mots de passe différents."""
        data = self.valid_data.copy()
        data["password2"] = "DifferentPassword123!"
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ne correspondent pas")

    def test_register_redirects_authenticated_user(self):
        """Teste qu'un utilisateur connecté est redirigé."""
        User.objects.create_user(
            email="user@cc-sudavesnois.fr",
            password="TestPassword123!",
            first_name="Test",
            last_name="User",
        )
        self.client.login(email="user@cc-sudavesnois.fr", password="TestPassword123!")
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 302)


class LoginViewTests(TestCase):
    """Tests pour la vue de connexion."""

    def setUp(self):
        """Configure les données initiales pour les tests."""
        self.client = Client()
        self.login_url = reverse("accounts:login")
        self.user = User.objects.create_user(
            email="test@cc-sudavesnois.fr",
            password="TestPassword123!",
            first_name="Jean",
            last_name="Dupont",
        )

    def test_login_view_get(self):
        """Teste l'affichage du formulaire de connexion."""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_login_view_post_valid(self):
        """Teste une connexion valide."""
        response = self.client.post(
            self.login_url,
            {
                "username": "test@cc-sudavesnois.fr",
                "password": "TestPassword123!",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/")

    def test_login_view_post_invalid(self):
        """Teste une connexion invalide."""
        response = self.client.post(
            self.login_url,
            {
                "username": "test@cc-sudavesnois.fr",
                "password": "WrongPassword123!",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Saisissez un adresse email")

    def test_login_redirects_authenticated_user(self):
        """Teste qu'un utilisateur connecté est redirigé."""
        self.client.login(email="test@cc-sudavesnois.fr", password="TestPassword123!")
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 302)


class LogoutViewTests(TestCase):
    """Tests pour la vue de déconnexion."""

    def setUp(self):
        """Configure les données initiales pour les tests."""
        self.client = Client()
        self.logout_url = reverse("accounts:logout")
        self.user = User.objects.create_user(
            email="test@cc-sudavesnois.fr",
            password="TestPassword123!",
            first_name="Jean",
            last_name="Dupont",
        )

    def test_logout_view(self):
        """Teste la déconnexion."""
        self.client.login(email="test@cc-sudavesnois.fr", password="TestPassword123!")
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, 302)


class ProfileViewTests(TestCase):
    """Tests pour la vue de profil."""

    def setUp(self):
        """Configure les données initiales pour les tests."""
        self.client = Client()
        self.profile_url = reverse("accounts:profile")
        self.user = User.objects.create_user(
            email="test@cc-sudavesnois.fr",
            password="TestPassword123!",
            first_name="Jean",
            last_name="Dupont",
        )

    def test_profile_view_requires_login(self):
        """Teste que la vue de profil nécessite une connexion."""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_profile_view_get(self):
        """Teste l'affichage du profil."""
        self.client.login(email="test@cc-sudavesnois.fr", password="TestPassword123!")
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/profile.html")
        self.assertContains(response, "Jean")
        self.assertContains(response, "Dupont")


class ProfileEditViewTests(TestCase):
    """Tests pour la vue d'édition de profil."""

    def setUp(self):
        """Configure les données initiales pour les tests."""
        self.client = Client()
        self.profile_edit_url = reverse("accounts:profile_edit")
        self.profile_url = reverse("accounts:profile")
        self.user = User.objects.create_user(
            email="test@cc-sudavesnois.fr",
            password="TestPassword123!",
            first_name="Jean",
            last_name="Dupont",
        )

    def test_profile_edit_requires_login(self):
        """Teste que l'édition de profil nécessite une connexion."""
        response = self.client.get(self.profile_edit_url)
        self.assertEqual(response.status_code, 302)

    def test_profile_edit_view_get(self):
        """Teste l'affichage du formulaire d'édition."""
        self.client.login(email="test@cc-sudavesnois.fr", password="TestPassword123!")
        response = self.client.get(self.profile_edit_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/profile_edit.html")

    def test_profile_edit_view_post_valid(self):
        """Teste une édition de profil valide."""
        self.client.login(email="test@cc-sudavesnois.fr", password="TestPassword123!")
        response = self.client.post(
            self.profile_edit_url,
            {
                "email": "test@cc-sudavesnois.fr",
                "first_name": "Jeanne",
                "last_name": "Durand",
                "bio": "Nouvelle bio",
                "location": "Paris",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.profile_url)

        # Vérifier les modifications
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Jeanne")
        self.assertEqual(self.user.last_name, "Durand")
        self.assertEqual(self.user.profile.bio, "Nouvelle bio")


class PasswordChangeViewTests(TestCase):
    """Tests pour la vue de changement de mot de passe."""

    def setUp(self):
        """Configure les données initiales pour les tests."""
        self.client = Client()
        self.password_change_url = reverse("accounts:password_change")
        self.user = User.objects.create_user(
            email="test@cc-sudavesnois.fr",
            password="OldPassword123!",
            first_name="Jean",
            last_name="Dupont",
        )

    def test_password_change_requires_login(self):
        """Teste que le changement de mot de passe nécessite une connexion."""
        response = self.client.get(self.password_change_url)
        self.assertEqual(response.status_code, 302)

    def test_password_change_view_get(self):
        """Teste l'affichage du formulaire de changement de mot de passe."""
        self.client.login(email="test@cc-sudavesnois.fr", password="OldPassword123!")
        response = self.client.get(self.password_change_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/password_change.html")

    def test_password_change_view_post_valid(self):
        """Teste un changement de mot de passe valide."""
        self.client.login(email="test@cc-sudavesnois.fr", password="OldPassword123!")
        response = self.client.post(
            self.password_change_url,
            {
                "old_password": "OldPassword123!",
                "new_password1": "NewPassword123!",
                "new_password2": "NewPassword123!",
            },
        )
        self.assertEqual(response.status_code, 302)

        # Vérifier que le mot de passe a été changé
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewPassword123!"))


class PasswordResetViewTests(TestCase):
    """Tests pour les vues de réinitialisation de mot de passe."""

    def setUp(self):
        """Configure les données initiales pour les tests."""
        self.client = Client()
        self.password_reset_url = reverse("accounts:password_reset")
        self.user = User.objects.create_user(
            email="test@cc-sudavesnois.fr",
            password="TestPassword123!",
            first_name="Jean",
            last_name="Dupont",
        )

    def test_password_reset_view_get(self):
        """Teste l'affichage du formulaire de réinitialisation."""
        response = self.client.get(self.password_reset_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/password_reset.html")

    def test_password_reset_view_post_valid(self):
        """Teste une demande de réinitialisation valide."""
        response = self.client.post(
            self.password_reset_url,
            {
                "email": "test@cc-sudavesnois.fr",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("accounts:password_reset_done"))


class SessionsViewTests(TestCase):
    """Tests pour la vue des sessions actives."""

    def setUp(self):
        """Configure les données initiales pour les tests."""
        self.client = Client()
        self.sessions_url = reverse("accounts:sessions")
        self.user = User.objects.create_user(
            email="test@cc-sudavesnois.fr",
            password="TestPassword123!",
            first_name="Jean",
            last_name="Dupont",
        )

    def test_sessions_view_requires_login(self):
        """Teste que la vue des sessions nécessite une connexion."""
        response = self.client.get(self.sessions_url)
        self.assertEqual(response.status_code, 302)

    def test_sessions_view_get(self):
        """Teste l'affichage des sessions actives."""
        self.client.login(email="test@cc-sudavesnois.fr", password="TestPassword123!")
        response = self.client.get(self.sessions_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/sessions.html")
