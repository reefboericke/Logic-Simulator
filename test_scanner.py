"""Test the scanner module."""
import pytest

from scanner import Symbol
from scanner import Scanner

@pytest.fixture
def new_symbol():
    """ Returns a new symbol. """
    return Symbol()

@pytest.fixture
def new_scanner():
    """ Returns a scanner operating on a sample BNA file """
    return Scanner('test_BNA_file.txt', )

def test_next_symbol(new_scanner):
    next_symbol = new_scanner.get_symbol()

    assert(next_symbol == 'begindevices')

def 
