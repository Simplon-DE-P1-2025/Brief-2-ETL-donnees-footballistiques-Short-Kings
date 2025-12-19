"""
Tests unitaires pour normalize_teams.py

Ces tests utilisent des données mockées pour valider la logique
de normalisation, déduplication et mise à jour des matches.
"""

import json
import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import patch
import tempfile
import shutil

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from teams_reference import (
    normalize_team_name,
    get_confederation,
    get_aliases,
    build_alias_to_fifa_mapping,
    CONFEDERATIONS,
)

class TestNormalizeTeamName:
    """Tests pour la fonction normalize_team_name."""

    def test_normalize_basic_team_name(self):
        """Une équipe standard reste inchangée."""
        assert normalize_team_name("France") == "France"
        assert normalize_team_name("Brazil") == "Brazil"
        assert normalize_team_name("Germany") == "Germany"

    def test_normalize_alias_team_name(self):
        """Les aliases sont convertis vers le nom FIFA."""
        assert normalize_team_name("West Germany") == "Germany"
        assert normalize_team_name("FRG") == "Germany"
        assert normalize_team_name("East Germany") == "GDR"

    def test_normalize_case_sensitivity(self):
        """La normalisation est insensible à la casse."""
        # Ces tests dépendent de CONFEDERATIONS_LOWER
        result = normalize_team_name("ARGENTINA")
        assert result == "Argentina"

        result = normalize_team_name("france")
        assert result == "France"

    def test_normalize_encoding_issues(self):
        """Les problèmes d'encodage sont gérés."""
        result = normalize_team_name("C�te d'Ivoire")
        assert result == "Côte d'Ivoire"

    def test_normalize_historical_team(self):
        """Les équipes historiques sont reconnues."""
        # Soviet Union est une équipe historique valide
        result = normalize_team_name("Soviet Union")
        assert result == "Soviet Union"

    def test_normalize_placeholder_returns_none(self):
        """Les placeholders retournent None."""
        assert normalize_team_name("A1") is None
        assert normalize_team_name("B2") is None
        assert normalize_team_name("1") is None

    def test_normalize_nan_returns_none(self):
        """NaN retourne None."""
        assert normalize_team_name(pd.NA) is None
        assert normalize_team_name(float('nan')) is None

    def test_normalize_special_cases_ethiopia(self):
        """Cas spécial Ethiopia avec script Ge'ez."""
        result = normalize_team_name("Ethiopia (ኢትዮጵያ)")
        assert result == "Ethiopia"

    def test_normalize_ivory_coast_variants(self):
        """Variantes de Côte d'Ivoire."""
        result = normalize_team_name("Ivory Coast (Côte d'Ivoire)")
        assert result == "Côte d'Ivoire"
    
class TestGetConfederation:
    """Tests pour la fonction get_confederation."""

    def test_get_confederation_uefa(self):
        """Récupère les confédérations UEFA."""
        assert get_confederation("France") == "UEFA"
        assert get_confederation("Germany") == "UEFA"

    def test_get_confederation_conmebol(self):
        """Récupère les confédérations CONMEBOL."""
        assert get_confederation("Brazil") == "CONMEBOL"
        assert get_confederation("Argentina") == "CONMEBOL"

    def test_get_confederation_from_alias(self):
        """Récupère la confédération via un alias."""
        result = get_confederation("West Germany")
        assert result == "UEFA"

    def test_get_confederation_unknown_team(self):
        """Équipe inconnue retourne None."""
        result = get_confederation("Unknown Team XYZ")
        assert result is None

    def test_get_confederation_placeholder(self):
        """Placeholder retourne None."""
        assert get_confederation("A1") is None


class TestGetAliases:
    """Tests pour la fonction get_aliases."""

    def test_get_aliases_germany(self):
        """Germany a plusieurs aliases."""
        aliases = get_aliases("Germany")
        assert "West Germany" in aliases
        assert "FRG" in aliases

    def test_get_aliases_empty(self):
        """Équipe sans alias retourne liste vide."""
        aliases = get_aliases("France")
        # France n'a pas d'alias dans notre dictionnaire
        assert isinstance(aliases, list)
        assert aliases == []

    def test_get_aliases_unknown_team(self):
        """Équipe inconnue retourne liste vide."""
        aliases = get_aliases("Unknown Team XYZ")
        assert aliases == []
        
