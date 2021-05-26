"""Test the scanner module."""
import pytest
import os

from scanner import Symbol
from scanner import Scanner
from names import Names

@pytest.fixture
def new_scanner():
    """ Returns scanner and name objects operating on passed file present in test cases folder. """
    def _method(file):
        names = Names()
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, 'scanner_test_cases/' + file)
        return Scanner(filename, names), names

    return _method

@pytest.fixture
def return_symbols(new_scanner):
    """ Returns a list of all found symbols in provided file and the names list built during scan. """
    def _method(file):
        scanner, names = new_scanner(file)
        current_symbol = scanner.get_symbol()
        symbols = []
        while(current_symbol.type != 7):  # i.e. break on EOF
            symbols.append(current_symbol)
            current_symbol = scanner.get_symbol()
        return(symbols, names)

    return _method

def test_comments_and_whitespace(return_symbols):
    """ Tests scanner able to pick out symbols amidst comments and whitespace. """
    symbols, names = return_symbols('comments.bna')
    symbols_name = [names.get_name_string(symbol.id) for symbol in symbols]
    expected_names = ['test', 'names', 'that', 'should', 'be', 'picked', 'up', 'more', 'symbols']
    for id in range(len(symbols_name)):
        assert symbols_name[id] ==  expected_names[id]

def test_punctuation(return_symbols):
    symbols, names = return_symbols('punctuation.bna')
    expected_punctuation = [3, # dot
                            0, # semicolon
                            8, # arrow
                            0, # semicolon
                            3, # dot
                            1, # colon
                            2, # equals
                            0, # semicolon
                            3  # dot
    ]
    punctuation_only = []
    for id in range(len(symbols)):
        if symbols[id].type  in [0, 1, 2, 3, 8]:  # is punctuation
            punctuation_only.append(symbols[id])
    for id in range(len([punctuation_only])):
        assert symbols[id].type == expected_punctuation[id]

def test_numbers_and_names(return_symbols):
    return True

def test_unexpected_characters(return_symbols):
    return True
    