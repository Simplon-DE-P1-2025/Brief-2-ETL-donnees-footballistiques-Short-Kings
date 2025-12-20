# Notebooks - ETL World Cup

Documentation des notebooks du projet ETL données footballistiques couvrant les Coupes du Monde FIFA de 1930 à 2022.

## Vue d'ensemble

| Notebook | Phase | Description |
|----------|-------|-------------|
| `00-database-setup.ipynb` | Infrastructure | Création schéma PostgreSQL (tables, partitions, index, vues) |
| `01a-validate-2014.ipynb` | Extract | Validation qualité données 2014 |
| `01b-clean-1930-2014.ipynb` | Extract | Nettoyage données historiques 1930-2014 |
| `02a-extract-json-2018.ipynb` | Extract | Extraction WC 2018 depuis JSON FIFA API |
| `02b-transform-2018.ipynb` | Transform | Transformation et normalisation 2018 |
| `03-extract-2022.ipynb` | Extract | Extraction WC 2022 depuis Kaggle |
| `04-concat-and-index.ipynb` | Transform | Concaténation datasets + indexation |
| `05-create-json-mapping.ipynb` | Transform | Création référentiel équipes (confédérations, aliases) |
| `05b-map-team-ids.ipynb` | Transform | Attribution IDs numériques aux équipes |
| `06-normalize-teams.ipynb` | Transform | Normalisation et déduplication noms d'équipes |
| `07-load-database.ipynb` | Load | Chargement teams et matches dans PostgreSQL |
| `08-data-quality-kpi.ipynb` | Analyse | Qualité données + KPI de base |
| `09-sql-analytics.ipynb` | Analyse | Démonstration SQL avancé (partitionnement, vues, CTE) |
| `10-group-knockout-correlation.ipynb` | Analyse | Corrélation groupes → éliminatoires |

---

## Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    PIPELINE ETL COMPLET                      │
└─────────────────────────────────────────────────────────────┘

INFRASTRUCTURE (exécuter une fois)
└── 00-database-setup.ipynb
    └─→ Schéma PostgreSQL (teams, matches, vues analytiques)

