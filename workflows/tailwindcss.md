# Skill Tailwind CSS - Bonnes Pratiques et Conventions

## 🎯 Objectif

Ce skill définit les bonnes pratiques et conventions pour l'utilisation de Tailwind CSS dans les projets web. **Il doit être consulté obligatoirement avant chaque création ou modification de fichiers CSS/HTML/JSX avec Tailwind.**

## ⚠️ Règle d'Or

> **AUCUN fichier utilisant Tailwind CSS ne doit être créé ou modifié sans respecter ces conventions.**

---

## 📋 Installation et Configuration

### Installation de Tailwind CSS

```bash
# Via npm (recommandé)
npm install -D tailwindcss postcss autoprefixer

# Initialiser la configuration
npx tailwindcss init -p

# Via CDN (développement uniquement)
<script src="https://cdn.tailwindcss.com"></script>
```

### Configuration de base (tailwind.config.js)

```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/**/*.{html,js,jsx,ts,tsx,vue}',
    './templates/**/*.html',
    './static/**/*.js',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },
        secondary: {
          // Définir votre palette secondaire
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        serif: ['Georgia', 'serif'],
        mono: ['Fira Code', 'monospace'],
      },
      spacing: {
        '128': '32rem',
        '144': '36rem',
      },
      borderRadius: {
        '4xl': '2rem',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    require('@tailwindcss/aspect-ratio'),
  ],
}
```

### Fichier CSS principal (input.css)

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Couche base - Reset et styles de base */
@layer base {
  html {
    @apply antialiased;
  }
  
  body {
    @apply bg-gray-50 text-gray-900 font-sans;
  }
  
  h1 {
    @apply text-4xl font-bold text-gray-900;
  }
  
  h2 {
    @apply text-3xl font-semibold text-gray-800;
  }
  
  h3 {
    @apply text-2xl font-semibold text-gray-800;
  }
  
  a {
    @apply text-primary-600 hover:text-primary-700 transition-colors;
  }
}

/* Couche components - Composants réutilisables */
@layer components {
  .btn {
    @apply px-4 py-2 rounded-lg font-medium transition-all duration-200 
           focus:outline-none focus:ring-2 focus:ring-offset-2;
  }
  
  .btn-primary {
    @apply btn bg-primary-600 text-white hover:bg-primary-700 
           focus:ring-primary-500;
  }
  
  .btn-secondary {
    @apply btn bg-gray-200 text-gray-800 hover:bg-gray-300 
           focus:ring-gray-500;
  }
  
  .btn-danger {
    @apply btn bg-red-600 text-white hover:bg-red-700 
           focus:ring-red-500;
  }
  
  .card {
    @apply bg-white rounded-xl shadow-md hover:shadow-lg 
           transition-shadow duration-300 overflow-hidden;
  }
  
  .input {
    @apply w-full px-4 py-2 border border-gray-300 rounded-lg 
           focus:ring-2 focus:ring-primary-500 focus:border-primary-500 
           transition-all duration-200;
  }
  
  .badge {
    @apply inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium;
  }
  
  .badge-success {
    @apply badge bg-green-100 text-green-800;
  }
  
  .badge-warning {
    @apply badge bg-yellow-100 text-yellow-800;
  }
  
  .badge-error {
    @apply badge bg-red-100 text-red-800;
  }
}

/* Couche utilities - Utilitaires personnalisés */
@layer utilities {
  .text-shadow {
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }
  
  .text-shadow-lg {
    text-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  }
  
  .gradient-primary {
    @apply bg-gradient-to-r from-primary-500 to-primary-700;
  }
}
```

### Compilation

```bash
# Mode développement (watch)
npx tailwindcss -i ./src/input.css -o ./dist/output.css --watch

# Mode production (minifié)
NODE_ENV=production npx tailwindcss -i ./src/input.css -o ./dist/output.css --minify

