# Skill JavaScript Moderne - Bonnes Pratiques et Clean Code (ES2023/ES2024)

## 🎯 Objectif

Ce skill définit les bonnes pratiques, conventions et outils pour développer en JavaScript moderne (ES2023/ES2024). **Il doit être consulté obligatoirement avant chaque création ou modification de fichier JavaScript.**

## ⚠️ Règle d'Or

> **AUCUN fichier JavaScript ne doit être créé ou modifié sans respecter ces conventions de qualité et de style.**

---

## 🔄 Ordre d'Exécution des Outils

Pour un code JavaScript optimal, exécuter les outils dans cet ordre :

```bash
# 1. ESLint - Vérification et correction automatique
npx eslint --fix .

# 2. Prettier - Formatage automatique
npx prettier --write .

# 3. Vérification finale
npx eslint .
npx prettier --check .
```

**⚠️ Important :** ESLint avec `--fix` doit TOUJOURS être exécuté avant Prettier pour éviter les conflits.

---

## 📋 Installation des Outils

### Installation via npm

```bash
# Installation de base
npm install --save-dev eslint prettier eslint-config-prettier eslint-plugin-import

# Plugins recommandés
npm install --save-dev eslint-plugin-unicorn eslint-plugin-security eslint-plugin-jsdoc

# Pour les projets avec modules ES
npm install --save-dev @eslint/js

# Installation complète (recommandé)
npm install --save-dev eslint prettier eslint-config-prettier eslint-plugin-import eslint-plugin-unicorn eslint-plugin-security
```

### Fichier package.json

```json
{
  "devDependencies": {
    "@eslint/js": "^8.57.0",
    "eslint": "^8.57.0",
    "eslint-config-prettier": "^9.1.0",
    "eslint-plugin-import": "^2.29.1",
    "eslint-plugin-jsdoc": "^48.2.0",
    "eslint-plugin-security": "^2.1.0",
    "eslint-plugin-unicorn": "^51.0.1",
    "prettier": "^3.2.5"
  },
  "scripts": {
    "lint": "eslint .",
    "lint:fix": "eslint --fix .",
    "format": "prettier --write .",
    "format:check": "prettier --check .",
    "code:check": "npm run lint && npm run format:check",
    "code:fix": "npm run lint:fix && npm run format"
  }
}
```

---

## 🔧 Configuration ESLint

### Fichier eslint.config.js (Flat Config - Recommandé)