EXTRACT
├── 01a-validate-2014.ipynb
│   └─→ Validation (pas d'output direct)
├── 01b-clean-1930-2014.ipynb
│   └─→ données historiques nettoyées (7299 matchs)
├── 02a-extract-json-2018.ipynb
│   └─→ data/staging/matches_2018_raw.csv (64 matchs)
└── 03-extract-2022.ipynb
    └─→ data/processed/df_matches_final.csv (64 matchs)

TRANSFORM
├── 02b-transform-2018.ipynb
│   └─→ data/processed/matches_2018_clean.csv
├── 04-concat-and-index.ipynb
│   └─→ data/processed/matches.csv (7427 matchs)
├── 05-create-json-mapping.ipynb
│   └─→ data/reference/teams_mapping.json (231 équipes)
├── 05b-map-team-ids.ipynb
│   └─→ matches.csv avec IDs numériques
└── 06-normalize-teams.ipynb
    └─→ data/processed/teams_traitees.csv (226 équipes)

LOAD
└── 07-load-database.ipynb
    └─→ PostgreSQL (226 équipes, 7427 matchs)

ANALYSE
├── 08-data-quality-kpi.ipynb
├── 09-sql-analytics.ipynb
└── 10-group-knockout-correlation.ipynb
```

---

## Détail des notebooks

### Infrastructure

#### `00-database-setup.ipynb`
- **Objectif** : Configuration initiale de la base de données
- **Process** :
  - Création table `teams` (id_team, nom_standard, confederation, aliases)
  - Création table `matches` partitionnée par édition (22 partitions: 1930-2022)
  - Création de 3 vues analytiques :
    - `v_team_stats` : Statistiques globales par équipe
    - `v_team_by_edition` : Stats par équipe par édition
    - `v_head_to_head` : Confrontations directes
- **Output** : Schéma PostgreSQL sur Render

---

### Phase Extract

#### `01a-validate-2014.ipynb`
- **Input** : `data/raw/WorldCupMatches2014.csv`
- **Process** :
  - Contrôle qualité (valeurs manquantes, doublons)
  - Détection de 16 MatchIDs dupliqués
  - Identification problèmes d'encodage (Côte d'Ivoire, caractères spéciaux)
- **Output** : Rapport de validation (pas de fichier CSV)

#### `01b-clean-1930-2014.ipynb`
- **Input** : `data/raw/matches_19302010.csv` (7299 lignes)
- **Process** :
  - Extraction édition depuis champs composites ("1930-URUGUAY")
  - Standardisation noms de rounds
  - Parsing scores complexes ("4-1 (3-0)" avec AET/replay/penalty)
  - Nettoyage noms d'équipes (suppression variantes localisées)
  - Suppression codes placeholder (A1, A2, WINNER, LOSER)
  - Détermination vainqueur matchs nuls éliminatoires
- **Output** : 7299 matchs prêts pour concaténation

#### `02a-extract-json-2018.ipynb`
- **Input** : `data/raw/data_2018.json` (structure FIFA API)
- **Process** :
  - Parsing JSON (équipes, groupes, phases éliminatoires)
  - Extraction détails matchs (IDs équipes, scores, dates, stades)
  - Séparation phase de groupes (48 matchs) / éliminatoires (16 matchs)
- **Output** : `data/staging/matches_2018_raw.csv` (64 matchs, 10 colonnes)

#### `03-extract-2022.ipynb`
- **Input** : Dataset Kaggle + FIFA API
- **Process** :
  - Téléchargement via `kagglehub`
  - Nettoyage pourcentages possession
  - Gestion des tirs au but (score affiché vs vainqueur)
  - Feature engineering (total_goals, goal_difference)
- **Output** : `data/processed/df_matches_final.csv` (64 matchs, 14 colonnes)

---

### Phase Transform

#### `02b-transform-2018.ipynb`
- **Input** : `data/staging/matches_2018_raw.csv`
- **Process** :
  - Validation schéma (colonnes requises)
  - Normalisation dates (datetime UTC)
  - Normalisation scores (int64)
  - Création colonne `result` (home_team/away_team/draw)
  - Standardisation noms de rounds
  - Construction dimension équipes (32 équipes)
- **Output** : `data/processed/matches_2018_clean.csv` (64 matchs)

#### `04-concat-and-index.ipynb`
- **Input** :
  - `df_matches_final.csv` (2022, 64 matchs)
  - `matches_2018_clean.csv` (2018, 64 matchs)
  - Données historiques nettoyées (1930-2014, 7299 matchs)
- **Process** :
  - Concaténation des 3 sources (7427 lignes)
  - Tri par édition + date
  - Attribution `id_match` séquentiel
- **Output** : `data/processed/matches.csv` (7427 matchs)

#### `05-create-json-mapping.ipynb`
- **Input** : Noms d'équipes de tous les datasets
- **Process** :
  - Construction référentiel équipes (231 équipes)
  - Attribution confédérations FIFA
  - Gestion équipes historiques (URSS, Yougoslavie, etc.)
  - Création aliases (FRG→Germany, South Korea→Korea Republic)
- **Output** : `data/reference/teams_mapping.json` (231 équipes avec confédération + aliases)

#### `05b-map-team-ids.ipynb`
- **Input** :
  - `data/processed/matches.csv`
  - `data/reference/teams_mapping.json`
- **Process** :
  - Mapping noms équipes → IDs numériques
  - Résolution des aliases
- **Output** : `data/processed/matches.csv` avec colonnes `home_team_id` et `away_team_id`

#### `06-normalize-teams.ipynb`
- **Input** : `data/reference/teams_mapping.json`
- **Process** :
  - Déduplication (231 → 226 équipes)
  - Gestion doublons (ex: Antigua and Barbuda ID 8 & 9 → merge vers 8)
  - Création table finale équipes
- **Output** : `data/processed/teams_traitees.csv` (226 équipes)

---

### Phase Load

#### `07-load-database.ipynb`
- **Input** :
  - `data/processed/teams_traitees.csv` (226 équipes)
  - `data/processed/matches.csv` (7427 matchs 1930-2022)
- **Process** :
  - Insertion 226 équipes dans table `teams`
  - Insertion 7427 matchs dans table `matches` partitionnée
  - Gestion remapping IDs (doublons)
  - Validation qualité (nulls, scores, éditions)
  - Test des vues analytiques
- **Output** : Base PostgreSQL peuplée
- **Vérifications** : 226 équipes, 7427 matchs, vues testées

---

### Phase Analyse

#### `08-data-quality-kpi.ipynb`
- **Objectif** : Validation données et KPIs de base
- **KPIs calculés** :
  1. Qualité données : 6480 dates null (données 1930-2010)
  2. Validité scores : min/max (0-31 buts)
  3. Couverture : 22 éditions, 7427 matchs
  4. Champions : Top 8 (Brésil 5, Allemagne 4, Italie 4, Argentine 3...)
  5. Distribution résultats : 52.9% domicile, 26.2% extérieur, 20.9% nuls
  6. Scores extrêmes : Australie 31-0 Samoa américaines (2002)

#### `09-sql-analytics.ipynb`
- **Objectif** : Démonstration SQL avancé
- **Techniques SQL démontrées** :
  - Partitionnement : `EXPLAIN ANALYZE`, Partition Pruning
  - Vues : `v_team_stats`, `v_team_by_edition`, `v_head_to_head`
  - CTE (WITH) : Requêtes complexes avec sous-requêtes nommées
  - Window Functions : `RANK()`, `SUM() OVER`, `LAG()`, `DENSE_RANK()`
  - Conditional Aggregation : `CASE WHEN` dans agrégats
  - Requêtes paramétrées : `:team1`, `:team2`

#### `10-group-knockout-correlation.ipynb`
- **Objectif** : Analyse prédictive groupes → parcours final (1954-2022)
- **Hypothèses testées** :
  - "7+ points = quarts quasi-certains" → **73.9%** atteignent les quarts
  - "Champions rarement invaincus" → **72.2%** ÉTAIENT invaincus
  - "1er > 2ème de groupe" → **21.1% vs 14.3%** deviennent champions
  - "Victoire au 1er match déterminante" → **8.7% vs 1.2%**
- **KPIs avancés** :
  - KPI 13: Stats moyennes par parcours final
  - KPI 14: Probabilités conditionnelles par points
  - KPI 15: Équipes invaincues (137/432 = 31.7%)
  - KPI 16: Profil champion (+1.00 victoires, +2.40 buts vs moyenne)
  - KPI 17: Corrélation Spearman r=0.735 (points ↔ tour final)
  - KPI 18: 1er vs 2ème de groupe
  - KPI 19: Impact du 1er match
  - KPI 20: Synthèse facteurs prédictifs

> **Note sur Spearman** : Mesure la corrélation de rang entre deux variables. r proche de 1 = forte corrélation positive. r=0.735 indique une relation significative entre les points en groupes et la phase finale atteinte.

---

## Dépendances entre notebooks

```
EXTRACT (sources de données):
  ┌─ 01a-validate-2014 ─┐
  │                     │
  ├─ 01b-clean-1930-2014 ──────────────────┐
  │                                        │
  ├─ 02a-extract-json-2018 → 02b-transform-2018 ─┤
  │                                        │
  └─ 03-extract-2022 ──────────────────────┘
                                           │
                                           ▼
                                  04-concat-and-index.ipynb
                                           │
                                           ▼
                                  matches.csv (7427 matchs)
                                           │
                      ┌────────────────────┴────────────────────┐
                      ▼                                         ▼
            05-create-json-mapping             05b-map-team-ids.ipynb
                      │                                         │
                      ▼                                         │
            teams_mapping.json ─────────────────────────────────┤
                      │                                         │
                      ▼                                         ▼
            06-normalize-teams.ipynb                   matches.csv (avec IDs)
                      │                                         │
                      ▼                                         │
            teams_traitees.csv ─────────────────────────────────┤
                                                                │
                                                                ▼
                                                    07-load-database.ipynb
                                                                │
                                                                ▼
                                                    PostgreSQL Database
                                                                │
                              ┌──────────────────┬──────────────┴──────────────┐
                              ▼                  ▼                             ▼
                      08-data-quality    09-sql-analytics          10-group-knockout
```

---

## Notes techniques

### Stack
- **Python** : pandas, numpy, json, scipy, plotly
- **Base de données** : PostgreSQL (hébergé sur Render)
- **ORM** : SQLAlchemy
- **Sources** : FIFA API, Kaggle (`kagglehub`)

### Données
- **Couverture** : 22 éditions (1930-2022)
- **Volume** : 7427 matchs, 226 équipes
- **Qualité** : 6480 dates manquantes (données pré-2010)

### Connexion BDD
```python
from sqlalchemy import create_engine
engine = create_engine(DATABASE_URL)
```
