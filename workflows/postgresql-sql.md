# Skill SQL PostgreSQL - Bonnes Pratiques et Conventions

## 🎯 Objectif

Ce skill définit les bonnes pratiques et conventions pour l'écriture de requêtes SQL avec PostgreSQL. **Il doit être consulté obligatoirement avant chaque création ou modification de requête SQL, schéma de base de données, ou migration.**

## ⚠️ Règle d'Or

> **AUCUNE requête SQL ne doit être écrite sans respecter ces conventions de sécurité, performance et lisibilité.**

---

## 📋 Installation et Configuration

### Installation PostgreSQL

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# macOS (avec Homebrew)
brew install postgresql
brew services start postgresql

# Windows
# Télécharger depuis https://www.postgresql.org/download/windows/
```

### Configuration de base

```sql
-- Fichier postgresql.conf (optimisations courantes)
-- /etc/postgresql/14/main/postgresql.conf

-- Mémoire
shared_buffers = 25% de la RAM totale
effective_cache_size = 50% de la RAM totale
work_mem = 256MB
maintenance_work_mem = 512MB

-- WAL (Write-Ahead Logging)
wal_buffers = 16MB
max_wal_size = 2GB
min_wal_size = 1GB

-- Connexions
max_connections = 200

-- Query Planner
effective_io_concurrency = 200
random_page_cost = 1.1  -- Pour SSD
```

### Outils recommandés

```bash
# psql - Client en ligne de commande
psql -h localhost -U username -d database_name

# pgAdmin - Interface graphique
# DBeaver - Client universel
# DataGrip - IDE JetBrains
```

---

## 🗄️ Conventions de Nommage

### Règles générales

| Élément | Convention | Exemple |
|---------|-----------|---------|
| Tables | snake_case, pluriel | `users`, `order_items` |
| Colonnes | snake_case | `first_name`, `created_at` |
| Clés primaires | `id` ou `table_id` | `id`, `user_id` |
| Clés étrangères | `table_id` | `user_id`, `product_id` |
| Index | `idx_table_column` | `idx_users_email` |
| Contraintes | `chk_description`, `fk_description` | `chk_positive_price` |
| Vues | `view_description` | `view_active_users` |
| Fonctions | `verb_noun` | `get_user_orders` |
| Triggers | `trigger_description` | `trigger_update_timestamp` |

### Exemples

```sql
-- ✅ CORRECT
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10, 2) NOT NULL
);

-- Index
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_order_items_order_id ON order_items(order_id);

-- ❌ INCORRECT
CREATE TABLE Users (  -- Majuscule interdite
    ID int primary key,  -- Majuscule, pas de type explicite
    Email varchar(255),  -- Majuscule
    firstName varchar(100)  -- camelCase interdit
);
```

---

## 🏗️ Création de Tables

### Structure recommandée

```sql
-- Table avec toutes les bonnes pratiques
CREATE TABLE products (
    -- Clé primaire
    id SERIAL PRIMARY KEY,
    
    -- Champs obligatoires
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    
    -- Champs optionnels
    description TEXT,
    sku VARCHAR(100) UNIQUE,
    
    -- Données numériques
    price DECIMAL(10, 2) NOT NULL CHECK (price >= 0),
    stock_quantity INTEGER NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
    
    -- Clés étrangères
    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    
    -- Champs de statut
    status VARCHAR(20) NOT NULL DEFAULT 'draft' 
        CHECK (status IN ('draft', 'published', 'archived')),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    
    -- Métadonnées temporelles
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Contraintes supplémentaires
    CONSTRAINT chk_price_positive CHECK (price >= 0),
    CONSTRAINT chk_name_not_empty CHECK (LENGTH(TRIM(name)) > 0)
);

-- Commentaires sur les tables et colonnes
COMMENT ON TABLE products IS 'Table des produits du catalogue';
COMMENT ON COLUMN products.price IS 'Prix en euros TTC';
COMMENT ON COLUMN products.sku IS 'Stock Keeping Unit - référence unique';
```

### Types de données recommandés

```sql
-- Identifiants
id SERIAL PRIMARY KEY;  -- Auto-incrément
id UUID PRIMARY KEY DEFAULT gen_random_uuid();  -- UUID

-- Texte
VARCHAR(n)  -- Texte court avec limite
TEXT        -- Texte long sans limite
CHAR(n)     -- Texte de longueur fixe (éviter)

