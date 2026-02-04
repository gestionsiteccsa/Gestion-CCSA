"""Managers pour l'app accounts."""

from django.contrib.auth.models import BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """Manager personnalisé pour le modèle User."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Crée et sauvegarde un utilisateur avec email et password."""
        if not email:
            raise ValueError("L'adresse email est obligatoire")

        email = self.normalize_email(email)

        # Si c'est le premier utilisateur, le transformer en superuser
        if not self.model.objects.exists():
            extra_fields.setdefault("is_staff", True)
            extra_fields.setdefault("is_superuser", True)
            extra_fields.setdefault("is_active", True)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Crée un utilisateur standard."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """Crée un superutilisateur."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Le superutilisateur doit avoir is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Le superutilisateur doit avoir is_superuser=True.")

        return self._create_user(email, password, **extra_fields)

    def active(self):
        """Retourne uniquement les utilisateurs actifs."""
        return self.filter(is_active=True)


class UserSessionManager(models.Manager):
    """Manager pour le modèle UserSession."""

    def active(self):
        """Retourne uniquement les sessions actives."""
        return self.filter(is_active=True)

    def for_user(self, user):
        """Retourne les sessions d'un utilisateur spécifique."""
        return self.filter(user=user)

    def active_for_user(self, user):
        """Retourne les sessions actives d'un utilisateur."""
        return self.filter(user=user, is_active=True)
