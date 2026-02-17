# Skill Séparation CSS/HTML dans Django

## 🎯 Objectif et Règle d'Or

Ce skill définit les bonnes pratiques pour séparer proprement le CSS du HTML dans les projets Django. **Il doit être consulté obligatoirement avant chaque création ou modification de templates ou fichiers CSS.**

### ⚠️ Règle d'Or

> **ZERO CSS inline dans les templates HTML. TOUT le CSS doit être dans des fichiers `.css` externes, sauf pour les styles dynamiques (couleurs générées côté serveur).**

---

## 📁 Structure de Fichiers Recommandée

```
mon_projet/
├── static/
│   └── css/
│       ├── base/                 # Styles de base
│       │   ├── reset.css         # Reset/normalize
│       │   ├── variables.css     # Variables CSS
│       │   └── typography.css    # Typographie
│       ├── components/           # Composants réutilisables
│       │   ├── buttons.css       # Boutons
│       │   ├── cards.css         # Cartes
│       │   ├── forms.css         # Formulaires
│       │   ├── modals.css        # Modals
│       │   ├── timeline.css      # Timeline
│       │   └── badges.css        # Badges
│       ├── pages/                # Styles spécifiques par page
│       │   ├── event_list.css    # Liste des événements
│       │   ├── event_detail.css  # Détail événement
│       │   └── dashboard.css     # Tableau de bord
│       ├── utilities/            # Utilitaires CSS
│       │   ├── animations.css    # Animations
│       │   ├── helpers.css       # Classes utilitaires
│       │   └── responsive.css    # Media queries
│       └── main.css              # Point d'entrée principal
└── templates/
    ├── base.html                 # Template de base
    └── ...
```

---

## ⚙️ Configuration Django

### Configuration des Fichiers Statiques

```python
# settings/base.py

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Pour le développement
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]
```

### Template de Base avec Structure CSS

```html
<!-- templates/base.html -->
<!DOCTYPE html>
<html lang="{{ LANGUAGE_CODE }}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Mon Application{% endblock %}</title>
    
    <!-- CSS Global -->
    <link rel="stylesheet" href="{% static 'css/main.css' %}">
    {% block extra_css %}{% endblock %}
</head>
<body>
    {% block content %}{% endblock %}
    
    {% block extra_js %}{% endblock %}
</body>
</html>
```

---

## ✅ Bonnes Pratiques avec Exemples

### 1. Jamais de CSS Inline (sauf styles dynamiques)

❌ **INCORRECT - CSS inline dans le template**

```html
<!-- templates/events/event_list.html -->
<div style="background-color: #3b82f6; padding: 20px; border-radius: 8px;">
    <h1 style="color: white; font-size: 24px;">Événements</h1>
</div>

<style>
    .event-card {
        background: white;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .event-card:hover {
        transform: translateY(-4px);
    }
</style>
```

✅ **CORRECT - CSS dans un fichier externe**

```html
<!-- templates/events/event_list.html -->
{% extends 'base.html' %}
{% load static %}

{% block extra_css %}
<link rel="stylesheet" href="{% static 'css/pages/event_list.css' %}">
{% endblock %}

{% block content %}
<div class="event-header">
    <h1 class="event-title">Événements</h1>
</div>

<div class="event-card">
    <!-- Contenu -->
</div>
{% endblock %}
```

```css
/* static/css/pages/event_list.css */

/* Header des événements */
.event-header {
    background-color: var(--color-primary);
    padding: var(--spacing-lg);
    border-radius: var(--radius-md);
}

.event-title {
    color: white;
    font-size: var(--font-size-xl);
}

/* Cartes d'événements */
.event-card {
    background: white;
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-md);
    transition: transform var(--transition-fast);
}

.event-card:hover {
    transform: translateY(-4px);
}
```

### 2. Organisation des Fichiers CSS

#### Variables CSS (Custom Properties)

