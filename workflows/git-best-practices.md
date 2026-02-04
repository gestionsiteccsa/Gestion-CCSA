# Skill Git - Bonnes Pratiques et Conventions

## 🎯 Objectif

Ce skill définit les conventions et bonnes pratiques Git à suivre pour maintenir un historique de code propre, lisible et traçable. **Il doit être consulté obligatoirement avant chaque commit.**

## ⚠️ Règle d'Or

> **AUCUN commit ne doit être effectué sans suivre ces conventions.**

---

## 📋 Convention de Nommage des Commits

### Format Standard

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types de Commit

| Type | Description | Quand l'utiliser |
|------|-------------|------------------|
| `feat` | Nouvelle fonctionnalité | Ajout d'une nouvelle feature |
| `fix` | Correction de bug | Résolution d'un bug existant |
| `docs` | Documentation | Changements dans la documentation |
| `style` | Style de code | Formatage, point-virgules, etc. (pas de changement de code) |
| `refactor` | Refactoring | Restructuration du code sans changer le comportement |
| `perf` | Performance | Amélioration des performances |
| `test` | Tests | Ajout ou modification de tests |
| `chore` | Tâches diverses | Maintenance, build, dépendances |
| `ci` | Intégration continue | Changements dans les workflows CI/CD |
| `security` | Sécurité | Corrections de vulnérabilités |

### Exemples de Commits

```bash
# ✅ CORRECT - Feature avec scope
feat(auth): add OAuth2 login with Google

# ✅ CORRECT - Fix simple
fix(api): resolve null pointer exception in user endpoint

# ✅ CORRECT - Avec body détaillé
feat(database): implement connection pooling

Add connection pooling using SQLAlchemy's QueuePool to improve
performance under high load. Default pool size set to 10 with
overflow of 20.

Closes #123

# ✅ CORRECT - Breaking change
feat(api): change response format for /users endpoint

BREAKING CHANGE: response now returns paginated format instead
of full list. Update your integrations accordingly.

# ❌ INCORRECT - Message trop vague
fix: bug

# ❌ INCORRECT - Type incorrect
update: new feature

# ❌ INCORRECT - Majuscules dans le subject
feat: Add new Button component

# ❌ INCORRECT - Point à la fin
fix: resolve login issue.
```

---

## 🌿 Stratégie de Branching

### Branches Principales

| Branche | Description | Protection |
|---------|-------------|------------|
| `main` | Code en production | ✅ Protégée - merge via PR uniquement |
| `develop` | Branche de développement | ✅ Protégée - merge via PR uniquement |

### Branches de Feature

**Format :** `type/description-courte`

```bash
# ✅ CORRECT
feature/user-authentication
feat/oauth-integration
fix/memory-leak-dashboard
hotfix/critical-security-patch

# ❌ INCORRECT
feature
new-stuff
fix-bug-123
```

### Workflow Git Flow

```
main (production)
  │
  ├── develop (intégration)
  │     │
  │     ├── feature/nouvelle-fonctionnalite
  │     │     │
  │     │     └── (commits)
  │     │
  │     ├── feature/autre-fonctionnalite
  │     │     │
  │     │     └── (commits)
  │     │
  │     └── (merge via PR)
  │
  └── hotfix/correction-urgente
        │
        └── (merge vers main ET develop)
```

---

## 🔄 Workflow de Commit

### Avant chaque commit

```bash
# 1. Vérifier les fichiers modifiés
git status

# 2. Reviewer les changements
git diff

# 3. Stage uniquement les fichiers pertinents
git add <fichiers-spécifiques>

# ❌ Éviter
git add .  # Saufs cas exceptionnels
```

### Rédaction du message

**Subject (ligne 1) :**
- Maximum 50 caractères
- Commence par le type
- Utiliser l'impératif présent ("add" pas "added" ou "adds")
- Pas de majuscule au début
- Pas de point à la fin

**Body (optionnel) :**
- Séparé du subject par une ligne vide
- Explique le "pourquoi" pas le "quoi"
- Maximum 72 caractères par ligne
- Peut inclure des références aux issues

**Footer (optionnel) :**
- Références d'issues : `Closes #123`, `Fixes #456`
- Breaking changes : `BREAKING CHANGE: description`

### Exemple Complet

