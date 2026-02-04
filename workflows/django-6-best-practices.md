# Skill Django 6.0 - Bonnes Pratiques et Conventions

## 🎯 Objectif

Ce skill définit les bonnes pratiques et conventions pour le développement avec Django 6.0. **Il doit être consulté obligatoirement avant chaque création ou modification de fichier Django.**

## ⚠️ Règle d'Or

> **AUCUN fichier Django (models, views, forms, etc.) ne doit être créé ou modifié sans respecter ces conventions.**

---

## 📋 Installation et Configuration

### Installation de Django 6.0

```bash
# Installation de base
pip install Django>=6.0,<6.1

# Installation avec dépendances recommandées
pip install Django>=6.0,<6.1 psycopg2-binary pillow python-dotenv

# Pour le développement
pip install Django>=6.0,<6.1 django-debug-toolbar django-extensions

# Pour les tests
pip install Django>=6.0,<6.1 pytest-django factory-boy

# Pour la production
pip install Django>=6.0,<6.1 gunicorn whitenoise django-cors-headers
```

### Structure de Projet Recommandée

```
mon_projet/
├── config/                      # Configuration du projet
│   ├── __init__.py
│   ├── settings/               # Settings par environnement
│   │   ├── __init__.py
│   │   ├── base.py            # Configuration de base
│   │   ├── development.py     # Configuration développement
│   │   ├── production.py      # Configuration production
│   │   └── test.py            # Configuration tests
│   ├── urls.py                # URLs principales
│   ├── wsgi.py                # WSGI
│   ├── asgi.py                # ASGI
│   └── celery.py              # Configuration Celery (optionnel)
├── apps/                       # Applications Django
│   ├── __init__.py
│   ├── users/                 # App utilisateurs
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── forms.py
│   │   ├── admin.py
│   │   ├── urls.py
│   │   ├── tests/
│   │   └── apps.py
│   └── blog/                  # Autre app exemple
├── templates/                  # Templates globaux
│   ├── base.html
│   └── partials/
├── static/                     # Fichiers statiques
│   ├── css/
│   ├── js/
│   └── images/
├── media/                      # Fichiers uploadés
├── locale/                     # Fichiers de traduction
├── requirements/
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
├── manage.py
├── pyproject.toml
└── .env
```

### Configuration des Settings (Configuration Split)

#### config/settings/base.py

```python
"""Configuration de base Django 6.0."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Charger les variables d'environnement
load_dotenv(BASE_DIR / '.env')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is not set")

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sites',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'corsheaders',
    'django_filters',
    'crispy_forms',
    'crispy_bootstrap5',
]

LOCAL_APPS = [
    'apps.users',
    'apps.blog',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Production
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {
            'connect_timeout': 10,
        },
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 12,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication
AUTH_USER_MODEL = 'users.User'
LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Security Headers (base)
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.OrderingFilter',
        'rest_framework.filters.SearchFilter',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
}

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'maxBytes': 10485760,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console', 'file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}
```

#### config/settings/production.py

```python
"""Configuration production Django 6.0."""

from .base import *

DEBUG = False

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# Security
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Cookies sécurisés
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
CSRF_COOKIE_SAMESITE = 'Strict'

# Referrer Policy
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# Static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Cache
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://localhost:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL')

# Sentry (optionnel)
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=os.environ.get('SENTRY_DSN'),
    integrations=[DjangoIntegration()],
    traces_sample_rate=0.1,
    send_default_pii=True
)
```

---

## 🗄️ Models

### Bonnes Pratiques