```css
/* static/css/base/variables.css */

:root {
    /* Couleurs */
    --color-primary: #3b82f6;
    --color-primary-dark: #2563eb;
    --color-success: #22c55e;
    --color-warning: #f59e0b;
    --color-danger: #ef4444;
    
    /* Tailwind-like colors */
    --slate-50: #f8fafc;
    --slate-100: #f1f5f9;
    --slate-200: #e2e8f0;
    --slate-300: #cbd5e1;
    --slate-400: #94a3b8;
    --slate-500: #64748b;
    --slate-600: #475569;
    --slate-700: #334155;
    --slate-800: #1e293b;
    --slate-900: #0f172a;
    
    /* Espacements */
    --spacing-xs: 0.25rem;
    --spacing-sm: 0.5rem;
    --spacing-md: 1rem;
    --spacing-lg: 1.5rem;
    --spacing-xl: 2rem;
    
    /* Typographie */
    --font-size-sm: 0.875rem;
    --font-size-base: 1rem;
    --font-size-lg: 1.125rem;
    --font-size-xl: 1.5rem;
    --font-size-2xl: 2rem;
    
    /* Bordures */
    --radius-sm: 0.25rem;
    --radius-md: 0.5rem;
    --radius-lg: 0.75rem;
    --radius-xl: 1rem;
    --radius-full: 9999px;
    
    /* Ombres */
    --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    
    /* Transitions */
    --transition-fast: 150ms ease;
    --transition-base: 200ms ease;
    --transition-slow: 300ms ease;
}
```

#### Composants Réutilisables

```css
/* static/css/components/cards.css */

/* Card de base */
.card {
    background: white;
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-md);
    overflow: hidden;
    transition: all var(--transition-base);
}

.card:hover {
    box-shadow: var(--shadow-lg);
}

/* Card avec bordure colorée */
.card-border-left {
    border-left-width: 4px;
    border-left-style: solid;
}

.card-border-success { border-left-color: var(--color-success); }
.card-border-warning { border-left-color: var(--color-warning); }
.card-border-danger { border-left-color: var(--color-danger); }

/* Timeline Card */
.timeline-card {
    position: relative;
    overflow: visible !important;
}

/* Event Card spécifique */
.event-card {
    composes: card;
    display: flex;
    flex-direction: column;
}

.event-card__header {
    padding: var(--spacing-md);
    border-bottom: 1px solid var(--slate-200);
}

.event-card__body {
    padding: var(--spacing-md);
    flex: 1;
}

.event-card__footer {
    padding: var(--spacing-md);
    border-top: 1px solid var(--slate-200);
    display: flex;
    justify-content: space-between;
    align-items: center;
}
```

```css
/* static/css/components/badges.css */

.badge {
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    padding: 0.25rem 0.625rem;
    border-radius: var(--radius-full);
    font-size: 0.6875rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.025em;
    transition: all var(--transition-base);
}

.badge__icon {
    width: 14px;
    height: 14px;
}

/* Variantes de badges */
.badge--success {
    background-color: rgb(34 197 94 / 0.1);
    color: rgb(21 128 61);
}

.badge--warning {
    background-color: rgb(245 158 11 / 0.1);
    color: rgb(180 83 9);
}

.badge--danger {
    background-color: rgb(239 68 68 / 0.1);
    color: rgb(185 28 28);
}

.badge--info {
    background-color: rgb(59 130 246 / 0.1);
    color: rgb(29 78 216);
}

/* Badge avec tooltip */
.badge--tooltip {
    cursor: help;
    position: relative;
}
```

```css
/* static/css/components/timeline.css */

.timeline {
    position: relative;
}

.timeline__line {
    position: absolute;
    top: 2rem;
    left: 0;
    right: 0;
    height: 2px;
    background-color: var(--slate-200);
}

.timeline__container {
    display: flex;
    gap: 1.5rem;
    overflow-x: auto;
    scroll-behavior: smooth;
    scrollbar-width: thin;
    scrollbar-color: var(--slate-300) transparent;
    padding-bottom: 1rem;
}

.timeline__container::-webkit-scrollbar {
    height: 6px;
}

.timeline__container::-webkit-scrollbar-track {
    background: transparent;
}

.timeline__container::-webkit-scrollbar-thumb {
    background-color: var(--slate-300);
    border-radius: 3px;
}

.timeline__container::-webkit-scrollbar-thumb:hover {
    background-color: var(--slate-400);
}

.timeline__item {
    position: relative;
    flex-shrink: 0;
    width: 16rem;
}

.timeline__point {
    position: absolute;
    top: 1.5rem;
    left: 50%;
    transform: translateX(-50%);
    width: 1rem;
    height: 1rem;
    border-radius: 50%;
    border: 2px solid white;
    box-shadow: var(--shadow-sm);
    z-index: 10;
}

.timeline__date {
    text-align: center;
    margin-bottom: 1.5rem;
}

.timeline__date-day {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--slate-900);
}

.timeline__date-month {
    font-size: 0.875rem;
    color: var(--slate-500);
    text-transform: uppercase;
}

/* Navigation flèches */
.timeline__nav {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    width: 40px;
    height: 40px;
    background: white;
    border: 1px solid var(--slate-200);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    box-shadow: var(--shadow-md);
    transition: all var(--transition-base);
    z-index: 20;
}

.timeline__nav:hover {
    background: var(--slate-50);
    transform: translateY(-50%) scale(1.1);
}

.timeline__nav:focus {
    outline: 2px solid var(--color-primary);
    outline-offset: 2px;
}

.timeline__nav--left {
    left: -10px;
}

.timeline__nav--right {
    right: -10px;
}
```