```javascript
import js from '@eslint/js';
import prettierConfig from 'eslint-config-prettier';
import importPlugin from 'eslint-plugin-import';
import unicornPlugin from 'eslint-plugin-unicorn';
import securityPlugin from 'eslint-plugin-security';
import jsdocPlugin from 'eslint-plugin-jsdoc';

export default [
  js.configs.recommended,
  {
    files: ['**/*.js', '**/*.mjs'],
    languageOptions: {
      ecmaVersion: 2024,
      sourceType: 'module',
      globals: {
        window: 'readonly',
        document: 'readonly',
        console: 'readonly',
        fetch: 'readonly',
        setTimeout: 'readonly',
        clearTimeout: 'readonly',
        setInterval: 'readonly',
        clearInterval: 'readonly',
        localStorage: 'readonly',
        sessionStorage: 'readonly',
        location: 'readonly',
        navigator: 'readonly',
        process: 'readonly', // Pour Node.js
      },
    },
    plugins: {
      import: importPlugin,
      unicorn: unicornPlugin,
      security: securityPlugin,
      jsdoc: jsdocPlugin,
    },
    rules: {
      // ESLint de base
      'no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
      'no-console': 'warn',
      'no-debugger': 'error',
      'no-var': 'error',
      'prefer-const': 'error',
      'prefer-arrow-callback': 'error',
      'prefer-template': 'error',
      'template-curly-spacing': 'error',
      'arrow-parens': ['error', 'always'],
      'arrow-spacing': 'error',
      'no-duplicate-imports': 'error',
      'object-shorthand': 'error',
      'prefer-destructuring': ['error', { object: true, array: false }],
      'prefer-rest-params': 'error',
      'prefer-spread': 'error',
      'rest-spread-spacing': 'error',
      'sort-imports': ['error', { ignoreDeclarationSort: true }],

      // Imports
      'import/order': [
        'error',
        {
          groups: [
            'builtin',
            'external',
            'internal',
            'parent',
            'sibling',
            'index',
          ],
          'newlines-between': 'always',
          alphabetize: { order: 'asc', caseInsensitive: true },
        },
      ],
      'import/no-duplicates': 'error',

      // Unicorn (bonnes pratiques modernes)
      'unicorn/prefer-module': 'error',
      'unicorn/prefer-node-protocol': 'error',
      'unicorn/prefer-optional-catch-binding': 'error',
      'unicorn/prefer-string-slice': 'error',
      'unicorn/prefer-type-error': 'error',
      'unicorn/throw-new-error': 'error',
      'unicorn/no-array-for-each': 'off', // Parfois pratique

      // Security
      'security/detect-object-injection': 'warn',
      'security/detect-non-literal-regexp': 'warn',
      'security/detect-unsafe-regex': 'error',

      // JSDoc
      'jsdoc/require-jsdoc': [
        'warn',
        {
          require: {
            FunctionDeclaration: true,
            MethodDefinition: true,
            ClassDeclaration: true,
            ArrowFunctionExpression: false,
          },
        },
      ],
      'jsdoc/require-description': 'warn',
      'jsdoc/require-param': 'warn',
      'jsdoc/require-returns': 'warn',
    },
    settings: {
      'import/resolver': {
        node: {
          extensions: ['.js', '.mjs'],
        },
      },
    },
  },
  // Configuration pour les fichiers de test
  {
    files: ['**/*.test.js', '**/*.spec.js', '**/test/**/*.js'],
    rules: {
      'no-console': 'off',
      'security/detect-object-injection': 'off',
    },
  },
  // Ignorer les fichiers
  {
    ignores: [
      'node_modules/**',
      'dist/**',
      'build/**',
      'coverage/**',
      '*.min.js',
      '**/vendor/**',
    ],
  },
  prettierConfig, // Doit être en dernier
];
```

### Fichier .eslintrc.json (Legacy - si nécessaire)

```json
{
  "env": {
    "browser": true,
    "es2024": true,
    "node": true
  },
  "extends": [
    "eslint:recommended",
    "plugin:import/errors",
    "plugin:import/warnings",
    "plugin:security/recommended",
    "prettier"
  ],
  "parserOptions": {
    "ecmaVersion": 2024,
    "sourceType": "module"
  },
  "plugins": ["import", "unicorn", "security", "jsdoc"],
  "rules": {
    "no-unused-vars": ["error", { "argsIgnorePattern": "^_" }],
    "no-console": "warn",
    "no-var": "error",
    "prefer-const": "error",
    "prefer-arrow-callback": "error",
    "prefer-template": "error",
    "object-shorthand": "error",
    "import/order": [
      "error",
      {
        "groups": ["builtin", "external", "internal", "parent", "sibling", "index"],
        "newlines-between": "always"
      }
    ]
  },
  "ignorePatterns": ["node_modules/", "dist/", "build/", "*.min.js"]
}
```

---

## 🔧 Configuration Prettier

### Fichier .prettierrc

```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 100,
  "tabWidth": 2,
  "useTabs": false,
  "bracketSpacing": true,
  "arrowParens": "always",
  "endOfLine": "lf",
  "quoteProps": "as-needed",
  "jsxSingleQuote": false
}
```

### Fichier .prettierignore

```
node_modules/
dist/
build/
coverage/
*.min.js
package-lock.json
yarn.lock
pnpm-lock.yaml
```

---

## 📝 Conventions de Style JavaScript

### ES Modules (Recommandé)

