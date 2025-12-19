# Notebooks - ETL World Cup

Documentation des notebooks du projet ETL données footballistiques couvrant les Coupes du Monde FIFA de 1930 à 2022.

## Vue d'ensemble

| Notebook | Phase | Description |
|----------|-------|-------------|
| `00-database-setup.ipynb` | Infrastructure | Création schéma PostgreSQL (tables, partitions, index, vues) |
| `01-extract-json-2018.ipynb` | Extract | Extraction WC 2018 depuis JSON FIFA API |
| `01b-validate-2014.ipynb` | Extract | Validation qualité données 2014 |
| `01c-clean-1930-2014.ipynb` | Extract | Nettoyage données historiques 1930-2014 |
| `01d-extract-2022.ipynb` | Extract | Extraction WC 2022 depuis Kaggle |
| `02-transform-2018.ipynb` | Transform | Transformation et normalisation 2018 |
| `02b-normalize-teams.ipynb` | Transform | Normalisation noms d'équipes (aliases) |
| `03-concat-and-index.ipynb` | Transform | Concaténation datasets + indexation |
| `04-load-database.ipynb` | Load | Chargement teams et matches dans PostgreSQL |
| `05-data-quality-kpi.ipynb` | Analyse | Qualité données + KPI de base |
| `06-sql-analytics.ipynb` | Analyse | Démonstration SQL avancé (partitionnement, vues, CTE) |
| `07-group-knockout-correlation.ipynb` | Analyse | Corrélation groupes → éliminatoires |

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
├── 01-extract-json-2018.ipynb
│   └─→ data/staging/matches_2018_raw.csv (64 matchs)
├── 01d-extract-2022.ipynb
│   └─→ data/processed/df_matches_final.csv (64 matchs)
├── 01b-validate-2014.ipynb
│   └─→ Validation (pas d'output direct)
└── 01c-clean-1930-2014.ipynb
    └─→ matches_complet_preli_dates.csv (7318 matchs)

TRANSFORM
├── 02-transform-2018.ipynb
│   └─→ data/processed/matches_2018_clean.csv
├── 02b-normalize-teams.ipynb
│   └─→ data/processed/teams_traitees.csv (226 équipes)
└── 03-concat-and-index.ipynb
    └─→ ONAFINILESAMIS.csv (7446 matchs avec IDs)

LOAD
└── 04-load-database.ipynb
    └─→ PostgreSQL (226 équipes, 7446 matchs)

ANALYSE
├── 05-data-quality-kpi.ipynb
├── 06-sql-analytics.ipynb
└── 07-group-knockout-correlation.ipynb
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

#### `01-extract-json-2018.ipynb`
- **Input** : `data/raw/data_2018.json` (structure FIFA API)
- **Process** :
  - Parsing JSON (équipes, groupes, phases éliminatoires)
  - Extraction détails matchs (IDs équipes, scores, dates, stades)
  - Séparation phase de groupes (48 matchs) / éliminatoires (16 matchs)
- **Output** : `data/staging/matches_2018_raw.csv` (64 matchs, 10 colonnes)

#### `01d-extract-2022.ipynb`
- **Input** : Dataset Kaggle + FIFA API
- **Process** :
  - Téléchargement via `kagglehub`
  - Nettoyage pourcentages possession
  - Gestion des tirs au but (score affiché vs vainqueur)
  - Feature engineering (total_goals, goal_difference)
- **Output** : `data/processed/df_matches_final.csv` (64 matchs, 14 colonnes)

#### `01b-validate-2014.ipynb`
- **Input** : `data/raw/WorldCupMatches2014.csv`
- **Process** :
  - Contrôle qualité (valeurs manquantes, doublons)
  - Détection de 16 MatchIDs dupliqués
  - Identification problèmes d'encodage (Côte d'Ivoire, caractères spéciaux)
- **Output** : Rapport de validation (pas de fichier CSV)

#### `01c-clean-1930-2014.ipynb`
- **Input** : `data/raw/matches_19302010.csv` (7299 lignes)
- **Process** :
  - Extraction édition depuis champs composites ("1930-URUGUAY")
  - Standardisation noms de rounds
  - Parsing scores complexes ("4-1 (3-0)" avec AET/replay/penalty)
  - Nettoyage noms d'équipes (suppression variantes localisées)
  - Suppression codes placeholder (A1, A2, WINNER, LOSER)
  - Détermination vainqueur matchs nuls éliminatoires
- **Output** : 7299 matchs prêts pour concaténation

---

### Phase Transform