#### Animations

```css
/* static/css/utilities/animations.css */

/* Keyframes */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes fadeInLeft {
    from {
        opacity: 0;
        transform: translateX(-20px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

@keyframes pulse {
    0%, 100% {
        opacity: 1;
    }
    50% {
        opacity: 0.5;
    }
}

/* Classes d'animation */
.animate-fade-in-up {
    animation: fadeInUp 0.5s ease-out forwards;
}

.animate-fade-in-left {
    animation: fadeInLeft 0.4s ease-out forwards;
}

.animate-pulse {
    animation: pulse 2s infinite;
}

/* Délais */
.delay-100 { animation-delay: 100ms; }
.delay-200 { animation-delay: 200ms; }
.delay-300 { animation-delay: 300ms; }
.delay-400 { animation-delay: 400ms; }
.delay-500 { animation-delay: 500ms; }
```

#### Tooltips

```css
/* static/css/components/tooltips.css */

.tooltip-container {
    position: relative;
}

.tooltip {
    position: absolute;
    bottom: 100%;
    left: 50%;
    transform: translateX(-50%) translateY(-8px);
    padding: 0.5rem 0.75rem;
    background-color: var(--slate-900);
    color: white;
    font-size: 0.75rem;
    font-weight: 500;
    white-space: nowrap;
    border-radius: var(--radius-md);
    opacity: 0;
    visibility: hidden;
    transition: all var(--transition-base);
    z-index: 9999;
    box-shadow: var(--shadow-lg);
    pointer-events: none;
    min-width: max-content;
}

.tooltip::after {
    content: '';
    position: absolute;
    top: 100%;
    left: 50%;
    transform: translateX(-50%);
    border-width: 5px;
    border-style: solid;
    border-color: var(--slate-900) transparent transparent transparent;
}

.tooltip-container:hover .tooltip,
.tooltip-container:focus .tooltip,
.tooltip-container:focus-within .tooltip {
    opacity: 1;
    visibility: visible;
    transform: translateX(-50%) translateY(-4px);
}
```

### 3. Gestion des Styles Dynamiques

✅ **CORRECT - Styles dynamiques avec inline style pour les couleurs uniquement**

```html
<!-- templates/events/event_list.html -->
{% for event in upcoming_events %}
<article class="timeline-item">
    <!-- Point coloré dynamique -->
    <div class="timeline-point"
         style="background-color: {{ first_sector.color_code|default:'#64748b' }};">
    </div>
    
    <!-- Badge avec couleur dynamique -->
    <span class="badge"
          style="background-color: {{ first_sector.color_code }}20; 
                 color: {{ first_sector.color_code }}; 
                 border: 1px solid {{ first_sector.color_code }}40;">
        {{ first_sector.name }}
    </span>
</article>
{% endfor %}
```

```css
/* static/css/pages/event_list.css */
/* Tout le reste des styles statiques ici */

.timeline-point {
    position: absolute;
    top: 1.5rem;
    left: 50%;
    transform: translateX(-50%);
    width: 1rem;
    height: 1rem;
    border-radius: 50%;
    border: 2px solid white;
    box-shadow: var(--shadow-sm);
    z-index: 10;
    /* background-color est défini inline dans le HTML */
}

.badge {
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    padding: 0.25rem 0.625rem;
    border-radius: var(--radius-full);
    font-size: 0.6875rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.025em;
    /* background-color, color, border définis inline */
}
```

