"""Test the scanner module."""
import pytest
import os

from scanner import Symbol
from scanner import Scanner
from names import Names


@pytest.fixture
def new_scanner():
    """Return scanner and name objects operating on passed file
       present in test cases folder."""
    def _method(file):
        names = Names()
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, 'scanner_test_cases/' + file)
        return Scanner(filename, names), names

    return _method


@pytest.fixture
def return_symbols(new_scanner):
    """Return a list of all found symbols in provided
       file and the names list built during scan."""
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
    """Test scanner able to pick out symbols amidst
       comments and whitespace."""
    symbols, names = return_symbols('comments.bna')
    symbols_name = [names.get_name_string(symbol.id) for symbol in symbols]
    expected_names = ['test', 'names', 'that', 'should',
                      'be', 'picked', 'up', 'more', 'symbols']
    for id in range(len(symbols_name)):
        assert symbols_name[id] == expected_names[id]


def test_punctuation(return_symbols):
    """Test scanner picks out correct punctuation
       and non-alphanumerics."""
    symbols = return_symbols('punctuation.bna')[0]
    expected_punctuation = [3,  # dot
                            0,  # semicolon
                            8,  # arrow
                            0,  # semicolon
                            3,  # dot
                            1,  # colon
                            2,  # equals
                            0,  # semicolon
                            3  # dot
                            ]
    punctuation_only = []
    for id in range(len(symbols)):
        if symbols[id].type in [0, 1, 2, 3, 8]:  # is punctuation
            punctuation_only.append(symbols[id])
    for id in range(len([punctuation_only])):
        assert symbols[id].type == expected_punctuation[id]


def test_unexpected_characters(return_symbols):
    """Test scanner able to spot and
       not crash on unused chars."""
    symbols, names = return_symbols('unexpected_chars.bna')
    expected_words = ['begin', 'devices', 'NAND', 'G1', 'inputs']
    expected_others = [1,  # colon
                       1,  # colon
                       2,  # equals
                       5,  # number
                       0  # semicolon
                       ]
    found_words = []
    others = []
    number_unexpected = 0
    for index in range(len(symbols)):
        symbol_type = symbols[index].type
        if symbol_type == 9:  # if unexpected char
            number_unexpected += 1
        elif symbol_type == 4 or symbol_type == 6:  # is a name / keyword
            found_words.append(symbols[index])
        else:  # punctuation etc.
            others.append(symbols[index])
    found_words = [names.get_name_string(symbol.id) for symbol in found_words]
    for index in range(len(found_words)):
        assert found_words[index] == expected_words[index]
    assert number_unexpected == 50
    for index in range(len(others)):
        assert others[index].type == expected_others[index]


def test_numbers_and_names(return_symbols):
    """Test scanner correctly identifies
       names, keywords and numbers."""
    symbols, names = return_symbols('numbers_names.bna')
    expected_data = ['begin', 'end', 'connections', 'monitors',
                     'OR', 'NAND', 'AND', 'NOR', 'XOR', 'CLOCK',
                     'SWITCH', 'DTYPE', 'DATA', 'CLK', 'SET', 'CLEAR',
                     'inputs', 'period', 'initial', 'SIGGEN', 'waveform',
                     'gate1', 'gate2', '350', '758', '1']
    for index in range(len(symbols)):
        if index <= 20:
            assert symbols[index].type == 4  # should all be keywords
            assert names.get_name_string(
                symbols[index].id) == expected_data[index]
        elif index <= 22:
            assert symbols[index].type == 6  # should be names
            assert names.get_name_string(
                symbols[index].id) == expected_data[index]
        else:
            assert symbols[index].type == 5  # should be numbers
            assert symbols[index].id == expected_data[index]
