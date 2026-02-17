# Changelog

Tous les changements notables de ce projet seront documentés dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère à [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.0] - 2026-02-09

### 🔒 Sécurité

- **CRITIQUE** : Correction de vulnérabilités XSS dans les templates
  - `event_detail.html` : Échappement des descriptions et commentaires
  - `video_request.html` : Échappement des variables dans les emails
  - `communication_dashboard.html` : Protection contre l'injection JavaScript dans Chart.js
- **ÉLEVÉ** : Ajout de l'échappement ICS selon RFC 5545 pour les fichiers de calendrier
- **MOYEN** : Implémentation du rate limiting sur les endpoints de notifications
  - `notification_mark_read` : 10 requêtes/minute
  - `notification_mark_all_read` : 5 requêtes/minute
- **MOYEN** : Validation robuste des entrées utilisateur dans le dashboard
  - Validation des dates personnalisées
  - Limite de période à 2 ans maximum
  - Messages d'erreur utilisateur appropriés

### ⚡ Performance

- **ÉLEVÉ** : Optimisation des requêtes N+1 dans le dashboard
  - Réduction de 50+ requêtes SQL à 1 requête pour les statistiques par secteur
  - Utilisation de `annotate()` et `Count()` de Django ORM
- **MOYEN** : Mise en place du caching pour les villes dans EventListView
  - Cache de 1 heure avec clé basée sur le rôle utilisateur
  - Réduction drastique des requêtes répétées
- **MOYEN** : Ajout de `transaction.atomic()` pour la duplication d'événements
  - Garantie d'intégrité des données
  - Rollback automatique en cas d'erreur

### 🧪 Tests

- Configuration complète de pytest avec 80% de couverture minimale requise
- Ajout de tests de sécurité XSS
- Ajout de tests pour les fonctionnalités de tournage vidéo
- Ajout de tests pour le rate limiting

### 📚 Documentation

- Création du CHANGELOG.md (ce fichier)
- Création du SECURITY.md avec les bonnes pratiques
- Mise à jour du README.md avec les nouvelles fonctionnalités

### 🔧 Maintenance

- Audit de sécurité complet avec Bandit (aucune vulnérabilité critique trouvée)
- Corrections de bugs mineurs
- Amélioration de la gestion des erreurs

## [1.0.0] - 2026-01-15

### 🎉 Première version stable

- Gestion complète des événements (CRUD)
- Système de validation par l'équipe Communication
- Gestion des secteurs d'activité
- Système de notifications
- Authentification et autorisation par rôles
- Upload de documents et images
- Dashboard statistiques pour l'équipe Communication
- Système de demande de tournage vidéo
- Génération de fichiers ICS
- Recurrence d'événements
- Gestion des commentaires

---

## Types de changements

- `🔒 Sécurité` : Correction de vulnérabilités de sécurité
- `⚡ Performance` : Améliorations de performance
- `🐛 Corrections` : Correction de bugs
- `✨ Fonctionnalités` : Nouvelles fonctionnalités
- `🔄 Changements` : Changements comportementaux
- `🗑️ Dépréciations` : Fonctionnalités dépréciées
- `⛔ Retraits` : Fonctionnalités supprimées
- `📚 Documentation` : Changements de documentation