```javascript
// ✅ CORRECT - Utiliser ES Modules
import { helper } from './utils.js';
import config from './config.js';

export function myFunction() {
  return helper(config);
}

export default class MyClass {
  // ...
}

// ❌ INCORRECT - CommonJS (sauf si nécessaire)
const helper = require('./utils.js');
module.exports = myFunction;
```

### Déclaration de Variables

```javascript
// ✅ CORRECT - const par défaut, let si nécessaire
const API_URL = 'https://api.example.com';
const user = { name: 'John', age: 30 };
let counter = 0;

// ❌ INCORRECT - var jamais utilisé
var name = 'John'; // ÉVITER

// ✅ CORRECT - Destructuration
const { name, email } = user;
const [first, second] = items;

// ❌ INCORRECT - Pas de destructuration
const name = user.name;
const email = user.email;
```

### Fonctions

```javascript
// ✅ CORRECT - Arrow functions pour les fonctions courtes
const add = (a, b) => a + b;

const calculateTotal = (items) => {
  return items.reduce((sum, item) => sum + item.price, 0);
};

// ✅ CORRECT - Fonctions nommées pour les méthodes complexes
function processUserData(userData) {
  // Logique complexe ici
  return transformedData;
}

// ✅ CORRECT - Méthodes de classe
class UserService {
  async getUserById(id) {
    const response = await fetch(`/api/users/${id}`);
    return response.json();
  }

  // Méthode privée (ES2022+)
  #validateUser(user) {
    return user && user.id && user.email;
  }
}

// ❌ INCORRECT - Fonctions anonymes non fléchées
items.forEach(function (item) {
  console.log(item);
});

// ✅ CORRECT - Arrow function
items.forEach((item) => {
  console.log(item);
});
```

### Template Literals

```javascript
const userName = 'John';
const age = 30;

// ✅ CORRECT - Template literals
const message = `Bonjour ${userName}, vous avez ${age} ans.`;
const html = `
  <div class="user">
    <h2>${userName}</h2>
    <p>Age: ${age}</p>
  </div>
`;

// ❌ INCORRECT - Concaténation de strings
const message = 'Bonjour ' + userName + ', vous avez ' + age + ' ans.';
```

### Async/Await

```javascript
// ✅ CORRECT - async/await avec try/catch
async function fetchUserData(userId) {
  try {
    const response = await fetch(`/api/users/${userId}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching user:', error);
    throw error;
  }
}

// ✅ CORRECT - Promise.all pour les appels parallèles
async function fetchMultipleUsers(userIds) {
  const promises = userIds.map((id) => fetchUserData(id));
  const users = await Promise.all(promises);
  return users;
}

// ❌ INCORRECT - Callbacks imbriquées (callback hell)
fetchData((data) => {
  processData(data, (result) => {
    saveData(result, (saved) => {
      console.log(saved);
    });
  });
});

// ✅ CORRECT - Chaîne de promesses
fetchData()
  .then(processData)
  .then(saveData)
  .then((saved) => console.log(saved))
  .catch((error) => console.error(error));
```

### Manipulation de Tableaux et Objets

```javascript
const users = [
  { id: 1, name: 'Alice', active: true },
  { id: 2, name: 'Bob', active: false },
  { id: 3, name: 'Charlie', active: true },
];

// ✅ CORRECT - Méthodes fonctionnelles
const activeUsers = users.filter((user) => user.active);
const userNames = users.map((user) => user.name);
const totalActive = users.reduce((sum, user) => (user.active ? sum + 1 : sum), 0);

// ✅ CORRECT - Optional chaining et nullish coalescing
const userEmail = user?.contact?.email ?? 'no-email@example.com';

// ✅ CORRECT - Spread operator pour copie immuable
const updatedUser = { ...user, age: user.age + 1 };
const newArray = [...existingArray, newItem];

// ✅ CORRECT - Object.entries/keys/values
Object.entries(config).forEach(([key, value]) => {
  console.log(`${key}: ${value}`);
});

