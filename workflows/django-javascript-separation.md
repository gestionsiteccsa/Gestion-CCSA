# Skill Séparation JavaScript/HTML dans Django

## 🎯 Objectif et Règle d'Or

Ce skill définit les bonnes pratiques pour séparer proprement le JavaScript du HTML dans les projets Django. **Il doit être consulté obligatoirement avant chaque création ou modification de templates ou fichiers JavaScript.**

### ⚠️ Règle d'Or

> **ZERO JavaScript inline dans les templates HTML. TOUT le JavaScript doit être dans des fichiers `.js` externes.**

---

## 📁 Structure de Fichiers Recommandée

```
mon_projet/
├── static/
│   └── js/
│       ├── modules/              # Modules JS réutilisables
│       │   ├── forms.js          # Gestion des formulaires
│       │   ├── validators.js     # Validation côté client
│       │   ├── api.js            # Appels API
│       │   └── ui.js             # Manipulation UI
│       ├── pages/                # Scripts spécifiques par page
│       │   ├── article_form.js   # JS pour la création d'articles
│       │   ├── user_profile.js   # JS pour le profil utilisateur
│       │   └── dashboard.js      # JS pour le tableau de bord
│       ├── components/           # Composants JS réutilisables
│       │   ├── modal.js          # Gestion des modals
│       │   ├── dropdown.js       # Dropdowns personnalisés
│       │   └── notifications.js  # Système de notifications
│       ├── utils/                # Utilitaires JS
│       │   ├── helpers.js        # Fonctions utilitaires
│       │   └── constants.js      # Constantes globales
│       ├── main.js               # Point d'entrée principal
│       └── config.js             # Configuration JS globale
└── templates/
    ├── base.html                 # Template de base avec structure JS
    └── ...
```

---

## ⚙️ Configuration Django (settings.py)

### Configuration des Fichiers Statiques

```python
# settings/base.py

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Pour le développement - afficher les fichiers non trouvés
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# Compression et minification (production)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### Configuration Template pour les Scripts

```python
# settings/base.py

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
                'django.template.context_processors.static',
            ],
            # Pour les scripts globaux dans les templates
            'builtins': [
                'django.templatetags.static',
            ],
        },
    },
]
```

---

## ✅ Bonnes Pratiques avec Exemples

### 1. Jamais de JavaScript Inline

❌ **INCORRECT - JavaScript inline dans le template**

```html
<!-- templates/blog/article_form.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Créer un article</title>
</head>
<body>
    <form id="articleForm">
        <input type="text" name="title" id="title">
        <button type="submit">Publier</button>
    </form>

    <script>
        // ❌ JAMAIS FAIRE ÇA !
        document.getElementById('articleForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const title = document.getElementById('title').value;
            if (title.length < 5) {
                alert('Le titre doit faire au moins 5 caractères');
                return false;
            }
            // Soumission AJAX...
        });
    </script>
</body>
</html>
```

✅ **CORRECT - JavaScript dans un fichier externe**

```html
<!-- templates/blog/article_form.html -->
{% extends 'base.html' %}
{% load static %}

{% block extra_js %}
<script src="{% static 'js/pages/article_form.js' %}" defer></script>
{% endblock %}
```

```javascript
// static/js/pages/article_form.js
import { validateTitle } from '../modules/validators.js';
import { showNotification } from '../components/notifications.js';

/**
 * Gestion du formulaire de création d'article
 */
class ArticleForm {
    constructor() {
        this.form = document.getElementById('articleForm');
        this.titleInput = document.getElementById('title');
        this.init();
    }

    init() {
        if (!this.form) return;
        
        this.form.addEventListener('submit', this.handleSubmit.bind(this));
    }

    handleSubmit(event) {
        event.preventDefault();
        
        const title = this.titleInput.value.trim();
        
        if (!validateTitle(title)) {
            showNotification('Le titre doit faire au moins 5 caractères', 'error');
            return;
        }
        
        this.submitForm();
    }