# Via npm scripts
npm run build:css    # Production
npm run dev:css      # Développement
```

---

## 🎨 Conventions de Nommage des Classes

### Ordre des Classes (méthodologie)

```html
<!-- ❌ INCORRECT - Classes désordonnées -->
<div class="text-white p-4 flex bg-blue-500 rounded-lg m-2 items-center">

<!-- ✅ CORRECT - Ordre logique -->
<div class="
  m-2 p-4                    /* 1. Layout (margin, padding) */
  flex items-center          /* 2. Flexbox/Grid */
  bg-blue-500 text-white     /* 3. Couleurs */
  rounded-lg                 /* 4. Bordures */
">
```

**Ordre recommandé :**
1. **Layout** : `block`, `flex`, `grid`, `hidden`
2. **Box Model** : `m-`, `p-`, `w-`, `h-`, `max-w-`
3. **Position** : `relative`, `absolute`, `fixed`, `top-`, `left-`
4. **Flexbox/Grid** : `flex-`, `justify-`, `items-`, `grid-`, `col-`
5. **Typography** : `text-`, `font-`, `leading-`, `tracking-`
6. **Background** : `bg-`, `bg-gradient-`
7. **Borders** : `border`, `rounded-`, `shadow-`
8. **Effects** : `opacity-`, `transition-`, `transform-`
9. **Interactivity** : `cursor-`, `hover:`, `focus:`, `active:`

### Exemples de Structure

```html
<!-- Layout de page -->
<body class="min-h-screen bg-gray-50">
  <header class="sticky top-0 z-50 bg-white shadow-sm">
    <nav class="container mx-auto px-4 py-4 flex items-center justify-between">
      <!-- Navigation -->
    </nav>
  </header>
  
  <main class="container mx-auto px-4 py-8">
    <!-- Contenu principal -->
  </main>
  
  <footer class="bg-gray-800 text-white py-8">
    <!-- Footer -->
  </footer>
</body>
```

---

## 📐 Système de Grille et Layout

### Container

```html
<!-- Container responsive avec padding automatique -->
<div class="container mx-auto px-4 sm:px-6 lg:px-8">
  <!-- Contenu -->
</div>

<!-- Container avec largeur maximale personnalisée -->
<div class="max-w-7xl mx-auto px-4">
  <!-- Contenu -->
</div>
```

### Grille (Grid)

```html
<!-- Grille simple -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  <div class="bg-white p-6 rounded-lg shadow">Item 1</div>
  <div class="bg-white p-6 rounded-lg shadow">Item 2</div>
  <div class="bg-white p-6 rounded-lg shadow">Item 3</div>
</div>

<!-- Grille avec tailles différentes -->
<div class="grid grid-cols-12 gap-4">
  <div class="col-span-12 md:col-span-8">Contenu principal</div>
  <div class="col-span-12 md:col-span-4">Sidebar</div>
</div>

<!-- Grille auto-fit -->
<div class="grid grid-cols-[repeat(auto-fit,minmax(250px,1fr))] gap-6">
  <!-- Items -->
</div>
```

### Flexbox

```html
<!-- Flexbox horizontal avec espacement -->
<div class="flex items-center justify-between gap-4">
  <div>Left</div>
  <div>Right</div>
</div>

<!-- Flexbox vertical -->
<div class="flex flex-col gap-4">
  <div>Item 1</div>
  <div>Item 2</div>
  <div>Item 3</div>
</div>

<!-- Flexbox responsive -->
<div class="flex flex-col md:flex-row gap-4">
  <div class="flex-1">Colonne 1</div>
  <div class="flex-1">Colonne 2</div>
</div>

<!-- Centrage parfait -->
<div class="flex items-center justify-center min-h-screen">
  <div>Contenu centré</div>
</div>
```

---

## 🎯 Composants Communs

### Boutons

```html
<!-- Bouton primaire -->
<button class="
  px-6 py-2.5 
  bg-primary-600 text-white font-medium 
  rounded-lg 
  hover:bg-primary-700 
  focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
  transition-colors duration-200
  disabled:opacity-50 disabled:cursor-not-allowed
">
  Cliquez ici
</button>