class TestBuildAliasToFifaMapping:
    """Tests pour la fonction build_alias_to_fifa_mapping."""

    def test_mapping_contains_standard_names(self):
        """Le mapping contient les noms standards comme clés."""
        mapping = build_alias_to_fifa_mapping()
        assert "France" in mapping
        assert mapping["France"] == "France"

    def test_mapping_contains_aliases(self):
        """Le mapping contient les aliases."""
        mapping = build_alias_to_fifa_mapping()
        assert "West Germany" in mapping
        assert mapping["West Germany"] == "Germany"

    def test_mapping_is_complete(self):
        """Le mapping contient toutes les confédérations."""
        mapping = build_alias_to_fifa_mapping()
        for team in CONFEDERATIONS.keys():
            assert team in mapping
            
class TestNormalizeTeamsFunction:
    """Tests pour la fonction principale normalize_teams."""
    
    def test_normalize_teams_output_schema(self, temp_data_dir):
        """Vezrifie le chéma de sortie du Dataframe."""
        from normalize_teams import normalize_teams, BASE_DIR, TEAMS_CSV, OUTPUT_CSV, MATCHES_CSV

        # patcher les chemins
        temp_path = Path(temp_data_dir)
        with patch.object(
            sys.modules["normalize_teams"],
            'BASE_DIR',
            temp_path
        ), patch.object(
                sys.modules['normalize_teams'],
                'TEAMS_CSV',
                temp_path / "data/processed/teams.csv"
            ), patch.object(
                sys.modules['normalize_teams'],
                'OUTPUT_CSV',
                temp_path / "data/processed/teams_traitees.csv"
            ), patch.object(
                sys.modules['normalize_teams'],
                'MATCHES_CSV',
                temp_path / "data/processed/matches.csv"
            ):
                df_result, unmatched = normalize_teams(update_matches=False)
                
        # Verifier les colonnes
        expected_columuns = ['id_team', 'nom_standard', 'confederation', 'aliases']
        assert list(df_result.columns) == expected_columuns
        
    def test_normalize_teams_unmatched_tracking(self, temp_data_dir):
        """Les équipes non reconnues sont suivies."""
        from normalize_teams import normalize_teams

        temp_path = Path(temp_data_dir)
        with patch.object(
            sys.modules['normalize_teams'],
            'BASE_DIR',
            temp_path
        ), patch.object(
            sys.modules['normalize_teams'],
            'TEAMS_CSV',
            temp_path / "data/processed/teams.csv"
        ), patch.object(
            sys.modules['normalize_teams'],
            'OUTPUT_CSV',
            temp_path / "data/processed/teams_traitees.csv"
        ), patch.object(
            sys.modules['normalize_teams'],
            'MATCHES_CSV',
            temp_path / "data/processed/matches.csv"
        ):
            df_result, unmatched = normalize_teams(update_matches=False)

        # "Unknown Team" du sample devrait être dans unmatched
        assert "Unknown Team" in unmatched
        
    def test_deduplication_keeps_lowest_id(self, temp_data_dir_with_duplicates):
        """La déduplication conserve l'ID le plus bas."""
        from normalize_teams import normalize_teams

        temp_path = Path(temp_data_dir_with_duplicates)
        with patch.object(
            sys.modules['normalize_teams'],
            'BASE_DIR',
            temp_path
        ), patch.object(
            sys.modules['normalize_teams'],
            'TEAMS_CSV',
            temp_path / "data/processed/teams.csv"
        ), patch.object(
            sys.modules['normalize_teams'],
            'OUTPUT_CSV',
            temp_path / "data/processed/teams_traitees.csv"
        ), patch.object(
            sys.modules['normalize_teams'],
            'MATCHES_CSV',
            temp_path / "data/processed/matches.csv"
        ):
            df_result, unmatched = normalize_teams(update_matches=False)
            
        # Germany (ID 2), West Germany (ID 3), FRG (ID 4) -> tous normalisés en Germany
        # Seul l'ID 2 devrait être conservé
        germany_rows = df_result[df_result['nom_standard'] == 'Germany']
        assert set(germany_rows['id_team']) == {2}

    def test_deduplication_removes_duplicates(self, temp_data_dir_with_duplicates):
        """La déduplication supprime les doublons."""
        from normalize_teams import normalize_teams

        temp_path = Path(temp_data_dir_with_duplicates)
        with patch.object(
            sys.modules['normalize_teams'],
            'BASE_DIR',
            temp_path
        ), patch.object(
            sys.modules['normalize_teams'],
            'TEAMS_CSV',
            temp_path / "data/processed/teams.csv"
        ), patch.object(
            sys.modules['normalize_teams'],
            'OUTPUT_CSV',
            temp_path / "data/processed/teams_traitees.csv"
        ), patch.object(
            sys.modules['normalize_teams'],
            'MATCHES_CSV',
            temp_path / "data/processed/matches.csv"
        ):
            df_result, unmatched = normalize_teams(update_matches=False)

        # Pas de doublons dans nom_standard
        assert df_result['nom_standard'].is_unique
        
    def test_matches_update_replaces_ids(self, temp_data_dir_with_duplicates):
        """La mise à jour des matches remplace correctement les IDs."""
        from normalize_teams import normalize_teams

        temp_path = Path(temp_data_dir_with_duplicates)
        with patch.object(
            sys.modules['normalize_teams'],
            'BASE_DIR',
            temp_path
        ), patch.object(
            sys.modules['normalize_teams'],
            'TEAMS_CSV',
            temp_path / "data/processed/teams.csv"
        ), patch.object(
            sys.modules['normalize_teams'],
            'OUTPUT_CSV',
            temp_path / "data/processed/teams_traitees.csv"
        ), patch.object(
            sys.modules['normalize_teams'],
            'MATCHES_CSV',
            temp_path / "data/processed/matches.csv"
        ):
            normalize_teams(update_matches=True)

        # Lire le fichier matches.csv mis à jour
        matches_path = temp_path / "data/processed/matches.csv"
        matches_df = pd.read_csv(matches_path)

        # Les IDs 3 et 4 (West Germany et FRG) devraient être remplacés par 2 (Germany)
        assert 3 not in matches_df['home_team_id'].values
        assert 3 not in matches_df['away_team_id'].values
        assert 4 not in matches_df['home_team_id'].values
        assert 4 not in matches_df['away_team_id'].values 
        
    def test_matches_no_update_when_flag_false(self, temp_data_dir_with_duplicates):
        """Matches.csv n'est pas modifié si update_matches=False."""
        from normalize_teams import normalize_teams

        temp_path = Path(temp_data_dir_with_duplicates)
        matches_path = temp_path / "data/processed/matches.csv"

        # Lire le fichier original
        matches_before = pd.read_csv(matches_path)

        with patch.object(
            sys.modules['normalize_teams'],
            'BASE_DIR',
            temp_path
        ), patch.object(
            sys.modules['normalize_teams'],
            'TEAMS_CSV',
            temp_path / "data/processed/teams.csv"
        ), patch.object(
            sys.modules['normalize_teams'],
            'OUTPUT_CSV',
            temp_path / "data/processed/teams_traitees.csv"
        ), patch.object(
            sys.modules['normalize_teams'],
            'MATCHES_CSV',
            matches_path
        ):
            normalize_teams(update_matches=False)

        # Lire après exécution
        matches_after = pd.read_csv(matches_path)

        # Le fichier ne devrait pas avoir changé
        pd.testing.assert_frame_equal(matches_before, matches_after)
        
    def test_output_file_created(self, temp_data_dir):
        """Le fichier teams_traitees.csv est créé."""
        from normalize_teams import normalize_teams

        temp_path = Path(temp_data_dir)
        output_path = temp_path / "data/processed/teams_traitees.csv"

        with patch.object(
            sys.modules['normalize_teams'],
            'BASE_DIR',
            temp_path
        ), patch.object(
            sys.modules['normalize_teams'],
            'TEAMS_CSV',
            temp_path / "data/processed/teams.csv"
        ), patch.object(
            sys.modules['normalize_teams'],
            'OUTPUT_CSV',
            output_path
        ), patch.object(
            sys.modules['normalize_teams'],
            'MATCHES_CSV',
            temp_path / "data/processed/matches.csv"
        ):
            normalize_teams(update_matches=False)

        assert output_path.exists()

    def test_aliases_column_is_json(self, temp_data_dir):
        """La colonne aliases contient du JSON valide."""
        from normalize_teams import normalize_teams

        temp_path = Path(temp_data_dir)
        with patch.object(
            sys.modules['normalize_teams'],
            'BASE_DIR',
            temp_path
        ), patch.object(
            sys.modules['normalize_teams'],
            'TEAMS_CSV',
            temp_path / "data/processed/teams.csv"
        ), patch.object(
            sys.modules['normalize_teams'],
            'OUTPUT_CSV',
            temp_path / "data/processed/teams_traitees.csv"
        ), patch.object(
            sys.modules['normalize_teams'],
            'MATCHES_CSV',
            temp_path / "data/processed/matches.csv"
        ):
            df_result, _ = normalize_teams(update_matches=False)

        # Vérifier que chaque valeur aliases est du JSON valide
        for aliases_str in df_result['aliases']:
            parsed = json.loads(aliases_str)
            assert isinstance(parsed, list)
            