```bash
feat(payment): implement Stripe integration

Add Stripe payment gateway support for credit card processing.
Includes webhook handling for payment confirmations and
automatic invoice generation.

- Add Stripe SDK dependency
- Create PaymentIntent service
- Implement webhook verification middleware
- Add payment status tracking

Closes #234
```

---

## 📝 Messages de Commit par Type

### Feature (`feat`)

```bash
feat(scope): add <what-it-does>

# Exemples :
feat(auth): add JWT token refresh mechanism
feat(api): implement rate limiting
feat(ui): add dark mode toggle
```

### Fix (`fix`)

```bash
fix(scope): resolve <what-was-fixed>

# Exemples :
fix(database): resolve connection timeout issue
fix(api): correct validation error response
fix(ui): fix button alignment on mobile
```

### Documentation (`docs`)

```bash
docs(scope): update <what-was-documented>

# Exemples :
docs(api): add authentication endpoints documentation
docs(readme): update installation instructions
docs(changelog): add version 2.0.0 changes
```

### Refactoring (`refactor`)

```bash
refactor(scope): restructure <what-was-refactored>

# Exemples :
refactor(services): extract payment logic to separate module
refactor(models): normalize database schema
refactor(tests): reorganize test directory structure
```

### Tests (`test`)

```bash
test(scope): add tests for <what-is-tested>

# Exemples :
test(auth): add unit tests for login flow
test(api): add integration tests for user endpoints
test(utils): improve coverage for date helpers
```

### Performance (`perf`)

```bash
perf(scope): improve <what-was-optimized>

# Exemples :
perf(queries): optimize database queries with indexing
perf(caching): implement Redis cache for user sessions
perf(assets): compress images and enable lazy loading
```

---

## 🔀 Pull Requests

### Titre du PR

```
[type]: Brief description of changes

# Exemples :
[Feature]: Implement user authentication system
[Fix]: Resolve memory leak in dashboard
[Refactor]: Restructure API error handling
```

### Template de Description

```markdown
## Description
Brief description of what this PR does.

## Changes Made
- Change 1
- Change 2
- Change 3

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)

## Related Issues
Closes #123
Relates to #456

## Screenshots (if applicable)
[Add screenshots here]
```

### Process de Review

