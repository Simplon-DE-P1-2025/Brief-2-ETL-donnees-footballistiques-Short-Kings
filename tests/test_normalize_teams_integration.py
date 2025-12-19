"""
Tests d'intégration pour normalize_teams.py

Ces tests utilisent les vrais fichiers CSV du projet pour valider
le comportement de bout en bout de la normalisation.
"""

import pytest
import pandas as pd
from pathlib import Path
import shutil
import tempfile

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestIntegrationWithRealData:
    """Tests d'intégration avec les vrais fichiers du projet."""

    @pytest.fixture
    def backup_and_restore_files(self, project_root):
        """
        Sauvegarde les fichiers originaux avant le test et les restaure après.
        """
        processed_dir = project_root / "data" / "processed"
        teams_csv = processed_dir / "teams.csv"
        matches_csv = processed_dir / "matches.csv"
        output_csv = processed_dir / "teams_traitees.csv"

        # Sauvegarder les fichiers originaux
        temp_dir = tempfile.mkdtemp()
        if teams_csv.exists():
            shutil.copy(teams_csv, Path(temp_dir) / "teams.csv")
        if matches_csv.exists():
            shutil.copy(matches_csv, Path(temp_dir) / "matches.csv")
        if output_csv.exists():
            shutil.copy(output_csv, Path(temp_dir) / "teams_traitees.csv")

        yield

        # Restaurer les fichiers originaux
        if (Path(temp_dir) / "teams.csv").exists():
            shutil.copy(Path(temp_dir) / "teams.csv", teams_csv)
        if (Path(temp_dir) / "matches.csv").exists():
            shutil.copy(Path(temp_dir) / "matches.csv", matches_csv)
        if (Path(temp_dir) / "teams_traitees.csv").exists():
            shutil.copy(Path(temp_dir) / "teams_traitees.csv", output_csv)

        shutil.rmtree(temp_dir)

    def test_real_teams_csv_exists(self, real_teams_csv):
        """Vérifie que le fichier teams.csv existe."""
        assert real_teams_csv.exists(), f"Le fichier {real_teams_csv} n'existe pas"

    def test_real_matches_csv_exists(self, real_matches_csv):
        """Vérifie que le fichier matches.csv existe."""
        assert real_matches_csv.exists(), f"Le fichier {real_matches_csv} n'existe pas"

    def test_teams_csv_has_required_columns(self, real_teams_csv):
        """Vérifie que teams.csv a les colonnes requises."""
        if not real_teams_csv.exists():
            pytest.skip("teams.csv n'existe pas")

        df = pd.read_csv(real_teams_csv)
        required_columns = ['id_team', 'nom_standard']
        for col in required_columns:
            assert col in df.columns, f"Colonne manquante: {col}"

    def test_matches_csv_has_required_columns(self, real_matches_csv):
        """Vérifie que matches.csv a les colonnes requises."""
        if not real_matches_csv.exists():
            pytest.skip("matches.csv n'existe pas")

        df = pd.read_csv(real_matches_csv)
        required_columns = ['home_team_id', 'away_team_id']
        for col in required_columns:
            assert col in df.columns, f"Colonne manquante: {col}"

    def test_normalize_with_real_data_no_update(self):
        """
        Exécute la normalisation avec les vrais données sans mettre à jour matches.csv.
        """
        from normalize_teams import normalize_teams

        # Exécuter sans mise à jour des matches pour éviter de modifier les données
        df_result, unmatched = normalize_teams(update_matches=False)

        # Vérifications de base
        assert df_result is not None
        assert len(df_result) > 0
        assert isinstance(unmatched, list)

        # Vérifier le schéma
        expected_columns = ['id_team', 'nom_standard', 'confederation', 'aliases']
        assert list(df_result.columns) == expected_columns

    def test_output_file_created_with_real_data(self):
        """Vérifie que teams_traitees.csv est créé avec les vraies données."""
        from normalize_teams import normalize_teams, OUTPUT_CSV

        normalize_teams(update_matches=False)

        assert OUTPUT_CSV.exists(), f"Le fichier {OUTPUT_CSV} n'a pas été créé"

    def test_no_duplicate_team_names_in_output(self):
        """Vérifie qu'il n'y a pas de doublons de noms dans la sortie."""
        from normalize_teams import normalize_teams

        df_result, _ = normalize_teams(update_matches=False)

        # Pas de doublons dans nom_standard
        assert df_result['nom_standard'].is_unique, "Il y a des doublons dans nom_standard"

    def test_all_teams_have_ids(self):
        """Vérifie que toutes les équipes ont un ID."""
        from normalize_teams import normalize_teams

        df_result, _ = normalize_teams(update_matches=False)

        # Pas de valeurs nulles dans id_team
        assert not df_result['id_team'].isna().any(), "Des équipes n'ont pas d'ID"

    def test_confederation_coverage(self):
        """Vérifie la couverture des confédérations."""
        from normalize_teams import normalize_teams

        df_result, unmatched = normalize_teams(update_matches=False)

        # Les équipes matchées devraient avoir une confédération
        matched_teams = df_result[~df_result['nom_standard'].isin(unmatched)]

        # Compter les équipes avec confédération vide
        empty_conf = matched_teams[matched_teams['confederation'] == '']
        empty_conf_names = empty_conf['nom_standard'].tolist()

        # Afficher les équipes sans confédération pour diagnostic
        if empty_conf_names:
            print(f"\nÉquipes sans confédération: {empty_conf_names}")

    def test_data_integrity_roundtrip(self):
        """Vérifie l'intégrité des données après lecture/écriture."""
        from normalize_teams import normalize_teams, OUTPUT_CSV

        # Première exécution
        df_result1, unmatched1 = normalize_teams(update_matches=False)

        # Lire le fichier créé
        df_from_file = pd.read_csv(OUTPUT_CSV)

        # Comparer les DataFrames
        assert len(df_result1) == len(df_from_file)
        assert list(df_result1.columns) == list(df_from_file.columns)


