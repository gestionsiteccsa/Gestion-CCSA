# Skill Python Linting - Pylint, Flake8, Black et isort

## 🎯 Objectif

Ce skill définit les bonnes pratiques et configurations pour Pylint, Flake8, Black et isort afin de garantir la qualité du code Python. **Il doit être consulté obligatoirement avant chaque création ou modification de fichier Python.**

## ⚠️ Règle d'Or

> **AUCUN fichier Python ne doit être créé ou modifié sans respecter ces conventions de linting.**

## 🔄 Ordre d'Exécution des Outils

Pour un formatage optimal, exécuter les outils dans cet ordre :

```bash
# 1. isort - Trie les imports (doit être avant Black)
isort --profile=black --line-length=100 .

# 2. Black - Formate le code
black --line-length=100 .

# 3. Flake8 - Vérifie la qualité
flake8 --config=.flake8 .

# 4. Pylint - Analyse statique approfondie
pylint --rcfile=.pylintrc .
```

**⚠️ Important :** isort doit TOUJOURS être exécuté avant Black pour éviter les conflits de formatage.

---

## 📋 Installation des Outils

### Installation via pip

```bash
# Installation de base
pip install pylint flake8 black isort

# Installation avec plugins recommandés
pip install pylint flake8 flake8-docstrings flake8-import-order flake8-bugbear

# Pour les projets Django
pip install pylint-django

# Pour les projets avec type hints
pip install pylint flake8-mypy

# Installation complète (recommandé)
pip install pylint flake8 black isort flake8-docstrings flake8-bugbear flake8-black
```

### Installation via requirements.txt

```txt
# requirements-dev.txt
pylint>=2.17.0
flake8>=6.0.0
black>=23.0.0
isort>=5.12.0
flake8-docstrings>=1.7.0
flake8-import-order>=0.18.2
flake8-bugbear>=23.0.0
flake8-black>=0.3.6
pylint-django>=2.5.0
```

---

## 🔧 Configuration Black

### Fichier de Configuration

Créer un fichier `pyproject.toml` à la racine du projet :

```toml
[tool.black]
# Longueur de ligne maximale
line-length = 100

# Version cible de Python
target-version = ['py311']

# Fichiers à inclure
include = '\.pyi?$'

# Fichiers et dossiers à exclure
exclude = '''
/(
      \.eggs
    | \.git
    | \.hg
    | \.mypy_cache
    | \.tox
    | \.venv
    | _build
    | buck-out
    | build
    | dist
    | migrations
    | venv
    | env
)/
'''

# Mode strict (optionnel)
# strict = true

# Skip string normalization (optionnel)
# skip-string-normalization = true

# Skip magic trailing comma (optionnel)
# skip-magic-trailing-comma = true
```

### Utilisation de Black

```bash
# Formater un fichier spécifique
black mon_fichier.py

# Formater tout le projet
black .

# Vérifier le formatage sans modifier (mode check)
black --check .

# Afficher les différences sans modifier
black --diff .

# Formater avec une longueur de ligne spécifique
black --line-length 100 .

# Formater avec verbose
black --verbose .
```

### Exemples de Formatage Black

```python
# AVANT - Code non formaté
def ma_fonction(param1,param2,param3):
    if param1==True:
        return param2+param3
    else:
        return None

# APRÈS - Code formaté par Black
def ma_fonction(param1, param2, param3):
    if param1 == True:
        return param2 + param3
    else:
        return None


# AVANT - Longue ligne
def calculer_somme(nombre1, nombre2, nombre3, nombre4, nombre5, nombre6, nombre7, nombre8, nombre9, nombre10):
    return nombre1 + nombre2 + nombre3 + nombre4 + nombre5 + nombre6 + nombre7 + nombre8 + nombre9 + nombre10

# APRÈS - Black formate automatiquement
def calculer_somme(
    nombre1,
    nombre2,
    nombre3,
    nombre4,
    nombre5,
    nombre6,
    nombre7,
    nombre8,
    nombre9,
    nombre10,
):
    return (
        nombre1
        + nombre2
        + nombre3
        + nombre4
        + nombre5
        + nombre6
        + nombre7
        + nombre8
        + nombre9
        + nombre10
    )
```

---

## 🔧 Configuration isort

### Fichier de Configuration

Créer un fichier `pyproject.toml` ou `.isort.cfg` à la racine du projet :

#### Option 1 : pyproject.toml (recommandé)

