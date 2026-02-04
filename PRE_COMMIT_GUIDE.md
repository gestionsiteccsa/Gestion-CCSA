# 🚀 Guide Pré-Commit - Étapes Obligatoires Avant Commit

> **⚠️ IMPORTANT** : Ce guide doit être suivi **OBLIGATOIREMENT** avant chaque commit pour garantir la qualité et la sécurité du code.

---

## 📋 Checklist Pré-Commit

### ✅ Étape 1 : Vérification du Code

#### 1.1 Linter et Formatage
```bash
# Vérifier le style du code avec flake8
flake8 . --exclude=env,venv,__pycache__,migrations --max-line-length=120

# Formater le code avec black (si utilisé)
black . --exclude='/(env|venv|__pycache__|migrations)/'

# Trier les imports avec isort
isort . --skip=env --skip=venv --skip=__pycache__ --skip=migrations
```

#### 1.2 Vérification des Imports
```bash
# Vérifier qu'il n'y a pas d'imports circulaires
python -c "import app.settings"
```

---

### ✅ Étape 2 : Tests

#### 2.1 Exécuter les Tests
```bash
# Tous les tests
python manage.py test

# Tests avec couverture
pytest --cov=. --cov-report=html --cov-report=term

# Tests de sécurité spécifiques
python manage.py test home.tests
```

#### 2.2 Vérifier le Résultat
- [ ] Tous les tests passent (OK)
- [ ] Pas d'erreurs (FAILED)
- [ ] Couverture de code > 80%

---

### ✅ Étape 3 : Vérification Django

#### 3.1 Check Système
```bash
# Vérifier la configuration Django
python manage.py check

# Vérifier la configuration de production
python manage.py check --deploy
```

#### 3.2 Migrations
```bash
# Vérifier s'il y a des migrations à créer
python manage.py makemigrations --check --dry-run

# Si des migrations sont nécessaires, les créer
python manage.py makemigrations

# Vérifier que les migrations sont valides
python manage.py migrate --check
```

---

### ✅ Étape 4 : Audit de Sécurité (OBLIGATOIRE)

#### 4.1 Scan de Sécurité Automatisé
```bash
# Bandit - Analyse statique Python
bandit -r . -x ./tests,./migrations,./env,./venv,./.git,__pycache__ -ll

# Safety - Vulnérabilités des dépendances
safety check

# Pip-audit - Audit PyPI
pip-audit --desc
```

#### 4.2 Détection de Secrets
```bash
# Detect-secrets
# Si des secrets sont détectés, les ajouter au baseline si ce sont des faux positifs
detect-secrets scan --all-files --baseline .secrets.baseline

# Vérifier avec git-secrets
git secrets --scan
```

#### 4.3 Vérification Manuelle
- [ ] Pas de `SECRET_KEY` en dur dans le code
- [ ] Pas de mots de passe en dur
- [ ] Pas de tokens ou clés API exposés
- [ ] Pas de `DEBUG = True` en production
- [ ] Pas de `ALLOWED_HOSTS = ['*']`

---

### ✅ Étape 5 : Vérification des Fichiers

#### 5.1 Fichiers à Ne Pas Committer
```bash
# Vérifier que .env n'est pas suivi
git status | grep -E "\.env|db\.sqlite3|__pycache__|\.pyc"

# Si des fichiers sensibles apparaissent, les ajouter à .gitignore
```

#### 5.2 Vérifier le .gitignore
```bash
# S'assurer que les fichiers suivants sont ignorés :
# - .env
# - db.sqlite3
# - __pycache__/
# - *.pyc
# - env/, venv/
# - logs/*.log (sauf .gitkeep)
# - security-reports/
# - github.md
```

---

### ✅ Étape 6 : Pre-commit Hooks

#### 6.1 Installation (Première fois uniquement)
```bash
pip install pre-commit
pre-commit install
```

#### 6.2 Exécution
```bash
# Exécuter tous les hooks pre-commit
pre-commit run --all-files

# Ou laisser le hook se déclencher automatiquement
git commit -m "votre message"
```

---

### ✅ Étape 7 : Git

#### 7.1 Vérifier les Changements
```bash
# Voir les fichiers modifiés
git status

# Voir les différences
git diff

# Voir les fichiers staged
git diff --cached
```

#### 7.2 Messages de Commit
Suivre la convention : `type: description`

Types :
- `feat:` Nouvelle fonctionnalité
- `fix:` Correction de bug
- `docs:` Documentation
- `style:` Formatage (pas de changement de code)
- `refactor:` Refactoring
- `test:` Tests
- `chore:` Maintenance
- `security:` Sécurité