// ❌ INCORRECT - Mutation directe
users.push(newUser); // Si immutabilité requise
user.age = 31; // Si immutabilité requise
```

---

## 🎯 Bonnes Pratiques Modernes (ES2023/ES2024)

### Nouvelles fonctionnalités ES2023

```javascript
// ✅ CORRECT - Array.prototype.toSorted (copie immuable)
const numbers = [3, 1, 4, 1, 5];
const sorted = numbers.toSorted((a, b) => a - b); // [1, 1, 3, 4, 5]
// numbers reste inchangé: [3, 1, 4, 1, 5]

// ✅ CORRECT - Array.prototype.toReversed
const reversed = numbers.toReversed(); // [5, 1, 4, 1, 3]

// ✅ CORRECT - Array.prototype.toSpliced
const spliced = numbers.toSpliced(1, 2, 'a', 'b'); // [3, 'a', 'b', 1, 5]

// ✅ CORRECT - Array.prototype.with (modifier un élément par index)
const updated = numbers.with(2, 'X'); // [3, 1, 'X', 1, 5]

// ✅ CORRECT - Array.prototype.findLast et findLastIndex
const lastEven = numbers.findLast((n) => n % 2 === 0); // 4
const lastEvenIndex = numbers.findLastIndex((n) => n % 2 === 0); // 2
```

### Fonctionnalités ES2024

```javascript
// ✅ CORRECT - Array.prototype.groupBy (proposé pour ES2024)
// Note: Utiliser un polyfill ou attendre la stabilisation
const grouped = Object.groupBy(users, (user) => user.active ? 'active' : 'inactive');

// ✅ CORRECT - Promise.withResolvers
const { promise, resolve, reject } = Promise.withResolvers();

// ✅ CORRECT - String.prototype.isWellFormed et toWellFormed
const isValid = str.isWellFormed();
const wellFormed = str.toWellFormed();
```

### Classes Modernes

```javascript
// ✅ CORRECT - Classes avec champs privés et statiques
class User {
  // Champs privés (ES2022+)
  #id;
  #password;

  // Champs statiques
  static count = 0;
  static MAX_USERS = 100;

  constructor(id, name, email) {
    this.#id = id;
    this.name = name;
    this.email = email;
    User.count++;
  }

  // Getter
  get id() {
    return this.#id;
  }

  // Méthode privée
  #validateEmail(email) {
    return email.includes('@');
  }

  // Méthode statique
  static createGuest() {
    return new User(null, 'Guest', 'guest@example.com');
  }

  // Méthode publique
  toJSON() {
    return {
      id: this.#id,
      name: this.name,
      email: this.email,
    };
  }
}
```

---

## 🧹 Clean Code JavaScript

### Principes SOLID

```javascript
// ❌ INCORRECT - Violation du Single Responsibility Principle
class UserManager {
  createUser(data) {
    // Création utilisateur
  }

  sendEmail(user, message) {
    // Envoi d'email
  }

  generateReport() {
    // Génération de rapport
  }
}

// ✅ CORRECT - Séparation des responsabilités
class UserService {
  createUser(data) {
    // Création utilisateur uniquement
  }
}

class EmailService {
  sendEmail(user, message) {
    // Envoi d'email uniquement
  }
}

class ReportGenerator {
  generateReport() {
    // Génération de rapport uniquement
  }
}
```

### Nommage

```javascript
// ✅ CORRECT - Noms descriptifs et explicites
const MAX_RETRY_ATTEMPTS = 3;
const isUserActive = true;
const getUserById = (id) => { /* ... */ };
const calculateTotalPrice = (items) => { /* ... */ };

// ❌ INCORRECT - Noms ambigus
const max = 3;
const active = true;
const getUser = (id) => { /* ... */ };
const calc = (items) => { /* ... */ };

// ✅ CORRECT - Booléens avec préfixes interrogatifs
const isLoading = false;
const hasPermission = true;
const canEdit = false;
const shouldUpdate = true;