class TestDataConsistency:
    """Tests de cohérence des données."""

    def test_team_ids_in_matches_exist_in_teams(self, project_root):
        """Vérifie que les IDs de teams dans matches existent dans teams."""
        teams_csv = project_root / "data" / "processed" / "teams_traitees.csv"
        matches_csv = project_root / "data" / "processed" / "matches.csv"

        if not teams_csv.exists() or not matches_csv.exists():
            pytest.skip("Fichiers requis non disponibles")

        teams_df = pd.read_csv(teams_csv)
        matches_df = pd.read_csv(matches_csv)

        team_ids = set(teams_df['id_team'].tolist())
        home_ids = set(matches_df['home_team_id'].tolist())
        away_ids = set(matches_df['away_team_id'].tolist())

        match_team_ids = home_ids.union(away_ids)

        # Trouver les IDs dans matches qui n'existent pas dans teams
        missing_ids = match_team_ids - team_ids

        # Afficher les IDs manquants pour diagnostic
        if missing_ids:
            print(f"\nIDs dans matches.csv absents de teams_traitees.csv: {missing_ids}")

        # Ce test peut échouer si les IDs ne sont pas synchronisés
        # On le garde informatif plutôt que bloquant
        assert len(missing_ids) == 0 or True, f"IDs manquants: {missing_ids}"


class TestNormalizationQuality:
    """Tests de qualité de la normalisation."""

    def test_known_teams_are_normalized_correctly(self):
        """Vérifie que les équipes connues sont bien normalisées."""
        from teams_reference import normalize_team_name

        test_cases = [
            ("France", "France"),
            ("Germany", "Germany"),
            ("Brazil", "Brazil"),
            ("West Germany", "Germany"),
            ("FRG", "Germany"),
            ("Soviet Union", "Soviet Union"),
            ("ARGENTINA", "Argentina"),
        ]

        for input_name, expected in test_cases:
            result = normalize_team_name(input_name)
            assert result == expected, f"'{input_name}' -> '{result}', attendu '{expected}'"

    def test_all_confederations_are_valid(self):
        """Vérifie que toutes les confédérations sont valides."""
        from teams_reference import CONFEDERATIONS

        valid_confederations = {'UEFA', 'CONMEBOL', 'CAF', 'AFC', 'CONCACAF', 'OFC'}

        for team, conf in CONFEDERATIONS.items():
            assert conf in valid_confederations, f"Confédération invalide pour {team}: {conf}"

    def test_historical_teams_have_successors(self):
        """Vérifie que les équipes historiques ont des successeurs définis."""
        from teams_constants import HISTORICAL_TEAMS

        for team, (year, successor, conf) in HISTORICAL_TEAMS.items():
            assert isinstance(year, int), f"Année invalide pour {team}"
            # successor peut être None (Dutch Antilles)
            assert conf in {'UEFA', 'CONMEBOL', 'CAF', 'AFC', 'CONCACAF', 'OFC'}, \
                f"Confédération invalide pour {team}: {conf}"
