"""
Fixtures pytest partagées poru les tests de normalize_teams.
"""

import pytest
import pandas as pd
from pathlib import Path
import tempfile
import shutil

@pytest.fixture
def sample_teams_df():
    """Dataframe minimale avec différents cas de tests"""
    return pd.DataFrame({
        'id_team': [1, 2, 3, 4, 5, 6, 7],
        'nom_standard': [
            'France',           # Nom standard direct
            'West Germany',     # Alias -> Germany
            'Brazil',           # Nom standard direct
            'Germany',          # Doublon avec West Germany après normalisation
            "Côte d'Ivoire",    # Caractères spéciaux
            'ARGENTINA',        # Casse différente -> Argentina
            'Unknown Team',     # Équipe non reconnue
        ]
    })
    
@pytest.fixture
def sample_teams_with_duplicates_df():
    """Datframe avec doublons après normailsation"""
    return pd.DataFrame({
        'id_team': [1, 2, 3, 4, 5],
        'nom_standard': [
            'France',
            'Germany',           
            'West Germany',     
            'FRG',    
            'Brazil',     
        ]
    })

@pytest.fixture
def sample_matches_df():
    """DataFrame matches pour tester les mises à jour d'IDs."""
    return pd.DataFrame({
        'id_match': [1, 2, 3, 4],
        'home_team_id': [1, 3, 2, 5],  # IDs 3 et 4 devront être remappés
        'away_team_id': [2, 5, 1, 4],
        'home_score': [2, 1, 0, 3],
        'away_score': [1, 1, 0, 2],
    })
    
@pytest.fixture
def temp_data_dir(sample_teams_df, sample_matches_df):
    """
    Crée un répertoire temporaire avec les fichiers CSV de test.
    Retourne le chemin du répertoire.
    """
    temp_dir = tempfile.mkdtemp()
    processed_dir = Path(temp_dir) / "data" / "processed"
    processed_dir.mkdir(parents=True)

    # Créer teams.csv
    teams_path = processed_dir / "teams.csv"
    sample_teams_df.to_csv(teams_path, index=False)

    # Créer matches.csv
    matches_path = processed_dir / "matches.csv"
    sample_matches_df.to_csv(matches_path, index=False)

    yield temp_dir

    # Cleanup
    shutil.rmtree(temp_dir)
    
@pytest.fixture
def temp_data_dir_with_duplicates(sample_teams_with_duplicates_df, sample_matches_df):
    """
    Crée un répertoire temporaire avec des équipes en doublon.
    """
    temp_dir = tempfile.mkdtemp()
    processed_dir = Path(temp_dir) / "data" / "processed"
    processed_dir.mkdir(parents=True)

    # Créer teams.csv avec doublons
    teams_path = processed_dir / "teams.csv"
    sample_teams_with_duplicates_df.to_csv(teams_path, index=False)

    # Créer matches.csv
    matches_path = processed_dir / "matches.csv"
    sample_matches_df.to_csv(matches_path, index=False)

    yield temp_dir

    # Cleanup
    shutil.rmtree(temp_dir)
    
@pytest.fixture
def mock_confederations():
    """Dictionnaire de confédérations pour le mocking."""
    return {
        'France': 'UEFA',
        'Germany': 'UEFA',
        'Brazil': 'CONMEBOL',
        'Argentina': 'CONMEBOL',
        "Côte d'Ivoire": 'CAF',
        'Soviet Union': 'UEFA',
        'GDR': 'UEFA',
    }

@pytest.fixture
def mock_aliases_mapping():
    """Mapping d'aliases pour le mocking."""
    return {
        'West Germany': 'Germany',
        'FRG': 'Germany',
        'Allemagne de l\'Ouest': 'Germany',
        'East Germany': 'GDR',
        "Ivory Coast (Côte d'Ivoire)": "Côte d'Ivoire",
        "C�te d'Ivoire": "Côte d'Ivoire",
    }

@pytest.fixture
def project_root():
    """Retourne le chemin racine du projet."""
    return Path(__file__).parent.parent


@pytest.fixture
def real_teams_csv(project_root):
    """Chemin vers le vrai fichier teams.csv."""
    return project_root / "data" / "processed" / "teams.csv"


@pytest.fixture
def real_matches_csv(project_root):
    """Chemin vers le vrai fichier matches.csv."""
    return project_root / "data" / "processed" / "matches.csv"