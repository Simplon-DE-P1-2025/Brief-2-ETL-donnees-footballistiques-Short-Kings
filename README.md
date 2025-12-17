# ⚽ Projet ETL Données Footballistiques - Short Kings

Bienvenue sur le projet **Short Kings**, une pipeline ETL (Extract, Transform, Load) dédiée à l'analyse des données de la Coupe du Monde de la FIFA de 1930 à 2022. Ce projet a pour but de consolider, nettoyer et structurer des données historiques et récentes provenant de diverses sources (CSV, JSON, APIs) pour permettre des analyses statistiques approfondies.

## 📝 Description

Ce projet permet de traiter les données de matchs, d'équipes et de résultats de toutes les Coupes du Monde. Il est conçu de manière modulaire avec des notebooks Jupyter pour chaque étape ou édition du tournoi, et des scripts Python pour les fonctions utilitaires partagées.

**Objectifs principaux :**
*   **Extraction** : Récupération des données depuis des fichiers plats (CSV) et des APIs (JSON).
*   **Transformation** : Normalisation des noms de pays, gestion des formats de dates, nettoyage des scores et calcul de statistiques.
*   **Chargement** : Export des données propres pour analyse ou insertion en base de données.

## 📂 Architecture du Projet

La structure du projet est organisée comme suit :

```
Brief-2-ETL-donnees-footballistiques-Short-Kings/
│
├── notebooks/                       # Espace de travail Jupyter
│   ├── extract_matches19302010...   # Extraction des données historiques (1930-2010)
│   ├── nettoyage_matches19302010... # Nettoyage des données historiques
│   ├── extract-2014-romain.ipynb    # Extraction spécifique pour 2014
│   ├── 01-extract-json-2018.ipynb   # Extraction des données JSON 2018
│   ├── 02-transform-2018.ipynb      # Transformation des données 2018
│   ├── WorldCup2022.ipynb           # Pipeline complète pour 2022
│   ├── mapping-teams-romain.ipynb   # Normalisation des noms d'équipes
│   └── bdd-setup-romain.ipynb       # Configuration de la Base de Données
│
├── data/                            # Stockage des données
│   ├── matches_wc2018_en.json       # Source JSON brute (2018)
│   ├── matches_wc2022_en.json       # Source JSON brute (2022)
│   ├── raw/                         # Données brutes historiques (CSV)
│   │   ├── matches_19302010.csv
│   │   ├── WorldCupMatches2014.csv
│   │   └── ...
│   └── processed/                   # Données nettoyées et finales
│       ├── matches_2018_clean.csv
│       ├── df_matches_final.csv     # Dataset consolidé final
│       └── teams_ref_2018.csv
│
├── src/                             # Code source et utilitaires
│   ├── etl_utils.py                 # Fonctions partagées (chargement, sauvegarde)
│   └── normalize_teams.py           # Logique de standardisation des équipes
│
├── environment.yml                  # Environnement Conda
├── requirements.txt                 # Dépendances pip
└── README.md                        # Documentation du projet
```

## 🛠 Prérequis

*   **Python 3.8+**
*   **Jupyter Lab** ou **Notebook**
*   **Git**

## 🚀 Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/Simplon-DE-P1-2025/Brief-2-ETL-donnees-footballistiques-Short-Kings.git
cd Brief-2-ETL-donnees-footballistiques-Short-Kings
```

### 2. Configurer l'environnement

Il est fortement recommandé d'utiliser un environnement virtuel.

**Option A : Via Conda (Recommandé)**
```bash
conda env create -f environment.yml
conda activate football-etl
```

**Option B : Via venv**
```bash
# Création
python -m venv venv

# Activation (Windows)
venv\Scripts\activate

# Activation (Mac/Linux)
source venv/bin/activate

# Installation des dépendances
pip install -r requirements.txt
```

## ⚙️ Utilisation (Workflow ETL)

Lancez Jupyter Lab pour accéder aux notebooks :
```bash
jupyter lab
```

Suivez l'ordre logique de traitement des données :

1.  **Données Historiques (1930-2010)** :
    *   Exécutez `extract_matches19302010...` pour l'extraction brute.
    *   Puis `nettoyage_matches19302010...` pour le nettoyage.

2.  **Données 2014** :
    *   Utilisez le notebook `extract-2014-romain.ipynb`.

3.  **Données 2018** :
    *   Extraction : `01-extract-json-2018.ipynb`
    *   Transformation : `02-transform-2018.ipynb`

4.  **Données 2022 & Consolidation** :
    *   Le notebook `WorldCup2022.ipynb` traite les données les plus récentes et peut servir à l'analyse globale.

5.  **Utilitaires** :
    *   Le fichier `src/normalize_teams.py` est crucial pour assurer que "France" s'écrit de la même façon dans les fichiers de 1998 et de 2018.

## 📊 Technologies Utilisées

*   **Langage** : Python
*   **Analyse de Données** : Pandas, NumPy
*   **Interface** : Jupyter Lab
*   **Formats de Données** : CSV, JSON

## 👥 Auteurs

*   Équipe **Short Kings** (Simplon DE P1 2025)

## 📄 Licence

Ce projet est sous licence. Voir le fichier `LICENSE` pour plus de détails.

