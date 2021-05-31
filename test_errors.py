"""Test the errors module"""

import pytest
from scanner import Symbol
from scanner import Scanner
from names import Names
from errors import Error
from errors import Error_Store

@pytest.fixture
def new_scanner():
    """Return scanner and name objects operating on passed file
       present in test cases folder."""
    def _method(file):
        names = Names()
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, 'errors_test_cases/' + file)
        return Scanner(filename, names), names

    return _method

@pytest.fixture
def new_error_store(new_scanner):
    """Return opened error store."""
    def _method(file):
        scanner, names = new_scanner(file)
        return Error_Store(scanner)

    return _method

def test_error_counting(new_error_store):
    """Check error id / tracking correct."""
    error_db = new_error_store('empty.bna')
    assert(error_db.no_errors == 0)
    error_db.add_error('semantic', 0)
    assert(error_db.no_errors == 1)
    assert(error_db.errors[0].error_id == 1)

@pytest.mark.parametrize("error_type, error_id, expected_text", [
    ("semantic", 0, " "),
    ("semantic", 1, " "),
    ("semantic", 2, " "),
    ("semantic", 3, " ")
    ("syntax", 'begin', " ")
    ("syntax", ['a name', 'end'], "")
])

def test_error_reporting(new_error_store, error_type, error_id, expected_text):
    """Test different errors give expected error string."""
    error_db = new_error_store('empty.bna')
    error_db.add_error(error_type, error_id)
    assert( error_db.errors[0].report() == expected_text )

def test_error_sorting(new_error_store):
    """Test errors get sorted by line number correctly.

    Note error objects directly added to avoid requiring
    a non-tested parser. See test_parse.py for parser
    testing.
    """
    error_db = new_error_store('blank.bna')
    locations = [
        (12, '', 0)
        (2, '', 0)
        (5, '', 0)
        (31, '', 0)
    ]
    i = 1
    for loc in locations:
        new_error = Error(i, loc, 'semantic', 0)
        error_db.errors.append(new_error)
        i += 1

    error_db.sort_errors()
    assert(error_db.errors[0].location == locations[1])
    assert(error_db.errors[0].error_id == 2)

    assert(error_db.errors[1].location == locations[2])
    assert(error_db.errors[1].error_id = 3)

    assert(error_db.errors[2].location == locations[0])
    assert(errpr_db.errors[2].error_id == 1)

    assert(error_db.errors[3].location == locations[3])
    assert(error_db.errors[3].error_id == 4)