// ✅ CORRECT - Fonctions verbe + complément
function validateEmail(email) { }
function fetchUserData(userId) { }
function renderUserList(users) { }
function handleButtonClick(event) { }
```

### Commentaires et Documentation

```javascript
// ✅ CORRECT - JSDoc pour les fonctions publiques
/**
 * Calcule le prix total d'une commande avec remise.
 *
 * @param {Array<Object>} items - Les articles de la commande
 * @param {number} items[].price - Prix unitaire
 * @param {number} items[].quantity - Quantité
 * @param {number} [discountPercent=0] - Pourcentage de remise (0-100)
 * @returns {number} Le prix total après remise
 * @throws {Error} Si un prix est négatif
 *
 * @example
 * const total = calculateOrderTotal(
 *   [{ price: 100, quantity: 2 }, { price: 50, quantity: 1 }],
 *   10
 * ); // 225
 */
function calculateOrderTotal(items, discountPercent = 0) {
  const subtotal = items.reduce((sum, item) => {
    if (item.price < 0) {
      throw new Error('Le prix ne peut pas être négatif');
    }
    return sum + item.price * item.quantity;
  }, 0);

  return subtotal * (1 - discountPercent / 100);
}

// ❌ INCORRECT - Commentaires inutiles ou redondants
// Incrémente i de 1
i++;

// ✅ CORRECT - Explication du POURQUOI, pas du QUOI
// Ajuster le compteur car l'API commence à 1, pas 0
currentPage = response.page - 1;
```

### Gestion des Erreurs

```javascript
// ✅ CORRECT - Erreurs personnalisées
class ValidationError extends Error {
  constructor(message, field) {
    super(message);
    this.name = 'ValidationError';
    this.field = field;
  }
}

class ApiError extends Error {
  constructor(message, statusCode) {
    super(message);
    this.name = 'ApiError';
    this.statusCode = statusCode;
  }
}

// ✅ CORRECT - Propager les erreurs avec contexte
async function fetchUser(userId) {
  try {
    const response = await fetch(`/api/users/${userId}`);
    if (!response.ok) {
      throw new ApiError(
        `Failed to fetch user ${userId}`,
        response.status
      );
    }
    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) {
      throw error; // Propager l'erreur API
    }
    throw new Error(`Network error while fetching user ${userId}: ${error.message}`);
  }
}

// ✅ CORRECT - Early returns
defunction processPayment(order) {
  if (!order) {
    throw new ValidationError('Order is required', 'order');
  }

  if (order.total <= 0) {
    throw new ValidationError('Order total must be positive', 'total');
  }

  if (!order.items || order.items.length === 0) {
    throw new ValidationError('Order must contain items', 'items');
  }

  // Logique de traitement du paiement...
  return processStripePayment(order);
}
```

### Modules et Architecture

```javascript
// ✅ CORRECT - Structure de fichiers claire
// src/
//   ├── components/
//   │   ├── Button.js
//   │   └── Card.js
//   ├── services/
//   │   ├── api.js
//   │   └── auth.js
//   ├── utils/
//   │   ├── helpers.js
//   │   └── validators.js
//   ├── constants.js
//   └── main.js

// ✅ CORRECT - Exports nommés pour les utilitaires
// utils/validators.js
export const isEmail = (email) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
export const isUrl = (url) => {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
};

// ✅ CORRECT - Export par défaut pour les composants/classes principaux
// components/Button.js
export default class Button {
  constructor(options) {
    this.options = options;
  }

  render() {
    // ...
  }
}

// ✅ CORRECT - Imports organisés
// main.js
// 1. Imports standards (Node.js/built-in)
import fs from 'node:fs';

// 2. Imports externes (node_modules)
import dayjs from 'dayjs';

// 3. Imports internes
import Button from './components/Button.js';
import { isEmail } from './utils/validators.js';

// 4. Imports constants/config
import { API_URL } from './constants.js';
```

---

## 🚀 Utilisation

### Commandes de Base

```bash
# Linter un fichier spécifique
npx eslint mon-fichier.js

# Linter tout le projet
npx eslint .