1. **Créer la PR** avec une description complète
2. **Assigner des reviewers** (minimum 1)
3. **Attendre les approvals** avant merge
4. **Résoudre les commentaires**
5. **Squash merge** si nécessaire (garder l'historique propre)

---

## 🏷️ Gestion des Versions (Semantic Versioning)

### Format : `MAJOR.MINOR.PATCH`

| Version | Quand incrémenter | Exemple de commit |
|---------|-------------------|-------------------|
| **MAJOR** | Breaking changes | `feat(api)!: change response format` |
| **MINOR** | Nouvelles features | `feat(auth): add OAuth support` |
| **PATCH** | Bug fixes | `fix(api): resolve null pointer` |

### Tags Git

```bash
# Créer un tag de version
git tag -a v1.2.0 -m "Release version 1.2.0"

# Pusher les tags
git push origin v1.2.0

# Lister les tags
git tag -l
```

---

## 🧹 Maintenance du Repository

### Nettoyage régulier

```bash
# Supprimer les branches locales mergées
git branch --merged | grep -v "\*\|main\|develop" | xargs -n 1 git branch -d

# Nettoyer les branches distantes obsolètes
git fetch --prune

# Supprimer les branches locales sans tracking
git branch -vv | grep ': gone]' | grep -v \* | xargs -n 1 git branch -D
```

### Historique Propre

```bash
# Rebaser avant de pusher (si travail solo sur la branche)
git pull --rebase origin develop

# Squash des commits avant merge
git rebase -i HEAD~3  # Squash les 3 derniers commits

# Modifier le dernier commit
git commit --amend

# ⚠️ Ne jamais amend/rebase sur des commits déjà pushés
```

---

## 🚨 Interdictions

### ❌ Ne JAMAIS faire

```bash
# Push forcé sur main/develop
git push --force origin main

# Commit de fichiers sensibles
git add .env credentials.json

# Commit de fichiers générés
*.pyc
node_modules/
dist/

# Messages de commit vagues
git commit -m "fix"
git commit -m "update"
git commit -m "WIP"

# Commit de code qui ne compile/passe pas les tests
git commit -m "feat: add feature"  # alors que tests échouent
```

---

## 📊 Checklist Pré-Commit

Avant chaque commit, vérifier :

- [ ] ✅ Les fichiers staged sont pertinents
- [ ] ✅ Le message suit la convention `<type>(<scope>): <subject>`
- [ ] ✅ Le subject est en impératif présent
- [ ] ✅ Pas de majuscule au début du subject
- [ ] ✅ Pas de point à la fin du subject
- [ ] ✅ Le body explique le "pourquoi" si nécessaire
- [ ] ✅ Les références d'issues sont incluses
- [ ] ✅ Le code compile/passe les tests
- [ ] ✅ Pas de secrets ou credentials dans les fichiers
- [ ] ✅ Pas de fichiers générés ou temporaires

---

## 🛠️ Configuration Git Recommandée

### Configuration globale

```bash
# Nom et email
git config --global user.name "Votre Nom"
git config --global user.email "votre.email@example.com"

# Éditeur par défaut
git config --global core.editor "code --wait"  # VS Code
git config --global core.editor "nano"         # Nano

# Alias utiles
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.lg "log --oneline --graph --decorate"
git config --global alias.last "log -1 HEAD"
git config --global alias.unstage "reset HEAD --"
git config --global alias.visual "!gitk"

# Push par défaut sur la branche courante
git config --global push.default current

# Rebase par défaut sur pull
git config --global pull.rebase true

# Gestion des fins de ligne (Windows)
git config --global core.autocrlf true

# Gestion des fins de ligne (Mac/Linux)
git config --global core.autocrlf input
```

### Hooks Git (Optionnel)

**pre-commit** - Vérifications avant commit :

```bash
#!/bin/sh
# .git/hooks/pre-commit

# Vérifier le format du message
commit_msg_file=$1
commit_msg=$(cat $commit_msg_file)

# Regex pour valider le format
if ! echo "$commit_msg" | grep -qE "^(feat|fix|docs|style|refactor|perf|test|chore|ci|security)(\(.+\))?: .+"; then
    echo "❌ Commit message format invalide !"
    echo "Format attendu: <type>(<scope>): <subject>"
    echo "Types: feat, fix, docs, style, refactor, perf, test, chore, ci, security"
    exit 1
fi

echo "✅ Commit message valide"
exit 0
```

---

## 📝 Exemples de Scénarios

### Scénario 1 : Nouvelle Feature

```bash
# 1. Créer une branche
git checkout -b feature/user-profile

# 2. Faire des commits réguliers
git add src/components/Profile.tsx
git commit -m "feat(profile): add user profile component"

git add src/api/user.ts
git commit -m "feat(api): add user profile endpoints"

# 3. Pousser la branche
git push -u origin feature/user-profile

# 4. Créer une Pull Request
# (via GitHub/GitLab interface)

# 5. Après review et merge, nettoyer
git checkout develop
git pull origin develop
git branch -d feature/user-profile
```

### Scénario 2 : Correction de Bug Urgent

```bash
# 1. Créer une branche hotfix depuis main
git checkout main
git pull origin main
git checkout -b hotfix/critical-login-bug

# 2. Corriger le bug et commit
git add src/auth/login.ts
git commit -m "fix(auth): resolve critical login vulnerability

Fix SQL injection vulnerability in login endpoint.
Added parameterized queries to prevent injection attacks.

Security: CVE-2024-XXXX"

# 3. Pousser et créer PR vers main
git push -u origin hotfix/critical-login-bug

# 4. Après merge dans main, merger aussi dans develop
git checkout develop
git merge main
```

### Scénario 3 : Commit avec Breaking Change

```bash
git add src/api/routes.ts
git commit -m "feat(api): change user response format

BREAKING CHANGE: The /api/users endpoint now returns a paginated
response instead of a full list. The response structure has
changed from:

  { users: [...] }

to:

  {
    data: [...],
    pagination: {
      page: 1,
      per_page: 20,
      total: 100
    }
  }

Update your integrations accordingly.

Closes #456"
```

---

## 📚 Ressources

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/)
- [Semantic Versioning](https://semver.org/)
- [GitHub Flow](https://docs.github.com/en/get-started/quickstart/github-flow)
- [GitLab Flow](https://docs.gitlab.com/ee/topics/gitlab_flow.html)

---

**Dernière mise à jour** : 2026-01-15  
**Version** : 1.0.0  
**Auteur** : Équipe Développement
