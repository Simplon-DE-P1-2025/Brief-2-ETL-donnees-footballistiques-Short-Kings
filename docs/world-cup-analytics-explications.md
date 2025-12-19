# Explication des Requêtes SQL - World Cup Analytics

Ce document explique en détail les requêtes SQL avancées utilisées dans le notebook `06-sql-analytics.ipynb`.

---

## Table des matières

1. [Setup et Connexion](#1-setup-et-connexion)
2. [Démonstration du Partitionnement](#2-démonstration-du-partitionnement)
3. [Utilisation des Vues](#3-utilisation-des-vues)
4. [Requêtes Analytiques (aperçu)](#4-requêtes-analytiques-aperçu)

---

## 1. Setup et Connexion

### 1.1 Fonction `run_query`

```python
def run_query(query: str, params: dict = None) -> pd.DataFrame:
    """Exécute une requête SQL et retourne un DataFrame."""
    with engine.connect() as conn:
        return pd.read_sql(text(query), conn, params=params)
```

**Explication :**
- `text(query)` : Convertit la chaîne SQL en objet SQLAlchemy, permettant l'utilisation de **paramètres nommés** (`:param`)
- `params=params` : Dictionnaire des paramètres à injecter dans la requête (protection contre les injections SQL)
- Le `with` garantit la fermeture propre de la connexion

### 1.2 Fonction `run_explain`

```python
def run_explain(query: str) -> pd.DataFrame:
    explain_query = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) {query}"
```

**Explication des options EXPLAIN :**

| Option | Description |
|--------|-------------|
| `ANALYZE` | Exécute réellement la requête et mesure les temps |
| `BUFFERS` | Affiche les statistiques d'accès aux buffers (cache) |
| `FORMAT TEXT` | Format de sortie lisible par l'humain |

Cette fonction permet d'analyser le **plan d'exécution** de PostgreSQL pour comprendre comment une requête est optimisée.

---

## 2. Démonstration du Partitionnement

Le partitionnement est une technique qui divise une grande table en plusieurs sous-tables plus petites (partitions). Dans ce projet, la table `matches` est **partitionnée par année d'édition** (1930, 1934, ..., 2022).

### 2.1 Exemple 1 : Sans filtre sur `edition`

```sql
SELECT COUNT(*) FROM matches WHERE home_team_id = 1
```

**Analyse du plan d'exécution :**

```
Aggregate  (cost=29.93..29.94 rows=1 width=8) (actual time=0.581..0.616 rows=1 loops=1)
  Buffers: shared hit=31
  ->  Append  (cost=0.00..29.86 rows=28 width=0)
        ->  Seq Scan on matches_1930 matches_1
              Filter: (home_team_id = 1)
        ->  Seq Scan on matches_1934 matches_2
              Filter: (home_team_id = 1)
        ...
        ->  Index Only Scan on matches_2022 matches_22
              Index Cond: (home_team_id = 1)
Planning Time: 22.302 ms
Execution Time: 1.007 ms
```

**Interprétation détaillée :**

| Élément | Signification |
|---------|---------------|
| `Aggregate` | Opération de comptage final |
| `Append` | PostgreSQL combine les résultats de **toutes les partitions** |
| `Seq Scan on matches_XXXX` | Scan séquentiel sur chaque partition (1930 à 2022) |
| `Index Only Scan` | Utilisation des index sur les partitions récentes |
| `Filter: (home_team_id = 1)` | Le filtre est appliqué sur chaque partition |
| `Buffers: shared hit=31` | 31 pages lues depuis le cache mémoire |
| `Planning Time: 22.302 ms` | Temps de planification (élevé car beaucoup de partitions) |
| `Execution Time: 1.007 ms` | Temps d'exécution total |

**Problème :** Sans filtre sur `edition`, PostgreSQL doit scanner les **22 partitions** (1930-2022).

### 2.2 Exemple 2 : Avec filtre sur `edition` (Partition Pruning)

```sql
SELECT COUNT(*) FROM matches WHERE home_team_id = 1 AND edition = 2018
```

**Plan d'exécution :**

```
Aggregate  (cost=1.26..1.27 rows=1 width=8) (actual time=0.009..0.009 rows=1 loops=1)
  Buffers: shared hit=1
  ->  Index Only Scan using matches_2018_home_team_id_edition_idx on matches_2018 matches
        Index Cond: ((home_team_id = 1) AND (edition = 2018))
        Heap Fetches: 0
Planning Time: 0.265 ms
Execution Time: 0.036 ms
```

**Interprétation détaillée :**

| Élément | Signification |
|---------|---------------|
| `Index Only Scan on matches_2018` | **Une seule partition** est scannée ! |
| `Buffers: shared hit=1` | Seulement 1 page lue (vs 31 avant) |
| `Planning Time: 0.265 ms` | ~84x plus rapide à planifier |
| `Execution Time: 0.036 ms` | ~28x plus rapide à exécuter |

**Partition Pruning :** PostgreSQL détecte automatiquement que seule la partition `matches_2018` contient des données pour `edition = 2018` et ignore toutes les autres.

### 2.3 Exemple 3 : Plage d'éditions

```sql
SELECT * FROM matches WHERE edition BETWEEN 2014 AND 2022
```

**Plan d'exécution :**

```
Append  (cost=0.00..44.24 rows=1012 width=264) (actual time=0.032..0.298 rows=1012 loops=1)
  Buffers: shared hit=24
  ->  Seq Scan on matches_2014 matches_1
        Filter: ((edition >= 2014) AND (edition <= 2022))
  ->  Seq Scan on matches_2018 matches_2
  ->  Seq Scan on matches_2022 matches_3
Planning Time: 0.731 ms
Execution Time: 0.377 ms
```

**Interprétation :**
- PostgreSQL identifie que seules **3 partitions** (2014, 2018, 2022) correspondent à la plage
- Les 19 autres partitions sont **ignorées** (pruning)
- Performance optimisée : scan de 3 partitions au lieu de 22

### 2.4 Exemple 4 : Agrégation par partition

```sql
SELECT
    edition,
    COUNT(*) as matches,
    ROUND(AVG(home_result + away_result), 2) AS avg_goals
FROM matches
WHERE round != 'Preliminary'
GROUP BY edition
ORDER BY edition
```

**Explication :**

| Clause | Rôle |
|--------|------|
| `COUNT(*)` | Compte le nombre de matchs par édition |
| `AVG(home_result + away_result)` | Moyenne des buts totaux par match |
| `ROUND(..., 2)` | Arrondit à 2 décimales |
| `WHERE round != 'Preliminary'` | Exclut les matchs préliminaires |
| `GROUP BY edition` | Agrège par année d'édition |

**Avantage du partitionnement :** Chaque partition correspond exactement à un groupe `edition`, donc PostgreSQL peut traiter chaque partition indépendamment.

### 2.5 Résumé : Avantages du Partitionnement

| Avantage | Description |
|----------|-------------|
| **Partition Pruning** | Seules les partitions pertinentes sont scannées |
| **Maintenance facilitée** | Possibilité de supprimer/archiver une partition entière |
| **Index plus petits** | Chaque partition a ses propres index, plus rapides |
| **Parallélisation** | PostgreSQL peut scanner plusieurs partitions en parallèle |
| **Temps de planification** | Plus rapide quand le filtre exclut beaucoup de partitions |

---

## 3. Utilisation des Vues

### 3.1 Qu'est-ce qu'une Vue ?

Une **vue** est une requête SQL stockée sous forme de "table virtuelle". Elle ne stocke pas de données, mais exécute la requête à chaque appel.

```sql
-- Lister les vues disponibles
SELECT table_name
FROM information_schema.views
WHERE table_schema = 'public'
```

**Vues disponibles :**
- `v_team_stats` : Statistiques globales par équipe
- `v_team_by_edition` : Statistiques par équipe ET par édition
- `v_head_to_head` : Historique des confrontations directes

### 3.2 Exemple d'utilisation de `v_team_stats`

```sql
SELECT * FROM v_team_stats
WHERE total_matches >= 10
ORDER BY win_rate DESC
LIMIT 30
```

**Ce que contient la vue :**

| Colonne | Description |
|---------|-------------|
| `id_team` | Identifiant unique de l'équipe |
| `nom_standard` | Nom standardisé de l'équipe |
| `confederation` | Confédération (UEFA, CONMEBOL, etc.) |
| `total_matches` | Nombre total de matchs joués |
| `editions` | Nombre de participations |
| `wins`, `draws`, `losses` | Victoires, nuls, défaites |
| `goals_for`, `goals_against` | Buts pour/contre |
| `goal_difference` | Différence de buts |
| `win_rate` | Taux de victoire (%) |
| `avg_goals_scored` | Moyenne buts marqués/match |
| `avg_goals_conceded` | Moyenne buts encaissés/match |
| `clean_sheets` | Matchs sans encaisser de but |

**Avantage :** Au lieu de réécrire une requête complexe avec de multiples `JOIN` et agrégations, on interroge simplement la vue.

---

## 4. Requêtes Analytiques (aperçu)

### 4.1 Head-to-Head avec CTE et CASE WHEN

```sql
WITH confrontations AS (
    SELECT
        m.edition,
        m.round,
        t1.nom_standard AS home_team,
        t2.nom_standard AS away_team,
        m.home_result,
        m.away_result,
        -- Déterminer le vainqueur avec CASE
        CASE
            WHEN m.result = 'home_team' THEN t1.nom_standard
            WHEN m.result = 'away_team' THEN t2.nom_standard
            ELSE 'Draw'
        END AS winner
    FROM matches m
    JOIN teams t1 ON m.home_team_id = t1.id_team
    JOIN teams t2 ON m.away_team_id = t2.id_team
    WHERE
        (t1.nom_standard = :team1 AND t2.nom_standard = :team2)
        OR (t1.nom_standard = :team2 AND t2.nom_standard = :team1)
)
SELECT * FROM confrontations
```

**Explication des éléments :**

| Élément | Description |
|---------|-------------|
| `WITH ... AS` | **CTE** (Common Table Expression) - requête temporaire nommée |
| `:team1`, `:team2` | **Paramètres** injectés par Python (sécurisés) |
| `CASE WHEN ... END` | Expression conditionnelle pour déterminer le vainqueur |
| `JOIN teams t1 ON ...` | Jointure pour récupérer les noms d'équipes |

### 4.2 Window Functions (Fonctions de Fenêtrage)

```sql
SELECT
    edition,
    wins,
    -- Rang par nombre de victoires
    RANK() OVER (ORDER BY wins DESC) AS rank_by_wins,

    -- Cumul des victoires (somme progressive)
    SUM(wins) OVER (ORDER BY edition ROWS UNBOUNDED PRECEDING) AS cumul_wins,

    -- Moyenne mobile sur 3 éditions
    AVG(goals_for) OVER (
        ORDER BY edition
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS avg_goals_3_editions,

    -- Valeur de l'édition précédente
    LAG(wins) OVER (ORDER BY edition) AS prev_edition_wins
FROM v_team_by_edition
WHERE nom_standard = :team
```

**Explication des fonctions de fenêtrage :**

| Fonction | Description |
|----------|-------------|
| `RANK() OVER (ORDER BY ...)` | Attribue un rang basé sur le tri |
| `SUM() OVER (ORDER BY ... ROWS UNBOUNDED PRECEDING)` | Somme cumulative depuis le début |
| `AVG() OVER (ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)` | Moyenne des 3 dernières lignes (mobile) |
| `LAG(col) OVER (ORDER BY ...)` | Valeur de la ligne précédente |
| `DENSE_RANK() OVER (...)` | Rang sans trous (ex: 1, 2, 2, 3 au lieu de 1, 2, 2, 4) |

### 4.3 Conditional Aggregation

```sql
SELECT
    COUNT(*) AS total_matches,
    SUM(CASE WHEN winner = :team1 THEN 1 ELSE 0 END) AS team1_wins,
    SUM(CASE WHEN winner = :team2 THEN 1 ELSE 0 END) AS team2_wins,
    SUM(CASE WHEN winner = 'Draw' THEN 1 ELSE 0 END) AS draws
FROM confrontations
```

**Principe :** On utilise `CASE WHEN` à l'intérieur de `SUM()` pour compter conditionnellement. C'est équivalent à plusieurs `COUNT(*) WHERE ...` mais en une seule passe sur les données.

### 4.4 NULLIF pour éviter les divisions par zéro

```sql
SELECT
    nom_standard,
    goals_for,
    goals_against,
    ROUND(goals_for::DECIMAL / NULLIF(goals_against, 0), 2) AS goal_ratio
FROM v_team_stats
```

**Explication :**
- `NULLIF(goals_against, 0)` : Retourne `NULL` si `goals_against = 0`, sinon retourne la valeur
- Évite l'erreur `division by zero`
- `::DECIMAL` : Cast pour obtenir une division décimale (pas entière)

---

## Glossaire des Termes SQL

| Terme | Définition |
|-------|------------|
| **Partition Pruning** | Optimisation où PostgreSQL ignore les partitions non pertinentes |
| **CTE** | Common Table Expression - sous-requête nommée réutilisable |
| **Window Function** | Fonction qui calcule sur un ensemble de lignes liées à la ligne courante |
| **EXPLAIN ANALYZE** | Commande pour voir le plan d'exécution réel d'une requête |
| **Seq Scan** | Scan séquentiel (lecture de toutes les lignes) |
| **Index Scan** | Scan utilisant un index (plus rapide pour les filtres sélectifs) |
| **Index Only Scan** | Scan où toutes les données viennent de l'index (encore plus rapide) |
| **Buffers** | Pages de données en mémoire cache |
| **NULLIF** | Fonction retournant NULL si les deux arguments sont égaux |

---

## Conclusion

Ce notebook (`06-sql-analytics.ipynb`) démontre plusieurs techniques SQL avancées :

1. **Partitionnement** : Division de `matches` par `edition` pour des performances optimales
2. **Vues** : Pré-calcul des agrégats fréquemment utilisés (`v_team_stats`, `v_team_by_edition`, `v_head_to_head`)
3. **CTE** : Organisation lisible des requêtes complexes
4. **Window Functions** : Calculs analytiques (rang, cumul, moyenne mobile, LAG)
5. **Conditional Aggregation** : Comptages conditionnels en une seule requête
6. **Paramètres** : Requêtes réutilisables et sécurisées (`:team1`, `:team2`)
7. **NULLIF** : Protection contre les divisions par zéro
