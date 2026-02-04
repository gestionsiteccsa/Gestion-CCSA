# Skill de Sécurité - Audit Complet du Projet

## 🎯 Objectif

Ce skill permet de réaliser un audit de sécurité complet du projet Django/Python/JavaScript. **Il doit être exécuté obligatoirement avant chaque mise en production ou merge de feature.**

## ⚠️ Règle d'Or

> **AUCUNE feature ne peut être mergée tant que ce skill n'a pas été exécuté et validé.**

## 📋 Prérequis

### Installation des outils de sécurité

```bash
# Outils Python
pip install bandit safety pip-audit semgrep pylint-security

# Outils Django
pip install django-security django-csp django-defender django-cors-headers

# Outils de détection de secrets
pip install detect-pre-commit-hooks truffleHog3

# Outils JavaScript (si package.json existe)
npm install -g eslint eslint-plugin-security retire
```

## 🔍 Scans de Sécurité

### 1. Scan Python - Analyse Statique

#### Bandit (Analyse de code Python)
```bash
# Scan basique
bandit -r . -f json -o bandit-report.json

# Scan avec niveau de sévérité HIGH et CRITICAL uniquement
bandit -r . -ll -ii -f json -o bandit-report.json

# Exclusion des tests et migrations
bandit -r . -x ./tests,./migrations,./env,./venv -f json -o bandit-report.json
```

**Problèmes détectés :**
- Utilisation de `eval()` ou `exec()`
- Injection SQL
- Hardcoded passwords
- Utilisation de pickle sur des données non fiables
- Protocoles réseau non sécurisés

#### Semgrep (Analyse avancée)
```bash
# Scan avec règles de sécurité OWASP
semgrep --config=auto --json -o semgrep-report.json

# Scan avec règles spécifiques Python/Django
semgrep --config=p/python --config=p/django --json -o semgrep-report.json

# Scan avec règles de sécurité
semgrep --config=p/security-audit --json -o semgrep-report.json
```

#### Pylint Security
```bash
pylint --load-plugins=pylint_security --output-format=json > pylint-security-report.json
```

### 2. Scan Django - Configuration et Bonnes Pratiques

#### Django Security Check
```bash
python manage.py check --deploy
```

#### Vérifications manuelles obligatoires

**Fichier : `settings.py`**

```python
# ✅ CORRECT
DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY')  # Jamais en dur !
ALLOWED_HOSTS = ['votredomaine.com', 'www.votredomaine.com']

# ❌ INCORRECT - Bloquant
DEBUG = True
SECRET_KEY = "django-insecure-..."  # En dur dans le code
ALLOWED_HOSTS = []  # ou ['*']
```

**Checklist Django Security :**

- [ ] `DEBUG = False` en production
- [ ] `SECRET_KEY` chargé depuis les variables d'environnement
- [ ] `ALLOWED_HOSTS` configuré avec les domaines spécifiques
- [ ] HTTPS forcé (`SECURE_SSL_REDIRECT = True`)
- [ ] HSTS activé (`SECURE_HSTS_SECONDS = 31536000`)
- [ ] Cookies sécurisés (`SESSION_COOKIE_SECURE = True`, `CSRF_COOKIE_SECURE = True`)
- [ ] XSS Protection (`SECURE_BROWSER_XSS_FILTER = True`)
- [ ] Content Type nosniff (`SECURE_CONTENT_TYPE_NOSNIFF = True`)
- [ ] Referrer Policy (`SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'`)
- [ ] CSP (Content Security Policy) configuré
- [ ] X-Frame-Options activé (`X_FRAME_OPTIONS = 'DENY'`)
- [ ] CSRF middleware présent
- [ ] Authentication middleware présent
- [ ] Password validators configurés
- [ ] Database credentials en variables d'environnement

#### Configuration CSP (Content Security Policy)

```python
# settings.py
INSTALLED_APPS = [
    ...
    'csp',
]

MIDDLEWARE = [
    ...
    'csp.middleware.CSPMiddleware',
    ...
]

# CSP Configuration
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'")  # Éviter 'unsafe-inline' si possible
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
CSP_IMG_SRC = ("'self'", "data:", "https:")
CSP_FONT_SRC = ("'self'", "https:", "data:")
CSP_CONNECT_SRC = ("'self'",)
CSP_FRAME_ANCESTORS = ("'none'",)
CSP_FORM_ACTION = ("'self'",)
```

### 3. Scan des Dépendances

#### Safety (Vulnérabilités connues)
```bash
# Scan des dépendances installées
safety check --json --output safety-report.json

# Scan avec full report
safety check --full-report --json --output safety-report.json
```