### 4. Point d'Entrée Principal

```css
/* static/css/main.css */

/* 1. Base */
@import 'base/variables.css';
@import 'base/reset.css';
@import 'base/typography.css';

/* 2. Composants */
@import 'components/buttons.css';
@import 'components/cards.css';
@import 'components/badges.css';
@import 'components/forms.css';
@import 'components/timeline.css';
@import 'components/tooltips.css';

/* 3. Utilitaires */
@import 'utilities/animations.css';
@import 'utilities/helpers.css';
@import 'utilities/responsive.css';

/* 4. Pages (chargés conditionnellement dans les templates) */
/* @import 'pages/event_list.css'; */
/* @import 'pages/event_detail.css'; */
```

---

## 📝 Exemple Complet : Page Event List

### Structure des Fichiers

```
templates/
└── events/
    └── event_list.html

static/
└── css/
    ├── pages/
    │   └── event_list.css
    └── main.css
```

### Template Optimisé

```html
<!-- templates/events/event_list.html -->
{% extends 'base.html' %}
{% load static %}

{% block extra_css %}
<link rel="stylesheet" href="{% static 'css/pages/event_list.css' %}">
{% endblock %}

{% block content %}
<!-- Skip link pour accessibilité -->
<a href="#main-content" class="skip-link">Aller au contenu principal</a>

<div id="main-content" class="container">
    <!-- Header -->
    <header class="page-header animate-fade-in-up" role="banner">
        <div class="page-header__content">
            <div>
                <h1 class="page-title" id="page-title">Événements</h1>
                <p class="page-subtitle">Découvrez tous les événements</p>
            </div>
            {% if user.is_authenticated %}
            <a href="{% url 'events:event_create' %}" class="btn btn-primary">
                Créer un événement
            </a>
            {% endif %}
        </div>
    </header>

    <!-- Timeline -->
    {% if upcoming_events %}
    <section class="timeline-section animate-fade-in-up delay-200" aria-labelledby="upcoming-title">
        <div class="timeline">
            <div class="timeline__line" aria-hidden="true"></div>
            
            <button type="button" class="timeline__nav timeline__nav--left" id="scrollLeft">
                ←
            </button>
            <button type="button" class="timeline__nav timeline__nav--right" id="scrollRight">
                →
            </button>
            
            <div class="timeline__container" id="timelineContainer">
                {% for event in upcoming_events %}
                {% with first_sector=event.sectors.first %}
                <article class="timeline__item animate-fade-in-left delay-{{ forloop.counter|add:2|divisibleby:5 }}00"
                         style="animation-delay: {{ forloop.counter0 }}00ms;">
                    <div class="timeline__point"
                         style="background-color: {{ first_sector.color_code|default:'#64748b' }};">
                    </div>
                    
                    <div class="timeline__date">
                        <span class="timeline__date-day">{{ event.start_datetime|date:"d" }}</span>
                        <span class="timeline__date-month">{{ event.start_datetime|date:"M" }}</span>
                    </div>
                    
                    <div class="card card-border-left {% if event.validation.is_validated %}card-border-success{% elif event.validation %}card-border-danger{% else %}card-border-warning{% endif %}">
                        <!-- Contenu de la carte -->
                    </div>
                </article>
                {% endwith %}
                {% endfor %}
            </div>
        </div>
    </section>
    {% endif %}
</div>
{% endblock %}

{% block extra_js %}
<script src="{% static 'js/pages/event_list.js' %}"></script>
{% endblock %}
```

### CSS de la Page