```python
"""Models pour l'app users."""

import uuid
from datetime import datetime

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """Modèle utilisateur personnalisé.
    
    Utilise email comme identifiant principal au lieu de username.
    
    Attributes:
        id: UUID unique de l'utilisateur.
        email: Adresse email unique (identifiant).
        first_name: Prénom.
        last_name: Nom de famille.
        is_active: Statut actif du compte.
        is_staff: Accès à l'admin.
        date_joined: Date d'inscription.
        last_login: Dernière connexion.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('ID')
    )
    
    email = models.EmailField(
        _('email address'),
        unique=True,
        error_messages={
            'unique': _('Un utilisateur avec cet email existe déjà.'),
        }
    )
    
    first_name = models.CharField(
        _('first name'),
        max_length=150,
        blank=True
    )
    
    last_name = models.CharField(
        _('last name'),
        max_length=150,
        blank=True
    )
    
    phone_regex = RegexValidator(
        regex=r'^(?:(?:\+|00)33[\s.-]{0,3}(?:\(0\)[\s.-]{0,3})?|0)[1-9](?:(?:[\s.-]?\d{2}){4}|\d{2}(?:[\s.-]?\d{3}){2})$',
        message=_("Le numéro de téléphone doit être au format français.")
    )
    phone_number = models.CharField(
        _('phone number'),
        validators=[phone_regex],
        max_length=17,
        blank=True
    )
    
    avatar = models.ImageField(
        _('avatar'),
        upload_to='avatars/%Y/%m/',
        blank=True,
        null=True
    )
    
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_('Désactivez cette case au lieu de supprimer le compte.')
    )
    
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Détermine si l\'utilisateur peut accéder à l\'admin.')
    )
    
    is_verified = models.BooleanField(
        _('verified'),
        default=False,
        help_text=_('Email vérifié.')
    )
    
    date_joined = models.DateTimeField(
        _('date joined'),
        default=timezone.now
    )
    
    last_login = models.DateTimeField(
        _('last login'),
        blank=True,
        null=True
    )
    
    # Configuration
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['is_active', 'date_joined']),
        ]
    
    def __str__(self) -> str:
        """Représentation string de l'utilisateur."""
        return self.email
    
    def get_full_name(self) -> str:
        """Retourne le nom complet."""
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_short_name(self) -> str:
        """Retourne le prénom."""
        return self.first_name
    
    def activate(self) -> None:
        """Active le compte utilisateur."""
        self.is_active = True
        self.save(update_fields=['is_active'])
    
    def deactivate(self) -> None:
        """Désactive le compte utilisateur."""
        self.is_active = False
        self.save(update_fields=['is_active'])


class UserProfile(models.Model):
    """Profil étendu de l'utilisateur.
    
    One-to-One avec User pour stocker des informations supplémentaires.
    """
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name=_('user')
    )
    
    bio = models.TextField(
        _('biography'),
        max_length=500,
        blank=True
    )
    
    birth_date = models.DateField(
        _('birth date'),
        blank=True,
        null=True
    )
    
    website = models.URLField(
        _('website'),
        blank=True
    )
    
    location = models.CharField(
        _('location'),
        max_length=100,
        blank=True
    )
    
    notification_enabled = models.BooleanField(
        _('notifications enabled'),
        default=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('user profile')
        verbose_name_plural = _('user profiles')
    
    def __str__(self) -> str:
        return f"Profile de {self.user.email}"
    
    @property
    def age(self) -> int | None:
        """Calcule l'âge de l'utilisateur."""
        if not self.birth_date:
            return None
        today = datetime.today()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )


class Article(models.Model):
    """Modèle d'article de blog.
    
    Démontre les relations et les fonctionnalités avancées de Django 6.0.
    """
    
    class Status(models.TextChoices):
        """Choix de statut pour l'article."""
        DRAFT = 'draft', _('Brouillon')
        PUBLISHED = 'published', _('Publié')
        ARCHIVED = 'archived', _('Archivé')
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='articles',
        verbose_name=_('author')
    )
    
    title = models.CharField(
        _('title'),
        max_length=200,
        db_index=True
    )
    
    slug = models.SlugField(
        _('slug'),
        max_length=200,
        unique=True,
        db_index=True
    )
    
    content = models.TextField(_('content'))
    
    excerpt = models.TextField(
        _('excerpt'),
        max_length=500,
        blank=True,
        help_text=_('Résumé de l\'article. Auto-généré si vide.')
    )
    
    featured_image = models.ImageField(
        _('featured image'),
        upload_to='articles/%Y/%m/',
        blank=True,
        null=True
    )
    
    status = models.CharField(
        _('status'),
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True
    )
    
    tags = models.ManyToManyField(
        'Tag',
        related_name='articles',
        blank=True,
        verbose_name=_('tags')
    )
    
    views_count = models.PositiveIntegerField(
        _('views count'),
        default=0
    )
    
    is_featured = models.BooleanField(
        _('featured'),
        default=False,
        db_index=True
    )
    
    published_at = models.DateTimeField(
        _('published at'),
        blank=True,
        null=True,
        db_index=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('article')
        verbose_name_plural = _('articles')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'published_at']),
            models.Index(fields=['author', 'status']),
            models.Index(fields=['is_featured', 'status']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(status__in=['draft', 'published', 'archived']),
                name='valid_status'
            ),
        ]
    
    def __str__(self) -> str:
        return self.title
    
    def save(self, *args, **kwargs) -> None:
        """Sauvegarde avec génération automatique du slug et excerpt."""
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.title)
        
        if not self.excerpt and self.content:
            self.excerpt = self.content[:500] + '...' if len(self.content) > 500 else self.content
        
        if self.status == self.Status.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    def publish(self) -> None:
        """Publie l'article."""
        self.status = self.Status.PUBLISHED
        self.published_at = timezone.now()
        self.save(update_fields=['status', 'published_at'])
    
    def archive(self) -> None:
        """Archive l'article."""
        self.status = self.Status.ARCHIVED
        self.save(update_fields=['status'])
    
    @property
    def is_published(self) -> bool:
        """Vérifie si l'article est publié."""
        return self.status == self.Status.PUBLISHED
    
    @property
    def reading_time(self) -> int:
        """Estime le temps de lecture en minutes."""
        words_per_minute = 200
        word_count = len(self.content.split())
        return max(1, round(word_count / words_per_minute))


class Tag(models.Model):
    """Tags pour les articles."""
    
    name = models.CharField(
        _('name'),
        max_length=50,
        unique=True
    )
    
    slug = models.SlugField(
        _('slug'),
        max_length=50,
        unique=True
    )
    
    color = models.CharField(
        _('color'),
        max_length=7,
        default='#007bff',
        help_text=_('Code couleur HEX (ex: #007bff)')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('tag')
        verbose_name_plural = _('tags')
        ordering = ['name']
    
    def __str__(self) -> str:
        return self.name
    
    def save(self, *args, **kwargs) -> None:
        """Génère automatiquement le slug."""
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
```