-- Numériques
INTEGER         -- Entier standard
BIGINT          -- Grand entier (compteurs, IDs)
DECIMAL(10,2)   -- Monétaire (jamais FLOAT/DOUBLE)
REAL            -- Scientifique (éviter pour la monnaie)

-- Dates et heures
DATE                    -- Date seule
TIME                    -- Heure seule
TIMESTAMP               -- Date et heure (sans timezone)
TIMESTAMP WITH TIME ZONE -- Date et heure avec timezone (RECOMMANDÉ)
INTERVAL                -- Durée

-- Booléen
BOOLEAN  -- TRUE, FALSE, NULL

-- JSON
JSON   -- Stocké comme texte
JSONB  -- Stocké en binaire (RECOMMANDÉ - indexable)

-- Autres
INET      -- Adresse IP
CIDR      -- Plage d'IP
UUID      -- Identifiant universel
ARRAY     -- Tableau
ENUM      -- Énumération (ou CHECK constraint)
```

---

## 📊 Requêtes SELECT

### Structure de base

```sql
-- ✅ CORRECT - Format lisible
SELECT 
    u.id,
    u.first_name,
    u.last_name,
    u.email,
    COUNT(o.id) AS order_count,
    SUM(o.total_amount) AS total_spent
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.is_active = TRUE
    AND u.created_at >= '2024-01-01'
GROUP BY u.id, u.first_name, u.last_name, u.email
HAVING COUNT(o.id) > 0
ORDER BY total_spent DESC
LIMIT 10 OFFSET 0;

-- ❌ INCORRECT - Sur une ligne
select id,first_name,last_name from users where is_active=true order by id;
```

### Alias et jointures

```sql
-- Alias explicites
SELECT 
    p.name AS product_name,
    c.name AS category_name,
    pi.quantity AS stock_quantity
FROM products p
INNER JOIN categories c ON p.category_id = c.id
LEFT JOIN product_inventory pi ON p.id = pi.product_id
WHERE p.is_active = TRUE;

-- Types de jointures
INNER JOIN   -- Intersection (obligatoire)
LEFT JOIN    -- Tous les éléments de la table de gauche
RIGHT JOIN   -- Tous les éléments de la table de droite
FULL JOIN    -- Union des deux tables
CROSS JOIN   -- Produit cartésien (éviter)
```

### Filtres et conditions

```sql
-- WHERE avec opérateurs
SELECT * FROM products
WHERE 
    price BETWEEN 10 AND 100
    AND category_id IN (1, 2, 3)
    AND name ILIKE '%iphone%'  -- Insensible à la casse
    AND created_at >= CURRENT_DATE - INTERVAL '30 days'
    AND (stock_quantity > 0 OR allow_backorder = TRUE);

-- COALESCE pour valeurs NULL
SELECT 
    name,
    COALESCE(description, 'Pas de description') AS description
FROM products;

-- NULLIF pour éviter division par zéro
SELECT 
    total_sales / NULLIF(total_orders, 0) AS average_order_value
FROM sales_summary;
```

### Agrégations

```sql
-- GROUP BY avec fonctions d'agrégation
SELECT 
    DATE_TRUNC('month', created_at) AS month,
    status,
    COUNT(*) AS order_count,
    SUM(total_amount) AS total_revenue,
    AVG(total_amount) AS average_order_value,
    MIN(total_amount) AS min_order,
    MAX(total_amount) AS max_order
FROM orders
WHERE created_at >= CURRENT_DATE - INTERVAL '1 year'
GROUP BY DATE_TRUNC('month', created_at), status
HAVING COUNT(*) > 10
ORDER BY month DESC, total_revenue DESC;

-- GROUPING SETS pour rapports multi-niveaux
SELECT 
    COALESCE(category, 'TOTAL') AS category,
    COALESCE(status, 'ALL') AS status,
    COUNT(*) AS order_count,
    SUM(total_amount) AS revenue
FROM orders
GROUP BY GROUPING SETS (
    (category, status),
    (category),
    ()
)
ORDER BY category, status;
```

### Sous-requêtes

```sql
-- Sous-requête dans WHERE
SELECT * FROM products
WHERE category_id IN (
    SELECT id FROM categories 
    WHERE is_active = TRUE
);