<!-- Bouton secondaire -->
<button class="
  px-6 py-2.5 
  bg-white text-gray-700 font-medium 
  border border-gray-300 rounded-lg 
  hover:bg-gray-50 
  focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2
  transition-colors duration-200
">
  Annuler
</button>

<!-- Bouton avec icône -->
<button class="
  inline-flex items-center gap-2 
  px-6 py-2.5 
  bg-primary-600 text-white font-medium 
  rounded-lg 
  hover:bg-primary-700 
  transition-colors duration-200
">
  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
  </svg>
  Ajouter
</button>
```

### Formulaires

```html
<!-- Groupe de formulaire -->
<div class="space-y-4">
  <!-- Input texte -->
  <div>
    <label for="email" class="block text-sm font-medium text-gray-700 mb-1">
      Email
    </label>
    <input 
      type="email" 
      id="email"
      class="
        w-full px-4 py-2 
        border border-gray-300 rounded-lg 
        focus:ring-2 focus:ring-primary-500 focus:border-primary-500
        placeholder-gray-400
        transition-all duration-200
      "
      placeholder="votre@email.com"
    >
    <p class="mt-1 text-sm text-red-600">Message d'erreur</p>
  </div>
  
  <!-- Select -->
  <div>
    <label for="country" class="block text-sm font-medium text-gray-700 mb-1">
      Pays
    </label>
    <select 
      id="country"
      class="
        w-full px-4 py-2 
        border border-gray-300 rounded-lg 
        focus:ring-2 focus:ring-primary-500 focus:border-primary-500
        bg-white
      "
    >
      <option>France</option>
      <option>Belgique</option>
      <option>Suisse</option>
    </select>
  </div>
  
  <!-- Checkbox -->
  <div class="flex items-center">
    <input 
      type="checkbox" 
      id="terms"
      class="
        w-4 h-4 
        text-primary-600 
        border-gray-300 rounded 
        focus:ring-primary-500
      "
    >
    <label for="terms" class="ml-2 text-sm text-gray-700">
      J'accepte les conditions
    </label>
  </div>
</div>
```

### Cartes (Cards)

```html
<!-- Carte basique -->
<div class="bg-white rounded-xl shadow-md overflow-hidden hover:shadow-lg transition-shadow">
  <img src="image.jpg" alt="" class="w-full h-48 object-cover">
  <div class="p-6">
    <h3 class="text-xl font-semibold text-gray-900 mb-2">Titre de la carte</h3>
    <p class="text-gray-600 mb-4">Description de la carte...</p>
    <button class="text-primary-600 font-medium hover:text-primary-700">
      En savoir plus →
    </button>
  </div>
</div>

<!-- Carte horizontale -->
<div class="bg-white rounded-xl shadow-md overflow-hidden flex flex-col md:flex-row">
  <img src="image.jpg" alt="" class="w-full md:w-48 h-48 object-cover">
  <div class="p-6 flex-1">
    <h3 class="text-xl font-semibold text-gray-900 mb-2">Titre</h3>
    <p class="text-gray-600">Description...</p>
  </div>
</div>
```

### Navigation

```html
<!-- Navigation responsive -->
<nav class="bg-white shadow-sm">
  <div class="container mx-auto px-4">
    <div class="flex items-center justify-between h-16">
      <!-- Logo -->
      <a href="/" class="text-xl font-bold text-gray-900">Logo</a>
      
      <!-- Menu desktop -->
      <div class="hidden md:flex items-center space-x-8">
        <a href="/" class="text-gray-700 hover:text-primary-600 font-medium">Accueil</a>
        <a href="/about" class="text-gray-700 hover:text-primary-600 font-medium">À propos</a>
        <a href="/contact" class="text-gray-700 hover:text-primary-600 font-medium">Contact</a>
      </div>
      
      <!-- Bouton mobile -->
      <button class="md:hidden p-2 rounded-lg hover:bg-gray-100">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
        </svg>
      </button>
    </div>
  </div>