#### Pip-audit (Audit PyPI)
```bash
# Scan basique
pip-audit --format=json --output=pip-audit-report.json

# Scan avec description des vulnérabilités
pip-audit --desc --format=json --output=pip-audit-report.json

# Scan requirements.txt
pip-audit -r requirements.txt --format=json --output=pip-audit-report.json
```

#### Génération du fichier requirements.txt
```bash
pip freeze > requirements.txt
```

### 4. Scan des Secrets

#### Detect-secrets
```bash
# Initialisation du baseline
detect-secrets scan --all-files --baseline .secrets.baseline

# Scan avec le baseline
detect-secrets scan --baseline .secrets.baseline --all-files

# Audit des secrets trouvés
detect-secrets audit .secrets.baseline
```

#### TruffleHog3
```bash
# Scan du repo Git
truffleHog3 --json --output trufflehog-report.json .

# Scan avec règles personnalisées
truffleHog3 --config .truffleHog3.yml --json --output trufflehog-report.json .
```

#### Git-secrets
```bash
# Installation des hooks
git secrets --install

# Scan de l'historique
git secrets --scan-history

# Scan du working directory
git secrets --scan
```

**Secrets à détecter :**
- Clés API (AWS, Google, Azure, etc.)
- Tokens d'accès
- Mots de passe en dur
- Clés privées (SSH, RSA, etc.)
- Database credentials
- Secrets Django
- Tokens JWT

### 5. Scan JavaScript (si applicable)

#### NPM Audit
```bash
# Scan des vulnérabilités
npm audit --json > npm-audit-report.json

# Scan avec niveau de sévérité
npm audit --audit-level=high --json > npm-audit-report.json

# Fix automatique (si possible)
npm audit fix
```

#### ESLint Security
```bash
# Configuration ESLint avec plugin security
# .eslintrc.json
{
  "plugins": ["security"],
  "extends": ["plugin:security/recommended"],
  "rules": {
    "security/detect-object-injection": "error",
    "security/detect-non-literal-regexp": "error",
    "security/detect-unsafe-regex": "error",
    "security/detect-buffer-noassert": "error",
    "security/detect-eval-with-expression": "error",
    "security/detect-no-csrf-before-method-override": "error",
    "security/detect-non-literal-fs-filename": "error",
    "security/detect-non-literal-require": "error",
    "security/detect-possible-timing-attacks": "error",
    "security/detect-pseudoRandomBytes": "error"
  }
}

# Exécution
eslint . --format json --output-file eslint-security-report.json
```

#### Retire.js
```bash
# Scan des librairies JavaScript vulnérables
retire --js --outputformat json --outputpath retire-report.json

# Scan avec node
retire --node --outputformat json --outputpath retire-node-report.json
```

### 6. Scan SQL Injection

#### Manuel (Review de code)
Rechercher dans le code :
```python
# ❌ DANGEREUX - ÉVITER
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
User.objects.raw(f"SELECT * FROM users WHERE id = {user_id}")

# ✅ SÉCURISÉ
User.objects.filter(id=user_id)
cursor.execute("SELECT * FROM users WHERE id = %s", [user_id])
```

### 7. Scan XSS (Cross-Site Scripting)

#### Manuel (Review de code)
```python
# ❌ DANGEREUX - ÉVITER
template = "<div>{{ user_input }}</div>"  # Sans échappement
mark_safe(user_input)

# ✅ SÉCURISÉ
template = "<div>{{ user_input|escape }}</div>"
# Django échappe automatiquement par défaut
```

#### Dans les templates
```html
<!-- ❌ DANGEREUX -->
{{ user_input|safe }}

<!-- ✅ SÉCURISÉ -->
{{ user_input }}
```

## 🚀 Exécution Complète du Skill

### Script d'audit complet (Linux/Mac)

