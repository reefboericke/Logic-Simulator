"""Test the devices module."""
import pytest

from scanner import Symbol
from scanner import Scanner

@pytest.fixture:
def new_symbol():
    """ Returns a new symbol. """
    return Symbol()