    async submitForm() {
        try {
            const formData = new FormData(this.form);
            const response = await fetch('/api/articles/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': this.getCsrfToken(),
                },
            });
            
            if (!response.ok) throw new Error('Erreur serveur');
            
            showNotification('Article créé avec succès !', 'success');
            this.form.reset();
        } catch (error) {
            console.error('Erreur:', error);
            showNotification('Erreur lors de la création', 'error');
        }
    }

    getCsrfToken() {
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
}

// Initialisation
new ArticleForm();
```

### 2. Organisation des Fichiers JS en Modules

✅ **CORRECT - Structure modulaire avec ES Modules**

```javascript
// static/js/modules/validators.js

/**
 * Valide un titre d'article
 * @param {string} title - Le titre à valider
 * @param {number} minLength - Longueur minimale (défaut: 5)
 * @returns {boolean}
 */
export function validateTitle(title, minLength = 5) {
    return title && title.trim().length >= minLength;
}

/**
 * Valide une adresse email
 * @param {string} email
 * @returns {boolean}
 */
export function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

/**
 * Valide un numéro de téléphone français
 * @param {string} phone
 * @returns {boolean}
 */
export function validatePhone(phone) {
    const re = /^(?:(?:\+|00)33[\s.-]{0,3}(?:\(0\)[\s.-]{0,3})?|0)[1-9](?:(?:[\s.-]?\d{2}){4}|\d{2}(?:[\s.-]?\d{3}){2})$/;
    return re.test(phone);
}
```

```javascript
// static/js/components/notifications.js

const NOTIFICATION_DURATION = 5000;

/**
 * Affiche une notification toast
 * @param {string} message
 * @param {string} type - 'success', 'error', 'warning', 'info'
 */
export function showNotification(message, type = 'info') {
    const container = getNotificationContainer();
    const notification = createNotificationElement(message, type);
    
    container.appendChild(notification);
    
    // Animation d'entrée
    requestAnimationFrame(() => {
        notification.classList.add('show');
    });
    
    // Auto-suppression
    setTimeout(() => {
        hideNotification(notification);
    }, NOTIFICATION_DURATION);
}

function getNotificationContainer() {
    let container = document.getElementById('notification-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'notification-container';
        document.body.appendChild(container);
    }
    return container;
}

function createNotificationElement(message, type) {
    const div = document.createElement('div');
    div.className = `notification notification-${type}`;
    div.innerHTML = `
        <span class="notification-message">${escapeHtml(message)}</span>
        <button class="notification-close">&times;</button>
    `;
    
    div.querySelector('.notification-close').addEventListener('click', () => {
        hideNotification(div);
    });
    
    return div;
}