```toml
[tool.isort]
# Profil compatible avec Black
profile = "black"

# Longueur de ligne maximale
line_length = 100

# Nombre de lignes vides entre les sections
lines_between_sections = 1

# Nombre de lignes vides après les imports
lines_after_imports = 2

# Sections d'imports
sections = ["FUTURE", "STDLIB", "THIRDPARTY", "FIRSTPARTY", "LOCALFOLDER"]

# Imports à placer en premier
known_first_party = ["mon_projet"]

# Imports à placer dans une section spécifique
known_third_party = ["django", "requests", "sqlalchemy"]

# Forcer les imports sur une seule ligne
force_single_line = false

# Forcer les imports triés alphabétiquement
force_alphabetical_sort = false

# Inclure les imports de trailing comma
include_trailing_comma = true

# Utiliser des parenthèses pour les imports multi-lignes
use_parentheses = true

# Multi-line output mode
multi_line_output = 3

# Combinaison des imports as
combine_as_imports = false

# Ordre des imports
force_sort_within_sections = true

# Case sensitive sorting
case_sensitive = false

# Skip les fichiers
skip = ["migrations", "venv", "env", ".git", "__pycache__"]

# Fichiers à traiter
src_paths = ["src", "mon_projet"]
```

#### Option 2 : .isort.cfg

```ini
[settings]
profile = black
line_length = 100
lines_between_sections = 1
lines_after_imports = 2
sections = FUTURE,STDLIB,THIRDPARTY,FIRSTPARTY,LOCALFOLDER
known_first_party = mon_projet
known_third_party = django,requests,sqlalchemy
multi_line_output = 3
include_trailing_comma = true
use_parentheses = true
force_sort_within_sections = true
skip = migrations,venv,env,.git,__pycache__
src_paths = src,mon_projet
```

### Utilisation de isort

```bash
# Trier les imports d'un fichier spécifique
isort mon_fichier.py

# Trier les imports de tout le projet
isort .

# Vérifier le tri sans modifier (mode check)
isort --check-only .

# Afficher les différences sans modifier
isort --diff .

# Mode verbose
isort --verbose .

# Trier avec un profil spécifique
isort --profile black .

# Trier avec une longueur de ligne spécifique
isort --line-length 100 .
```

### Exemples de Tri isort

```python
# AVANT - Imports non triés
import os
from mon_projet.models import User
import sys
from django.db import models
import requests
from datetime import datetime
from typing import List
from mon_projet.utils import helper

# APRÈS - Imports triés par isort (profil Black)
import os
import sys
from datetime import datetime
from typing import List

import requests
from django.db import models

from mon_projet.models import User
from mon_projet.utils import helper
```

### Ordre des Imports avec isort

```python
# ✅ CORRECT - Ordre standard avec isort
"""Module exemple."""

# 1. __future__ imports
from __future__ import annotations

# 2. Standard library
import os
import sys
from datetime import datetime
from typing import List, Optional

# 3. Third-party
import requests
from django.db import models
from sqlalchemy import Column, Integer

# 4. First-party (votre projet)
from mon_projet.models import User
from mon_projet.services.auth import AuthService
from mon_projet.utils import helper

# 5. Local (imports relatifs si nécessaire)
from .models import Profile
from ..utils.validators import validate_email
```

---

## 🔧 Configuration Pylint

### Fichier de Configuration

Créer un fichier `.pylintrc` à la racine du projet :