class TestEdgeCases:
    """Tests des cas limites."""

    def test_empty_teams_file(self):
        """Gestion d'un fichier teams.csv vide."""
        from normalize_teams import normalize_teams

        temp_dir = tempfile.mkdtemp()
        try:
            processed_dir = Path(temp_dir) / "data" / "processed"
            processed_dir.mkdir(parents=True)

            # Créer un fichier teams.csv vide (avec headers)
            empty_df = pd.DataFrame(columns=['id_team', 'nom_standard'])
            empty_df.to_csv(processed_dir / "teams.csv", index=False)

            # Créer un fichier matches.csv vide
            empty_matches = pd.DataFrame(columns=['id_match', 'home_team_id', 'away_team_id'])
            empty_matches.to_csv(processed_dir / "matches.csv", index=False)

            temp_path = Path(temp_dir)
            with patch.object(
                sys.modules['normalize_teams'],
                'BASE_DIR',
                temp_path
            ), patch.object(
                sys.modules['normalize_teams'],
                'TEAMS_CSV',
                temp_path / "data/processed/teams.csv"
            ), patch.object(
                sys.modules['normalize_teams'],
                'OUTPUT_CSV',
                temp_path / "data/processed/teams_traitees.csv"
            ), patch.object(
                sys.modules['normalize_teams'],
                'MATCHES_CSV',
                temp_path / "data/processed/matches.csv"
            ):
                df_result, unmatched = normalize_teams(update_matches=False)

            assert len(df_result) == 0
            assert len(unmatched) == 0
        finally:
            shutil.rmtree(temp_dir)

    def test_all_teams_unmatched(self):
        """Toutes les équipes sont non reconnues."""
        from normalize_teams import normalize_teams

        temp_dir = tempfile.mkdtemp()
        try:
            processed_dir = Path(temp_dir) / "data" / "processed"
            processed_dir.mkdir(parents=True)

            # Créer un fichier avec des équipes inconnues
            unknown_df = pd.DataFrame({
                'id_team': [1, 2, 3],
                'nom_standard': ['Unknown1', 'Unknown2', 'Unknown3']
            })
            unknown_df.to_csv(processed_dir / "teams.csv", index=False)

            # Créer un fichier matches.csv
            matches_df = pd.DataFrame({
                'id_match': [1],
                'home_team_id': [1],
                'away_team_id': [2]
            })
            matches_df.to_csv(processed_dir / "matches.csv", index=False)

            temp_path = Path(temp_dir)
            with patch.object(
                sys.modules['normalize_teams'],
                'BASE_DIR',
                temp_path
            ), patch.object(
                sys.modules['normalize_teams'],
                'TEAMS_CSV',
                temp_path / "data/processed/teams.csv"
            ), patch.object(
                sys.modules['normalize_teams'],
                'OUTPUT_CSV',
                temp_path / "data/processed/teams_traitees.csv"
            ), patch.object(
                sys.modules['normalize_teams'],
                'MATCHES_CSV',
                temp_path / "data/processed/matches.csv"
            ):
                df_result, unmatched = normalize_teams(update_matches=False)

            assert len(unmatched) == 3
            assert set(unmatched) == {'Unknown1', 'Unknown2', 'Unknown3'}
        finally:
            shutil.rmtree(temp_dir)    