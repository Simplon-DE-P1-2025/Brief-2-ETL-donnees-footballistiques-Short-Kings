# Package ETL - World Cup Data

Ce package Python contient les utilitaires pour l'extraction, la transformation et le chargement (ETL) des données de la Coupe du Monde de football.

## Structure

```
src/
├── __init__.py           # Initialisation du package
├── cleaning.py           # Fonctions de nettoyage des données
├── teams_constants.py    # Données de référence des équipes
├── teams_reference.py    # Logique de normalisation
└── normalize_teams.py    # Script d'orchestration
```

## Modules

### cleaning.py

Fonctions de nettoyage des données brutes :

- `clean_percentage(x)` - Convertit une chaîne pourcentage en float (ex: "65%" → 65.0)
- `clean_round_name(r_raw)` - Normalise les noms des phases de compétition (Group Stage, Round of 16, Quarter-finals, Semi-final, Third Place, Final)

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
- `get_confederations()` - Retourne le dictionnaire complet {équipe: confédération}
- `get_aliases(team_name)` - Liste les noms alternatifs d'une équipe
- `is_historical_team(team_name)` - Vérifie si l'équipe est dissoute
- `get_successor(team_name)` - Retourne le successeur FIFA
- `get_dissolution_year(team_name)` - Retourne l'année de dissolution d'une équipe historique
- `build_alias_to_fifa_mapping()` - Construit le mapping alias → nom FIFA officiel
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
from src.cleaning import clean_percentage, clean_round_name
from src.teams_reference import normalize_team_name, get_confederation

# Nettoyer des données
pct = clean_percentage("65%")  # → 65.0
round_name = clean_round_name("QUARTER FINAL")  # → "Quarter-finals"

# Normaliser un nom d'équipe
nom_fifa = normalize_team_name("Ivory Coast")    # → "Côte d'Ivoire"
nom_fifa = normalize_team_name("South Korea")    # → "Korea Republic"

# Obtenir la confédération
conf = get_confederation("France")  # → "UEFA"
```

## Fonctionnalités principales

- Standardisation des noms d'équipes vers les normes FIFA
- Gestion des équipes historiques (URSS, Yougoslavie, etc.)
- Support de 180+ variations de noms
- Classification par confédération (UEFA, CONMEBOL, CAF, AFC, CONCACAF, OFC)
- Nettoyage des données brutes (pourcentages, noms de phases)
