# Security Policy

## 🔒 Politique de Sécurité

Ce document décrit les mesures de sécurité mises en place dans ce projet et comment signaler les vulnérabilités.

## Versions Supportées

| Version | Supportée          |
| ------- | ------------------ |
| 1.1.x   | :white_check_mark: |
| 1.0.x   | :x:                |

## 🛡️ Mesures de Sécurité Implémentées

### 1. Protection contre les attaques XSS

Toutes les entrées utilisateur sont échappées avant affichage :

```django
{# ✅ Correct #}
{{ user_input|escape }}
{{ comment|escape|linebreaksbr }}
{{ event.description|striptags|linebreaks }}

{# ❌ À éviter #}
{{ user_input|safe }}
```

### 2. Protection CSRF

- Protection CSRF activée par défaut sur tous les formulaires
- Tokens CSRF validés automatiquement par Django

### 3. SQL Injection

- Utilisation exclusive de l'ORM Django
- Aucune requête SQL brute avec concaténation
- Paramètres de requête validés et échappés

### 4. Rate Limiting

Protection contre les attaques par force brute :

| Endpoint | Limite | Fenêtre |
|----------|--------|---------|
| `notification_mark_read` | 10 requêtes | 1 minute |
| `notification_mark_all_read` | 5 requêtes | 1 minute |

### 5. Authentification et Autorisation

- Authentification obligatoire pour les vues sensibles (`@login_required`)
- Vérification des permissions par rôle (`UserPassesTestMixin`)
- Mots de passe hashés avec bcrypt (via Django)

### 6. Headers de Sécurité

Configuration recommandée pour `settings.py` :

```python
# HTTPS
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Cookies
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# Protection XSS
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Referrer Policy
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
```

### 7. Gestion des Fichiers

- Validation des extensions de fichiers
- Validation de la taille des fichiers
- Stockage sécurisé des fichiers uploadés
- Pas d'exécution de fichiers uploadés

### 8. Protection des Données Sensibles

- `SECRET_KEY` chargée depuis les variables d'environnement
- Aucun mot de passe ou clé API en dur dans le code
- Utilisation de `.env` pour la configuration locale

## 🚨 Signalement de Vulnérabilités

Si vous découvrez une vulnérabilité de sécurité, veuillez :

1. **Ne pas** créer une issue publique
2. Envoyer un email à : security@ccsa.fr
3. Inclure :
   - Description détaillée de la vulnérabilité
   - Étapes pour reproduire
   - Impact potentiel
   - Suggestions de correction (optionnel)

## 🔍 Audit de Sécurité

### Outils Utilisés

- **Bandit** : Analyse statique de code Python
- **Safety** : Scan des dépendances
- **Django Security Check** : Vérifications Django
- **Pip-audit** : Audit PyPI

### Exécution des Audits

```bash
# Audit complet
python scripts/security-audit.py

# Bandit uniquement
bandit -r . -x ./tests,./migrations,./venv -f json

# Safety
safety check

# Django
python manage.py check --deploy
```

## 📋 Checklist de Sécurité Pré-Déploiement

- [ ] Variables sensibles dans `.env` (pas dans le code)
- [ ] `DEBUG = False` en production
- [ ] `ALLOWED_HOSTS` configuré
- [ ] Headers de sécurité activés
- [ ] HTTPS forcé
- [ ] Audit de sécurité passé sans erreur CRITICAL/HIGH
- [ ] Tests de sécurité passés
- [ ] Dépendances à jour (`pip-audit`)

## 🛠️ Bonnes Pratiques pour les Développeurs

### Templates

```django
{# Toujours échapper les données utilisateur #}
{{ user_input|escape }}

# Utiliser striptags pour le HTML riche
{{ description|striptags|linebreaks }}

# Utiliser escapejs pour le JavaScript
{{ json_data|escapejs }}
```

### Vues

```python
# Toujours vérifier l'authentification
@login_required
def my_view(request):
    pass

# Valider les entrées utilisateur
try:
    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
except ValueError:
    return HttpResponseBadRequest("Invalid date")

# Utiliser transaction.atomic pour les opérations multiples
from django.db import transaction

with transaction.atomic():
    # opérations database
    pass
```

### Modèles

```python
# Utiliser des validators
from django.core.validators import validate_email

class MyModel(models.Model):
    email = models.EmailField(validators=[validate_email])
```

## 📚 Ressources

- [Django Security Documentation](https://docs.djangoproject.com/en/stable/topics/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Bandit Documentation](https://bandit.readthedocs.io/)
- [Mozilla Web Security Guidelines](https://infosec.mozilla.org/guidelines/web_security)

---

**Dernière mise à jour** : 2026-02-09  
**Version** : 1.1.0
