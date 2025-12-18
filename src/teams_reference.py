"""
Fonctions de référentiel pour la normalisation des équipes.

Ce module fournit les fonctions pour normaliser les noms d'équipes,
récupérer les confédérations, et gérer les équipes historiques.
"""

import json
import pandas as pd
from pathlib import Path

try:
    from .teams_constants import (
        ALIASES_MAPPING,
        ALIASES_MAPPING_LOWER,
        HISTORICAL_TEAMS,
        ADDITIONAL_TEAMS,
        PLACEHOLDERS,
    )
except ImportError:
    from teams_constants import (
        ALIASES_MAPPING,
        ALIASES_MAPPING_LOWER,
        HISTORICAL_TEAMS,
        ADDITIONAL_TEAMS,
        PLACEHOLDERS,
    )

# Chemin vers le fichier de confédérations FIFA (cache)
BASE_DIR = Path(__file__).parent.parent
CONFEDERATIONS_CACHE = BASE_DIR / "data/reference/teams_mapping.json"
FIFA_RANKING_CSV = BASE_DIR / "data/reference/fifa_ranking_source.csv"


def _load_confederations_from_cache() -> dict:
    """
    Charge les confédérations depuis le fichier JSON cache.

    Returns:
        Dictionnaire {nom_équipe: confédération}
    """
    if CONFEDERATIONS_CACHE.exists():
        with open(CONFEDERATIONS_CACHE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return {team: info.get('confederation') for team, info in data.items()}
    return {}


def _load_confederations_from_fifa_csv() -> dict:
    """
    Charge les confédérations depuis le fichier CSV FIFA.

    Returns:
        Dictionnaire {nom_équipe: confédération}
    """
    if FIFA_RANKING_CSV.exists():
        df = pd.read_csv(FIFA_RANKING_CSV)
        if 'confederation' in df.columns:
            latest_date = df['rank_date'].max()
            df_latest = df[df['rank_date'] == latest_date]
            return df_latest.set_index('country_full')['confederation'].to_dict()
    return {}


def get_confederations() -> dict:
    """
    Retourne le dictionnaire complet des confédérations.
    Combine: FIFA actuel + équipes historiques + équipes additionnelles.

    Returns:
        Dictionnaire {nom_équipe: confédération}
    """
    # Charger depuis le cache JSON ou le CSV FIFA
    confederations = _load_confederations_from_cache()

    if not confederations:
        confederations = _load_confederations_from_fifa_csv()

    # Ajouter les équipes historiques
    for team, (_, _, conf) in HISTORICAL_TEAMS.items():
        confederations[team] = conf

    # Ajouter les équipes additionnelles
    confederations.update(ADDITIONAL_TEAMS)

    return confederations


# Charger les confédérations une seule fois au démarrage
CONFEDERATIONS = get_confederations()

# Mapping insensible à la casse pour les noms standards
CONFEDERATIONS_LOWER = {k.lower(): k for k in CONFEDERATIONS.keys()}


def normalize_team_name(raw_name: str) -> str | None:
    """
    Convertit un nom brut en nom standard FIFA.
    Retourne None si c'est un placeholder.

    Args:
        raw_name: Nom brut de l'équipe (peut contenir des caractères spéciaux)

    Returns:
        Nom standard ou None si placeholder
    """
    if pd.isna(raw_name):
        return None

    name = str(raw_name).strip()

    # Exclure les placeholders
    if name in PLACEHOLDERS:
        return None

    # Recherche insensible à la casse dans les aliases
    if name.lower() in ALIASES_MAPPING_LOWER:
        return ALIASES_MAPPING_LOWER[name.lower()]

    # Appliquer le mapping des aliases (correspondance exacte)
    if name in ALIASES_MAPPING:
        return ALIASES_MAPPING[name]

    # -------------------------------------------------------------------------
    # RECHERCHE INSENSIBLE À LA CASSE DANS LES NOMS STANDARDS
    # Ex: "ARGENTINA" -> "Argentina", "france" -> "France"
    # -------------------------------------------------------------------------
    if name.lower() in CONFEDERATIONS_LOWER:
        return CONFEDERATIONS_LOWER[name.lower()]

    # -------------------------------------------------------------------------
    # GESTION DYNAMIQUE DES CAS PROBLÉMATIQUES
    # Pour les équipes avec caractères spéciaux difficiles à mapper exactement
    # -------------------------------------------------------------------------

    # Cas 1: Ethiopia avec différentes formes de l'écriture Ge'ez
    if name.startswith("Ethiopia ("):
        return "Ethiopia"

    # Cas 2: Ivory Coast avec différentes apostrophes (droite ' ou courbe ')
    if name.startswith("Ivory Coast (Côte d"):
        return "Côte d'Ivoire"

    # Cas 3: Armenia avec différentes formes arméniennes
    if name.startswith("Armenia ("):
        return "Armenia"

    return name


def get_confederation(team_name: str) -> str | None:
    """
    Retourne la confédération d'une équipe.

    Args:
        team_name: Nom de l'équipe (brut ou normalisé)

    Returns:
        Code de confédération (UEFA, CONMEBOL, CAF, AFC, CONCACAF, OFC) ou None
    """
    normalized = normalize_team_name(team_name)
    if normalized is None:
        return None

    return CONFEDERATIONS.get(normalized, None)


def get_aliases(team_name: str) -> list[str]:
    """
    Retourne tous les aliases connus pour une équipe.

    Args:
        team_name: Nom standard de l'équipe

    Returns:
        Liste des aliases (noms alternatifs)
    """
    aliases = []
    for alias, standard in ALIASES_MAPPING.items():
        if standard == team_name:
            aliases.append(alias)
    return aliases


def is_historical_team(team_name: str) -> bool:
    """
    Vérifie si l'équipe est une équipe historique dissoute.

    Args:
        team_name: Nom de l'équipe

    Returns:
        True si l'équipe est historique (dissoute)
    """
    return team_name in HISTORICAL_TEAMS


def get_successor(team_name: str) -> str | None:
    """
    Retourne le successeur FIFA d'une équipe dissoute.

    Args:
        team_name: Nom de l'équipe historique

    Returns:
        Nom du successeur FIFA ou None
    """
    if team_name in HISTORICAL_TEAMS:
        return HISTORICAL_TEAMS[team_name][1]
    return None


def get_dissolution_year(team_name: str) -> int | None:
    """
    Retourne l'année de dissolution d'une équipe historique.

    Args:
        team_name: Nom de l'équipe historique

    Returns:
        Année de dissolution ou None
    """
    if team_name in HISTORICAL_TEAMS:
        return HISTORICAL_TEAMS[team_name][0]
    return None


def build_alias_to_fifa_mapping() -> dict:
    """
    Construit un dictionnaire de mapping : alias -> nom FIFA officiel.
    Inclut les noms standards eux-mêmes comme clés.

    Returns:
        Dictionnaire {alias: nom_fifa}
    """
    alias_to_fifa = {}

    # Ajouter les noms standards
    for team_name in CONFEDERATIONS.keys():
        alias_to_fifa[team_name] = team_name

    # Ajouter les aliases
    for alias, fifa_name in ALIASES_MAPPING.items():
        alias_to_fifa[alias] = fifa_name

    return alias_to_fifa


def build_teams_reference() -> dict:
    """
    Construit le référentiel complet des équipes.

    Returns:
        Dictionnaire {nom_équipe: {confederation, aliases, is_historical, ...}}
    """
    teams_ref = {}

    # Ajouter toutes les équipes avec confédération
    for team_name, confederation in CONFEDERATIONS.items():
        teams_ref[team_name] = {
            "confederation": confederation,
            "aliases": get_aliases(team_name),
            "is_historical": is_historical_team(team_name),
            "fifa_successor": get_successor(team_name),
            "dissolved_year": get_dissolution_year(team_name),
        }

    return teams_ref
