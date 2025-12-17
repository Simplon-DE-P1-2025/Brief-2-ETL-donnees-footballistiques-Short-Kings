import json
import pandas as pd
from pathlib import Path

# Chemins des fichiers
BASE_DIR = Path(__file__).parent.parent
TEAMS_CSV = BASE_DIR / "data/processed/teams.csv"
TEAMS_MAPPING_JSON = BASE_DIR / "data/reference/teams_mapping.json"
OUTPUT_CSV = BASE_DIR / "data/processed/teams_traitees.csv"


def load_teams_mapping():
    """Charge le fichier teams_mapping.json."""
    with open(TEAMS_MAPPING_JSON, 'r', encoding='utf-8') as f:
        return json.load(f)


def build_mapping(teams_ref):
    """
    Construit un dictionnaire de mapping : alias -> nom FIFA officiel.
    Simple lookup car les variantes sont déjà dans le JSON.
    """
    alias_to_fifa = {}
    for fifa_name, data in teams_ref.items():
        alias_to_fifa[fifa_name] = fifa_name
        for alias in data.get('aliases', []):
            alias_to_fifa[alias] = fifa_name
    return alias_to_fifa


def normalize_teams():
    """
    Normalise les noms des équipes et enrichit avec confederation et aliases.
    """
    # Charger les données
    teams_ref = load_teams_mapping()
    alias_to_fifa = build_mapping(teams_ref)
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
            # Pas de correspondance trouvée
            fifa_name = original_name
            unmatched.append(original_name)

        # Récupérer les données du JSON
        if fifa_name in teams_ref:
            confederation = teams_ref[fifa_name].get('confederation', '')
            aliases = teams_ref[fifa_name].get('aliases', [])
        else:
            confederation = ''
            aliases = []

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

    # Sauvegarder
    df_result.to_csv(OUTPUT_CSV, index=False, encoding='utf-8')

    # Rapport
    print(f"Fichier créé : {OUTPUT_CSV}")
    print(f"Nombre d'équipes : {len(df_result)}")
    print(f"Équipes normalisées : {len(df_result) - len(unmatched)}")

    if unmatched:
        print(f"\nÉquipes non matchées ({len(unmatched)}) :")
        for name in sorted(unmatched):
            print(f"  - {name}")
    else:
        print("\nToutes les équipes ont été matchées !")

    # Afficher quelques exemples de normalisation
    print("\nExemples de normalisation :")
    examples = df[df['nom_standard'] != df_result['nom_standard']].head(10)
    for i, (_, orig_row) in enumerate(examples.iterrows()):
        if i < 10:
            orig = orig_row['nom_standard']
            norm = df_result.loc[orig_row.name, 'nom_standard']
            print(f"  {orig} → {norm}")

    return df_result, unmatched


if __name__ == "__main__":
    normalize_teams()
