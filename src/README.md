# Package ETL - World Cup Data

Ce package Python contient les utilitaires pour l'extraction, la transformation et le chargement (ETL) des données de la Coupe du Monde de football.

## Structure

```
src/
├── __init__.py           # Initialisation du package
├── etl_utils.py          # Fonctions utilitaires génériques
├── teams_constants.py    # Données de référence des équipes
├── teams_reference.py    # Logique de normalisation
└── normalize_teams.py    # Script d'orchestration
```

## Modules

### etl_utils.py

Fonctions utilitaires génériques pour le traitement des données :

- `load_csv_data(filepath)` - Charge un fichier CSV avec gestion d'erreurs
- `clean_dataframe(df)` - Nettoie un DataFrame (doublons, valeurs nulles)
- `save_data(df, filepath, format)` - Exporte en CSV, JSON ou Parquet
- `get_data_summary(df)` - Génère des statistiques descriptives

### teams_constants.py

Données de référence centralisées :

- **HISTORICAL_TEAMS** - Équipes dissoutes et leurs successeurs FIFA
- **ADDITIONAL_TEAMS** - Équipes membres FIFA non présentes dans le classement 2020
- **PLACEHOLDERS** - Entrées invalides à exclure
- **ALIASES_MAPPING** - Correspondances des variations de noms vers les noms FIFA standards

### teams_reference.py

Fonctions de normalisation des noms d'équipes :

- `normalize_team_name(raw_name)` - Convertit un nom brut vers le standard FIFA
- `get_confederation(team_name)` - Retourne la confédération (UEFA, CONMEBOL, etc.)
- `get_aliases(team_name)` - Liste les noms alternatifs d'une équipe
- `is_historical_team(team_name)` - Vérifie si l'équipe est dissoute
- `get_successor(team_name)` - Retourne le successeur FIFA
- `build_teams_reference()` - Construit le dictionnaire de référence complet

### normalize_teams.py

Script d'orchestration du workflow de normalisation :

- Lecture de `teams.csv` depuis `/data/processed/`
- Normalisation des noms d'équipes
- Enrichissement avec confédérations et alias
- Gestion de la déduplication et mise à jour des références dans `matches.csv`
- Export de `teams_traitees.csv`

## Utilisation

```python
from src.etl_utils import load_csv_data, clean_dataframe, save_data
from src.teams_reference import normalize_team_name, get_confederation

# Charger et nettoyer des données
df = load_csv_data("data/raw/matches.csv")
df = clean_dataframe(df)

# Normaliser un nom d'équipe
nom_fifa = normalize_team_name("Côte d'Ivoire")  # → "Côte d'Ivoire"
nom_fifa = normalize_team_name("Soviet Union")   # → "Russia"

# Obtenir la confédération
conf = get_confederation("France")  # → "UEFA"

# Exporter les données
save_data(df, "data/processed/matches.csv", format="csv")
```

## Fonctionnalités principales

- Standardisation des noms d'équipes vers les normes FIFA
- Gestion des équipes historiques (URSS, Yougoslavie, etc.)
- Support de 180+ variations de noms
- Classification par confédération (UEFA, CONMEBOL, CAF, AFC, CONCACAF, OFC)
- Export multi-format (CSV, JSON, Parquet)