```ini
[MASTER]
# Fichiers à ignorer
ignore=CVS,migrations,venv,env,.git,__pycache__,.pytest_cache

# Extensions à analyser
extension-pkg-whitelist=

# Nombre de jobs parallèles
jobs=4

# Plugins à charger
load-plugins=pylint_django

[MESSAGES CONTROL]
# Désactiver les messages spécifiques
disable=
    C0103,  # invalid-name (trop strict pour les variables courtes)
    C0114,  # missing-module-docstring (optionnel pour les petits modules)
    R0903,  # too-few-public-methods (acceptable pour les dataclasses)
    R0913,  # too-many-arguments (souvent nécessaire)
    W0613,  # unused-argument (souvent nécessaire pour les callbacks)
    W0511,  # fixme (autoriser les TODOs)
    R0801,  # duplicate-code (souvent faux positif)

[REPORTS]
# Format du rapport
output-format=colorized

# Afficher le score
score=yes

[REFACTORING]
# Nombre maximum de caractères par ligne
max-line-length=100

[FORMAT]
# Indentation
indent-string='    '
indent-after-paren=4

[BASIC]
# Noms de variables autorisés
good-names=i,j,k,ex,Run,_,pk,id

# Noms de variables interdits
bad-names=foo,bar,baz,toto,tutu,tata

# Expressions régulières pour les noms
function-rgx=[a-z_][a-z0-9_]{2,50}$
variable-rgx=[a-z_][a-z0-9_]{2,30}$
const-rgx=(([A-Z_][A-Z0-9_]*)|(__.*__))$
attr-rgx=[a-z_][a-z0-9_]{2,30}$
argument-rgx=[a-z_][a-z0-9_]{2,30}$
class-attribute-rgx=([A-Za-z_][A-Za-z0-9_]{2,50}|(__.*__))$
inlinevar-rgx=[A-Za-z_][A-Za-z0-9_]*$
class-rgx=[A-Z_][a-zA-Z0-9]+$
module-rgx=(([a-z_][a-z0-9_]*)|([A-Z][a-zA-Z0-9]+))$
method-rgx=[a-z_][a-z0-9_]{2,50}$

# Minimum de lignes publiques dans une classe
min-public-methods=1

# Maximum de lignes publiques dans une classe
max-public-methods=20

[DESIGN]
# Maximum d'arguments dans une fonction
max-args=8

# Maximum de locaux dans une fonction
max-locals=15

# Maximum de retours dans une fonction
max-returns=6

# Maximum de branches dans une fonction
max-branches=12

# Maximum de statements dans une fonction
max-statements=50

# Maximum de parents pour une classe
max-parents=7

# Maximum d'attributs pour une classe
max-attributes=10

[IMPORTS]
# Autoriser les imports wildcard
dallow-wildcard-with-all=no

[TYPECHECK]
# Modules à ignorer pour le type checking
generated-members=REQUEST,acl_users,aq_parent,objects,DoesNotExist

[VARIABLES]
# Autoriser les noms courts pour les variables de boucle
dummy-variables-rgx=_|dummy|unused

[CLASSES]
# Vérifier l'ordre des méthodes
check-protected-access-in-special-methods=no

[EXCEPTIONS]
# Exceptions à ignorer pour broad-except
overgeneral-exceptions=builtins.Exception

[STRING]
# Vérifier les chaînes de caractères
check-quote-consistency=yes
```

### Configuration Minimaliste

Pour les petits projets, créer `.pylintrc` :

```ini
[MASTER]
ignore=venv,env,migrations,__pycache__
jobs=4

[MESSAGES CONTROL]
disable=C0103,C0114,R0903

[FORMAT]
max-line-length=100

[BASIC]
good-names=i,j,k,_,pk,id
```

---

## 🔧 Configuration Flake8

### Fichier de Configuration

Créer un fichier `.flake8` ou `setup.cfg` à la racine du projet :

```ini
[flake8]
# Maximum de caractères par ligne
max-line-length = 100

# Nombre maximum de complexité cyclomatique
max-complexity = 10

# Fichiers et dossiers à exclure
exclude =
    .git,
    __pycache__,
    venv,
    env,
    .venv,
    .env,
    migrations,
    build,
    dist,
    *.egg-info,
    .pytest_cache,
    .tox

# Erreurs à ignorer
ignore =
    E203,  # whitespace before ':' (conflit avec black)
    E266,  # too many leading '#' for block comment
    E501,  # line too long (géré par max-line-length)
    W503,  # line break before binary operator (PEP8 a changé)
    W504,  # line break after binary operator
    F403,  # 'from module import *' used
    F405,  # name may be undefined or defined from star imports
    E402,  # module level import not at top of file

# Plugins spécifiques
import-order-style = google
application-import-names = mon_projet

# Docstrings
docstring-convention = google

# Sélecteurs d'erreurs
select =
    E,     # Erreurs pycodestyle
    F,     # Erreurs Pyflakes
    W,     # Warnings pycodestyle
    C,     # McCabe complexity
    D,     # Docstrings
    I,     # Import order
    B,     # Bugbear
    B9,    # Bugbear opinionated

# Format du rapport
format = pylint
show-source = true
statistics = true

# Nombre de lignes vides entre les fonctions
blank-lines-before-imports = 1
blank-lines-after-imports = 2
blank-lines-between-methods = 1
blank-lines-between-classes = 2
```

### Configuration Minimaliste

Pour les petits projets, créer `.flake8` :

```ini
[flake8]
max-line-length = 100
exclude = venv,env,__pycache__,migrations
ignore = E203,W503
max-complexity = 10
```

---

## 🚀 Utilisation

### Commandes de Base

