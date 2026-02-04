"""Tests pour les formulaires de l'app accounts."""

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from accounts.forms import (
    PasswordChangeForm,
    UserLoginForm,
    UserProfileForm,
    UserRegistrationForm,
    UserUpdateForm,
)

User = get_user_model()


@override_settings(
    ACCOUNTS_RESTRICT_EMAIL_DOMAIN=True, ACCOUNTS_ALLOWED_EMAIL_DOMAIN="cc-sudavesnois.fr"
)
class UserRegistrationFormTests(TestCase):
    """Tests pour le formulaire d'inscription."""

    def setUp(self):
        """Configure les données initiales pour les tests."""
        self.valid_data = {
            "email": "test@cc-sudavesnois.fr",
            "first_name": "Jean",
            "last_name": "Dupont",
            "password1": "TestPassword123!",
            "password2": "TestPassword123!",
            "accept_terms": True,
        }

    def test_valid_registration_form(self):
        """Teste un formulaire d'inscription valide."""
        form = UserRegistrationForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_invalid_email_domain(self):
        """Teste que les emails avec domaine non autorisé sont rejetés."""
        data = self.valid_data.copy()
        data["email"] = "test@gmail.com"
        form = UserRegistrationForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_valid_email_domain(self):
        """Teste que les emails avec domaine autorisé sont acceptés."""
        data = self.valid_data.copy()
        data["email"] = "test@cc-sudavesnois.fr"
        form = UserRegistrationForm(data=data)

        self.assertTrue(form.is_valid())

    def test_password_mismatch(self):
        """Teste que les mots de passe différents sont rejetés."""
        data = self.valid_data.copy()
        data["password2"] = "DifferentPassword123!"
        form = UserRegistrationForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_missing_accept_terms(self):
        """Teste que l'acceptation des conditions est obligatoire."""
        data = self.valid_data.copy()
        data["accept_terms"] = False
        form = UserRegistrationForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("accept_terms", form.errors)

    def test_duplicate_email(self):
        """Teste que les emails en double sont rejetés."""
        User.objects.create_user(
            email="test@cc-sudavesnois.fr",
            password="TestPassword123!",
            first_name="Jean",
            last_name="Dupont",
        )

        form = UserRegistrationForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_email_normalization_on_save(self):
        """Teste que l'email est normalisé lors de la sauvegarde."""
        data = self.valid_data.copy()
        data["email"] = "Test.User@CC-SUDAVESNOIS.FR"
        form = UserRegistrationForm(data=data)

        self.assertTrue(form.is_valid())
        user = form.save()
        # L'email complet est mis en minuscules pour la cohérence
        self.assertEqual(user.email, "test.user@cc-sudavesnois.fr")


class UserLoginFormTests(TestCase):
    """Tests pour le formulaire de connexion."""

    def setUp(self):
        """Configure les données initiales pour les tests."""
        self.user = User.objects.create_user(
            email="test@cc-sudavesnois.fr",
            password="TestPassword123!",
            first_name="Jean",
            last_name="Dupont",
        )

    def test_valid_login_form(self):
        """Teste un formulaire de connexion valide."""
        form = UserLoginForm(
            data={
                "username": "test@cc-sudavesnois.fr",
                "password": "TestPassword123!",
            }
        )
        self.assertTrue(form.is_valid())

    def test_invalid_credentials(self):
        """Teste que les identifiants invalides sont rejetés."""
        form = UserLoginForm(
            data={
                "username": "test@cc-sudavesnois.fr",
                "password": "WrongPassword123!",
            }
        )
        self.assertFalse(form.is_valid())

    def test_email_field_used_for_username(self):
        """Teste que le champ email est utilisé comme username."""
        form = UserLoginForm()
        self.assertEqual(form.fields["username"].widget.input_type, "email")


class UserUpdateFormTests(TestCase):
    """Tests pour le formulaire de mise à jour utilisateur."""

    def setUp(self):
        """Configure les données initiales pour les tests."""
        self.user = User.objects.create_user(
            email="test@cc-sudavesnois.fr",
            password="TestPassword123!",
            first_name="Jean",
            last_name="Dupont",
        )

    def test_valid_update_form(self):
        """Teste une mise à jour valide."""
        form = UserUpdateForm(
            instance=self.user,
            data={
                "email": "test@cc-sudavesnois.fr",
                "first_name": "Jeanne",
                "last_name": "Durand",
                "phone_number": "0612345678",
            },
        )
        self.assertTrue(form.is_valid())

    def test_duplicate_email_rejected(self):
        """Teste que l'email en double est rejeté."""
        User.objects.create_user(
            email="other@cc-sudavesnois.fr",
            password="TestPassword123!",
            first_name="Other",
            last_name="User",
        )

        form = UserUpdateForm(
            instance=self.user,
            data={
                "email": "other@cc-sudavesnois.fr",
                "first_name": "Jean",
                "last_name": "Dupont",
            },
        )
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)


class UserProfileFormTests(TestCase):
    """Tests pour le formulaire de profil."""

    def setUp(self):
        """Configure les données initiales pour les tests."""
        self.user = User.objects.create_user(
            email="test@cc-sudavesnois.fr",
            password="TestPassword123!",
            first_name="Jean",
            last_name="Dupont",
        )
        self.profile = self.user.profile

    def test_valid_profile_form(self):
        """Teste un formulaire de profil valide."""
        form = UserProfileForm(
            instance=self.profile,
            data={
                "bio": "Ma bio",
                "location": "Paris",
                "website": "https://example.com",
                "notification_enabled": True,
            },
        )
        self.assertTrue(form.is_valid())

    def test_optional_fields(self):
        """Teste que tous les champs sont optionnels."""
        form = UserProfileForm(instance=self.profile, data={})
        self.assertTrue(form.is_valid())


class PasswordChangeFormTests(TestCase):
    """Tests pour le formulaire de changement de mot de passe."""

    def setUp(self):
        """Configure les données initiales pour les tests."""
        self.user = User.objects.create_user(
            email="test@cc-sudavesnois.fr",
            password="OldPassword123!",
            first_name="Jean",
            last_name="Dupont",
        )

    def test_valid_password_change(self):
        """Teste un changement de mot de passe valide."""
        form = PasswordChangeForm(
            user=self.user,
            data={
                "old_password": "OldPassword123!",
                "new_password1": "NewPassword123!",
                "new_password2": "NewPassword123!",
            },
        )
        self.assertTrue(form.is_valid())

    def test_wrong_old_password(self):
        """Teste que l'ancien mot de passe incorrect est rejeté."""
        form = PasswordChangeForm(
            user=self.user,
            data={
                "old_password": "WrongPassword123!",
                "new_password1": "NewPassword123!",
                "new_password2": "NewPassword123!",
            },
        )
        self.assertFalse(form.is_valid())
        self.assertIn("old_password", form.errors)

    def test_password_mismatch(self):
        """Teste que les nouveaux mots de passe différents sont rejetés."""
        form = PasswordChangeForm(
            user=self.user,
            data={
                "old_password": "OldPassword123!",
                "new_password1": "NewPassword123!",
                "new_password2": "DifferentPassword123!",
            },
        )
        self.assertFalse(form.is_valid())
        self.assertIn("new_password2", form.errors)