```css
/* static/css/pages/event_list.css */

/* Header de page */
.page-header {
    margin-bottom: var(--spacing-xl);
}

.page-header__content {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
}

@media (min-width: 640px) {
    .page-header__content {
        flex-direction: row;
        align-items: center;
        justify-content: space-between;
    }
}

.page-title {
    font-size: var(--font-size-2xl);
    font-weight: 700;
    color: var(--slate-900);
}

.page-subtitle {
    margin-top: 0.25rem;
    color: var(--slate-600);
}

/* Section Timeline */
.timeline-section {
    margin-bottom: var(--spacing-xl);
}

/* Légende */
.legend {
    margin-top: var(--spacing-lg);
    background-color: var(--slate-50);
    border-radius: var(--radius-lg);
    padding: var(--spacing-md);
    border: 1px solid var(--slate-200);
}

.legend__title {
    font-size: var(--font-size-sm);
    font-weight: 600;
    color: var(--slate-700);
    margin-bottom: var(--spacing-md);
}

.legend__items {
    display: flex;
    flex-wrap: wrap;
    gap: var(--spacing-md);
    font-size: 0.75rem;
}

/* Skip link */
.skip-link {
    position: absolute;
    top: -40px;
    left: 0;
    background: var(--slate-800);
    color: white;
    padding: var(--spacing-sm);
    text-decoration: none;
    z-index: 10000;
    transition: top var(--transition-fast);
}

.skip-link:focus {
    top: 0;
}
```

---

## ⚡ Exceptions Acceptables

### Cas où le CSS inline est toléré

✅ **CORRECT - Styles dynamiques depuis Django**

```html
<!-- Couleurs dynamiques -->
<div style="background-color: {{ sector.color_code }};"></div>

<!-- Positions dynamiques -->
<div style="left: {{ progress }}%;"></div>

<!-- Valeurs calculées -->
<div style="width: {{ percentage }}%;"></div>
```

❌ **À ÉVITER - Styles statiques inline**

```html
<!-- Ne jamais faire ça -->
<div style="padding: 20px; margin: 10px; border-radius: 8px;">
```

---

## ✅ Checklist Pré-Création

Avant de créer ou modifier un fichier template ou CSS :

- [ ] **Zero CSS inline** - Tout le CSS statique est dans des fichiers `.css` externes
- [ ] **Variables CSS** - Utilisation de custom properties pour la cohérence
- [ ] **Structure claire** - Les fichiers CSS sont organisés (base/components/pages/utilities)
- [ ] **Composants réutilisables** - Extraction des patterns communs
- [ ] **Styles dynamiques uniquement** - Seules les valeurs générées côté serveur sont inline
- [ ] **Responsive** - Media queries pour les différents breakpoints
- [ ] **Accessibilité** - Focus visible, contrastes suffisants
- [ ] **Performance** - Fichiers CSS regroupés et minifiés en production

---

## 🔍 Commandes de Vérification

### Vérifier l'absence de CSS inline

```bash
# Rechercher les balises style dans les templates
find templates -name "*.html" -exec grep -l "<style>" {} \;

# Rechercher les attributs style (exclure les variables Django)
grep -r "style=\"" templates/ --include="*.html" | grep -v "{{\|{%"

# Compter les lignes de CSS inline
grep -r "<style" templates/ --include="*.html" -A 100 | wc -l
```

### Vérifier la structure CSS

```bash
# Lister les fichiers CSS par catégorie
echo "=== Base ==="
find static/css/base -name "*.css" 2>/dev/null | sort

echo "=== Components ==="
find static/css/components -name "*.css" 2>/dev/null | sort

echo "=== Pages ==="
find static/css/pages -name "*.css" 2>/dev/null | sort

echo "=== Utilities ==="
find static/css/utilities -name "*.css" 2>/dev/null | sort
```

### Vérifier l'utilisation des variables CSS

```bash
# Compter les variables CSS utilisées
grep -r "var(--" static/css --include="*.css" | wc -l

# Vérifier que les variables sont définies
grep -r "--" static/css/base/variables.css | wc -l
```

---

## 📚 Ressources

### Documentation Officielle

- [Django Static Files](https://docs.djangoproject.com/en/5.1/howto/static-files/)
- [CSS Custom Properties](https://developer.mozilla.org/en-US/docs/Web/CSS/--*)
- [BEM Methodology](http://getbem.com/introduction/)

### Articles et Tutoriels

- [Organizing CSS in Django](https://www.mattlayman.com/blog/2020/django-css/)
- [CSS Architecture](https://philipwalton.com/articles/css-architecture/)
- [CUBE CSS](https://cube.fyi/)

### Outils Recommandés

- **PostCSS** - Transformation CSS moderne
- **Autoprefixer** - Préfixes navigateurs automatiques
- **PurgeCSS** - Suppression du CSS inutilisé
- **Stylelint** - Linter CSS

---

**Dernière mise à jour** : 2026-02-11
**Version** : 1.0.0
**Auteur** : Équipe Développement Django