```bash
# Linter un fichier spécifique
pylint mon_fichier.py
flake8 mon_fichier.py

# Linter tout le projet
pylint .
flake8 .

# Linter avec rapport détaillé
pylint --reports=yes .
flake8 --statistics .

# Linter avec format JSON
pylint --output-format=json .
flake8 --format=json .

# Ignorer des erreurs spécifiques
pylint --disable=C0103,W0613 mon_fichier.py
flake8 --ignore=E501,W503 mon_fichier.py

# Vérifier uniquement certaines erreurs
pylint --disable=all --enable=E,W mon_fichier.py
flake8 --select=E,W mon_fichier.py
```

### Intégration avec Pre-commit

Créer `.pre-commit-config.yaml` :

```yaml
repos:
  # Black - Formatage automatique
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3.11
        args: [--line-length=100]

  # isort - Tri des imports
  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: [--profile=black, --line-length=100]

  # Flake8 - Linting
  - repo: https://github.com/pycqa/flake8
    rev: 6.1.0
    hooks:
      - id: flake8
        args: [--config=.flake8]
        additional_dependencies: [flake8-docstrings, flake8-bugbear, flake8-black]

  # Pylint - Analyse statique
  - repo: https://github.com/pycqa/pylint
    rev: v3.0.3
    hooks:
      - id: pylint
        args: [--rcfile=.pylintrc]
        additional_dependencies: [pylint-django]
```

### Intégration CI/CD (GitHub Actions)

```yaml
# .github/workflows/lint.yml
name: Lint

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install pylint flake8 black isort flake8-docstrings flake8-bugbear flake8-black
      
      - name: Run Black (check)
        run: black --check --line-length=100 .
      
      - name: Run isort (check)
        run: isort --check-only --profile=black --line-length=100 .
      
      - name: Run Flake8
        run: flake8 --config=.flake8 .
      
      - name: Run Pylint
        run: pylint --rcfile=.pylintrc .
```

---

## 📝 Règles de Style Python

### PEP 8 - Règles de Base

```python
# ✅ CORRECT - Indentation avec 4 espaces
def ma_fonction():
    pass

# ❌ INCORRECT - Indentation avec tabs ou 2 espaces
def ma_fonction():
  pass

# ✅ CORRECT - Longueur de ligne (max 100 caractères)
ma_variable = "Ceci est une ligne de code qui respecte la limite de 100 caractères"

# ❌ INCORRECT - Ligne trop longue
ma_variable = "Ceci est une ligne de code qui dépasse la limite de 100 caractères et qui devrait être coupée"

# ✅ CORRECT - Imports sur plusieurs lignes
from mon_module import (
    fonction_a,
    fonction_b,
    fonction_c,
)

# ❌ INCORRECT - Imports sur une ligne trop longue
from mon_module import fonction_a, fonction_b, fonction_c, fonction_d, fonction_e
```

### Naming Conventions

```python
# ✅ CORRECT - Variables et fonctions (snake_case)
ma_variable = 10
def ma_fonction():
    pass

# ✅ CORRECT - Classes (PascalCase)
class MaClasse:
    pass

# ✅ CORRECT - Constantes (UPPER_CASE)
MA_CONSTANTE = 100

# ✅ CORRECT - Variables privées (_single_leading_underscore)
_variable_privee = 10

# ✅ CORRECT - Variables protégées (_single_trailing_underscore_)
class_ = "nom de classe"

# ❌ INCORRECT - Mauvaises conventions
MaVariable = 10  # Devrait être ma_variable
maClasse = None  # Devrait être MaClasse pour une classe
ma_constante = 10  # Devrait être MA_CONSTANTE
```

### Docstrings

```python
# ✅ CORRECT - Docstring Google Style
def calculer_aire(longueur, largeur):
    """Calcule l'aire d'un rectangle.

    Args:
        longueur (float): La longueur du rectangle.
        largeur (float): La largeur du rectangle.

    Returns:
        float: L'aire du rectangle.

    Raises:
        ValueError: Si longueur ou largeur est négative.

    Example:
        >>> calculer_aire(5, 3)
        15.0
    """
    if longueur < 0 or largeur < 0:
        raise ValueError("Les dimensions doivent être positives")
    return longueur * largeur


# ✅ CORRECT - Docstring pour classe
class Rectangle:
    """Représente un rectangle géométrique.

    Cette classe permet de créer et manipuler des rectangles.
    Elle supporte les opérations de calcul d'aire et de périmètre.

    Attributes:
        longueur (float): La longueur du rectangle.
        largeur (float): La largeur du rectangle.

    Example:
        >>> rect = Rectangle(5, 3)
        >>> rect.aire()
        15.0
    """

    def __init__(self, longueur, largeur):
        """Initialise un rectangle.

        Args:
            longueur (float): La longueur.
            largeur (float): La largeur.
        """
        self.longueur = longueur
        self.largeur = largeur


# ❌ INCORRECT - Docstring manquante ou incomplète
def calculer(x, y):  # Pas de docstring
    return x * y

def calculer(x, y):
    """Calcule quelque chose."""  # Trop vague
    return x * y
```