</nav>
```

### Alertes

```html
<!-- Alerte succès -->
<div class="bg-green-50 border-l-4 border-green-500 p-4 rounded-r-lg">
  <div class="flex items-start">
    <svg class="w-5 h-5 text-green-500 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
    </svg>
    <div class="ml-3">
      <h3 class="text-sm font-medium text-green-800">Succès</h3>
      <p class="text-sm text-green-700 mt-1">Votre action a été effectuée avec succès.</p>
    </div>
  </div>
</div>

<!-- Alerte erreur -->
<div class="bg-red-50 border-l-4 border-red-500 p-4 rounded-r-lg">
  <div class="flex items-start">
    <svg class="w-5 h-5 text-red-500 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
    </svg>
    <div class="ml-3">
      <h3 class="text-sm font-medium text-red-800">Erreur</h3>
      <p class="text-sm text-red-700 mt-1">Une erreur s'est produite. Veuillez réessayer.</p>
    </div>
  </div>
</div>
```

---

## 📱 Responsive Design

### Breakpoints

| Breakpoint | Préfixe | Taille | Usage |
|------------|---------|--------|-------|
| sm | `sm:` | 640px | Mobile paysage |
| md | `md:` | 768px | Tablette |
| lg | `lg:` | 1024px | Desktop |
| xl | `xl:` | 1280px | Grand écran |
| 2xl | `2xl:` | 1536px | Très grand écran |

### Approche Mobile-First

```html
<!-- ✅ CORRECT - Mobile-first -->
<div class="w-full md:w-1/2 lg:w-1/3">
  <!-- Mobile: 100%, Tablette: 50%, Desktop: 33% -->
</div>

<!-- ❌ INCORRECT - Desktop-first -->
<div class="w-1/3 md:w-1/2 sm:w-full">
  <!-- Évitez cette approche -->
</div>
```

### Exemples Responsive

```html
<!-- Grille responsive -->
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
  <!-- Items -->
</div>

<!-- Navigation responsive -->
<nav class="hidden md:flex">
  <!-- Menu desktop -->
</nav>
<button class="md:hidden">
  <!-- Bouton hamburger -->
</button>

<!-- Texte responsive -->
<h1 class="text-2xl md:text-3xl lg:text-4xl font-bold">
  Titre responsive
</h1>

<!-- Padding responsive -->
<div class="p-4 md:p-6 lg:p-8">
  <!-- Contenu avec padding adaptatif -->
</div>
```

---

## 🎭 États et Interactions

### États de base

```html
<!-- Hover -->
<button class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded">
  Hover me
</button>

<!-- Focus -->
<input class="border-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500">

<!-- Active -->
<button class="bg-blue-500 active:bg-blue-700 text-white px-4 py-2 rounded">
  Click me
</button>

<!-- Disabled -->
<button disabled class="bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed">
  Disabled
</button>

<!-- Checked (pour checkbox/radio) -->
<input type="checkbox" class="checked:bg-blue-500">
```

### États combinés

```html
<!-- Bouton avec tous les états -->
<button class="
  px-6 py-2.5 
  bg-primary-600 text-white font-medium 
  rounded-lg 
  hover:bg-primary-700 
  active:bg-primary-800 
  focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
  disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-primary-600
  transition-colors duration-200
">
  Bouton complet
</button>

<!-- Lien avec états -->
<a href="#" class="
  text-primary-600 
  hover:text-primary-700 
  hover:underline 
  focus:outline-none focus:ring-2 focus:ring-primary-500
  visited:text-purple-600
">
  Lien stylisé
</a>
```

### Groupes et pairs

```html
<!-- Group hover -->
<div class="group relative">
  <img src="image.jpg" class="group-hover:opacity-75 transition-opacity">
  <div class="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
    <span class="text-white font-bold">Voir plus</span>
  </div>
</div>

<!-- Peer (pour formulaires) -->
<input type="checkbox" id="toggle" class="peer sr-only">
<label for="toggle" class="
  w-11 h-6 bg-gray-200 rounded-full cursor-pointer
  peer-checked:bg-primary-600
  peer-focus:ring-2 peer-focus:ring-primary-500
  transition-colors