-- Sous-requête dans FROM (CTE préférable)
WITH active_categories AS (
    SELECT id, name
    FROM categories
    WHERE is_active = TRUE
)
SELECT p.*, ac.name AS category_name
FROM products p
JOIN active_categories ac ON p.category_id = ac.id;

-- Sous-requête corrélée
SELECT 
    u.*,
    (SELECT COUNT(*) FROM orders o WHERE o.user_id = u.id) AS order_count
FROM users u;

-- EXISTS (plus performant que IN pour grandes tables)
SELECT * FROM users u
WHERE EXISTS (
    SELECT 1 FROM orders o 
    WHERE o.user_id = u.id 
    AND o.total_amount > 1000
);
```

---

## 🔄 Requêtes DML (INSERT, UPDATE, DELETE)

### INSERT

```sql
-- Insertion simple
INSERT INTO users (first_name, last_name, email)
VALUES ('John', 'Doe', 'john.doe@example.com');

-- Insertion multiple (préférable)
INSERT INTO users (first_name, last_name, email)
VALUES 
    ('John', 'Doe', 'john@example.com'),
    ('Jane', 'Smith', 'jane@example.com'),
    ('Bob', 'Johnson', 'bob@example.com')
ON CONFLICT (email) DO NOTHING;  -- Ignorer les doublons

-- Insertion avec RETURNING
INSERT INTO users (first_name, last_name, email)
VALUES ('John', 'Doe', 'john@example.com')
RETURNING id, created_at;

-- Insertion depuis SELECT
INSERT INTO user_archive (user_id, email, archived_at)
SELECT id, email, CURRENT_TIMESTAMP
FROM users
WHERE is_active = FALSE
  AND updated_at < CURRENT_DATE - INTERVAL '1 year';

-- Upsert (INSERT ou UPDATE)
INSERT INTO users (id, first_name, last_name, email)
VALUES (1, 'John', 'Doe', 'john@example.com')
ON CONFLICT (id) DO UPDATE SET
    first_name = EXCLUDED.first_name,
    last_name = EXCLUDED.last_name,
    email = EXCLUDED.email,
    updated_at = CURRENT_TIMESTAMP;
```

### UPDATE

```sql
-- Mise à jour simple
UPDATE users
SET 
    last_login = CURRENT_TIMESTAMP,
    login_count = login_count + 1
WHERE id = 123;

-- Mise à jour avec JOIN
UPDATE users u
SET 
    status = 'premium',
    updated_at = CURRENT_TIMESTAMP
FROM orders o
WHERE u.id = o.user_id
GROUP BY u.id
HAVING SUM(o.total_amount) > 10000;

-- Mise à jour avec RETURNING
UPDATE products
SET stock_quantity = stock_quantity - 1
WHERE id = 456
RETURNING id, name, stock_quantity;

-- Mise à jour conditionnelle avec CASE
UPDATE products
SET price = CASE
    WHEN category_id = 1 THEN price * 0.9  -- 10% de réduction
    WHEN category_id = 2 THEN price * 0.85 -- 15% de réduction
    ELSE price
END
WHERE is_active = TRUE;
```

### DELETE

```sql
-- Suppression simple
DELETE FROM users WHERE id = 123;

-- Suppression avec RETURNING
DELETE FROM users 
WHERE is_active = FALSE 
  AND created_at < CURRENT_DATE - INTERVAL '1 year'
RETURNING id, email;

-- Suppression avec sous-requête
DELETE FROM order_items
WHERE order_id IN (
    SELECT id FROM orders 
    WHERE status = 'cancelled'
);

-- TRUNCATE (suppression rapide de toute la table)
TRUNCATE TABLE temp_logs RESTART IDENTITY;

-- Suppression en cascade (attention !)
DELETE FROM users WHERE id = 123 CASCADE;
```

---

## 🛡️ Sécurité et Injection SQL

### Requêtes paramétrées (OBLIGATOIRE)

```python
# ✅ CORRECT - Python avec psycopg2
import psycopg2

conn = psycopg2.connect("dbname=mydb user=myuser")
cur = conn.cursor()

# JAMAIS de f-string ou concatenation
user_id = request.args.get('user_id')

# ✅ Paramétré
sql = "SELECT * FROM users WHERE id = %s AND is_active = %s"
cur.execute(sql, (user_id, True))

# ✅ Avec nom de paramètres
cur.execute(
    "SELECT * FROM users WHERE id = %(user_id)s AND is_active = %(active)s",
    {'user_id': user_id, 'active': True}
)