### Imports (Automatique avec isort)

```python
# ✅ CORRECT - isort gère automatiquement l'ordre
"""Module exemple."""

from __future__ import annotations

import os
import sys
from datetime import datetime
from typing import List, Optional

import requests
from django.db import models
from sqlalchemy import Column, Integer

from mon_projet.models import User
from mon_projet.services.auth import AuthService
from mon_projet.utils import helper


# Commande pour formater automatiquement :
# isort mon_fichier.py


# ❌ INCORRECT - Avant isort (imports mélangés)
from mon_projet.models import User
import os
import requests
from datetime import datetime
from typing import List, Optional
from django.db import models
from mon_projet.utils import helper


# ✅ CORRECT - Après isort (imports triés par groupe)
import os
from datetime import datetime
from typing import List, Optional

import requests
from django.db import models

from mon_projet.models import User
from mon_projet.utils import helper
```

### Structure du Code

```python
# ✅ CORRECT - Ordre dans un module
"""Module de gestion des utilisateurs.

Ce module contient les fonctions et classes pour gérer
les utilisateurs de l'application.
"""

# 1. Imports
import os
from typing import List

from django.db import models

from mon_projet.models import Profile


# 2. Constantes
MAX_USERS = 100
DEFAULT_ROLE = "user"


# 3. Classes
class User(models.Model):
    """Représente un utilisateur."""
    
    class Meta:
        db_table = "users"
    
    def __init__(self, username: str):
        self.username = username
    
    def save(self) -> None:
        """Sauvegarde l'utilisateur."""
        super().save()


# 4. Fonctions
def creer_utilisateur(username: str) -> User:
    """Crée un nouvel utilisateur."""
    return User(username=username)


# 5. Code exécutable (si nécessaire)
if __name__ == "__main__":
    user = creer_utilisateur("test")
    user.save()
```

---

## 🧪 Bonnes Pratiques

### Workflow Complet avec Black et isort

```python
# EXEMPLE COMPLET - Fichier Python bien formaté

"""Module de gestion des utilisateurs.

Ce module contient les fonctions et classes pour gérer
les utilisateurs de l'application avec validation.
"""

from __future__ import annotations

import hashlib
import re
from datetime import datetime
from typing import List, Optional

from django.db import models
from pydantic import BaseModel, EmailStr, validator

from mon_projet.exceptions import ValidationError
from mon_projet.utils.logger import get_logger

logger = get_logger(__name__)

MAX_USERNAME_LENGTH = 50
MIN_PASSWORD_LENGTH = 8


class User(BaseModel):
    """Représente un utilisateur du système.

    Cette classe utilise Pydantic pour la validation automatique
    des données utilisateur.

    Attributes:
        id: Identifiant unique de l'utilisateur.
        username: Nom d'utilisateur unique.
        email: Adresse email valide.
        created_at: Date de création du compte.
        is_active: Indique si le compte est actif.

    Example:
        >>> user = User(
        ...     id=1,
        ...     username="john_doe",
        ...     email="john@example.com"
        ... )
        >>> user.is_valid_email()
        True
    """

    id: Optional[int] = None
    username: str
    email: EmailStr
    created_at: datetime = datetime.now()
    is_active: bool = True

    @validator("username")
    def validate_username(cls, value: str) -> str:
        """Valide le format du nom d'utilisateur.

        Args:
            value: Le nom d'utilisateur à valider.

        Returns:
            Le nom d'utilisateur validé.

        Raises:
            ValidationError: Si le format est invalide.
        """
        if not re.match(r"^[a-zA-Z0-9_]+$", value):
            raise ValidationError(
                "Le username ne doit contenir que des lettres, chiffres et underscores"
            )
        if len(value) > MAX_USERNAME_LENGTH:
            raise ValidationError(f"Le username ne doit pas dépasser {MAX_USERNAME_LENGTH} caractères")
        return value.lower()

    def hash_password(self, password: str) -> str:
        """Hache le mot de passe avec SHA-256.

        Args:
            password: Le mot de passe en clair.

        Returns:
            Le hash du mot de passe.

        Raises:
            ValidationError: Si le mot de passe est trop court.
        """
        if len(password) < MIN_PASSWORD_LENGTH:
            raise ValidationError(
                f"Le mot de passe doit contenir au moins {MIN_PASSWORD_LENGTH} caractères"
            )
        return hashlib.sha256(password.encode()).hexdigest()

    def is_valid_email(self) -> bool:
        """Vérifie si l'email est valide.

        Returns:
            True si l'email est valide, False sinon.
        """
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, self.email))


def create_user(username: str, email: str, password: str) -> User:
    """Crée un nouvel utilisateur avec validation.

    Args:
        username: Nom d'utilisateur souhaité.
        email: Adresse email.
        password: Mot de passe.

    Returns:
        L'utilisateur créé.

    Raises:
        ValidationError: Si les données sont invalides.

    Example:
        >>> user = create_user("john_doe", "john@example.com", "password123")
        >>> user.username
        'john_doe'
    """
    user = User(username=username, email=email)
    user.hash_password(password)

    logger.info(f"Utilisateur créé: {user.username}")

    return user


def get_active_users(users: List[User]) -> List[User]:
    """Filtre les utilisateurs actifs.

    Args:
        users: Liste des utilisateurs à filtrer.

    Returns:
        Liste des utilisateurs actifs.
    """
    return [user for user in users if user.is_active]


if __name__ == "__main__":
    # Exemple d'utilisation
    try:
        new_user = create_user("test_user", "test@example.com", "password123")
        print(f"Utilisateur créé: {new_user.username}")
    except ValidationError as e:
        logger.error(f"Erreur de validation: {e}")
```