# Linter avec correction automatique
npx eslint --fix .

# Linter avec rapport détaillé
npx eslint --format=stylish .

# Linter avec format JSON
npx eslint --format=json . > lint-report.json

# Ignorer des règles spécifiques
npx eslint --rule 'no-console: off' .
```

### Formatage avec Prettier

```bash
# Formater un fichier
npx prettier --write mon-fichier.js

# Formater tout le projet
npx prettier --write .

# Vérifier le formatage sans modifier
npx prettier --check .

# Formater avec une largeur spécifique
npx prettier --write --print-width 120 .

# Formater des fichiers spécifiques
npx prettier --write "src/**/*.{js,ts}"
```

### Scripts NPM recommandés

```json
{
  "scripts": {
    "lint": "eslint . --ext .js,.mjs",
    "lint:fix": "eslint . --ext .js,.mjs --fix",
    "format": "prettier --write \"**/*.{js,mjs,json,md}\"",
    "format:check": "prettier --check \"**/*.{js,mjs,json,md}\"",
    "code:check": "npm run lint && npm run format:check",
    "code:fix": "npm run lint:fix && npm run format",
    "precommit": "npm run code:check"
  }
}
```

### Intégration avec Pre-commit

```yaml
# .pre-commit-config.yaml
repos:
  # ESLint
  - repo: https://github.com/pre-commit/mirrors-eslint
    rev: v8.55.0
    hooks:
      - id: eslint
        files: \.(js|mjs)$
        types: [file]
        additional_dependencies:
          - eslint@8.57.0
          - eslint-config-prettier@9.1.0
          - eslint-plugin-import@2.29.1
          - eslint-plugin-unicorn@51.0.1
          - eslint-plugin-security@2.1.0

  # Prettier
  - repo: https://github.com/pre-commit/mirrors-prettier
    rev: v3.1.0
    hooks:
      - id: prettier
        files: \.(js|mjs|json|md)$
```

### Intégration CI/CD (GitHub Actions)

```yaml
# .github/workflows/lint.yml
name: Lint JavaScript

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run ESLint
        run: npm run lint

      - name: Run Prettier (check)
        run: npm run format:check
```

---

## 📝 Règles de Style JavaScript

### Indentation et Formatage

```javascript
// ✅ CORRECT - Indentation avec 2 espaces
function example() {
  if (condition) {
    doSomething();
  }
}

// ✅ CORRECT - Point-virgules obligatoires
const x = 5;
const y = 10;

// ✅ CORRECT - Accolades sur la même ligne
if (condition) {
  doSomething();
} else {
  doOtherThing();
}

// ✅ CORRECT - Espaces autour des opérateurs
const sum = a + b;
const isValid = age >= 18 && hasLicense;

// ✅ CORRECT - Pas d'espaces dans les objets/tableaux simples
const obj = { a: 1, b: 2 };
const arr = [1, 2, 3];

// ✅ CORRECT - Espaces dans les objets/tableaux complexes
const complexObj = {
  user: {
    name: 'John',
    email: 'john@example.com',
  },
  settings: {
    theme: 'dark',
    notifications: true,
  },
};
```

### Naming Conventions

```javascript
// ✅ CORRECT - Variables et fonctions (camelCase)
const userName = 'John';
const emailAddress = 'john@example.com';
function calculateTotal() { }
function fetchUserData() { }

// ✅ CORRECT - Classes (PascalCase)
class UserService { }
class PaymentProcessor { }

// ✅ CORRECT - Constantes (UPPER_SNAKE_CASE)
const MAX_RETRY_COUNT = 3;
const API_BASE_URL = 'https://api.example.com';

// ✅ CORRECT - Booléens avec préfixes
const isActive = true;
const hasPermission = false;
const canEdit = true;
const shouldUpdate = false;

// ❌ INCORRECT
const user_name = 'John'; // snake_case pour variables
const EmailAddress = 'john@example.com'; // PascalCase pour variable
class userService { } // camelCase pour classe
```

### Structure du Code

```javascript
// ✅ CORRECT - Ordre dans un fichier
/**
 * @fileoverview Module de gestion des utilisateurs
 * @module UserModule
 */