function hideNotification(element) {
    element.classList.remove('show');
    element.classList.add('hide');
    setTimeout(() => element.remove(), 300);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
```

### 3. Passer des Données Django vers JavaScript

#### Méthode 1 : data-attributes (Recommandé pour données simples)

✅ **CORRECT - Utilisation de data-attributes**

```html
<!-- templates/blog/article_detail.html -->
<article 
    id="article"
    data-article-id="{{ article.id }}"
    data-article-slug="{{ article.slug }}"
    data-author-id="{{ article.author.id }}"
    data-is-author="{{ user == article.author|yesno:'true,false' }}"
    data-csrf-token="{{ csrf_token }}"
>
    <h1>{{ article.title }}</h1>
    <div class="content">{{ article.content }}</div>
</article>
```

```javascript
// static/js/pages/article_detail.js

class ArticleDetail {
    constructor() {
        this.articleElement = document.getElementById('article');
        if (!this.articleElement) return;
        
        // Récupération des données depuis les data-attributes
        this.articleId = this.articleElement.dataset.articleId;
        this.articleSlug = this.articleElement.dataset.articleSlug;
        this.authorId = this.articleElement.dataset.authorId;
        this.isAuthor = this.articleElement.dataset.isAuthor === 'true';
        this.csrfToken = this.articleElement.dataset.csrfToken;
        
        this.init();
    }
    
    init() {
        if (this.isAuthor) {
            this.setupAuthorFeatures();
        }
        this.setupLikeButton();
    }
    
    setupAuthorFeatures() {
        // Affiche les boutons d'édition/suppression
        const editBtn = document.getElementById('edit-btn');
        if (editBtn) editBtn.style.display = 'block';
    }
}

new ArticleDetail();
```

#### Méthode 2 : json_script (Recommandé pour données complexes)

✅ **CORRECT - Utilisation de json_script**

```html
<!-- templates/blog/article_detail.html -->
{{ article_data|json_script:"article-data" }}
```

```python
# views.py
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import json

class ArticleDetailView(DetailView):
    model = Article
    template_name = 'blog/article_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = self.get_object()
        
        # Prépare les données pour le JS
        context['article_data'] = {
            'id': str(article.id),
            'title': article.title,
            'slug': article.slug,
            'author': {
                'id': str(article.author.id),
                'name': article.author.get_full_name(),
            },
            'tags': list(article.tags.values_list('name', flat=True)),
            'is_author': self.request.user == article.author,
            'can_edit': self.request.user.is_staff or self.request.user == article.author,
        }
        
        return context
```

```javascript
// static/js/pages/article_detail.js

/**
 * Parse les données JSON injectées par Django
 * @returns {Object|null}
 */
function getArticleData() {
    const scriptElement = document.getElementById('article-data');
    if (!scriptElement) return null;
    
    try {
        return JSON.parse(scriptElement.textContent);
    } catch (error) {
        console.error('Erreur parsing article data:', error);
        return null;
    }
}

class ArticleDetail {
    constructor() {
        this.data = getArticleData();
        if (!this.data) {
            console.warn('Aucune donnée article trouvée');
            return;
        }
        
        this.init();
    }
    
    init() {
        console.log(`Chargement article: ${this.data.title}`);
        
        if (this.data.can_edit) {
            this.setupEditFeatures();
        }
        
        this.renderTags(this.data.tags);
    }
    
    renderTags(tags) {
        const container = document.getElementById('tags-container');
        if (!container || !tags.length) return;
        
        container.innerHTML = tags
            .map(tag => `<span class="tag">${this.escapeHtml(tag)}</span>`)
            .join('');
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

new ArticleDetail();
```

#### Méthode 3 : JSON manuel (Alternative)

✅ **CORRECT - JSON manuel avec échappement**

```html
<!-- templates/blog/article_detail.html -->
<script id="app-config" type="application/json">
{
    "apiBaseUrl": "{% url 'api:base' %}",
    "csrfToken": "{{ csrf_token }}",
    "user": {
        "id": "{{ user.id|default:'' }}",
        "isAuthenticated": {{ user.is_authenticated|yesno:"true,false" }},
        "isStaff": {{ user.is_staff|yesno:"true,false" }}
    },
    "translations": {
        "error": "{% trans 'Une erreur est survenue' %}",
        "success": "{% trans 'Opération réussie' %}"
    }
}
</script>
```

```javascript
// static/js/config.js

/**
 * Configuration globale de l'application
 */
class AppConfig {
    constructor() {
        this.config = this.loadConfig();
    }
    
    loadConfig() {
        const script = document.getElementById('app-config');
        if (!script) {
            console.warn('Configuration non trouvée');
            return this.getDefaults();
        }
        
        try {
            return JSON.parse(script.textContent);
        } catch (error) {
            console.error('Erreur parsing config:', error);
            return this.getDefaults();
        }
    }
    
    getDefaults() {
        return {
            apiBaseUrl: '/api/',
            csrfToken: '',
            user: { isAuthenticated: false, isStaff: false },
        };
    }
    
    get(key) {
        return this.config[key];
    }
    
    getCsrfToken() {
        return this.config.csrfToken;
    }
}

export const config = new AppConfig();
```

### 4. Organisation des Templates avec base.html

✅ **CORRECT - Structure de base avec extra_js**

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
    
    <!-- Configuration globale JS -->
    {% include 'partials/js_config.html' %}
</head>
<body>
    {% include 'partials/navbar.html' %}
    
    <main id="main-content">
        {% block content %}{% endblock %}
    </main>
    
    {% include 'partials/footer.html' %}
    
    <!-- Scripts globaux -->
    <script src="{% static 'js/main.js' %}" type="module"></script>
    
    <!-- Scripts spécifiques à la page -->
    {% block extra_js %}{% endblock %}
</body>
</html>
```

```html
<!-- templates/partials/js_config.html -->
<script id="django-config" type="application/json">
{
    "staticUrl": "{{ STATIC_URL }}",
    "mediaUrl": "{{ MEDIA_URL }}",
    "csrfToken": "{{ csrf_token }}",
    "language": "{{ LANGUAGE_CODE }}",
    "user": {
        "isAuthenticated": {{ user.is_authenticated|yesno:"true,false" }},
        "id": "{{ user.id|default:'' }}"
    }
}
</script>
```

```html
<!-- templates/blog/article_form.html -->
{% extends 'base.html' %}
{% load static %}

{% block title %}Créer un Article{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="{% static 'css/forms.css' %}">
{% endblock %}

{% block content %}
<div class="container">
    <h1>Créer un article</h1>
    
    <form id="article-form" 
          data-mode="create"
          data-api-url="{% url 'api:article-list' %}">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit" class="btn btn-primary">Publier</button>
    </form>
</div>
{% endblock %}

{% block extra_js %}
<script src="{% static 'js/pages/article_form.js' %}" type="module"></script>
{% endblock %}
```

---

## 📝 Exemple Complet : Formulaire avec Validation

### Structure des fichiers

```
templates/
└── blog/
    └── article_form.html

static/
└── js/
    ├── modules/
    │   ├── validators.js
    │   └── api.js
    ├── components/
    │   └── notifications.js
    └── pages/
        └── article_form.js
```

### Template

```html
<!-- templates/blog/article_form.html -->
{% extends 'base.html' %}
{% load static %}

{% block content %}
<div class="form-container">
    <h1>Nouvel Article</h1>
    
    <form id="article-form" 
          action="{% url 'blog:article_create' %}" 
          method="post"
          novalidate>
        {% csrf_token %}
        
        <div class="form-group">
            <label for="title">Titre *</label>
            <input type="text" 
                   id="title" 
                   name="title" 
                   class="form-control"
                   data-validate="required,min:5,max:200"
                   autocomplete="off">
            <span class="error-message" id="title-error"></span>
        </div>
        
        <div class="form-group">
            <label for="content">Contenu *</label>
            <textarea id="content" 
                      name="content" 
                      class="form-control"
                      rows="10"
                      data-validate="required,min:50"></textarea>
            <span class="error-message" id="content-error"></span>
        </div>
        
        <div class="form-group">
            <label for="tags">Tags (séparés par des virgules)</label>
            <input type="text" 
                   id="tags" 
                   name="tags" 
                   class="form-control"
                   placeholder="python, django, tutorial">
        </div>
        
        <div class="form-actions">
            <button type="submit" class="btn btn-primary" id="submit-btn">
                <span class="btn-text">Publier</span>
                <span class="btn-loader" hidden>Publication...</span>
            </button>
            <a href="{% url 'blog:article_list' %}" class="btn btn-secondary">Annuler</a>
        </div>
    </form>
</div>
{% endblock %}

{% block extra_js %}
<script src="{% static 'js/pages/article_form.js' %}" type="module"></script>
{% endblock %}
```

### JavaScript

```javascript
// static/js/pages/article_form.js
import { FormValidator } from '../modules/validators.js';
import { ArticleApi } from '../modules/api.js';
import { showNotification } from '../components/notifications.js';

/**
 * Gestionnaire de formulaire d'article
 */
class ArticleForm {
    constructor() {
        this.form = document.getElementById('article-form');
        if (!this.form) return;
        
        this.validator = new FormValidator(this.form);
        this.api = new ArticleApi();
        this.submitBtn = document.getElementById('submit-btn');
        
        this.init();
    }
    
    init() {
        this.form.addEventListener('submit', this.handleSubmit.bind(this));
        
        // Validation en temps réel
        this.form.querySelectorAll('[data-validate]').forEach(field => {
            field.addEventListener('blur', () => this.validator.validateField(field));
            field.addEventListener('input', () => this.clearError(field));
        });
    }
    
    async handleSubmit(event) {
        event.preventDefault();
        
        // Validation
        if (!this.validator.validate()) {
            showNotification('Veuillez corriger les erreurs', 'error');
            return;
        }
        
        this.setLoading(true);
        
        try {
            const formData = new FormData(this.form);
            const result = await this.api.createArticle(formData);
            
            showNotification('Article publié avec succès !', 'success');
            window.location.href = result.redirectUrl;
        } catch (error) {
            console.error('Erreur:', error);
            showNotification(error.message || 'Erreur lors de la publication', 'error');
        } finally {
            this.setLoading(false);
        }
    }
    
    setLoading(isLoading) {
        this.submitBtn.disabled = isLoading;
        this.submitBtn.querySelector('.btn-text').hidden = isLoading;
        this.submitBtn.querySelector('.btn-loader').hidden = !isLoading;
    }
    
    clearError(field) {
        field.classList.remove('is-invalid');
        const errorEl = document.getElementById(`${field.id}-error`);
        if (errorEl) errorEl.textContent = '';
    }
}

// Initialisation
document.addEventListener('DOMContentLoaded', () => {
    new ArticleForm();
});
```

```javascript
// static/js/modules/validators.js

/**
 * Validateur de formulaire
 */
export class FormValidator {
    constructor(form) {
        this.form = form;
        this.errors = new Map();
    }
    
    validate() {
        this.errors.clear();
        let isValid = true;
        
        this.form.querySelectorAll('[data-validate]').forEach(field => {
            if (!this.validateField(field)) {
                isValid = false;
            }
        });
        
        return isValid;
    }
    
    validateField(field) {
        const rules = field.dataset.validate.split(',');
        const value = field.value.trim();
        
        for (const rule of rules) {
            const [ruleName, ruleValue] = rule.split(':');
            
            switch (ruleName) {
                case 'required':
                    if (!value) {
                        this.setError(field, 'Ce champ est obligatoire');
                        return false;
                    }
                    break;
                    
                case 'min':
                    if (value.length < parseInt(ruleValue)) {
                        this.setError(field, `Minimum ${ruleValue} caractères`);
                        return false;
                    }
                    break;
                    
                case 'max':
                    if (value.length > parseInt(ruleValue)) {
                        this.setError(field, `Maximum ${ruleValue} caractères`);
                        return false;
                    }
                    break;
                    
                case 'email':
                    if (value && !this.isValidEmail(value)) {
                        this.setError(field, 'Email invalide');
                        return false;
                    }
                    break;
            }
        }
        
        this.clearError(field);
        return true;
    }
    
    setError(field, message) {
        field.classList.add('is-invalid');
        const errorEl = document.getElementById(`${field.id}-error`);
        if (errorEl) errorEl.textContent = message;
        this.errors.set(field.id, message);
    }
    
    clearError(field) {
        field.classList.remove('is-invalid');
        const errorEl = document.getElementById(`${field.id}-error`);
        if (errorEl) errorEl.textContent = '';
        this.errors.delete(field.id);
    }
    
    isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }
}
```

---

## ⚡ Exceptions Acceptables

### Cas où le JS inline est toléré

✅ **CORRECT - Analytics et tracking**

```html
<!-- OK: Scripts de tracking externes -->
<script async src="https://www.googletagmanager.com/gtag/js?id={{ GA_TRACKING_ID }}"></script>
<script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', '{{ GA_TRACKING_ID }}');
</script>
```

✅ **CORRECT - Configuration globale minimale**

```html
<!-- OK: Configuration dans <head> pour éviter le flash -->
<script>
    // Thème dark/light avant rendu
    (function() {
        const theme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-theme', theme);
    })();
</script>
```

✅ **CORRECT - Clés API publiques**

```html
<!-- OK: Variables d'environnement côté client -->
<script>
    window.APP_CONFIG = {
        MAP_API_KEY: '{{ MAPS_API_KEY }}',
        STRIPE_PUBLIC_KEY: '{{ STRIPE_PUBLIC_KEY }}',
    };
</script>
```

---

## ✅ Checklist Pré-Création

Avant de créer ou modifier un fichier template ou JavaScript :

- [ ] **Zero JavaScript inline** - Tout le JS est dans des fichiers `.js` externes
- [ ] **Structure claire** - Les fichiers JS sont organisés par fonction (modules/pages/components)
- [ ] **Attribut defer** - Les scripts externes utilisent `defer` ou `type="module"`
- [ ] **Data attributes** - Les données Django → JS passent par `data-*` ou `json_script`
- [ ] **Pas de logique dans templates** - Aucune balise `<script>` avec du JS dans les `.html`
- [ ] **CSRF Token** - Le token CSRF est correctement passé aux requêtes AJAX
- [ ] **Sécurité XSS** - Les données injectées sont échappées avec `|escapejs` si nécessaire
- [ ] **Tests fonctionnels** - Le JS fonctionne sans erreurs dans la console

---

## 🚀 Intégration avec HTMX (Optionnel)

### Configuration HTMX sans JS inline

```html
<!-- templates/base.html -->
<head>
    <script src="{% static 'js/lib/htmx.min.js' %}" defer></script>
    <meta name="htmx-config" content='{"historyCacheSize": 20}'>
</head>
```

```javascript
// static/js/main.js
// Écouteurs d'événements HTMX

document.addEventListener('htmx:afterRequest', (event) => {
    const response = event.detail.xhr;
    
    if (!response.ok) {
        showNotification('Erreur lors de la requête', 'error');
    }
});

document.addEventListener('htmx:afterSwap', (event) => {
    // Réinitialiser les composants sur le nouveau contenu
    initializeComponents(event.target);
});

function initializeComponents(container) {
    // Réinitialiser les dropdowns, modals, etc.
    container.querySelectorAll('[data-dropdown]').forEach(el => {
        new Dropdown(el);
    });
}
```

### HTMX + Django avec data-attributes

```html
<!-- templates/blog/article_list.html -->
<div id="articles-container">
    {% for article in articles %}
    <article class="card"
             hx-get="{% url 'blog:article_detail_partial' article.slug %}"
             hx-target="#article-modal"
             hx-trigger="click"
             data-article-slug="{{ article.slug }}">
        <h3>{{ article.title }}</h3>
        <p>{{ article.excerpt }}</p>
    </article>
    {% endfor %}
</div>

<div id="article-modal" hx-target="this"></div>
```

---

## 🔍 Commandes de Vérification

### Vérifier l'absence de JS inline

```bash
# Rechercher les balises script dans les templates
find templates -name "*.html" -exec grep -l "<script[^>]*>" {} \;

# Vérifier qu'il n'y a pas de JS inline (hors script src ou json_script)
find templates -name "*.html" -exec grep -l "<script>" {} \;

# Rechercher les attributs d'événements inline (onclick, onsubmit, etc.)
find templates -name "*.html" -exec grep -E "on(click|submit|change|load|keyup|keydown)=" {} + | head -20
```

### Vérifier la structure JS

```bash
# Lister les fichiers JS par catégorie
echo "=== Modules ==="
find static/js/modules -name "*.js" 2>/dev/null | sort

echo "=== Pages ==="
find static/js/pages -name "*.js" 2>/dev/null | sort

echo "=== Components ==="
find static/js/components -name "*.js" 2>/dev/null | sort

# Vérifier l'utilisation des modules ES
grep -r "^import\|^export" static/js --include="*.js" | wc -l
```

### Linter et formater le JS

```bash
# ESLint
npx eslint static/js --ext .js

# Prettier
npx prettier --check "static/js/**/*.js"

# Correction automatique
npx eslint static/js --ext .js --fix
npx prettier --write "static/js/**/*.js"
```

### Script de vérification complet

```bash
#!/bin/bash
# verify-js-separation.sh

echo "🔍 Vérification de la séparation JS/HTML..."
echo "=========================================="

# 1. Vérifier les scripts inline
echo ""
echo "1️⃣  Vérification des scripts inline..."
INLINE_SCRIPTS=$(find templates -name "*.html" -exec grep -l "<script>" {} \; 2>/dev/null | wc -l)
if [ "$INLINE_SCRIPTS" -gt 0 ]; then
    echo "   ❌ $INLINE_SCRIPTS template(s) avec scripts inline trouvé(s):"
    find templates -name "*.html" -exec grep -l "<script>" {} \; 2>/dev/null
else
    echo "   ✅ Aucun script inline détecté"
fi

# 2. Vérifier les événements inline
echo ""
echo "2️⃣  Vérification des événements inline..."
INLINE_EVENTS=$(find templates -name "*.html" -exec grep -E "on(click|submit|change|load|keyup|keydown|focus|blur)=" {} + 2>/dev/null | wc -l)
if [ "$INLINE_EVENTS" -gt 0 ]; then
    echo "   ❌ $INLINE_EVENTS événement(s) inline trouvé(s)"
    find templates -name "*.html" -exec grep -E "on(click|submit|change|load|keyup|keydown|focus|blur)=" {} + 2>/dev/null | head -10
else
    echo "   ✅ Aucun événement inline détecté"
fi

# 3. Vérifier la structure
echo ""
echo "3️⃣  Vérification de la structure JS..."
for dir in modules pages components utils; do
    count=$(find static/js/$dir -name "*.js" 2>/dev/null | wc -l)
    echo "   📁 $dir/: $count fichier(s)"
done

# 4. ESLint
echo ""
echo "4️⃣  ESLint..."
if command -v npx &> /dev/null; then
    npx eslint static/js --ext .js --quiet && echo "   ✅ ESLint: pas d'erreurs" || echo "   ❌ ESLint: erreurs détectées"
else
    echo "   ⚠️  ESLint non disponible"
fi

echo ""
echo "✅ Vérification terminée !"
```

---

## 📚 Ressources

### Documentation Officielle

- [Django Static Files](https://docs.djangoproject.com/en/5.1/howto/static-files/)
- [Django Templates](https://docs.djangoproject.com/en/5.1/topics/templates/)
- [MDN - Organizing your JavaScript](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules)

### Articles et Tutoriels

- [Django Best Practices: JavaScript](https://django-best-practices.readthedocs.io/en/latest/javascript.html)
- [Separating JavaScript from HTML in Django](https://www.mattlayman.com/blog/2020/separate-javascript-from-html-django/)
- [Modern JavaScript in Django](https://www.valentinog.com/blog/drf/)

### Outils Recommandés

- **ESLint** - Linter JavaScript
- **Prettier** - Formateur de code
- **django-compressor** - Compression des assets (optionnel)
- **django-webpack-loader** - Intégration Webpack (optionnel)

### Librairies Complémentaires

- **Alpine.js** - Framework léger pour réactivité sans JS inline
- **HTMX** - AJAX sans JS écrit
- **Stimulus** - Framework JS pour HTML au comportement progressif

---

**Dernière mise à jour** : 2026-02-09  
**Version** : 1.0.0  
**Auteur** : Équipe Développement Django