```bash
#!/bin/bash

# security-audit.sh

echo "🔒 DÉMARRAGE DE L'AUDIT DE SÉCURITÉ COMPLET"
echo "============================================"

# Création du dossier de rapports
mkdir -p security-reports

echo ""
echo "📊 1/8 - Scan Bandit (Python)..."
bandit -r . -x ./tests,./migrations,./env,./venv,./.git -f json -o security-reports/bandit-report.json || true

echo ""
echo "📊 2/8 - Scan Semgrep..."
semgrep --config=p/python --config=p/django --config=p/security-audit --json -o security-reports/semgrep-report.json || true

echo ""
echo "📊 3/8 - Scan Safety..."
safety check --json --output security-reports/safety-report.json || true

echo ""
echo "📊 4/8 - Scan Pip-audit..."
pip-audit --desc --format=json --output=security-reports/pip-audit-report.json || true

echo ""
echo "📊 5/8 - Scan Detect-secrets..."
detect-secrets scan --all-files --baseline .secrets.baseline > security-reports/detect-secrets-report.json || true

echo ""
echo "📊 6/8 - Django Security Check..."
python manage.py check --deploy > security-reports/django-security-check.txt 2>&1 || true

echo ""
echo "📊 7/8 - Scan TruffleHog..."
truffleHog3 --json --output security-reports/trufflehog-report.json . || true

echo ""
echo "📊 8/8 - Scan JavaScript (si applicable)..."
if [ -f "package.json" ]; then
    npm audit --json > security-reports/npm-audit-report.json 2>&1 || true
fi

echo ""
echo "✅ AUDIT TERMINÉ !"
echo ""
echo "📁 Rapports générés dans : security-reports/"
echo ""
echo "🔍 Prochaines étapes :"
echo "   1. Consulter les rapports dans security-reports/"
echo "   2. Corriger les vulnérabilités HIGH et CRITICAL"
echo "   3. Relancer l'audit pour validation"
echo "   4. Commiter le fichier .secrets.baseline si nouveau secrets détectés"
```

### Script d'audit complet (Windows PowerShell)

```powershell
# security-audit.ps1

Write-Host "🔒 DÉMARRAGE DE L'AUDIT DE SÉCURITÉ COMPLET" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green

# Création du dossier de rapports
New-Item -ItemType Directory -Force -Path security-reports

Write-Host ""
Write-Host "📊 1/8 - Scan Bandit (Python)..." -ForegroundColor Yellow
bandit -r . -x ./tests,./migrations,./env,./venv,./.git -f json -o security-reports/bandit-report.json

Write-Host ""
Write-Host "📊 2/8 - Scan Semgrep..." -ForegroundColor Yellow
semgrep --config=p/python --config=p/django --config=p/security-audit --json -o security-reports/semgrep-report.json

Write-Host ""
Write-Host "📊 3/8 - Scan Safety..." -ForegroundColor Yellow
safety check --json --output security-reports/safety-report.json

Write-Host ""
Write-Host "📊 4/8 - Scan Pip-audit..." -ForegroundColor Yellow
pip-audit --desc --format=json --output=security-reports/pip-audit-report.json

Write-Host ""
Write-Host "📊 5/8 - Scan Detect-secrets..." -ForegroundColor Yellow
detect-secrets scan --all-files --baseline .secrets.baseline | Out-File -FilePath security-reports/detect-secrets-report.json

Write-Host ""
Write-Host "📊 6/8 - Django Security Check..." -ForegroundColor Yellow
python manage.py check --deploy | Out-File -FilePath security-reports/django-security-check.txt

Write-Host ""
Write-Host "📊 7/8 - Scan TruffleHog..." -ForegroundColor Yellow
truffleHog3 --json --output security-reports/trufflehog-report.json .

Write-Host ""
Write-Host "📊 8/8 - Scan JavaScript (si applicable)..." -ForegroundColor Yellow
if (Test-Path "package.json") {
    npm audit --json 2>&1 | Out-File -FilePath security-reports/npm-audit-report.json
}

Write-Host ""
Write-Host "✅ AUDIT TERMINÉ !" -ForegroundColor Green
Write-Host ""
Write-Host "📁 Rapports générés dans : security-reports/" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔍 Prochaines étapes :" -ForegroundColor White
Write-Host "   1. Consulter les rapports dans security-reports/" -ForegroundColor White
Write-Host "   2. Corriger les vulnérabilités HIGH et CRITICAL" -ForegroundColor White
Write-Host "   3. Relancer l'audit pour validation" -ForegroundColor White
Write-Host "   4. Commiter le fichier .secrets.baseline si nouveau secrets détectés" -ForegroundColor White
```

## 📊 Interprétation des Résultats

### Niveaux de Sévérité

| Niveau | Description | Action Requise |
|--------|-------------|----------------|
| 🔴 **CRITICAL** | Vulnérabilité critique - Exploitation immédiate possible | **BLOQUANT** - Doit être corrigé avant merge |
| 🟠 **HIGH** | Vulnérabilité élevée - Risque important | **BLOQUANT** - Doit être corrigé avant merge |
| 🟡 **MEDIUM** | Vulnérabilité moyenne - Risque modéré | À corriger dans la semaine |
| 🟢 **LOW** | Vulnérabilité faible - Risque limité | À corriger si possible |
| ⚪ **INFO** | Information - Bonne pratique | Recommandé |