// 1. Imports
import { helper } from './utils.js';
import { API_URL } from './constants.js';

// 2. Constantes
const MAX_USERS = 100;
const CACHE_DURATION = 300000; // 5 minutes

// 3. Variables privées
let currentUser = null;
const userCache = new Map();

// 4. Fonctions utilitaires
function validateUserData(data) {
  // ...
}

// 5. Classe principale
class UserService {
  constructor() {
    this.users = [];
  }

  async getUser(id) {
    // ...
  }
}

// 6. Export
export { UserService, validateUserData };
export default UserService;
```

---

## 🧪 Bonnes Pratiques pour les Tests

### Structure des Tests

```javascript
// ✅ CORRECT - Tests bien structurés avec describe/it
import { describe, it, expect, beforeEach } from 'vitest';
import { Calculator } from './calculator.js';

describe('Calculator', () => {
  let calculator;

  beforeEach(() => {
    calculator = new Calculator();
  });

  describe('add', () => {
    it('should add two positive numbers', () => {
      expect(calculator.add(2, 3)).toBe(5);
    });

    it('should handle negative numbers', () => {
      expect(calculator.add(-2, 3)).toBe(1);
    });

    it('should return zero when adding zero', () => {
      expect(calculator.add(5, 0)).toBe(5);
    });
  });

  describe('divide', () => {
    it('should throw when dividing by zero', () => {
      expect(() => calculator.divide(10, 0)).toThrow('Division by zero');
    });
  });
});

// ✅ CORRECT - Tests async/await
describe('UserService', () => {
  it('should fetch user by id', async () => {
    const user = await userService.getUser(1);
    expect(user).toHaveProperty('id', 1);
    expect(user).toHaveProperty('name');
  });

  it('should throw error for non-existent user', async () => {
    await expect(userService.getUser(999)).rejects.toThrow('User not found');
  });
});
```

### Mocks et Stubs

```javascript
// ✅ CORRECT - Mocking avec vi.fn()
import { vi, describe, it, expect } from 'vitest';
import { sendEmail } from './email.js';

vi.mock('./email.js', () => ({
  sendEmail: vi.fn().mockResolvedValue({ success: true }),
}));

describe('UserRegistration', () => {
  it('should send welcome email after registration', async () => {
    const user = await registerUser({ email: 'test@example.com' });

    expect(sendEmail).toHaveBeenCalledWith({
      to: 'test@example.com',
      template: 'welcome',
    });
    expect(sendEmail).toHaveBeenCalledTimes(1);
  });
});
```

---

## 🛠️ Configuration VS Code

### Extensions Recommandées

1. **ESLint** - Integrates ESLint JavaScript
2. **Prettier - Code: formatter** - Code: formatter using prettier
3. **JavaScript (ES6) code snippets** - Code: snippets for JavaScript
4. **JSDoc** - JSDoc comment support
5. **npm Intellisense** - Autocompletes npm modules
6. **Path Intellisense** - Autocompletes filenames

### settings.json

```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "eslint.validate": ["javascript", "javascriptreact"],
  "eslint.workingDirectories": [{ "mode": "auto" }],
  "javascript.updateImportsOnFileMove.enabled": "always",
  "javascript.preferences.importModuleSpecifier": "relative",
  "emmet.includeLanguages": {
    "javascript": "javascriptreact"
  },
  "[javascript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode",
    "editor.formatOnSave": true
  }
}
```

---

## 📊 Checklist Pré-Création de Fichier

Avant de créer ou modifier un fichier JavaScript, vérifier :

- [ ] ✅ Le fichier utilise ES Modules (`import`/`export`)
- [ ] ✅ ESLint ne rapporte aucune erreur
- [ ] ✅ Prettier est appliqué (formatage cohérent)
- [ ] ✅ Les noms respectent les conventions (camelCase, PascalCase)
- [ ] ✅ Les fonctions ont des noms descriptifs (verbe + complément)
- [ ] ✅ Les JSDoc sont présents pour les fonctions publiques
- [ ] ✅ Les lignes ne dépassent pas 100 caractères
- [ ] ✅ L'indentation utilise 2 espaces
- [ ] ✅ Les points-virgules sont présents
- [ ] ✅ `const` est utilisé par défaut, `let` si nécessaire
- [ ] ✅ Pas de `var` utilisé
- [ ] ✅ Les fonctions fléchées sont utilisées quand approprié
- [ ] ✅ Les template literals sont utilisés pour les strings complexes
- [ ] ✅ La destructuration est utilisée pour les objets/tableaux
- [ ] ✅ L'optional chaining (`?.`) et nullish coalescing (`??`) sont utilisés
- [ ] ✅ Les erreurs sont gérées avec try/catch
- [ ] ✅ Pas de console.log en production (utiliser un logger)
- [ ] ✅ Pas de secrets ou credentials dans le code
- [ ] ✅ Les imports sont triés (builtin → external → internal)

### Workflow Recommandé

```bash
# 1. Après avoir écrit/modifié le fichier
npx eslint --fix mon-fichier.js