# ❌ INCORRECT - Vulnérable aux injections
sql = f"SELECT * FROM users WHERE id = {user_id}"  # DANGER !
cur.execute(sql)
```

```python
# ✅ CORRECT - Django ORM
from django.db import connection

with connection.cursor() as cursor:
    cursor.execute(
        "SELECT * FROM users WHERE email = %s",
        [user_email]
    )

# ✅ CORRECT - SQLAlchemy
from sqlalchemy import text

result = session.execute(
    text("SELECT * FROM users WHERE id = :user_id"),
    {"user_id": user_id}
)
```

### Échappement des identifiants

```python
# ✅ Utiliser des identifiants sécurisés
from psycopg2 import sql

table_name = 'users'  # Ne jamais venir d'input utilisateur directement
column_name = 'email'

query = sql.SQL("SELECT {} FROM {}").format(
    sql.Identifier(column_name),
    sql.Identifier(table_name)
)
```

---

## ⚡ Optimisation des Performances

### Indexation

```sql
-- Index simple
CREATE INDEX idx_users_email ON users(email);

-- Index unique
CREATE UNIQUE INDEX idx_users_email_unique ON users(email);

-- Index composite (ordre important)
CREATE INDEX idx_orders_user_status ON orders(user_id, status);

-- Index partiel (filtre)
CREATE INDEX idx_orders_active ON orders(created_at) 
WHERE status = 'active';

-- Index pour recherche texte (GIN)
CREATE INDEX idx_products_name_gin ON products 
USING gin(to_tsvector('french', name));

-- Index pour JSONB
CREATE INDEX idx_products_metadata ON products 
USING gin(metadata);

-- Supprimer un index
DROP INDEX IF EXISTS idx_users_email;

-- Analyser les index
SELECT 
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE tablename = 'users'
ORDER BY pg_relation_size(indexrelid) DESC;
```

### Analyse des requêtes

```sql
-- EXPLAIN ANALYZE pour voir le plan d'exécution
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT u.*, COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.created_at > '2024-01-01'
GROUP BY u.id;

-- Vérifier les requêtes lentes
SELECT 
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    rows
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Statistiques des tables
SELECT 
    schemaname,
    tablename,
    n_live_tup AS row_count,
    n_dead_tup AS dead_rows,
    last_vacuum,
    last_autovacuum
FROM pg_stat_user_tables
ORDER BY n_live_tup DESC;
```

### Optimisations courantes

```sql
-- Éviter SELECT *
-- ❌
SELECT * FROM users WHERE id = 123;

-- ✅
SELECT id, first_name, last_name, email FROM users WHERE id = 123;

-- Utiliser LIMIT pour pagination
SELECT * FROM orders
ORDER BY created_at DESC
LIMIT 20 OFFSET 0;  -- Page 1

-- Ou utiliser CURSOR pour grandes tables
DECLARE orders_cursor CURSOR FOR
SELECT * FROM orders WHERE status = 'pending';

FETCH 100 FROM orders_cursor;

