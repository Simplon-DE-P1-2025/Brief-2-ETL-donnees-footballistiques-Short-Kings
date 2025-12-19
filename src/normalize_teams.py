"""
Normalisation des équipes pour le projet World Cup ETL.

Ce module lit teams.csv, normalise les noms des équipes selon le référentiel FIFA,
et enrichit avec les confédérations et aliases.
"""

import json
import pandas as pd
from pathlib import Path

try:
    from .teams_reference import (
        normalize_team_name,
        get_confederation,
        get_aliases,
        build_alias_to_fifa_mapping,
        CONFEDERATIONS,
    )
except ImportError:
    from teams_reference import (
        normalize_team_name,
        get_confederation,
        get_aliases,
        build_alias_to_fifa_mapping,
        CONFEDERATIONS,
    )

# Chemins des fichiers
BASE_DIR = Path(__file__).parent.parent
TEAMS_CSV = BASE_DIR / "data/processed/teams.csv"
OUTPUT_CSV = BASE_DIR / "data/processed/teams_traitees.csv"
MATCHES_CSV = BASE_DIR / "data/processed/matches.csv"


def normalize_teams(update_matches: bool = True):
    """
    Normalise les noms des équipes et enrichit avec confederation et aliases.

    Args:
        update_matches: Si True, met à jour matches.csv avec les IDs fusionnés

    Returns:
        Tuple (DataFrame résultat, liste des équipes non matchées)
    """
    # Construire le mapping alias -> nom FIFA
    alias_to_fifa = build_alias_to_fifa_mapping()

    # Charger les données
    df = pd.read_csv(TEAMS_CSV)

    # Listes pour stocker les résultats
    normalized_names = []
    confederations = []
    aliases_list = []
    unmatched = []

    for _, row in df.iterrows():
        original_name = row['nom_standard']

        # Chercher le nom FIFA officiel
        if original_name in alias_to_fifa:
            fifa_name = alias_to_fifa[original_name]
        else:
            # Essayer la normalisation avec gestion des cas spéciaux
            fifa_name = normalize_team_name(original_name)
            if fifa_name is None or fifa_name not in CONFEDERATIONS:
                fifa_name = original_name
                unmatched.append(original_name)

        # Récupérer les données
        confederation = get_confederation(fifa_name) or ''
        aliases = get_aliases(fifa_name)

        normalized_names.append(fifa_name)
        confederations.append(confederation)
        aliases_list.append(json.dumps(aliases, ensure_ascii=False))

    # Créer le DataFrame résultat
    df_result = pd.DataFrame({
        'id_team': df['id_team'],
        'nom_standard': normalized_names,
        'confederation': confederations,
        'aliases': aliases_list
    })

    # =========================================================================
    # DÉDUPLICATION : Si plusieurs entrées ont le même nom_standard,
    # garder une seule et fusionner les IDs dans matches.csv
    # =========================================================================

    # Identifier les doublons
    duplicates = df_result[df_result.duplicated(subset=['nom_standard'], keep=False)]
    id_mapping = {}  # old_id → new_id

    if len(duplicates) > 0:
        print("\n" + "=" * 60)
        print("FUSION DES ÉQUIPES EN DOUBLON")
        print("=" * 60)

        for name in duplicates['nom_standard'].unique():
            dup_rows = df_result[df_result['nom_standard'] == name]
            ids = dup_rows['id_team'].tolist()

            # Garder le plus petit ID comme ID principal
            main_id = min(ids)
            other_ids = [i for i in ids if i != main_id]

            print(f"\n{name}:")
            print(f"  IDs trouvés: {ids}")
            print(f"  ID conservé: {main_id}")
            print(f"  IDs à remapper: {other_ids} → {main_id}")

            # Enregistrer le mapping
            for old_id in other_ids:
                id_mapping[old_id] = main_id

        # Supprimer les doublons (garder le premier = plus petit ID après tri)
        df_result = df_result.sort_values('id_team').drop_duplicates(
            subset=['nom_standard'],
            keep='first'
        ).reset_index(drop=True)

        print(f"\nÉquipes après déduplication: {len(df_result)}")

    # Sauvegarder teams_traitees.csv
    df_result.to_csv(OUTPUT_CSV, index=False, encoding='utf-8')

    # =========================================================================
    # MISE À JOUR DES IDs DANS MATCHES.CSV
    # =========================================================================

    if update_matches and id_mapping and MATCHES_CSV.exists():
        print("\n" + "=" * 60)
        print("MISE À JOUR DES IDs DANS MATCHES.CSV")
        print("=" * 60)

        matches_df = pd.read_csv(MATCHES_CSV)
        total_updates = 0

        for old_id, new_id in id_mapping.items():
            count_home = (matches_df['home_team_id'] == old_id).sum()
            count_away = (matches_df['away_team_id'] == old_id).sum()

            matches_df['home_team_id'] = matches_df['home_team_id'].replace(old_id, new_id)
            matches_df['away_team_id'] = matches_df['away_team_id'].replace(old_id, new_id)

            total = count_home + count_away
            if total > 0:
                print(f"  ID {old_id} → {new_id}: {count_home} (home) + {count_away} (away) = {total} matchs")
                total_updates += total

        matches_df.to_csv(MATCHES_CSV, index=False)
        print(f"\nTotal: {total_updates} références mises à jour dans matches.csv")

    # Rapport
    print("\n" + "=" * 60)
    print("RÉSUMÉ")
    print("=" * 60)
    print(f"Fichier créé : {OUTPUT_CSV}")
    print(f"Nombre d'équipes : {len(df_result)}")
    print(f"Équipes normalisées : {len(df_result)}")

    if unmatched:
        print(f"\nÉquipes non matchées ({len(unmatched)}) :")
        for name in sorted(set(unmatched)):
            print(f"  - {name}")
    else:
        print("\nToutes les équipes ont été matchées !")

    # Afficher quelques exemples de normalisation
    original_names = df['nom_standard'].tolist()
    print("\nExemples de normalisation :")
    count = 0
    for orig in original_names:
        norm = alias_to_fifa.get(orig, orig)
        if orig != norm and count < 10:
            print(f"  {orig} → {norm}")
            count += 1

    return df_result, unmatched


if __name__ == "__main__":
    normalize_teams()