### Managers Personnalisés

```python
"""Managers pour l'app users."""

from django.contrib.auth.models import BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Manager personnalisé pour le modèle User."""
    
    use_in_migrations = True
    
    def _create_user(self, email: str, password: str, **extra_fields) -> 'User':
        """Crée et sauvegarde un utilisateur avec email et password."""
        if not email:
            raise ValueError(_('L\'adresse email est obligatoire'))
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_user(self, email: str, password: str | None = None, **extra_fields) -> 'User':
        """Crée un utilisateur standard."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)
    
    def create_superuser(self, email: str, password: str | None = None, **extra_fields) -> 'User':
        """Crée un superutilisateur."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Le superutilisateur doit avoir is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Le superutilisateur doit avoir is_superuser=True.'))
        
        return self._create_user(email, password, **extra_fields)
    
    def active(self) -> models.QuerySet:
        """Retourne uniquement les utilisateurs actifs."""
        return self.filter(is_active=True)
    
    def verified(self) -> models.QuerySet:
        """Retourne uniquement les utilisateurs vérifiés."""
        return self.filter(is_verified=True, is_active=True)


class ArticleManager(models.Manager):
    """Manager personnalisé pour les articles."""
    
    def published(self) -> models.QuerySet:
        """Retourne uniquement les articles publiés."""
        from django.utils import timezone
        return self.filter(
            status='published',
            published_at__lte=timezone.now()
        )
    
    def featured(self) -> models.QuerySet:
        """Retourne les articles en vedette."""
        return self.published().filter(is_featured=True)
    
    def recent(self, count: int = 5) -> models.QuerySet:
        """Retourne les articles les plus récents."""
        return self.published().order_by('-published_at')[:count]
    
    def popular(self, count: int = 5) -> models.QuerySet:
        """Retourne les articles les plus populaires."""
        return self.published().order_by('-views_count')[:count]
    
    def by_author(self, author_id) -> models.QuerySet:
        """Retourne les articles d'un auteur spécifique."""
        return self.filter(author_id=author_id)
    
    def with_tags(self, *tag_slugs) -> models.QuerySet:
        """Retourne les articles avec certains tags."""
        return self.published().filter(tags__slug__in=tag_slugs).distinct()
    
    def search(self, query: str) -> models.QuerySet:
        """Recherche dans les articles."""
        return self.published().filter(
            models.Q(title__icontains=query) |
            models.Q(content__icontains=query) |
            models.Q(excerpt__icontains=query)
        )
```

---

## 🎨 Forms

### Bonnes Pratiques

```python
"""Forms pour l'app users."""

from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    UserCreationForm,
)
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import User, UserProfile


class UserRegistrationForm(UserCreationForm):
    """Formulaire d'inscription utilisateur."""
    
    email = forms.EmailField(
        label=_('Email'),
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('votre@email.com')
        })
    )
    
    first_name = forms.CharField(
        label=_('Prénom'),
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Votre prénom')
        })
    )
    
    last_name = forms.CharField(
        label=_('Nom'),
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Votre nom')
        })
    )
    
    password1 = forms.CharField(
        label=_('Mot de passe'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('••••••••')
        }),
        help_text=_('12 caractères minimum avec lettres, chiffres et symboles.')
    )
    
    password2 = forms.CharField(
        label=_('Confirmation du mot de passe'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('••••••••')
        })
    )
    
    accept_terms = forms.BooleanField(
        label=_('J\'accepte les conditions d\'utilisation'),
        required=True,
        error_messages={
            'required': _('Vous devez accepter les conditions pour continuer.')
        }
    )
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password1', 'password2']
    
    def clean_email(self) -> str:
        """Vérifie que l'email n'est pas déjà utilisé."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError(_('Cette adresse email est déjà utilisée.'))
        return email.lower()
    
    def save(self, commit: bool = True) -> User:
        """Sauvegarde l'utilisateur."""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email'].lower()
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
        
        return user


class UserLoginForm(AuthenticationForm):
    """Formulaire de connexion."""
    
    username = forms.EmailField(
        label=_('Email'),
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('votre@email.com'),
            'autofocus': True
        })
    )
    
    password = forms.CharField(
        label=_('Mot de passe'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('••••••••')
        })
    )
    
    remember_me = forms.BooleanField(
        label=_('Se souvenir de moi'),
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


class UserUpdateForm(forms.ModelForm):
    """Formulaire de mise à jour du profil."""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'avatar']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def clean_email(self) -> str:
        """Vérifie que le nouvel email n'est pas déjà utilisé."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError(_('Cette adresse email est déjà utilisée.'))
        return email.lower()


class UserProfileForm(forms.ModelForm):
    """Formulaire du profil étendu."""
    
    class Meta:
        model = UserProfile
        fields = ['bio', 'birth_date', 'website', 'location', 'notification_enabled']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': _('Parlez-nous de vous...')
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': _('https://votresite.com')
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Paris, France')
            }),
            'notification_enabled': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class ArticleForm(forms.ModelForm):
    """Formulaire de création/édition d'article."""
    
    tags = forms.CharField(
        label=_('Tags'),
        required=False,
        help_text=_('Séparez les tags par des virgules'),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('python, django, tutoriel')
        })
    )
    
    class Meta:
        model = Article
        fields = ['title', 'content', 'excerpt', 'featured_image', 'status', 'is_featured', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Titre de l\'article')
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control editor',
                'rows': 20,
                'placeholder': _('Contenu de l\'article...')
            }),
            'excerpt': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Résumé de l\'article (optionnel)')
            }),
            'featured_image': forms.FileInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, user=None, **kwargs):
        """Initialise le formulaire avec l'utilisateur courant."""
        self.user = user
        super().__init__(*args, **kwargs)
        
        # Si c'est une édition, pré-remplir les tags
        if self.instance.pk:
            self.fields['tags'].initial = ', '.join(
                tag.name for tag in self.instance.tags.all()
            )
    
    def clean_tags(self) -> list:
        """Parse et valide les tags."""
        tags_str = self.cleaned_data.get('tags', '')
        if not tags_str:
            return []
        
        tags = [tag.strip().lower() for tag in tags_str.split(',') if tag.strip()]
        
        # Limite de 10 tags
        if len(tags) > 10:
            raise ValidationError(_('Maximum 10 tags autorisés.'))
        
        # Validation de la longueur
        for tag in tags:
            if len(tag) > 50:
                raise ValidationError(_('Chaque tag doit faire moins de 50 caractères.'))
        
        return tags
    
    def save(self, commit: bool = True) -> Article:
        """Sauvegarde l'article et les tags."""
        article = super().save(commit=False)
        
        if self.user:
            article.author = self.user
        
        if commit:
            article.save()
            self.save_tags(article)
        
        return article
    
    def save_tags(self, article: Article) -> None:
        """Sauvegarde les tags associés."""
        from .models import Tag
        
        tags_names = self.cleaned_data.get('tags', [])
        tags = []
        
        for tag_name in tags_names:
            tag, created = Tag.objects.get_or_create(
                name=tag_name,
                defaults={'slug': tag_name.replace(' ', '-')}
            )
            tags.append(tag)
        
        article.tags.set(tags)
```

