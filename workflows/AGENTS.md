# Guide d'Utilisation des Workflows pour les Agents

## 🎯 Objectif

Ce document guide les agents AI sur quand et comment utiliser les différents workflows du dossier `workflows/` lors du développement de code.

## ⚠️ Règle d'Or

> **Avant toute création ou modification de code, consulter les workflows pertinents pour garantir la qualité et la cohérence du projet.**

---

## 📋 Structure des Workflows

Les workflows sont organisés en **deux formats** :

### 1. Fichiers .md à la racine (fichiers autonomes)
- `AGENTS.md` - Ce guide
- `django-css-separation.md` - Séparation CSS/HTML
- `django-javascript-separation.md` - Séparation JS/HTML

### 2. Sous-dossiers avec SKILL.md (skills organisés)
Chaque sous-dossier contient :
- `SKILL.md` - Documentation principale
- `QUICKSTART.md` - Guide rapide (optionnel)
- Dossiers supplémentaires (scripts, configs, etc.)

---

## 🗂️ Index des Workflows Disponibles

### Développement Python/Django
| Workflow | Chemin | Description |
|----------|--------|-------------|
| **Django Best Practices** | `django-best-practices/SKILL.md` | Bonnes pratiques Django 6.0 |
| **Python Linting** | `python-linting/SKILL.md` | Pylint, Flake8, Black, isort |
| **Django REST** | `django-rest/SKILL.md` | API REST avec Django |
| **Django CSS Separation** | `django-css-separation.md` | Séparation CSS/HTML (ZERO CSS inline) |
| **Django JS Separation** | `django-javascript-separation.md` | Séparation JS/HTML (ZERO JS inline) |

### Frontend
| Workflow | Chemin | Description |
|----------|--------|-------------|
| **JavaScript Moderne** | `javascript-modern/SKILL.md` | ES2024/ES2025, ESLint, Prettier |
| **Tailwind CSS** | `tailwindcss/SKILL.md` | Framework CSS utilitaire |
| **HTMX** | `htmx/SKILL.md` | AJAX moderne sans JS lourd |
| **Frontend Pipeline** | `frontend-assets-pipeline/SKILL.md` | Gestion des assets |

### Base de Données
| Workflow | Chemin | Description |
|----------|--------|-------------|
| **PostgreSQL** | `sql-postgresql/SKILL.md` | SQL PostgreSQL, requêtes, optimisation |

### Architecture & Code Quality
| Workflow | Chemin | Description |
|----------|--------|-------------|
| **Clean Code** | `clean-code/SKILL.md` | Principes de code propre |
| **SOLID** | `solid/SKILL.md` | Principes SOLID |
| **API Documentation** | `api-documentation/SKILL.md` | Documentation d'APIs |

### DevOps & Infrastructure
| Workflow | Chemin | Description |
|----------|--------|-------------|
| **Docker** | `docker-containers/SKILL.md` | Conteneurisation |
| **CI/CD Pipeline** | `ci-cd-pipeline/SKILL.md` | Intégration continue |
| **Deployment** | `deployment/SKILL.md` | Déploiement |
| **Environment Mgmt** | `environment-management/SKILL.md` | Gestion des environnements |

### Testing & Qualité
| Workflow | Chemin | Description |
|----------|--------|-------------|
| **Testing** | `testing/SKILL.md` | Stratégies de test |
| **Performance** | `performance-optimization/SKILL.md` | Optimisation |
| **Async Tasks** | `async-tasks/SKILL.md` | Tâches asynchrones |

### Sécurité & Monitoring
| Workflow | Chemin | Description |
|----------|--------|-------------|
| **Security Check** | `security-check/SKILL.md` | Audit de sécurité |
| **Error Monitoring** | `error-monitoring/SKILL.md` | Surveillance des erreurs |

### Git & Workflow
| Workflow | Chemin | Description |
|----------|--------|-------------|
| **Git Workflow** | `git-workflow/SKILL.md` | Conventions Git |

---

## 🗺️ Matrice de Décision Rapide

| Type de fichier/action | Workflow à consulter |
|------------------------|----------------------|
| **Fichier Python (.py)** | `python-linting/SKILL.md` |
| **Model Django** | `django-best-practices/SKILL.md` + `python-linting/SKILL.md` |
| **View/Form Django** | `django-best-practices/SKILL.md` + `python-linting/SKILL.md` |
| **API Django REST** | `django-rest/SKILL.md` |
| **Template HTML Django** | `django-css-separation.md` + `django-javascript-separation.md` |
| **Fichier CSS** | `django-css-separation.md` (+ `tailwindcss/SKILL.md`) |
| **Fichier JavaScript** | `javascript-modern/SKILL.md` (+ `django-javascript-separation.md`) |
| **Requête SQL** | `sql-postgresql/SKILL.md` |
| **Migration Django** | `django-best-practices/SKILL.md` + `sql-postgresql/SKILL.md` |
| **Docker/Conteneurs** | `docker-containers/SKILL.md` |
| **CI/CD** | `ci-cd-pipeline/SKILL.md` |
| **Tests** | `testing/SKILL.md` |
| **Commit Git** | `git-workflow/SKILL.md` |
| **Merge PR** | `security-check/SKILL.md` + `git-workflow/SKILL.md` |
| **Mise en production** | `security-check/SKILL.md` (obligatoire) |

