# Projet ETL - Consolidation des Données Coupe du Monde FIFA 1930-2022

---

**Équipe Short Kings**
Formation Simplon Data Engineering
Décembre 2025

---

| Métrique | Valeur |
|----------|--------|
| Matchs consolidés | 7 446 |
| Équipes normalisées | 226 |
| Éditions couvertes | 22 (1930-2022) |
| Sources harmonisées | 4 |
| Durée du sprint | 4 jours |
| Contributeurs | 4 |

---

## Table des Matières

1. [Résumé Exécutif](#1-résumé-exécutif)
2. [Introduction et Contexte](#2-introduction-et-contexte)
3. [Sources de Données](#3-sources-de-données)
4. [Architecture du Pipeline ETL](#4-architecture-du-pipeline-etl)
5. [Qualité des Données et KPIs](#5-qualité-des-données-et-kpis)
6. [Difficultés Rencontrées et Solutions](#6-difficultés-rencontrées-et-solutions)
7. [Stack Technique et Compétences](#7-stack-technique-et-compétences)
8. [Conclusion et Perspectives](#8-conclusion-et-perspectives)
9. [Annexes](#9-annexes)

---

## 1. Résumé Exécutif

### Contexte

Dans le cadre de la formation Simplon Data Engineering, l'équipe **Short Kings** a réalisé un projet ETL complet visant à consolider **92 ans d'histoire** de la Coupe du Monde FIFA (1930-2022) en une base de données unique et exploitable.

### Objectif

Construire un pipeline ETL robuste permettant de :
- **Extraire** des données de 4 sources hétérogènes (CSV, JSON, API)
- **Transformer** et normaliser les données (notamment les 350+ variantes de noms d'équipes)
- **Charger** dans une base PostgreSQL partitionnée et optimisée

### Résultats Clés

| Livrable | Détail |
|----------|--------|
| Dataset consolidé | 7 446 matchs uniques avec IDs standardisés |
| Référentiel équipes | 226 équipes normalisées (incluant équipes historiques) |
| Base de données | PostgreSQL partitionnée par édition (22 partitions) |
| Vues analytiques | 3 vues pré-calculées (stats globales, par édition, confrontations) |
| Documentation | Pipeline reproductible avec 11 notebooks documentés |

### Valeur Ajoutée

- **Unicité** : Premier dataset consolidant l'intégralité des 22 éditions
- **Qualité** : Normalisation rigoureuse des noms d'équipes selon la FIFA sur 92 ans
- **Scalabilité** : Architecture extensible pour les futures éditions (2026, 2030)
- **Analyses** : Corrélation statistique phase de groupes → parcours final (r=0.735)

---

## 2. Introduction et Contexte

### 2.1 Présentation du Brief

Le brief Simplon demandait de créer une **pipeline ETL complète** pour les données de la Coupe du Monde FIFA, depuis l'extraction de données brutes jusqu'à leur exploitation analytique. Les contraintes principales étaient :

- Données provenant de sources multiples et hétérogènes
- Incohérences historiques (noms d'équipes, formats de dates)
- Nécessité d'une base de données relationnelle optimisée

### 2.2 Équipe et Répartition des Rôles

| Membre | Responsabilités | Commits |
|--------|-----------------|---------|
| **Zoubir** | Coordination (12+ PRs mergés), extraction WC 2022, gestion des APIs, documentation | 22 (37%) |
| **Romain** | Setup PostgreSQL partitionné, normalisation équipes (350+ aliases), requêtes SQL analytiques, refactoring | 19 (32%) |
| **JS** | Extraction données historiques 1930-2010, nettoyage CSV, concaténation datasets, parsing dates | 8 (13%) |
| **Sabine** | Extraction JSON WC 2018, transformation et mapping rounds, validation schémas, exports CSV | 7 (12%) |

### 2.3 Contraintes et Enjeux

| Contrainte | Impact | Solution |
|------------|--------|----------|
| **Temporelle** | 4 jours | Parallélisation des tâches, répartition par édition |
| **Hétérogénéité sources** | Formats CSV/JSON différents | Notebooks dédiés par source |
| **Données historiques** | Noms d'équipes incohérents, dates manquantes | Module de normalisation centralisé |
| **Scalabilité** | Futures éditions à intégrer | Partitionnement PostgreSQL |

Le projet reposait sur la validation collective du fichier ONAFINILESAMIS.csv avant tout chargement en base, et donc en amont sur la cohérence des 3 csv avec les tables de la base de données.

---

## 3. Sources de Données

### 3.1 Inventaire des Sources

| Source | Format | Période | Volume | Problèmes identifiés |
|--------|--------|---------|--------|---------------------|
| `matches_19302010.csv` | CSV | 1930-2010 | 7 299 lignes | Dates manquantes, noms avec caractères locaux |
| `WorldCupMatches2014.csv` | CSV | 2014 | 64 matchs | 16 MatchIDs dupliqués, encodage Côte d'Ivoire |
| `data_2018.json` | JSON | 2018 | 64 matchs | Structure imbriquée (groupes/éliminatoires) |
| Kaggle 2022 | API/CSV | 2022 | 64 matchs | Tirs au but non normalisés |

### 3.2 Analyse Exploratoire des Données

#### Problèmes identifiés par source

**Source 1930-2010 :**
- 6 480 dates manquantes (87% du dataset)
- 350+ variantes de noms d'équipes (ex: "Germany (Deutschland)", "FRG", "West Germany")
- Scores au format complexe : "4-1 (3-0)" avec indicateurs AET/replay/penalties
- Équipes historiques dissoutes (URSS, Yougoslavie, Tchécoslovaquie)

**Source 2014 :**
- 16 MatchIDs dupliqués à dédupliquer
- Caractères spéciaux corrompus (Côte d'Ivoire → "C�te d'Ivoire")

**Source 2018 :**
- JSON hiérarchique : `teams → groups → matches → knockouts`
- Nécessité de parsing récursif

**Source 2022 :**
- Distinction score affiché vs vainqueur final (tirs au but)
- Colonnes de possession en pourcentages

### 3.3 Schéma de Données Cible

```
┌─────────────────────────────────────────────────────────────┐
│                         SCHÉMA BDD                          │
└─────────────────────────────────────────────────────────────┘

┌──────────────────────┐         ┌──────────────────────────────┐
│       TEAMS          │         │          MATCHES             │
├──────────────────────┤         ├──────────────────────────────┤
│ id_team (PK)         │◄───────┐│ id_match (PK)                │
│ nom_standard         │        ││ home_team_id (FK) ──────────►│
│ confederation        │        ││ away_team_id (FK) ──────────►│
│ aliases (JSONB)      │        │└──────────────────────────────┤
└──────────────────────┘        │ home_result                   │
                                │ away_result                   │
                                │ result                        │
                                │ extra_time                    │
                                │ penalties                     │
                                │ replay                        │
                                │ date                          │
                                │ round                         │
                                │ city                          │
                                │ edition (partition key)       │
                                └──────────────────────────────┘
                                          │
                                          ▼
                                ┌──────────────────────┐
                                │    PARTITIONS        │
                                ├──────────────────────┤
                                │ matches_1930         │
                                │ matches_1934         │
                                │ ...                  │
                                │ matches_2022         │
                                └──────────────────────┘
```

---

## 4. Architecture du Pipeline ETL

### 4.1 Vue d'Ensemble

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
│   └─→ Validation (rapport qualité)
└── 01c-clean-1930-2014.ipynb
    └─→ 7 299 matchs nettoyés

TRANSFORM
├── 02-transform-2018.ipynb
│   └─→ data/processed/matches_2018_clean.csv
├── 02b-normalize-teams.ipynb
│   └─→ data/processed/teams_traitees.csv (226 équipes)
└── 03-concat-and-index.ipynb
    └─→ Dataset consolidé (7 446 matchs avec IDs)

LOAD
└── 04-load-database.ipynb
    └─→ PostgreSQL (226 équipes, 7 299 matchs)

ANALYSE
├── 05-data-quality-kpi.ipynb
├── 06-sql-analytics.ipynb
└── 07-group-knockout-correlation.ipynb
```

### 4.2 Phase Extract

#### Notebook `01-extract-json-2018.ipynb`

| Élément | Détail |
|---------|--------|
| **Input** | `data/raw/data_2018.json` |
| **Process** | Parsing JSON FIFA API, séparation groupes/éliminatoires |
| **Output** | `data/staging/matches_2018_raw.csv` (64 matchs) |
| **Défi** | Structure imbriquée sur 4 niveaux |

#### Notebook `01c-clean-1930-2014.ipynb`

| Élément | Détail |
|---------|--------|
| **Input** | `data/raw/matches_19302010.csv` |
| **Process** | Extraction édition, parsing scores complexes ("4-1 (3-0)") |
| **Output** | 7 299 matchs nettoyés |
| **Défi** | Gestion AET/replay/penalties dans les scores |

#### Notebook `01d-extract-2022.ipynb`

| Élément | Détail |
|---------|--------|
| **Input** | Dataset Kaggle via `kagglehub` |
| **Process** | Nettoyage possession, gestion tirs au but |
| **Output** | `data/processed/df_matches_final.csv` (64 matchs) |
| **Défi** | Distinction score affiché vs vainqueur final |

### 4.3 Phase Transform

#### Normalisation des Équipes (`02b-normalize-teams.ipynb`)

C'est le **cœur technique** du projet. Problématique : 350+ variantes de noms pour 226 équipes.

**Exemples de normalisation :**

| Alias original | Nom FIFA standard |
|----------------|-------------------|
| FRG (BRD / Westdeutschland) | Germany |
| Belgium (België) | Belgium |
| Ivory Coast (Côte d'Ivoire) | Côte d'Ivoire |
| South Korea (한국) | Korea Republic |
| C�te d'Ivoire | Côte d'Ivoire |
| Soviet Union (СССР) | Soviet Union |

**Gestion des équipes historiques :**

| Équipe dissoute | Année | Successeur FIFA | Confédération |
|-----------------|-------|-----------------|---------------|
| Soviet Union | 1991 | Russia | UEFA |
| Yugoslavia | 2003 | Serbia | UEFA |
| Czechoslovakia | 1993 | Czech Republic | UEFA |
| GDR | 1990 | Germany | UEFA |
| Zaire | 1997 | Congo DR | CAF |

**Règle spéciale Allemagne :**
> La RFA (FRG) est la continuité juridique de l'Allemagne actuelle selon les règles FIFA/UEFA. Tous les matchs de la RFA sont attribués à "Germany". Seule la RDA (GDR) reste une entité historique distincte.

#### Concaténation (`03-concat-and-index.ipynb`)

| Élément | Détail |
|---------|--------|
| **Inputs** | 3 datasets (2022: 64, 2018: 64, 1930-2014: 7 318) |
| **Process** | Fusion, tri chronologique, mapping équipes → IDs |
| **Output** | Dataset unifié avec `id_match` séquentiel |
| **Validation** | Vérification doublons, cohérence scores |

### 4.4 Détail par Dataset

#### 4.4.1 Dataset A : Éditions 1930-2010 (CSV Historique)

**A. Extract**

| Élément | Détail |
|---------|--------|
| **Source** | `data/raw/matches_19302010 (1).csv` |
| **Format** | CSV encodé Latin-1, 7 299 lignes × 8 colonnes |
| **Méthode** | Chargement pandas avec parsing manuel des champs complexes |
| **Résultat** | Dataset brut nécessitant un nettoyage intensif |

**B. Transform**

| Script | `01c-clean-1930-2014.ipynb` |
|--------|----------------------------|

| Problème / Besoin | Action Technique | Justification ("Pourquoi ?") | Impact |
|-------------------|------------------|------------------------------|--------|
| **167 variantes de noms d'équipes** | Module `teams_constants.py` avec `ALIASES_MAPPING` (167 entrées) | "Yugoslavia (Југославија)", "FRG", "West Germany" empêchent toute jointure SQL. C'était le **problème le plus bloquant** du projet. | Mapping centralisé vers 226 noms FIFA standards. Réutilisable pour toutes les éditions. |
| **Règles FIFA sur les pays disparus** | Dictionnaire `HISTORICAL_TEAMS` + décision d'équipe | URSS, Yougoslavie, Tchécoslovaquie : fusionner avec successeurs ou garder distincts ? La FIFA considère la RFA comme continuité juridique de l'Allemagne (10 aliases vers "Germany"), mais pas la RDA. | FRG → Germany, GDR reste distincte, URSS/Yougoslavie = entités historiques séparées dans le schéma. |
| **Détermination du vainqueur knockout** | Fonction `find_winner_from_next_round()` | Score 1-1 en demi-finale : qui a gagné ? Le CSV ne contient pas l'info des penalties. La fonction vérifie quelle équipe apparaît au tour suivant (`WINNER_ROUND_MAP`). | Seules 2 finales hardcodées (`FINALS_PENALTY_WINNERS`: 1994 Brazil, 2006 Italy). Le reste est déduit automatiquement. |
| **Dates absentes (87% des matchs)** | Schéma BDD avec `DATE NULL` | Débat équipe : inventer des dates ou accepter NULL ? Choix de l'intégrité sur la complétude. | PostgreSQL accepte les nulls, index partiels créés pour les requêtes avec date. |
| **25 formats de rounds différents** | Fonction `clean_round()` avec logique conditionnelle | `1/4_FINAL`, `QUARTERFINAL_STAGE` (1982), `SEMIFINAL_STAGE` (1974/78), `FINAL_ROUND` (1950). Formats historiques selon les époques. | Standardisation en 8 catégories : Preliminary, Group Stage, Second Group Stage, Round of 16, Quarter-finals, Semi-finals, Third Place, Final. |
| **Parsing scores complexes** | Regex `r'(\d+)-(\d+)'` + détection `(a.e.t.)`, `(r.)`, `(p)` | Format "4-1 (3-0)" mêlant score final et mi-temps. Détection prolongations via substring. | Colonnes séparées : `home_result`, `away_result`, `extra_time`, `penalties`, `replay`. |

---

#### 4.4.2 Dataset B : Édition 2014 (CSV Kaggle)

**A. Extract**

| Élément | Détail |
|---------|--------|
| **Source** | `data/raw/WorldCupMatches2014 (1).csv` |
| **Format** | CSV séparé par `;`, encodage Latin-1, **80 lignes** (dont 16 doublons cachés) |
| **Méthode** | Validation qualité via `duplicated().sum()` |
| **Résultat** | Anomalies détectées : `Nombre de doublons exacts : 16` |

**B. Transform**

| Script | `01b-validate-2014.ipynb` + `01c-clean-1930-2014.ipynb` |
|--------|--------------------------------------------------------|

| Problème / Besoin | Action Technique | Justification ("Pourquoi ?") | Impact |
|-------------------|------------------|------------------------------|--------|
| **16 MatchIDs dupliqués** | `df_raw.duplicated().sum()` puis inspection manuelle | 80 lignes au lieu de 64 attendues. Code : `matchids_dupliques = df_raw[df_raw['MatchID'].duplicated(keep=False)]['MatchID'].unique()` révèle 16 IDs concernés (ex: Brazil-Chile RO16, MatchID 300186487). | `drop_duplicates()` appliqué. **Leçon : toujours valider `shape` vs volume officiel FIFA (64 matchs).** |
| **Encodage cassé** | Mapping dans `ALIASES_MAPPING` | Fichier lu avec `encoding='latin-1'` mais contient UTF-8 : `"Cï¿½te d'Ivoire"` au lieu de `"Côte d'Ivoire"`. | Alias corrompu ajouté au dictionnaire de normalisation. |
| **Fragments HTML** | Détecté lors de `equipes.unique()` | `'rn">Bosnia and Herzegovina'` : résidu de scraping web visible lors de l'affichage de la liste des équipes. | Pattern regex pour supprimer les balises HTML résiduelles. |
| **Espaces parasites dans villes** | Détecté : `'Belo Horizonte '`, `'Salvador '` | Trailing spaces dans toutes les 12 villes. Cause des échecs de jointure silencieux. | `.str.strip()` appliqué sur la colonne City. |
| **Débat : stadium vs city** | Conservation de `city` uniquement | L'équipe a débattu : les deux colonnes existent dans 2014 mais pas dans 1930-2010. Cohérence historique prioritaire. | Colonne `stadium` abandonnée du schéma final. |

---

#### 4.4.3 Dataset C : Édition 2018 (JSON)

**A. Extract**

| Élément | Détail |
|---------|--------|
| **Source** | `data/raw/data_2018.json` |
| **Format** | JSON FIFA API sur 4 niveaux : `{stadiums, tvchannels, teams, groups: {a-h}, knockout: {round_16, round_8, round_4, round_2_loser, round_2}}` |
| **Méthode** | Parsing JSON et aplanissement (flattening) via itération sur `groups.values()` et `knockout.items()` |
| **Résultat** | Fichier intermédiaire `matches_2018_raw.csv` (64 lignes) |

**B. Transform**

| Script | `02-transform-2018.ipynb` |
|--------|--------------------------|

| Problème / Besoin | Action Technique | Justification ("Pourquoi ?") | Impact |
|-------------------|------------------|------------------------------|--------|
| **Dates avec Timezone** `2018-06-14T18:00:00+03:00` | `pd.to_datetime(utc=True).dt.normalize()` | Conversion UTC puis suppression de l'heure. Le schéma cible et les données de 1930 n'ont pas d'heure. Simplifie les tris chronologiques. | Format final `YYYY-MM-DD 00:00:00+00:00` puis export `.strftime("%Y-%m-%d")`. **Étape ayant demandé plusieurs itérations.** |
| **JSON hiérarchique (4 niveaux)** | Dictionnaires lookup + double boucle | `teams_lookup = {t["id"]: t["name"] for t in data["teams"]}`. Itération : `for group_data in data["groups"].values()` puis `for ko_key, ko_data in data["knockout"].items()`. **Étape la plus itérative** : nécessité de comprendre la structure avant de coder. | 3 lookups créés : `teams_lookup`, `stadiums_lookup_name`, `stadiums_lookup_city`. IDs résolus en noms lisibles. |
| **Absence de "Vainqueur"** | Fonction `compute_result()` | Seuls `home_result` et `away_result` sont présents. Logique : `if row["home_result"] > row["away_result"]: return row["home_team"]`. Nécessaire pour les KPI "Taux de victoire". | Colonne `result` = nom du vainqueur ou `"draw"`. |
| **Schéma hétérogène** | Renommage via `.rename(columns={...})` | Colonnes brutes `match_id`, `home_team` vs schéma cible `id_match`, `home_team_id`. L'insertion en base échoue si les noms diffèrent. | Structure alignée avec fichiers 1930-2014. |
| **Référentiel Équipes** | `pd.concat([home, away]).drop_duplicates()` | Besoin de la liste unique des 32 participants 2018 pour la table dimension. | DataFrame `teams_ref_2018` de 32 lignes généré. |
| **Incohérence Rounds** | Dictionnaire `KO_ROUND_MAP` + `round_mapping` | JSON utilise `round_16`, `round_2_loser`. Transformation : `"round_2_loser": "Third place"` puis normalisation `"Third place"` → `"Third Place"` (majuscule). | Filtres SQL uniformes sur toutes les années. |

---

#### 4.4.4 Dataset D : Édition 2022 (Hybride CSV/API)

**A. Extract**

| Élément | Détail |
|---------|--------|
| **Source primaire** | Dataset Kaggle (`Fifa_world_cup_matches.csv`) téléchargé via `kagglehub` pour les statistiques de jeu |
| **Enrichissement** | API Officielle FIFA (`api.fifa.com`) interrogée via `requests` pour récupérer les métadonnées officielles (Villes, Stades, Détails des Tirs au but) |
| **Méthode** | Extraction double et consolidation en mémoire |
| **Résultat** | Fichier `df_matches_final.csv` (64 matchs enrichis) |

**B. Transform**

| Script | `01d-extract-2022.ipynb` |
|--------|--------------------------|

| Problème / Besoin | Action Technique | Justification ("Pourquoi ?") | Impact |
|-------------------|------------------|------------------------------|--------|
| **Surcharge de données (88 colonnes)** | Feature Selection | Dataset Kaggle contenant xG, passes, pressings... Le schéma cible doit rester cohérent sur 100 ans. Les stats avancées (xG) n'existent pas pour 1930. | Dataset léger et performant (20 colonnes alignées avec l'historique). |
| **Types de données sales** `"52%"` | Cleaning & Casting | Possession stockée en string. Impossible d'effectuer des agrégations (moyenne de possession) sur du texte. | Fonction `clean_percentage` (strip %) + Conversion float. Analyses statistiques possibles. |
| **Métadonnées manquantes** | Enrichissement API FIFA | Le CSV Kaggle n'avait pas les noms des Stades ni les Villes (`None`). Nécessaire pour l'analyse géographique et la complétude des dimensions. | Appel API FIFA et Jointure (Merge) sur les noms d'équipes. Colonnes `city` et `id_stadium` remplies à 100%. |
| **Logique de Vainqueur (Tirs au but)** | Logique Hybride | Finale France-Argentine : Score 3-3. Le CSV brut ne donne pas le vainqueur final. Distinguer le score du match (nul) du sort du tournoi (élimination). | Calcul du score officiel (3-3) mais `result` indique correctement "Argentina" via les scores de penalty de l'API. |
| **Noms des Rounds** | Mapping Standard | API renvoie "Final", Kaggle "Category". Harmonisation avec les éditions 1930-2018. | Fonction `clean_round_name` pour normaliser (`1/2` → `Semi-final`). Filtres SQL uniformes sur toutes les années. |

---

### 4.5 Phase Load

#### Architecture PostgreSQL (`00-database-setup.ipynb`)

**Stratégie de partitionnement :**

```sql
CREATE TABLE matches (
    id_match        SERIAL,
    home_team_id    INTEGER NOT NULL REFERENCES teams(id_team),
    away_team_id    INTEGER NOT NULL REFERENCES teams(id_team),
    home_result     INTEGER NOT NULL CHECK (home_result >= 0),
    away_result     INTEGER NOT NULL CHECK (away_result >= 0),
    result          VARCHAR(20) NOT NULL,
    extra_time      BOOLEAN DEFAULT FALSE,
    penalties       BOOLEAN DEFAULT FALSE,
    date            DATE,  -- NULLABLE pour matchs 1930-2010
    round           VARCHAR(50) NOT NULL,
    edition         INTEGER NOT NULL,

    PRIMARY KEY (id_match, edition)
) PARTITION BY RANGE (edition);
```

**Justification du partitionnement :**
- Requêtes par édition optimisées (partition pruning)
- Maintenance simplifiée (archivage par édition)
- Scalabilité pour futures éditions

**Vues analytiques créées :**

| Vue | Description | Usage |
|-----|-------------|-------|
| `v_team_stats` | Stats globales par équipe | Classements historiques |
| `v_team_by_edition` | Performance par équipe par tournoi | Évolution temporelle |
| `v_head_to_head` | Confrontations directes | Analyse rivalités |

---

## 5. Qualité des Données et KPIs

### 5.1 Métriques de Qualité

| Critère | Attendu | Obtenu | Statut |
|---------|---------|--------|--------|
| Complétude scores | 100% | 100% | ✓ |
| Complétude dates | 100% | 13% (6 480 nulls) | ⚠ Acceptable (historique) |
| Doublons matchs | 0 | 0 | ✓ |
| Unicité équipes | Oui | 226 uniques | ✓ |
| Plage scores | 0-15 | 0-31 | ✓ (score extrême valide) |
| Couverture éditions | 22 | 22 | ✓ |

### 5.2 KPIs de Base

#### Distribution des Résultats

| Résultat | Pourcentage | Matchs |
|----------|-------------|--------|
| Victoire domicile | 52.9% | ~3 860 |
| Victoire extérieur | 26.2% | ~1 910 |
| Match nul | 20.9% | ~1 525 |

#### Palmarès des Champions

| Rang | Équipe | Titres |
|------|--------|--------|
| 1 | Brésil | 5 |
| 2 | Allemagne | 4 |
| 3 | Italie | 4 |
| 4 | Argentine | 3 |
| 5 | France | 2 |
| 6 | Uruguay | 2 |

#### Matchs Extrêmes

- **Plus large victoire** : Australie 31-0 Samoa américaines (2002, qualifications)
- **Prolongations** : 59 matchs (0.8%)
- **Tirs au but** : 37 matchs (0.5%)

### 5.3 KPIs Avancés - Analyse Prédictive

#### Corrélation Phase de Groupes → Parcours Final

**Hypothèse testée** : La performance en phase de groupes prédit le parcours final.

**Résultat** : Coefficient de Spearman **r = 0.735** (p < 0.001)

> Interprétation : Corrélation forte et statistiquement significative. Plus une équipe performe en groupes, plus elle avance dans le tournoi.

#### Probabilités Conditionnelles

| Points en groupes | % Quarts de finale | % Champion |
|-------------------|-------------------|------------|
| 0-3 pts | 2.3% | 0% |
| 4-6 pts | 35.1% | 1.9% |
| 7+ pts | 72.5% | 12.7% |

#### Profil Type du Champion

| Métrique | Champion | Moyenne globale | Écart |
|----------|----------|-----------------|-------|
| Points en groupes | 8.31 | 4.33 | +3.98 |
| Victoires | 2.56 | 1.18 | +1.38 |
| Buts marqués | 7.69 | 4.15 | +3.54 |
| Buts encaissés | 2.62 | 4.15 | -1.53 |

#### Impact du Premier Match

| Résultat 1er match | % Éliminé en groupes | % Champion |
|--------------------|---------------------|------------|
| Victoire | 20.5% | 7.5% |
| Nul | 45.5% | 1.8% |
| Défaite | 85.1% | 1.2% |

> Une victoire au premier match multiplie par **6.25x** les chances de devenir champion (7.5% vs 1.2%).

---

## 6. Difficultés Rencontrées et Solutions

### 6.1 Normalisation Germany/RFA

**Problème :**
L'Allemagne a participé sous plusieurs noms : RFA (1954-1990), Germany (1990+), avec la RDA comme entité distincte.

**Impact :**
Statistiques historiques séparées, analyses faussées.

**Solution :**
```python
# Dans teams_constants.py
"FRG (BRD / Westdeutschland)": "Germany",
"FRG": "Germany",
"West Germany": "Germany",
"GDR (DDR / Ostdeutschland)": "GDR",  # Reste distincte
```

### 6.2 Formats de Dates Hétérogènes

**Problème :**
- Données 1930-2010 : dates manquantes ou au format texte européen
- Données 2018 : format ISO 8601
- Données 2022 : format américain

**Solution :**
- Dates acceptées en `NULL` pour données historiques
- Index partiels PostgreSQL pour gérer les nulls :

```sql
CREATE UNIQUE INDEX idx_unique_match_with_date
ON matches (home_team_id, away_team_id, date, edition)
WHERE date IS NOT NULL;
```

### 6.3 Parsing JSON Imbriqué (2018)

**Problème :**
Structure FIFA API sur 4 niveaux : `teams → groups → matches → knockouts`

**Solution :**
Fonction de parsing récursive avec extraction séparée des phases de groupes et éliminatoires.

### 6.4 Doublons d'IDs Équipes

**Problème :**
Certaines équipes avaient plusieurs IDs (ex: Antigua and Barbuda ID 8 et 9).

**Solution :**
- Détection automatique dans `normalize_teams.py`
- Fusion vers l'ID le plus petit
- Mise à jour des références dans matches.csv

---

## 7. Stack Technique et Compétences

### 7.1 Technologies Utilisées

| Catégorie | Technologie | Utilisation |
|-----------|-------------|-------------|
| **Langage** | Python 3.8+ | Logique ETL, scripts |
| **Data Processing** | Pandas 2.1, NumPy | Manipulation DataFrames |
| **Base de données** | PostgreSQL 14+ | Stockage relationnel partitionné |
| **Hébergement BDD** | Render.com | Cloud PostgreSQL (Frankfurt) |
| **ORM** | SQLAlchemy 2.0 | Connexion Python-PostgreSQL |
| **Connecteur** | psycopg2-binary | Driver PostgreSQL |
| **Versioning** | Git/GitHub | Collaboration, PRs |
| **Notebooks** | Jupyter Lab 4.0 | Développement itératif |
| **Statistiques** | SciPy | Corrélation Spearman |
| **Visualisation** | Plotly, Matplotlib | Graphiques analytiques |
| **Data sources** | kagglehub | Téléchargement Kaggle |

### 7.2 Compétences Data Engineering Démontrées

| Compétence | Niveau | Justification |
|------------|--------|---------------|
| **Extraction multi-sources** | Avancé | CSV, JSON, API Kaggle |
| **Transformation données** | Avancé | Normalisation 350+ aliases, déduplication |
| **Modélisation relationnelle** | Intermédiaire | Schéma teams/matches avec FK |
| **SQL avancé** | Avancé | Partitionnement, CTE, Window Functions |
| **Qualité des données** | Avancé | Validation, KPIs, gestion nulls |
| **Collaboration Git** | Avancé | Branches, PRs, code reviews |
| **Documentation** | Avancé | README, notebooks documentés |
| **Analyse statistique** | Intermédiaire | Corrélation Spearman, probabilités |

---

## 8. Conclusion et Perspectives

### 8.1 Bilan du Projet

**Objectifs atteints :**
- ✓ Pipeline ETL complet et reproductible
- ✓ Données consolidées de haute qualité (7 299 matchs)
- ✓ Base de données PostgreSQL optimisée (partitionnement)
- ✓ Documentation professionnelle
- ✓ Analyses statistiques avancées

**Livrables produits :**
- 11 notebooks Jupyter documentés
- 2 fichiers CSV finaux (teams, matches)
- Base PostgreSQL avec 3 vues analytiques
- Module Python de normalisation (`src/`)

### 8.2 Axes d'Amélioration

| Axe | Description | Priorité |
|-----|-------------|----------|
| Tests unitaires | Couverture des fonctions de normalisation | Haute |
| CI/CD | Pipeline automatisé (GitHub Actions) | Moyenne |
| Monitoring | Alertes sur qualité des données | Moyenne |
| Logging | Traçabilité des transformations | Basse |

### 8.3 Perspectives d'Évolution

- [ ] Intégration des données de stades (capacité, coordonnées)
- [ ] API REST pour accès dynamique aux données
- [ ] Dashboard de visualisation (Metabase/Superset)
- [ ] Modèle prédictif ML pour la Coupe du Monde 2026

### 8.4 Apprentissages Clés

1. **La normalisation est critique** : Sans référentiel d'équipes unifié, aucune analyse fiable n'est possible sur 92 ans de données.

2. **Les données historiques sont chaotiques** : Accepter les contraintes (dates nulles) plutôt que d'inventer des données.

3. **Le partitionnement paie** : Sur 7 299 matchs, les requêtes par édition sont instantanées grâce au partition pruning.

4. **Git est essentiel en équipe** : 4 développeurs, 4 jours = nécessité absolue de branches et code reviews.

5. **Documenter au fil de l'eau** : Les notebooks auto-documentés facilitent la transmission de connaissances.

---

**Document généré le** : 17 Décembre 2025
**Version** : 1.0
**Équipe** : Short Kings - Simplon Data Engineering