---

## 👁️ Views

### Class-Based Views (CBV)

```python
"""Views pour l'app blog."""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import ArticleForm
from .models import Article, Tag


class ArticleListView(ListView):
    """Liste des articles publiés avec pagination et filtres."""
    
    model = Article
    template_name = 'blog/article_list.html'
    context_object_name = 'articles'
    paginate_by = 10
    ordering = ['-published_at']
    
    def get_queryset(self):
        """Filtre les articles publiés avec options de recherche."""
        queryset = Article.objects.published().select_related('author').prefetch_related('tags')
        
        # Filtre par tag
        tag_slug = self.request.GET.get('tag')
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)
        
        # Filtre par auteur
        author_id = self.request.GET.get('author')
        if author_id:
            queryset = queryset.filter(author_id=author_id)
        
        # Recherche
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(excerpt__icontains=query)
            )
        
        return queryset.distinct()
    
    def get_context_data(self, **kwargs):
        """Ajoute des données contextuelles."""
        context = super().get_context_data(**kwargs)
        
        # Tags populaires
        context['popular_tags'] = Tag.objects.annotate(
            article_count=Count('articles')
        ).order_by('-article_count')[:10]
        
        # Articles en vedette
        context['featured_articles'] = Article.objects.featured()[:3]
        
        # Paramètres de recherche actuels
        context['current_tag'] = self.request.GET.get('tag')
        context['search_query'] = self.request.GET.get('q')
        
        return context


class ArticleDetailView(DetailView):
    """Détail d'un article avec incrémentation des vues."""
    
    model = Article
    template_name = 'blog/article_detail.html'
    context_object_name = 'article'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        """Optimise les requêtes."""
        return Article.objects.select_related('author').prefetch_related('tags')
    
    def get_object(self, queryset=None):
        """Récupère l'article et incrémente les vues."""
        obj = super().get_object(queryset)
        
        # Incrémente les vues (sauf pour l'auteur)
        if self.request.user != obj.author:
            obj.views_count += 1
            obj.save(update_fields=['views_count'])
        
        return obj
    
    def get_context_data(self, **kwargs):
        """Ajoute des articles similaires."""
        context = super().get_context_data(**kwargs)
        article = self.get_object()
        
        # Articles similaires (mêmes tags)
        similar_articles = Article.objects.published().filter(
            tags__in=article.tags.all()
        ).exclude(id=article.id).distinct()[:3]
        
        context['similar_articles'] = similar_articles
        context['reading_time'] = article.reading_time
        
        return context


class ArticleCreateView(LoginRequiredMixin, CreateView):
    """Création d'un nouvel article."""
    
    model = Article
    form_class = ArticleForm
    template_name = 'blog/article_form.html'
    
    def get_form_kwargs(self):
        """Passe l'utilisateur au formulaire."""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        """Gère la soumission réussie."""
        response = super().form_valid(form)
        messages.success(
            self.request,
            _('Article "%(title)s" créé avec succès.') % {'title': self.object.title}
        )
        return response
    
    def get_success_url(self):
        """Redirige vers le détail de l'article."""
        return reverse('blog:article_detail', kwargs={'slug': self.object.slug})


class ArticleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Modification d'un article existant."""
    
    model = Article
    form_class = ArticleForm
    template_name = 'blog/article_form.html'
    slug_url_kwarg = 'slug'
    
    def test_func(self):
        """Vérifie que l'utilisateur est l'auteur ou un staff."""
        article = self.get_object()
        return self.request.user == article.author or self.request.user.is_staff
    
    def get_form_kwargs(self):
        """Passe l'utilisateur au formulaire."""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        """Gère la mise à jour."""
        response = super().form_valid(form)
        messages.success(
            self.request,
            _('Article "%(title)s" mis à jour avec succès.') % {'title': self.object.title}
        )
        return response
    
    def get_success_url(self):
        """Redirige vers le détail de l'article."""
        return reverse('blog:article_detail', kwargs={'slug': self.object.slug})


class ArticleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Suppression d'un article."""
    
    model = Article
    template_name = 'blog/article_confirm_delete.html'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('blog:article_list')
    
    def test_func(self):
        """Vérifie que l'utilisateur est l'auteur ou un staff."""
        article = self.get_object()
        return self.request.user == article.author or self.request.user.is_staff
    
    def delete(self, request, *args, **kwargs):
        """Gère la suppression avec message."""
        article = self.get_object()
        messages.success(
            request,
            _('Article "%(title)s" supprimé avec succès.') % {'title': article.title}
        )
        return super().delete(request, *args, **kwargs)


class ArticlePublishView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Publication d'un article (action rapide)."""
    
    model = Article
    fields = []
    http_method_names = ['post']
    
    def test_func(self):
        """Vérifie les permissions."""
        article = self.get_object()
        return self.request.user == article.author or self.request.user.is_staff
    
    def post(self, request, *args, **kwargs):
        """Publie l'article."""
        article = self.get_object()
        article.publish()
        messages.success(request, _('Article publié avec succès.'))
        return redirect('blog:article_detail', slug=article.slug)
```