### Format du Rapport Markdown

```markdown
# Rapport de Sécurité - [Date]

## Résumé Exécutif
- **Date du scan** : 2024-01-15 10:30:00
- **Projet** : Nom du projet
- **Branche** : feature/nouvelle-fonctionnalite
- **Commit** : abc123def456

## Statistiques
| Outil | Critical | High | Medium | Low | Info |
|-------|----------|------|--------|-----|------|
| Bandit | 0 | 2 | 5 | 10 | 3 |
| Safety | 0 | 1 | 3 | 8 | 0 |
| ... | ... | ... | ... | ... | ... |

## Vulnérabilités CRITICAL/HIGH

### [ID-001] Hardcoded Secret Key
- **Outil** : Bandit
- **Fichier** : `app/settings.py:12`
- **Sévérité** : HIGH
- **Description** : La SECRET_KEY est en dur dans le code
- **Correction** : Utiliser os.environ.get('SECRET_KEY')

## Recommandations
1. ...
2. ...
```

## 🛠️ Résolution des Problèmes Courants

### Problème 1 : Hardcoded Secret Key

**Erreur :**
```python
SECRET_KEY = "django-insecure-abc123..."
```

**Solution :**
```python
import os
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY non définie dans les variables d'environnement")
```

**Fichier .env :**
```
SECRET_KEY=votre-cle-super-secrete-et-tres-longue-ici
```

### Problème 2 : DEBUG = True en Production

**Erreur :**
```python
DEBUG = True
```

**Solution :**
```python
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
```

### Problème 3 : ALLOWED_HOSTS = ['*']

**Erreur :**
```python
ALLOWED_HOSTS = ['*']
```

**Solution :**
```python
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
```

### Problème 4 : SQL Injection

**Erreur :**
```python
cursor.execute(f"SELECT * FROM users WHERE name = '{username}'")
```

**Solution :**
```python
cursor.execute("SELECT * FROM users WHERE name = %s", [username])
# ou
User.objects.filter(name=username)
```

### Problème 5 : Secrets dans le code

**Erreur :**
```python
API_KEY = "sk-1234567890abcdef"
```

**Solution :**
```python
import os
API_KEY = os.environ.get('API_KEY')
```

## 🔧 Configuration Recommandée pour settings.py

```python
# settings.py - Configuration sécurisée

import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Charger .env
load_dotenv(BASE_DIR / '.env')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is not set")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Security Headers
SECURE_SSL_REDIRECT = not DEBUG
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# Secure Cookies
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
CSRF_COOKIE_SAMESITE = 'Strict'

# CSP Configuration
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'",)
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
CSP_IMG_SRC = ("'self'", "data:", "https:")
CSP_FONT_SRC = ("'self'", "https:", "data:")
CSP_CONNECT_SRC = ("'self'",)
CSP_FRAME_ANCESTORS = ("'none'",)
CSP_FORM_ACTION = ("'self'",)

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs/security.log',
        },
    },
    'loggers': {
        'django.security': {
            'handlers': ['security_file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}
```

## 📝 Checklist Pré-Merge Obligatoire

Avant de merger une feature, vérifier :

- [ ] ✅ Audit de sécurité exécuté avec succès
- [ ] ✅ Aucune vulnérabilité CRITICAL
- [ ] ✅ Aucune vulnérabilité HIGH
- [ ] ✅ Django `check --deploy` passe sans erreur
- [ ] ✅ Pas de secrets détectés (ou secrets ajoutés au baseline si faux positifs)
- [ ] ✅ Tests de sécurité passent
- [ ] ✅ Code review effectuée par un pair
- [ ] ✅ Documentation de sécurité mise à jour si nécessaire

## 🚨 En Cas de Vulnérabilité CRITICAL/HIGH

1. **Ne pas merger** la feature
2. **Créer une issue** avec label `security`
3. **Corriger immédiatement** la vulnérabilité
4. **Relancer l'audit** pour validation
5. **Documenter** la correction dans le CHANGELOG

## 📚 Ressources

- [Django Security Documentation](https://docs.djangoproject.com/en/stable/topics/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Bandit Documentation](https://bandit.readthedocs.io/)
- [Semgrep Rules](https://semgrep.dev/docs/)
- [Mozilla Web Security Guidelines](https://infosec.mozilla.org/guidelines/web_security)

---

**Dernière mise à jour** : 2026-01-15  
**Version** : 1.0.0  
**Auteur** : Équipe Sécurité
