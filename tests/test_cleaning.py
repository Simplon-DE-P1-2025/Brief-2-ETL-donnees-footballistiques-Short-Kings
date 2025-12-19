
import pytest
import sys
import os


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from cleaning import clean_percentage

def test_clean_percentage_standard():
    assert clean_percentage("50%") == 50.0
    assert clean_percentage("12.5%") == 12.5

def test_clean_percentage_no_change():
    assert clean_percentage(100) == 100
    assert clean_percentage(None) is None

def test_clean_percentage_error():
    with pytest.raises(ValueError):
        clean_percentage("erreur")