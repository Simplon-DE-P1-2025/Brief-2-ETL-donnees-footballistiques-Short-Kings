
import pytest
import sys
import os


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from cleaning import clean_percentage, clean_round_name 

def test_clean_percentage_standard():
    assert clean_percentage("50%") == 50.0
    assert clean_percentage("12.5%") == 12.5

def test_clean_percentage_no_change():
    assert clean_percentage(100) == 100
    assert clean_percentage(None) is None

def test_clean_percentage_error():
    with pytest.raises(ValueError):
        clean_percentage("erreur")



def test_clean_round_name_groups():
    assert clean_round_name("Group A") == "Group Stage"
    assert clean_round_name("First Stage") == "Preliminary"

def test_clean_round_name_knockout():
    assert clean_round_name("Round of 16") == "Round of 16"
    assert clean_round_name("1/8 Finals") == "Round of 16"
    assert clean_round_name("Quarter-finals") == "Quarter-finals"
    assert clean_round_name("1/4") == "Quarter-finals"
    assert clean_round_name("Semi-final") == "Semi-final"
    assert clean_round_name("Final") == "Final"

def test_clean_round_name_third_place():
    assert clean_round_name("Play-off for third place") == "Third Place"
    assert clean_round_name("3rd Place") == "Third Place"

def test_clean_round_name_unknown():
    assert clean_round_name("Unknown Round") == "Unknown Round"