### Function-Based Views (FBV)

```python
"""Function-based views pour l'app users."""

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

from .forms import (
    UserLoginForm,
    UserProfileForm,
    UserRegistrationForm,
    UserUpdateForm,
)
from .models import User, UserProfile


def register_view(request):
    """Gère l'inscription des utilisateurs."""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Crée automatiquement le profil
            UserProfile.objects.create(user=user)
            
            # Envoie l'email de vérification (à implémenter)
            # send_verification_email(user)
            
            messages.success(
                request,
                _('Compte créé avec succès ! Vérifiez votre email pour activer votre compte.')
            )
            return redirect('users:login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    """Gère la connexion des utilisateurs."""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me')
            
            user = authenticate(request, email=email, password=password)
            
            if user is not None:
                login(request, user)
                
                # Gère "Se souvenir de moi"
                if not remember_me:
                    request.session.set_expiry(0)
                
                messages.success(request, _('Bienvenue, %(name)s !') % {'name': user.first_name})
                
                # Redirige vers la page demandée ou l'accueil
                next_url = request.GET.get('next')
                return redirect(next_url or 'home')
            else:
                messages.error(request, _('Email ou mot de passe incorrect.'))
    else:
        form = UserLoginForm()
    
    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    """Gère la déconnexion."""
    logout(request)
    messages.info(request, _('Vous avez été déconnecté.'))
    return redirect('home')


@login_required
def profile_view(request):
    """Affiche le profil de l'utilisateur connecté."""
    user = request.user
    
    # Récupère ou crée le profil
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    context = {
        'user': user,
        'profile': profile,
        'articles_count': user.articles.filter(status='published').count(),
    }
    
    return render(request, 'users/profile.html', context)


@login_required
def profile_edit_view(request):
    """Permet de modifier le profil."""
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, request.FILES, instance=user)
        profile_form = UserProfileForm(request.POST, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, _('Profil mis à jour avec succès.'))
            return redirect('users:profile')
    else:
        user_form = UserUpdateForm(instance=user)
        profile_form = UserProfileForm(instance=profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    
    return render(request, 'users/profile_edit.html', context)


def user_detail_view(request, username):
    """Affiche le profil public d'un utilisateur."""
    user = get_object_or_404(User, username=username, is_active=True)
    
    # Récupère les articles publiés de l'utilisateur
    articles = user.articles.published()[:5]
    
    context = {
        'profile_user': user,
        'articles': articles,
    }
    
    return render(request, 'users/user_detail.html', context)
```

---

## 🔗 URLs

### Configuration

```python
"""URLs principales du projet."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Apps
    path('', include('apps.blog.urls', namespace='blog')),
    path('auth/', include('apps.users.urls', namespace='users')),
    path('api/', include('apps.api.urls', namespace='api')),
    
    # Auth Django (password reset, etc.)
    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='users/password_reset.html'
        ),
        name='password_reset'
    ),
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='users/password_reset_done.html'
        ),
        name='password_reset_done'
    ),
    path(
        'password-reset-confirm/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='users/password_reset_confirm.html'
        ),
        name='password_reset_confirm'
    ),
    path(
        'password-reset-complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='users/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
]

# Static et Media en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug Toolbar
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
```