#### `02-transform-2018.ipynb`
- **Input** : `data/staging/matches_2018_raw.csv`
- **Process** :
  - Validation schéma (colonnes requises)
  - Normalisation dates (datetime UTC)
  - Normalisation scores (int64)
  - Création colonne `result` (home_team/away_team/draw)
  - Standardisation noms de rounds
  - Construction dimension équipes (32 équipes)
- **Output** : `data/processed/matches_2018_clean.csv` (64 matchs)

#### `02b-normalize-teams.ipynb`
- **Input** : Noms d'équipes de tous les datasets
- **Process** :
  - Construction référentiel équipes (231 → 226 après déduplication)
  - Gestion équipes historiques (URSS, Yougoslavie, etc.)
  - Création mapping aliases (FRG→Germany, South Korea→Korea Republic)
  - Déduplication (ex: Antigua and Barbuda ID 8 & 9 → merge vers 8)
- **Output** : `data/processed/teams_traitees.csv` (226 équipes avec confederation + aliases JSON)

#### `03-concat-and-index.ipynb`
- **Input** :
  - `df_matches_finallast.csv` (2022, 64 matchs)
  - `matches_2018_cleanlast.csv` (2018, 64 matchs)
  - `matches_complet_preli_dateslast.csv` (1930-2014, 7318 matchs)
- **Process** :
  - Concaténation des 3 sources (7446 lignes)
  - Tri par édition + date
  - Mapping noms équipes → IDs (via teams_traitees.csv)
  - Attribution `id_match` séquentiel
- **Output** : `ONAFINILESAMIS.csv` (7446 matchs avec IDs numériques)

---

### Phase Load

#### `04-load-database.ipynb`
- **Input** :
  - `teams_traitees (2).csv` (226 équipes)
  - `ONAFINILESAMIS.csv` (7446 matchs 1930-2022)
- **Process** :
  - Insertion 226 équipes dans table `teams`
  - Insertion 7446 matchs dans table `matches` partitionnée
  - Gestion remapping IDs (doublons)
  - Validation qualité (nulls, scores, éditions)
  - Test des vues analytiques
- **Output** : Base PostgreSQL peuplée
- **Vérifications** : 226 équipes, 7446 matchs, vues testées

---

### Phase Analyse

#### `05-data-quality-kpi.ipynb`
- **Objectif** : Validation données et KPIs de base
- **KPIs calculés** :
  1. Qualité données : 6480 dates null (données 1930-2010)
  2. Validité scores : min/max (0-31 buts)
  3. Couverture : 22 éditions, 7446 matchs
  4. Champions : Top 8 (Brésil 5, Allemagne 4, Italie 4, Argentine 3...)
  5. Distribution résultats : 52.9% domicile, 26.2% extérieur, 20.9% nuls
  6. Scores extrêmes : Australie 31-0 Samoa américaines (2002)

#### `06-sql-analytics.ipynb`
- **Objectif** : Démonstration SQL avancé
- **Techniques SQL démontrées** :
  - Partitionnement : `EXPLAIN ANALYZE`, Partition Pruning
  - Vues : `v_team_stats`, `v_team_by_edition`, `v_head_to_head`
  - CTE (WITH) : Requêtes complexes avec sous-requêtes nommées
  - Window Functions : `RANK()`, `SUM() OVER`, `LAG()`, `DENSE_RANK()`
  - Conditional Aggregation : `CASE WHEN` dans agrégats
  - Requêtes paramétrées : `:team1`, `:team2`

#### `07-group-knockout-correlation.ipynb`
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
Teams (dimension):
  02b-normalize-teams.ipynb → teams_traitees.csv
                                     │
                                     ▼
Matches (faits):                03-concat-and-index.ipynb
  ┌─ 01-extract-json-2018 → 02-transform-2018 ─┐      │
  ├─ 01d-extract-2022.ipynb ───────────────────┼──────┤
  └─ 01c-clean-1930-2014.ipynb ────────────────┘      │
                                                       ▼
                                              ONAFINILESAMIS.csv
                                                       │
                                                       ▼
                                              04-load-database.ipynb
                                                       │
                                                       ▼
                                              PostgreSQL Database
                                                       │
                              ┌─────────────────┬──────┴──────┐
                              ▼                 ▼              ▼
                      05-data-quality   06-sql-analytics  07-group-knockout
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
- **Volume** : 7446 matchs, 226 équipes
- **Qualité** : 6480 dates manquantes (données pré-2010)

### Connexion BDD
```python
from sqlalchemy import create_engine
engine = create_engine(DATABASE_URL)
```