Exemples :
```bash
git commit -m "feat: Ajout de l'authentification JWT"
git commit -m "fix: Correction de la fuite mémoire dans le cache"
git commit -m "security: Mise à jour des dépendances critiques"
```

---

## 🔧 Script Automatisé

Créer un fichier `pre-commit-check.sh` :

```bash
#!/bin/bash

echo "🔍 Vérification pré-commit..."
echo "=============================="

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Compteur d'erreurs
ERRORS=0

# 1. Linter
echo -e "\n${YELLOW}1. Vérification du style de code...${NC}"
if flake8 . --exclude=env,venv,__pycache__,migrations --max-line-length=120; then
    echo -e "${GREEN}✓ Linter OK${NC}"
else
    echo -e "${RED}✗ Linter a détecté des erreurs${NC}"
    ERRORS=$((ERRORS + 1))
fi

# 2. Tests
echo -e "\n${YELLOW}2. Exécution des tests...${NC}"
if python manage.py test --verbosity=0; then
    echo -e "${GREEN}✓ Tests OK${NC}"
else
    echo -e "${RED}✗ Tests échoués${NC}"
    ERRORS=$((ERRORS + 1))
fi

# 3. Check Django
echo -e "\n${YELLOW}3. Vérification Django...${NC}"
if python manage.py check --verbosity=0; then
    echo -e "${GREEN}✓ Django OK${NC}"
else
    echo -e "${RED}✗ Erreurs Django${NC}"
    ERRORS=$((ERRORS + 1))
fi

# 4. Sécurité - Bandit
echo -e "\n${YELLOW}4. Scan de sécurité (Bandit)...${NC}"
if bandit -r . -x ./tests,./migrations,./env,./venv,./.git,__pycache__ -ll --quiet; then
    echo -e "${GREEN}✓ Bandit OK${NC}"
else
    echo -e "${RED}✗ Bandit a détecté des problèmes${NC}"
    ERRORS=$((ERRORS + 1))
fi

# 5. Sécurité - Safety
echo -e "\n${YELLOW}5. Vérification des dépendances (Safety)...${NC}"
if safety check --quiet; then
    echo -e "${GREEN}✓ Safety OK${NC}"
else
    echo -e "${RED}✗ Safety a détecté des vulnérabilités${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Résumé
echo -e "\n=============================="
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ Toutes les vérifications sont passées !${NC}"
    echo "Vous pouvez committer."
    exit 0
else
    echo -e "${RED}❌ $ERRORS vérification(s) ont échoué.${NC}"
    echo "Corrigez les erreurs avant de committer."
    exit 1
fi
```

Rendre exécutable :
```bash
chmod +x pre-commit-check.sh
```

Lancer :
```bash
./pre-commit-check.sh
```

---

## 📊 Récapitulatif des Commandes

### Commandes Rapides (À exécuter dans l'ordre)

```bash
# 1. Linter
flake8 . --exclude=env,venv,__pycache__,migrations --max-line-length=120

# 2. Tests
python manage.py test

# 3. Check Django
python manage.py check

# 4. Sécurité
bandit -r . -x ./tests,./migrations,./env,./venv,./.git,__pycache__ -ll
safety check

# 5. Git
git status
git add .
git commit -m "type: description"
```

### Commande Unique (Tout en un)

```bash
# Exécuter toutes les vérifications
python manage.py test && python manage.py check && bandit -r . -x ./tests,./migrations,./env,./venv,./.git,__pycache__ -ll && safety check && echo "✅ OK - Prêt à committer"
```

---

## ⚠️ En Cas d'Erreur

### Erreurs de Sécurité
1. **Ne pas committer**
2. Corriger immédiatement
3. Relancer les vérifications

### Erreurs de Tests
1. Corriger les tests échoués
2. Vérifier la couverture
3. Relancer les tests

### Erreurs de Linter
1. Corriger le style de code
2. Utiliser `black` ou `autopep8` si nécessaire
3. Relancer le linter

---

## 🚨 Rappels Importants

- [ ] **JAMAIS** committer de secrets (clés API, mots de passe, tokens)
- [ ] **JAMAIS** committer le fichier `.env`
- [ ] **JAMAIS** committer `db.sqlite3`
- [ ] **TOUJOURS** exécuter les tests avant de committer
- [ ] **TOUJOURS** passer l'audit de sécurité
- [ ] **TOUJOURS** utiliser des messages de commit descriptifs

---

## 📚 Ressources

- [Django Testing](https://docs.djangoproject.com/en/5.2/topics/testing/)
- [Bandit Documentation](https://bandit.readthedocs.io/)
- [Pre-commit Hooks](https://pre-commit.com/)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

**Dernière mise à jour** : 2026-02-02  
**Version** : 1.0