```python
"""URLs pour l'app blog."""

from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    # Article views
    path('', views.ArticleListView.as_view(), name='article_list'),
    path('article/<slug:slug>/', views.ArticleDetailView.as_view(), name='article_detail'),
    path('article/create/', views.ArticleCreateView.as_view(), name='article_create'),
    path('article/<slug:slug>/edit/', views.ArticleUpdateView.as_view(), name='article_edit'),
    path('article/<slug:slug>/delete/', views.ArticleDeleteView.as_view(), name='article_delete'),
    path('article/<slug:slug>/publish/', views.ArticlePublishView.as_view(), name='article_publish'),
    
    # Tag views
    path('tag/<slug:slug>/', views.ArticleListView.as_view(), name='articles_by_tag'),
]
```

---

## 🎛️ Admin

### Configuration Avancée

```python
"""Configuration de l'admin Django."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Article, Tag, User, UserProfile


class UserProfileInline(admin.StackedInline):
    """Inline pour le profil utilisateur."""
    model = UserProfile
    can_delete = False
    verbose_name_plural = _('Profil')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Configuration de l'admin pour User."""
    
    inlines = (UserProfileInline,)
    
    list_display = [
        'email',
        'first_name',
        'last_name',
        'is_active',
        'is_staff',
        'is_verified',
        'date_joined',
        'avatar_preview',
    ]
    
    list_filter = [
        'is_active',
        'is_staff',
        'is_verified',
        'date_joined',
    ]
    
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Informations personnelles'), {
            'fields': ('first_name', 'last_name', 'phone_number', 'avatar')
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Statut'), {
            'fields': ('is_verified', 'last_login', 'date_joined'),
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ['last_login', 'date_joined']
    
    def avatar_preview(self, obj):
        """Affiche un aperçu de l'avatar."""
        if obj.avatar:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; border-radius: 50%;" />',
                obj.avatar.url
            )
        return _('Pas d\'avatar')
    
    avatar_preview.short_description = _('Avatar')
    
    actions = ['activate_users', 'deactivate_users', 'verify_users']
    
    @admin.action(description=_('Activer les utilisateurs sélectionnés'))
    def activate_users(self, request, queryset):
        """Active les utilisateurs sélectionnés."""
        queryset.update(is_active=True)
    
    @admin.action(description=_('Désactiver les utilisateurs sélectionnés'))
    def deactivate_users(self, request, queryset):
        """Désactive les utilisateurs sélectionnés."""
        queryset.update(is_active=False)
    
    @admin.action(description=_('Vérifier les utilisateurs sélectionnés'))
    def verify_users(self, request, queryset):
        """Vérifie les utilisateurs sélectionnés."""
        queryset.update(is_verified=True)


class ArticleTagsInline(admin.TabularInline):
    """Inline pour les tags d'un article."""
    model = Article.tags.through
    extra = 1


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """Configuration de l'admin pour Article."""
    
    inlines = [ArticleTagsInline]
    
    list_display = [
        'title',
        'author',
        'status',
        'is_featured',
        'views_count',
        'published_at',
        'created_at',
    ]
    
    list_filter = [
        'status',
        'is_featured',
        'created_at',
        'published_at',
    ]
    
    search_fields = ['title', 'content', 'author__email']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_at'
    ordering = ['-created_at']
    
    fieldsets = (
        (_('Contenu'), {
            'fields': ('title', 'slug', 'content', 'excerpt')
        }),
        (_('Média'), {
            'fields': ('featured_image',),
            'classes': ('collapse',),
        }),
        (_('Publication'), {
            'fields': ('author', 'status', 'is_featured', 'published_at')
        }),
        (_('Statistiques'), {
            'fields': ('views_count',),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ['views_count']
    
    actions = ['publish_articles', 'unpublish_articles', 'feature_articles']
    
    @admin.action(description=_('Publier les articles sélectionnés'))
    def publish_articles(self, request, queryset):
        """Publie les articles sélectionnés."""
        from django.utils import timezone
        queryset.update(status='published', published_at=timezone.now())
    
    @admin.action(description=_('Dépublier les articles sélectionnés'))
    def unpublish_articles(self, request, queryset):
        """Dépublie les articles sélectionnés."""
        queryset.update(status='draft', published_at=None)
    
    @admin.action(description=_('Mettre en vedette les articles sélectionnés'))
    def feature_articles(self, request, queryset):
        """Met en vedette les articles sélectionnés."""
        queryset.update(is_featured=True)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Configuration de l'admin pour Tag."""
    
    list_display = ['name', 'slug', 'article_count', 'color_preview']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    
    def article_count(self, obj):
        """Compte les articles associés."""
        return obj.articles.count()
    
    article_count.short_description = _('Nombre d\'articles')
    
    def color_preview(self, obj):
        """Affiche un aperçu de la couleur."""
        return format_html(
            '<div style="width: 30px; height: 30px; background-color: {}; border-radius: 4px;"></div>',
            obj.color
        )
    
    color_preview.short_description = _('Couleur')


# Personnalisation de l'admin
admin.site.site_header = _('Administration Mon Projet')
admin.site.site_title = _('Mon Projet Admin')
admin.site.index_title = _('Tableau de bord')
```

---

## 🧪 Tests

### Configuration

