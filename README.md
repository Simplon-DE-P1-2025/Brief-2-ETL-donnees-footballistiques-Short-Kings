# Projet ETL Donnees Footballistiques - Short Kings

Pipeline ETL (Extract, Transform, Load) pour l'analyse des donnees de la Coupe du Monde FIFA de 1930 a 2022.

## Description

Ce projet consolide, nettoie et structure les donnees historiques de toutes les Coupes du Monde. Il est concu de maniere modulaire avec des notebooks Jupyter numerotes pour chaque etape du pipeline, et des modules Python pour les fonctions utilitaires partagees.

**Objectifs principaux :**
- **Extraction** : Recuperation des donnees depuis CSV, JSON et APIs (FIFA, Kaggle)
- **Transformation** : Normalisation des noms d'equipes, gestion des formats de dates, nettoyage des scores
- **Chargement** : Insertion dans une base PostgreSQL avec partitionnement par edition
- **Analyse** : KPIs, requetes SQL avancees, correlations statistiques

## Architecture du Projet

```
Brief-2-ETL-donnees-footballistiques-Short-Kings/
│
├── notebooks/                          # Pipeline ETL (executer dans l'ordre)
│   ├── 00-database-setup.ipynb         # Infrastructure PostgreSQL
│   ├── 01a-validate-2014.ipynb         # Validation qualite 2014
│   ├── 01b-clean-1930-2014.ipynb       # Nettoyage donnees historiques
│   ├── 02a-extract-json-2018.ipynb     # Extraction JSON 2018
│   ├── 02b-transform-2018.ipynb        # Transformation 2018
│   ├── 03-extract-2022.ipynb           # Extraction Kaggle 2022
│   ├── 04-concat-and-index.ipynb       # Concatenation et indexation
│   ├── 05-create-json-mapping.ipynb    # Referentiel equipes
│   ├── 05b-map-team-ids.ipynb          # Attribution IDs numeriques
│   ├── 06-normalize-teams.ipynb        # Normalisation noms equipes
│   ├── 07-load-database.ipynb          # Chargement PostgreSQL
│   ├── 08-data-quality-kpi.ipynb       # Qualite donnees et KPIs
│   ├── 09-sql-analytics.ipynb          # Requetes SQL avancees
│   └── 10-group-knockout-correlation.ipynb  # Analyse predictive
│
├── data/
│   ├── raw/                            # Donnees sources brutes
│   │   ├── matches_19302010 (1).csv    # Historique 1930-2010
│   │   ├── WorldCupMatches2014 (1).csv # WC 2014
│   │   ├── data_2018.json              # WC 2018 (FIFA API)
│   │   └── matches_wc2022_en.json      # WC 2022 (Kaggle)
│   ├── staging/                        # Donnees intermediaires
│   │   └── matches_2018_raw.csv
│   ├── processed/                      # Donnees finales
│   │   ├── matches.csv                 # 7427 matchs consolides
│   │   ├── teams.csv                   # 226 equipes
│   │   └── teams_traitees.csv          # Equipes normalisees
│   └── reference/                      # Donnees de reference
│       ├── teams_mapping.json          # Mapping equipes (231 entrees)
│       └── fifa_ranking_source.csv     # Classement FIFA
│
├── src/                                # Modules Python
│   ├── __init__.py
│   ├── cleaning.py                     # Fonctions de nettoyage
│   ├── teams_constants.py              # Constantes equipes/aliases
│   ├── teams_reference.py              # Logique de normalisation
│   └── normalize_teams.py              # Script d'orchestration
│
├── tests/                              # Tests unitaires
│
├── environment.yml                     # Environnement Conda
├── requirements.txt                    # Dependances pip
└── README.md
```

## Prerequis

- **Python 3.8+**
- **PostgreSQL** (ou acces a une instance distante)
- **Jupyter Lab**
- **Git**

## Installation

### 1. Cloner le depot

```bash
git clone https://github.com/Simplon-DE-P1-2025/Brief-2-ETL-donnees-footballistiques-Short-Kings.git
cd Brief-2-ETL-donnees-footballistiques-Short-Kings
```

### 2. Configurer l'environnement

**Option A : Via Conda (Recommande)**
```bash
conda env create -f environment.yml
conda activate football-etl
```

**Option B : Via venv**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

### 3. Configurer la base de donnees

Creer un fichier `.env` a la racine :
```
utilisation de Render, voir avec l'équipe
```

## Workflow ETL

Executer les notebooks dans l'ordre numerique :

```
INFRASTRUCTURE
└── 00-database-setup.ipynb → Schema PostgreSQL

EXTRACT
├── 01a-validate-2014.ipynb → Validation qualite
├── 01b-clean-1930-2014.ipynb → 7299 matchs historiques
├── 02a-extract-json-2018.ipynb → 64 matchs 2018
└── 03-extract-2022.ipynb → 64 matchs 2022

TRANSFORM
├── 02b-transform-2018.ipynb → Normalisation 2018
├── 04-concat-and-index.ipynb → 7427 matchs consolides
├── 05-create-json-mapping.ipynb → Referentiel 231 equipes
├── 05b-map-team-ids.ipynb → Attribution IDs
└── 06-normalize-teams.ipynb → 226 equipes finales

LOAD
└── 07-load-database.ipynb → PostgreSQL (226 equipes, 7427 matchs)

ANALYSE
├── 08-data-quality-kpi.ipynb → Qualite et KPIs de base
├── 09-sql-analytics.ipynb → SQL avance (partitions, vues, CTE)
└── 10-group-knockout-correlation.ipynb → Correlation groupes/eliminatoires
```

## Technologies

| Categorie | Technologies |
|-----------|--------------|
| Langage | Python 3.8+ |
| Donnees | Pandas, NumPy |
| Base de donnees | PostgreSQL, SQLAlchemy |
| Visualisation | Plotly, Matplotlib |
| Statistiques | SciPy |
| Sources | FIFA API, Kaggle |
| Interface | Jupyter Lab |

## Donnees

- **Couverture** : 22 editions (1930-2022)
- **Volume** : 7427 matchs, 226 equipes
- **Sources** : FIFA, Kaggle, archives historiques

## Auteurs

Equipe **Short Kings** (Simplon DE P1 2025)

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de details.