### Commandes pour Formater le Fichier Exemple

```bash
# 1. Formater avec Black
black --line-length=100 example.py

# 2. Trier les imports avec isort
isort --profile=black --line-length=100 example.py

# 3. Vérifier avec Flake8
flake8 example.py

# 4. Analyser avec Pylint
pylint example.py
```

### Configuration Complète des Fichiers

#### pyproject.toml (Configuration complète)

```toml
[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "mon-projet"
version = "1.0.0"
description = "Description du projet"
requires-python = ">=3.11"

[project.optional-dependencies]
dev = [
    "black>=23.0.0",
    "isort>=5.12.0",
    "flake8>=6.0.0",
    "pylint>=2.17.0",
    "flake8-docstrings>=1.7.0",
    "flake8-bugbear>=23.0.0",
    "flake8-black>=0.3.6",
    "pylint-django>=2.5.0",
]

# Configuration Black
[tool.black]
line-length = 100
target-version = ['py311']
include = '\.pyi?$'
exclude = '''
/(
      \.eggs
    | \.git
    | \.hg
    | \.mypy_cache
    | \.tox
    | \.venv
    | _build
    | buck-out
    | build
    | dist
    | migrations
    | venv
    | env
)/
'''

# Configuration isort
[tool.isort]
profile = "black"
line_length = 100
lines_between_sections = 1
lines_after_imports = 2
sections = ["FUTURE", "STDLIB", "THIRDPARTY", "FIRSTPARTY", "LOCALFOLDER"]
known_first_party = ["mon_projet"]
known_third_party = ["django", "requests", "pydantic", "sqlalchemy"]
multi_line_output = 3
include_trailing_comma = true
use_parentheses = true
force_sort_within_sections = true
skip = ["migrations", "venv", "env", ".git", "__pycache__"]
src_paths = ["src", "mon_projet"]

# Configuration pytest
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short"

# Configuration coverage
[tool.coverage.run]
source = ["mon_projet"]
omit = ["*/tests/*", "*/migrations/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
]
```

#### .pre-commit-config.yaml (Configuration complète)

```yaml
repos:
  # Black - Formatage automatique
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3.11
        args: [--line-length=100]
        exclude: ^(migrations/|venv/|env/)

  # isort - Tri des imports
  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: [--profile=black, --line-length=100]
        exclude: ^(migrations/|venv/|env/)

  # Flake8 - Linting
  - repo: https://github.com/pycqa/flake8
    rev: 6.1.0
    hooks:
      - id: flake8
        args: [--config=.flake8]
        additional_dependencies: 
          - flake8-docstrings
          - flake8-bugbear
          - flake8-black
          - flake8-isort
        exclude: ^(migrations/|venv/|env/)

  # Pylint - Analyse statique
  - repo: https://github.com/pycqa/pylint
    rev: v3.0.3
    hooks:
      - id: pylint
        args: [--rcfile=.pylintrc]
        additional_dependencies: 
          - pylint-django
          - pydantic
        exclude: ^(migrations/|venv/|env/)

  # Additional hooks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: [--maxkb=1000]
      - id: check-json
      - id: check-merge-conflict
      - id: debug-statements
```