```python
"""Configuration des tests."""

# pytest.ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings.test
python_files = tests.py test_*.py *_tests.py
addopts = -v --tb=short --strict-markers
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests

# conftest.py
import pytest
from django.test import Client

from apps.users.models import User


@pytest.fixture
def client():
    """Fixture pour le client de test."""
    return Client()


@pytest.fixture
def user(db):
    """Fixture pour un utilisateur de test."""
    return User.objects.create_user(
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )


@pytest.fixture
def admin_user(db):
    """Fixture pour un admin de test."""
    return User.objects.create_superuser(
        email='admin@example.com',
        password='adminpass123'
    )


@pytest.fixture
def authenticated_client(client, user):
    """Fixture pour un client authentifié."""
    client.force_login(user)
    return client
```

### Tests des Models

```python
"""Tests pour les models."""

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.blog.models import Article, Tag
from apps.users.models import User


@pytest.mark.django_db
class TestUserModel:
    """Tests pour le modèle User."""
    
    def test_user_creation(self):
        """Test la création d'un utilisateur."""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        
        assert user.email == 'test@example.com'
        assert user.first_name == 'John'
        assert user.last_name == 'Doe'
        assert user.is_active is True
        assert user.is_staff is False
        assert user.check_password('testpass123')
    
    def test_user_str(self, user):
        """Test la représentation string."""
        assert str(user) == user.email
    
    def test_get_full_name(self, user):
        """Test le nom complet."""
        assert user.get_full_name() == 'Test User'
    
    def test_email_normalization(self):
        """Test la normalisation de l'email."""
        user = User.objects.create_user(
            email='TEST@EXAMPLE.COM',
            password='testpass123'
        )
        assert user.email == 'test@example.com'
    
    def test_duplicate_email(self, user):
        """Test l'unicité de l'email."""
        with pytest.raises(Exception):  # IntegrityError
            User.objects.create_user(
                email='test@example.com',
                password='testpass123'
            )


@pytest.mark.django_db
class TestArticleModel:
    """Tests pour le modèle Article."""
    
    def test_article_creation(self, user):
        """Test la création d'un article."""
        article = Article.objects.create(
            title='Test Article',
            content='This is a test article.',
            author=user,
            status=Article.Status.PUBLISHED
        )
        
        assert article.title == 'Test Article'
        assert article.author == user
        assert article.status == Article.Status.PUBLISHED
        assert article.slug == 'test-article'
    
    def test_article_slug_generation(self, user):
        """Test la génération automatique du slug."""
        article = Article.objects.create(
            title='Mon Super Article!',
            content='Content',
            author=user
        )
        
        assert article.slug == 'mon-super-article'
    
    def test_article_publish(self, user):
        """Test la publication d'un article."""
        article = Article.objects.create(
            title='Draft Article',
            content='Content',
            author=user,
            status=Article.Status.DRAFT
        )
        
        article.publish()
        
        assert article.status == Article.Status.PUBLISHED
        assert article.published_at is not None
    
    def test_article_reading_time(self, user):
        """Test le calcul du temps de lecture."""
        content = 'Word ' * 400  # 400 words = 2 minutes
        article = Article.objects.create(
            title='Long Article',
            content=content,
            author=user
        )
        
        assert article.reading_time == 2
```

### Tests des Views

```python
"""Tests pour les views."""

import pytest
from django.urls import reverse

from apps.blog.models import Article


@pytest.mark.django_db
class TestArticleViews:
    """Tests pour les views d'articles."""
    
    def test_article_list_view(self, client):
        """Test la liste des articles."""
        response = client.get(reverse('blog:article_list'))
        
        assert response.status_code == 200
        assert 'articles' in response.context
    
    def test_article_detail_view(self, client, user):
        """Test le détail d'un article."""
        article = Article.objects.create(
            title='Test Article',
            content='Content',
            author=user,
            status=Article.Status.PUBLISHED
        )
        
        response = client.get(
            reverse('blog:article_detail', kwargs={'slug': article.slug})
        )
        
        assert response.status_code == 200
        assert response.context['article'] == article
    
    def test_article_create_view_requires_login(self, client):
        """Test que la création nécessite une connexion."""
        response = client.get(reverse('blog:article_create'))
        
        assert response.status_code == 302  # Redirect to login
    
    def test_article_create_view_authenticated(self, authenticated_client, user):
        """Test la création d'article authentifié."""
        data = {
            'title': 'New Article',
            'content': 'Article content',
            'status': 'draft',
        }
        
        response = authenticated_client.post(
            reverse('blog:article_create'),
            data
        )
        
        assert response.status_code == 302  # Redirect after success
        assert Article.objects.filter(title='New Article').exists()
```

### Tests des Forms

```python
"""Tests pour les forms."""

import pytest

from apps.users.forms import UserRegistrationForm
from apps.users.models import User


@pytest.mark.django_db
class TestUserRegistrationForm:
    """Tests pour le formulaire d'inscription."""
    
    def test_valid_registration(self):
        """Test une inscription valide."""
        data = {
            'email': 'new@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password1': 'strongpassword123',
            'password2': 'strongpassword123',
            'accept_terms': True,
        }
        
        form = UserRegistrationForm(data=data)
        
        assert form.is_valid()
    
    def test_duplicate_email(self, user):
        """Test l'erreur email dupliqué."""
        data = {
            'email': 'test@example.com',  # Already exists
            'first_name': 'John',
            'last_name': 'Doe',
            'password1': 'strongpassword123',
            'password2': 'strongpassword123',
            'accept_terms': True,
        }
        
        form = UserRegistrationForm(data=data)
        
        assert not form.is_valid()
        assert 'email' in form.errors
    
    def test_password_mismatch(self):
        """Test l'erreur de mot de passe différent."""
        data = {
            'email': 'new@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password1': 'password123',
            'password2': 'differentpassword',
            'accept_terms': True,
        }
        
        form = UserRegistrationForm(data=data)
        
        assert not form.is_valid()
        assert 'password2' in form.errors
    
    def test_terms_not_accepted(self):
        """Test l'erreur conditions non acceptées."""
        data = {
            'email': 'new@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password1': 'strongpassword123',
            'password2': 'strongpassword123',
            'accept_terms': False,
        }
        
        form = UserRegistrationForm(data=data)
        
        assert not form.is_valid()
        assert 'accept_terms' in form.errors
```