---

## 🚀 Workflows par Phase de Développement

### Phase 1 : Architecture & Setup
**Consulter :**
- `clean-code/SKILL.md` - Principes généraux
- `solid/SKILL.md` - Architecture SOLID
- `django-best-practices/SKILL.md` - Structure projet Django
- `environment-management/SKILL.md` - Configuration env

### Phase 2 : Développement Backend
**Consulter :**
- `python-linting/SKILL.md` - Qualité Python
- `django-best-practices/SKILL.md` - Django (models, views, forms)
- `django-rest/SKILL.md` - Si API REST
- `sql-postgresql/SKILL.md` - Requêtes SQL

**Workflow recommandé :**
```bash
# 1. Lire les skills
# 2. Écrire le code
# 3. Exécuter : isort → black → flake8 → pylint
# 4. Corriger si nécessaire
```

### Phase 3 : Développement Frontend
**Consulter :**
- `django-css-separation.md` - HTML/CSS
- `django-javascript-separation.md` - JS dans Django
- `javascript-modern/SKILL.md` - JS moderne
- `tailwindcss/SKILL.md` - Si Tailwind
- `htmx/SKILL.md` - Si HTMX

**Workflow recommandé :**
```bash
# 1. Lire les skills
# 2. Écrire le code
# 3. Exécuter : ESLint --fix → Prettier
# 4. Vérifier avec ESLint et Prettier --check
```

### Phase 4 : Testing
**Consulter :**
- `testing/SKILL.md` - Stratégies de test
- `python-linting/SKILL.md` - Vérification qualité

### Phase 5 : DevOps & Déploiement
**Consulter :**
- `docker-containers/SKILL.md` - Conteneurisation
- `ci-cd-pipeline/SKILL.md` - CI/CD
- `deployment/SKILL.md` - Déploiement
- `async-tasks/SKILL.md` - Si tâches async

### Phase 6 : Sécurité (Pré-merge obligatoire)
**Exécuter obligatoirement :**
- `security-check/SKILL.md` - Audit complet
  - Bandit (scan Python)
  - Safety (vulnérabilités)
  - Django check --deploy
  - Detect-secrets

**⚠️ Si vulnérabilité CRITICAL/HIGH :**
- Ne PAS merger
- Corriger immédiatement
- Relancer l'audit

### Phase 7 : Monitoring
**Consulter :**
- `error-monitoring/SKILL.md` - Surveillance
- `performance-optimization/SKILL.md` - Optimisation

---

## 📝 Conventions Git (Toutes Phases)

**Consulter :** `git-workflow/SKILL.md`

**Format de commit :**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types autorisés :** `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`, `ci`, `security`

---

## ✅ Checklist de Validation Pré-Commit

### Fichiers Python
- [ ] Lu `python-linting/SKILL.md`
- [ ] Pylint passe sans erreur
- [ ] Flake8 passe sans erreur
- [ ] Black formaté (line-length: 100)
- [ ] isort appliqué

### Fichiers Django
- [ ] Lu `django-best-practices/SKILL.md`
- [ ] Docstrings présentes
- [ ] Type hints utilisés
- [ ] Pas de logique dans templates

### Fichiers CSS
- [ ] Lu `django-css-separation.md`
- [ ] ZERO CSS inline (sauf dynamique)
- [ ] Variables CSS utilisées

### Fichiers JavaScript
- [ ] Lu `javascript-modern/SKILL.md`
- [ ] ESLint passe sans erreur
- [ ] Prettier formaté
- [ ] ZERO JS inline
- [ ] ES Modules utilisés

### Sécurité (pré-merge)
- [ ] Exécuté `security-check/SKILL.md`
- [ ] Aucune vulnérabilité HIGH/CRITICAL

---

## 🚨 Erreurs à Éviter

### Python
- ❌ Ignorer erreurs Pylint/Flake8
- ❌ Utiliser `print()` en production
- ❌ Committer secrets

### Django
- ❌ Logique métier dans templates
- ❌ `raw()` sans paramètres
- ❌ `DEBUG = True` en prod

### CSS/JS
- ❌ CSS/JS inline
- ❌ Balises `<style>` ou `<script>` dans templates
- ❌ `var` (utiliser `const`/`let`)

### Git
- ❌ Messages vagues ("fix", "update")
- ❌ Majuscules dans subject
- ❌ Point à la fin
- ❌ `git push --force` sur main/develop

---

## 📚 Astuces

- Chaque skill contient des exemples de code complets
- Les QUICKSTART.md offrent un démarrage rapide
- Les scripts/ dossiers contiennent des outils d'automatisation

**Ne jamais hésiter à consulter un skill avant de coder !**

---

**Dernière mise à jour** : 2026-02-24  
**Version** : 2.0.0  
**Auteur** : Guide pour Agents AI