### Intégration avec VS Code

#### settings.json (Configuration VS Code)

```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.pylintArgs": ["--rcfile=.pylintrc"],
  "python.linting.flake8Args": ["--config=.flake8"],
  
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length=100"],
  
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  
  "isort.args": ["--profile=black", "--line-length=100"],
  
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  }
}
```

### Commandes de Formatage en Masse

```bash
# Formater tous les fichiers Python
find . -name "*.py" -not -path "./venv/*" -not -path "./env/*" -not -path "./migrations/*" -exec black --line-length=100 {} \;

# Trier les imports de tous les fichiers
find . -name "*.py" -not -path "./venv/*" -not -path "./env/*" -not -path "./migrations/*" -exec isort --profile=black --line-length=100 {} \;

# Alternative avec xargs (plus rapide)
find . -name "*.py" -not -path "./venv/*" -not -path "./env/*" -not -path "./migrations/*" | xargs black --line-length=100
find . -name "*.py" -not -path "./venv/*" -not -path "./env/*" -not -path "./migrations/*" | xargs isort --profile=black --line-length=100
```

### Éviter les Erreurs Courantes

```python
# ❌ INCORRECT - Variable non utilisée
def ma_fonction():
    x = 10  # x n'est jamais utilisé
    return 5

# ✅ CORRECT
def ma_fonction():
    return 5


# ❌ INCORRECT - Exception trop générique
try:
    result = 1 / 0
except Exception:  # Trop générique
    pass

# ✅ CORRECT
try:
    result = 1 / 0
except ZeroDivisionError:
    logger.error("Division par zéro")


# ❌ INCORRECT - Variable redéfinie
def calculer(x):
    x = 10  # Redéfinition du paramètre
    return x

# ✅ CORRECT
def calculer(x):
    resultat = 10
    return resultat


# ❌ INCORRECT - Import wildcard
from module import *  # Ne pas faire

# ✅ CORRECT
from module import fonction_a, fonction_b
```

### Type Hints

```python
# ✅ CORRECT - Utilisation des type hints
from typing import List, Optional, Dict, Union

def calculer_somme(nombres: List[int]) -> int:
    """Calcule la somme d'une liste de nombres."""
    return sum(nombres)


def trouver_utilisateur(user_id: int) -> Optional[User]:
    """Trouve un utilisateur par son ID.
    
    Returns:
        L'utilisateur s'il existe, None sinon.
    """
    return User.objects.filter(id=user_id).first()


def traiter_donnees(data: Dict[str, Union[str, int]]) -> bool:
    """Traite les données fournies."""
    return True


# ❌ INCORRECT - Pas de type hints
def calculer_somme(nombres):
    return sum(nombres)
```

### Complexité Cyclomatique

```python
# ❌ INCORRECT - Complexité trop élevée (max-complexity: 10)
def traiter_commande(commande):
    if commande.type == "A":
        if commande.statut == "nouveau":
            if commande.priorite == "haute":
                traiter_urgent(commande)
            elif commande.priorite == "moyenne":
                traiter_normal(commande)
            else:
                traiter_bas(commande)
        elif commande.statut == "en_cours":
            verifier_progression(commande)
        else:
            archiver(commande)
    elif commande.type == "B":
        # ... encore plus de conditions
        pass
    # ... etc

# ✅ CORRECT - Refactoring avec des fonctions
class CommandeProcessor:
    def traiter(self, commande):
        handlers = {
            "A": self._traiter_type_a,
            "B": self._traiter_type_b,
        }
        handler = handlers.get(commande.type, self._traiter_defaut)
        return handler(commande)
    
    def _traiter_type_a(self, commande):
        if commande.statut == "nouveau":
            return self._traiter_nouveau(commande)
        elif commande.statut == "en_cours":
            return self._verifier_progression(commande)
        return self._archiver(commande)
    
    def _traiter_nouveau(self, commande):
        priorities = {
            "haute": traiter_urgent,
            "moyenne": traiter_normal,
        }
        handler = priorities.get(commande.priorite, traiter_bas)
        return handler(commande)
```

---

## 📊 Checklist Pré-Création de Fichier

Avant de créer ou modifier un fichier Python, vérifier :