---

## 📊 Checklist Pré-Création de Fichier Django

Avant de créer ou modifier un fichier Django, vérifier :

### Models
- [ ] ✅ Hérite de `models.Model` ou classes abstraites appropriées
- [ ] ✅ Utilise `UUIDField` pour les IDs (recommandé)
- [ ] ✅ Définit `verbose_name` et `verbose_name_plural`
- [ ] ✅ Ajoute des `db_index` sur les champs fréquemment filtrés
- [ ] ✅ Utilise `related_name` pour les ForeignKey et ManyToMany
- [ ] ✅ Implémente `__str__` pour tous les models
- [ ] ✅ Utilise `get_user_model()` pour les références utilisateur
- [ ] ✅ Ajoute des contraintes (`CheckConstraint`, `UniqueConstraint`)
- [ ] ✅ Utilise `TextChoices` pour les enums
- [ ] ✅ Implémente `save()` si logique métier nécessaire
- [ ] ✅ Crée un Manager personnalisé si besoin
- [ ] ✅ Ajoute des propriétés (`@property`) pour les calculs

### Forms
- [ ] ✅ Hérite de `ModelForm` ou `Form` approprié
- [ ] ✅ Définit `Meta` avec `model` et `fields` explicites
- [ ] ✅ Utilise des widgets personnalisés avec classes CSS
- [ ] ✅ Implémente `clean_<field>()` pour validation custom
- [ ] ✅ Implémente `clean()` pour validation multi-champs
- [ ] ✅ Utilise `save()` avec `commit=False` si nécessaire
- [ ] ✅ Ajoute des messages d'erreur traduits (`gettext_lazy`)

### Views
- [ ] ✅ Utilise Class-Based Views quand possible
- [ ] ✅ Hérite de mixins appropriés (`LoginRequiredMixin`, etc.)
- [ ] ✅ Implémente `get_queryset()` avec `select_related`/`prefetch_related`
- [ ] ✅ Utilise `get_context_data()` pour données additionnelles
- [ ] ✅ Définit `success_url` ou `get_success_url()`
- [ ] ✅ Ajoute des messages avec `django.contrib.messages`
- [ ] ✅ Gère les permissions avec `test_func()` ou `permission_required`

### Templates
- [ ] ✅ Étend `base.html` ou template parent approprié
- [ ] ✅ Utilise `{% load %}` pour les tags/filters nécessaires
- [ ] ✅ Utilise `{% url %}` pour les liens (pas d'URLs en dur)
- [ ] ✅ Échappe les variables avec `{{ variable|escape }}`
- [ ] ✅ Utilise `{% csrf_token %}` dans tous les formulaires
- [ ] ✅ Ajoute `{% block %}` pour contenu personnalisable
- [ ] ✅ Utilise `{% trans %}` pour le texte traduisible

### URLs
- [ ] ✅ Utilise `app_name` pour les URLs namespacing
- [ ] ✅ Définit des noms descriptifs pour les patterns
- [ ] ✅ Utilise des paramètres typés (`<int:pk>`, `<slug:slug>`)
- [ ] ✅ Organise les URLs par fonctionnalité

### Admin
- [ ] ✅ Enregistre les models avec `@admin.register()`
- [ ] ✅ Définit `list_display`, `list_filter`, `search_fields`
- [ ] ✅ Utilise `prepopulated_fields` pour les slugs
- [ ] ✅ Crée des `inlines` pour relations one-to-one/many
- [ ] ✅ Ajoute des `actions` personnalisées
- [ ] ✅ Utilise `readonly_fields` pour champs calculés

### Tests
- [ ] ✅ Utilise `pytest` avec `pytest-django`
- [ ] ✅ Crée des fixtures réutilisables
- [ ] ✅ Teste les cas positifs et négatifs
- [ ] ✅ Utilise `pytest.mark.django_db` pour les tests DB
- [ ] ✅ Teste les permissions et authentification
- [ ] ✅ Vérifie les messages flash

---

## 📚 Ressources

- [Django 6.0 Documentation](https://docs.djangoproject.com/en/6.0/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Django Best Practices](https://django-best-practices.readthedocs.io/)
- [Two Scoops of Django](https://www.feldroy.com/books/two-scoops-of-django-3-x)
- [Django Testing Docs](https://docs.djangoproject.com/en/6.0/topics/testing/)
- [Django Security Checklist](https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/)

---

**Dernière mise à jour** : 2024-01-15  
**Version** : 6.0.0  
**Auteur** : Équipe Développement Django