">
</label>
```

---

## 🎨 Thèmes et Personnalisation

### Mode sombre (Dark Mode)

```javascript
// tailwind.config.js
module.exports = {
  darkMode: 'class', // ou 'media' pour préférence système
  // ...
}
```

```html
<!-- Toggle dark mode -->
<html class="dark">
<body class="bg-white dark:bg-gray-900 text-gray-900 dark:text-white">
  <div class="bg-gray-100 dark:bg-gray-800 p-4 rounded-lg">
    <h2 class="text-gray-800 dark:text-gray-100">Titre</h2>
    <p class="text-gray-600 dark:text-gray-300">Contenu</p>
  </div>
</body>
</html>
```

### Thèmes personnalisés

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          // ... jusqu'à 900
        },
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in',
        'slide-up': 'slideUp 0.5s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
}
```

---

## 🚀 Bonnes Pratiques

### ✅ À FAIRE

```html
<!-- Utiliser les composants @layer -->
<div class="btn-primary">Bouton</div>

<!-- Extraire les classes répétées -->
<!-- ❌ Éviter -->
<div class="flex items-center justify-between p-4 bg-white rounded-lg shadow">
<div class="flex items-center justify-between p-4 bg-white rounded-lg shadow">

<!-- ✅ Utiliser @apply ou un composant -->
<div class="card flex-between">

<!-- Utiliser les utilitaires pour les valeurs uniques -->
<div class="mt-[117px]">

<!-- Organiser les classes par ordre logique -->
```

### ❌ À ÉVITER

```html
<!-- Ne pas utiliser de valeurs arbitraires sauf si nécessaire -->
<!-- ❌ -->
<div class="w-[123px] h-[456px]">

<!-- ✅ -->
<div class="w-32 h-96">

<!-- Ne pas mélanger Tailwind avec CSS custom sauf si nécessaire -->
<!-- ❌ -->
<div class="text-red-500" style="color: blue;">

<!-- Ne pas surcharger les éléments -->
<!-- ❌ -->
<div class="p-4 sm:p-4 md:p-4 lg:p-4">

<!-- ✅ -->
<div class="p-4">

<!-- Éviter les classes inutiles -->
<!-- ❌ -->
<div class="block"> <!-- div est déjà block par défaut -->
```

### Performance

```javascript
// PurgeCSS - Configuration pour production
module.exports = {
  content: [
    './src/**/*.{html,js,jsx,ts,tsx}',
    // Ajouter tous les fichiers utilisant Tailwind
  ],
  // Active le purge automatique en production
  purge: {
    enabled: process.env.NODE_ENV === 'production',
    content: ['./src/**/*.{html,js,jsx,ts,tsx}'],
  },
}
```

---

## 🧪 Checklist Pré-Utilisation

Avant d'utiliser Tailwind CSS dans un fichier, vérifier :

- [ ] ✅ Le fichier `tailwind.config.js` est configuré avec les bonnes sources
- [ ] ✅ Les couleurs de marque sont définies dans le thème
- [ ] ✅ Les classes sont ordonnées selon la méthodologie
- [ ] ✅ L'approche mobile-first est utilisée
- [ ] ✅ Les états (hover, focus, active) sont gérés
- [ ] ✅ Le dark mode est pris en compte si applicable
- [ ] ✅ Les composants réutilisables sont extraits avec `@layer components`
- [ ] ✅ Pas de valeurs arbitraires inutiles
- [ ] ✅ Le CSS est compilé et minifié pour la production

---

## 📚 Ressources

- [Documentation Tailwind CSS](https://tailwindcss.com/docs)
- [Cheat Sheet](https://nerdcave.com/tailwind-cheat-sheet)
- [Tailwind UI](https://tailwindui.com/)
- [Headless UI](https://headlessui.com/)
- [Tailwind Components](https://tailwindcomponents.com/)

---

**Dernière mise à jour** : 2026-02-04  
**Version** : 1.0.0  
**Auteur** : Équipe Développement Frontend