-- Éviter les fonctions sur colonnes indexées
-- ❌ (ne peut pas utiliser l'index)
SELECT * FROM users WHERE LOWER(email) = 'john@example.com';

-- ✅ (si index fonctionnel créé)
CREATE INDEX idx_users_email_lower ON users(LOWER(email));
SELECT * FROM users WHERE LOWER(email) = 'john@example.com';

-- Utiliser EXISTS au lieu de COUNT pour vérifier l'existence
-- ❌
SELECT COUNT(*) > 0 FROM orders WHERE user_id = 123;

-- ✅
SELECT EXISTS(SELECT 1 FROM orders WHERE user_id = 123);

-- Utiliser UNION ALL au lieu de UNION si pas de doublons
-- ❌ (vérifie les doublons - coûteux)
SELECT id FROM table_a
UNION
SELECT id FROM table_b;

-- ✅ (plus rapide)
SELECT id FROM table_a
UNION ALL
SELECT id FROM table_b;
```

---

## 🔄 Transactions

### Gestion des transactions

```sql
-- Transaction simple
BEGIN;

UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;

COMMIT;

-- Transaction avec rollback
BEGIN;

INSERT INTO orders (user_id, total_amount) VALUES (1, 150.00);
INSERT INTO order_items (order_id, product_id, quantity) 
VALUES (currval('orders_id_seq'), 5, 2);

-- Si erreur
ROLLBACK;

-- Ou si succès
COMMIT;

-- Points de sauvegarde
BEGIN;

INSERT INTO orders (user_id, total_amount) VALUES (1, 150.00);
SAVEPOINT after_order_insert;

INSERT INTO order_items (order_id, product_id, quantity) 
VALUES (currval('orders_id_seq'), 5, 2);

-- Si erreur sur les items
ROLLBACK TO SAVEPOINT after_order_insert;

COMMIT;

-- Niveaux d'isolation
BEGIN TRANSACTION ISOLATION LEVEL READ COMMITTED;
-- ou REPEATABLE READ, SERIALIZABLE
```

### Python avec transactions

```python
import psycopg2
from psycopg2.extras import RealDictCursor

conn = psycopg2.connect("dbname=mydb user=myuser")

try:
    with conn.cursor() as cur:
        # Début implicite de transaction
        cur.execute(
            "UPDATE accounts SET balance = balance - %s WHERE id = %s",
            (100, 1)
        )
        cur.execute(
            "UPDATE accounts SET balance = balance + %s WHERE id = %s",
            (100, 2)
        )
        
    # Commit automatique si pas d'exception
    conn.commit()
    
except Exception as e:
    conn.rollback()
    print(f"Erreur: {e}")
    raise
finally:
    conn.close()
```

---

## 🔄 CTE (Common Table Expressions)

### CTE simple

```sql
WITH active_users AS (
    SELECT id, email, created_at
    FROM users
    WHERE is_active = TRUE
),
user_orders AS (
    SELECT 
        user_id,
        COUNT(*) AS order_count,
        SUM(total_amount) AS total_spent
    FROM orders
    WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY user_id
)
SELECT 
    au.id,
    au.email,
    COALESCE(uo.order_count, 0) AS order_count,
    COALESCE(uo.total_spent, 0) AS total_spent
FROM active_users au
LEFT JOIN user_orders uo ON au.id = uo.user_id
ORDER BY total_spent DESC;
```

### CTE récursive

```sql
-- Hiérarchie des catégories
WITH RECURSIVE category_tree AS (
    -- Base case
    SELECT 
        id,
        name,
        parent_id,
        0 AS level,
        name AS path
    FROM categories
    WHERE parent_id IS NULL
    
    UNION ALL
    
    -- Recursive case
    SELECT 
        c.id,
        c.name,
        c.parent_id,
        ct.level + 1,
        ct.path || ' > ' || c.name
    FROM categories c
    INNER JOIN category_tree ct ON c.parent_id = ct.id
)
SELECT 
    id,
    REPEAT('  ', level) || name AS indented_name,
    path
FROM category_tree
ORDER BY path;
```

---

## 📊 Vues et Fonctions

### Vues

```sql
-- Vue simple
CREATE OR REPLACE VIEW view_active_users AS
SELECT 
    u.id,
    u.first_name,
    u.last_name,
    u.email,
    COUNT(o.id) AS order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.is_active = TRUE
GROUP BY u.id, u.first_name, u.last_name, u.email;

-- Vue matérialisée (pour données lourdes)
CREATE MATERIALIZED VIEW view_monthly_sales AS
SELECT 
    DATE_TRUNC('month', created_at) AS month,
    COUNT(*) AS order_count,
    SUM(total_amount) AS revenue
FROM orders
GROUP BY DATE_TRUNC('month', created_at)
ORDER BY month;

-- Rafraîchir la vue matérialisée
REFRESH MATERIALIZED VIEW view_monthly_sales;
REFRESH MATERIALIZED VIEW CONCURRENTLY view_monthly_sales;  -- Sans verrou

-- Supprimer une vue
DROP VIEW IF EXISTS view_active_users;
```

### Fonctions

```sql
-- Fonction simple
CREATE OR REPLACE FUNCTION get_user_full_name(user_id INTEGER)
RETURNS VARCHAR AS $$
DECLARE
    full_name VARCHAR;
BEGIN
    SELECT first_name || ' ' || last_name
    INTO full_name
    FROM users
    WHERE id = user_id;
    
    RETURN full_name;
END;
$$ LANGUAGE plpgsql;

-- Fonction avec paramètres par défaut
CREATE OR REPLACE FUNCTION get_orders_by_date(
    start_date DATE DEFAULT CURRENT_DATE - INTERVAL '30 days',
    end_date DATE DEFAULT CURRENT_DATE
)
RETURNS TABLE (
    order_id INTEGER,
    user_email VARCHAR,
    total_amount DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        o.id,
        u.email,
        o.total_amount
    FROM orders o
    JOIN users u ON o.user_id = u.id
    WHERE o.created_at BETWEEN start_date AND end_date
    ORDER BY o.created_at DESC;
END;
$$ LANGUAGE plpgsql;

-- Utilisation
SELECT * FROM get_orders_by_date('2024-01-01', '2024-01-31');
SELECT * FROM get_orders_by_date();  -- Utilise les valeurs par défaut
```

### Triggers

```sql
-- Fonction pour mettre à jour updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger sur table
CREATE TRIGGER trigger_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger pour audit
CREATE TABLE users_audit (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    action VARCHAR(10),
    old_data JSONB,
    new_data JSONB,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    changed_by VARCHAR(100)
);

CREATE OR REPLACE FUNCTION audit_users_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        INSERT INTO users_audit (user_id, action, old_data)
        VALUES (OLD.id, 'DELETE', to_jsonb(OLD));
        RETURN OLD;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO users_audit (user_id, action, old_data, new_data)
        VALUES (NEW.id, 'UPDATE', to_jsonb(OLD), to_jsonb(NEW));
        RETURN NEW;
    ELSIF TG_OP = 'INSERT' THEN
        INSERT INTO users_audit (user_id, action, new_data)
        VALUES (NEW.id, 'INSERT', to_jsonb(NEW));
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_users_audit
    AFTER INSERT OR UPDATE OR DELETE ON users
    FOR EACH ROW
    EXECUTE FUNCTION audit_users_changes();
```

---

## 🧪 Tests et Validation

### Tests de schéma

```sql
-- Vérifier les contraintes
SELECT 
    tc.constraint_name,
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
    ON tc.constraint_name = kcu.constraint_name
LEFT JOIN information_schema.constraint_column_usage ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_name = 'orders';

-- Vérifier les index
SELECT 
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename = 'users';

-- Tester les performances
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM orders 
WHERE user_id = 123 
ORDER BY created_at DESC 
LIMIT 10;
```

### Validation des données

```sql
-- Vérifier l'intégrité référentielle
SELECT 
    o.id,
    o.user_id
FROM orders o
LEFT JOIN users u ON o.user_id = u.id
WHERE u.id IS NULL;

-- Vérifier les doublons
SELECT email, COUNT(*) as count
FROM users
GROUP BY email
HAVING COUNT(*) > 1;

-- Vérifier les valeurs NULL inattendues
SELECT * FROM products
WHERE price IS NULL OR name IS NULL;

-- Statistiques des données
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'users'
ORDER BY ordinal_position;
```

---

## 📝 Checklist Pré-Écriture SQL

Avant d'écrire une requête SQL, vérifier :

- [ ] ✅ Utiliser des requêtes paramétrées (jamais de concaténation)
- [ ] ✅ Vérifier que les identifiants suivent la convention snake_case
- [ ] ✅ Prévoir les index nécessaires pour les colonnes filtrées/jointes
- [ ] ✅ Utiliser EXPLAIN ANALYZE pour les requêtes complexes
- [ ] ✅ Limiter les résultats avec LIMIT pour les requêtes interactives
- [ ] ✅ Utiliser des transactions pour les opérations multi-tables
- [ ] ✅ Ajouter des commentaires pour les requêtes complexes
- [ ] ✅ Vérifier les permissions nécessaires
- [ ] ✅ Tester avec des jeux de données représentatifs
- [ ] ✅ Documenter les requêtes dans le code source

---

## 📚 Ressources

- [Documentation PostgreSQL](https://www.postgresql.org/docs/)
- [PostgreSQL Exercises](https://pgexercises.com/)
- [Use The Index, Luke](https://use-the-index-luke.com/)
- [PostgreSQL Wiki - Performance Optimization](https://wiki.postgresql.org/wiki/Performance_Optimization)
- [pgMustard - Explain Analyze Visualizer](https://pgmustard.com/)

---

**Dernière mise à jour** : 2026-02-04  
**Version** : 1.0.0  
**Auteur** : Équipe Développement Base de Données