- [ ] ✅ Le fichier suit la structure standard (imports, constantes, classes, fonctions)
- [ ] ✅ Les imports sont ordonnés avec isort (standard, third-party, local)
- [ ] ✅ Le formatage Black est appliqué (longueur de ligne 100)
- [ ] ✅ Les noms respectent les conventions (snake_case, PascalCase, UPPER_CASE)
- [ ] ✅ Les docstrings sont présentes pour les modules, classes et fonctions publiques
- [ ] ✅ Les lignes ne dépassent pas 100 caractères
- [ ] ✅ L'indentation utilise 4 espaces
- [ ] ✅ Les type hints sont utilisés pour les fonctions
- [ ] ✅ Pas de variables non utilisées
- [ ] ✅ Pas d'exceptions trop génériques
- [ ] ✅ La complexité cyclomatique est raisonnable (< 10)
- [ ] ✅ Pas de code dupliqué
- [ ] ✅ Pas de secrets ou credentials dans le code

### Workflow Recommandé

```bash
# 1. Après avoir écrit/modifié le fichier
black --line-length=100 mon_fichier.py

# 2. Trier les imports
isort --profile=black --line-length=100 mon_fichier.py

# 3. Vérifier avec Flake8
flake8 mon_fichier.py

# 4. Vérifier avec Pylint
pylint mon_fichier.py

# 5. Si tout est OK, commit
```

---

## 🛠️ Commandes de Vérification

### Script de Vérification Complet

```bash
#!/bin/bash
# lint-check.sh

echo "🔍 Vérification du code Python..."
echo "================================"

# Vérifier si les fichiers de config existent
if [ ! -f ".pylintrc" ]; then
    echo "⚠️  Fichier .pylintrc manquant"
fi

if [ ! -f ".flake8" ]; then
    echo "⚠️  Fichier .flake8 manquant"
fi

if [ ! -f "pyproject.toml" ]; then
    echo "⚠️  Fichier pyproject.toml manquant"
fi

echo ""
echo "📊 1/4 - Vérification du formatage avec Black..."
black --check --line-length=100 . || echo "❌ Black a détecté des problèmes de formatage"

echo ""
echo "📊 2/4 - Vérification de l'ordre des imports avec isort..."
isort --check-only --profile=black --line-length=100 . || echo "❌ isort a détecté des problèmes d'ordre des imports"

echo ""
echo "📊 3/4 - Exécution de Flake8..."
flake8 --config=.flake8 . || echo "❌ Flake8 a détecté des problèmes"

echo ""
echo "📊 4/4 - Exécution de Pylint..."
pylint --rcfile=.pylintrc . || echo "❌ Pylint a détecté des problèmes"

echo ""
echo "✅ Vérification terminée !"
echo ""
echo "💡 Pour corriger automatiquement :"
echo "   black --line-length=100 ."
echo "   isort --profile=black --line-length=100 ."
```

### Makefile

```makefile
# Makefile

.PHONY: lint lint-fix install-dev format format-check

install-dev:
	pip install -r requirements-dev.txt

# Vérification complète
lint:
	@echo "🔍 Vérification du formatage avec Black..."
	black --check --line-length=100 .
	@echo "🔍 Vérification de l'ordre des imports avec isort..."
	isort --check-only --profile=black --line-length=100 .
	@echo "🔍 Exécution de Flake8..."
	flake8 --config=.flake8 .
	@echo "🔍 Exécution de Pylint..."
	pylint --rcfile=.pylintrc .

# Formatage automatique
format:
	@echo "🎨 Formatage avec Black..."
	black --line-length=100 .
	@echo "📋 Tri des imports avec isort..."
	isort --profile=black --line-length=100 .
	@echo "✅ Formatage terminé !"

# Vérification du formatage sans modification
format-check:
	black --check --line-length=100 .
	isort --check-only --profile=black --line-length=100 .

# Correction automatique (legacy)
lint-fix:
	@echo "⚠️  Utilisez 'make format' pour le formatage automatique"
	@echo "🎨 Formatage avec Black et isort..."
	make format

# Statistiques
lint-stats:
	pylint --reports=yes .
	flake8 --statistics .
```

---

## 📚 Ressources

- [PEP 8 - Style Guide for Python Code](https://pep8.org/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Pylint Documentation](https://pylint.readthedocs.io/)
- [Flake8 Documentation](https://flake8.pycqa.org/)
- [Black Documentation](https://black.readthedocs.io/)
- [isort Documentation](https://pycqa.github.io/isort/)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

**Dernière mise à jour** : 2026-01-15  
**Version** : 1.0.0  
**Auteur** : Équipe Développement Python