# 2. Formater avec Prettier
npx prettier --write mon-fichier.js

# 3. Vérifier qu'il n'y a plus d'erreurs
npx eslint mon-fichier.js
npx prettier --check mon-fichier.js

# 4. Si tout est OK, commit
```

---

## 🚀 Commandes de Vérification

### Script de Vérification Complet

```bash
#!/bin/bash
# lint-check-js.sh

echo "🔍 Vérification du code JavaScript..."
echo "=================================="

# Vérifier si les fichiers de config existent
if [ ! -f "eslint.config.js" ] && [ ! -f ".eslintrc.json" ]; then
    echo "⚠️  Fichier de configuration ESLint manquant"
fi

if [ ! -f ".prettierrc" ]; then
    echo "⚠️  Fichier .prettierrc manquant"
fi

echo ""
echo "📊 1/2 - ESLint..."
npx eslint . --ext .js,.mjs || echo "❌ ESLint a détecté des problèmes"

echo ""
echo "📊 2/2 - Prettier..."
npx prettier --check "**/*.{js,mjs}" || echo "❌ Prettier a détecté des problèmes de formatage"

echo ""
echo "✅ Vérification terminée !"
echo ""
echo "💡 Pour corriger automatiquement :"
echo "   npm run code:fix"
```

### Makefile

```makefile
.PHONY: lint lint-fix format format-check install-dev

install-dev:
	npm install

# Vérification complète
lint:
	@echo "🔍 ESLint..."
	npx eslint . --ext .js,.mjs

# Correction automatique
lint-fix:
	@echo "🔧 ESLint --fix..."
	npx eslint . --ext .js,.mjs --fix

# Formatage
format:
	@echo "🎨 Prettier..."
	npx prettier --write "**/*.{js,mjs,json,md}"

# Vérification du formatage
format-check:
	@echo "🔍 Prettier check..."
	npx prettier --check "**/*.{js,mjs,json,md}"

# Tout vérifier
code-check: lint format-check

# Tout corriger
code-fix: lint-fix format
```

---

## 📚 Ressources

- [MDN JavaScript](https://developer.mozilla.org/fr/docs/Web/JavaScript)
- [JavaScript.info](https://javascript.info/)
- [ESLint Documentation](https://eslint.org/docs/latest/)
- [Prettier Documentation](https://prettier.io/docs/en/)
- [Clean Code JavaScript](https://github.com/ryanmcdermott/clean-code-javascript)
- [JavaScript Style Guide](https://github.com/airbnb/javascript)
- [You Don't Know JS](https://github.com/getify/You-Dont-Know-JS)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

**Dernière mise à jour** : 2026-02-09  
**Version** : 1.0.0  
**Auteur** : Équipe Développement JavaScript
