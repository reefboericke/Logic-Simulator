"""Test the errors module"""

import pytest
import os
from scanner import Scanner
from names import Names
from errors import Error
from errors import Error_Store
import wx


@pytest.fixture
def new_scanner():
    """Return scanner and name objects operating on passed file
       present in test cases folder."""
    def _method(file):
        names = Names()
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, 'errors_test_cases/' + file)
        return Scanner(filename, names)

    return _method


@pytest.fixture
def new_error_store(new_scanner):
    """Return opened error store."""
    def _method(file):
        scanner = new_scanner(file)
        return Error_Store(scanner)

    return _method


def test_error_counting(new_error_store):
    """Check error id / tracking correct."""
    error_db = new_error_store('empty.bna')
    assert(error_db.no_errors == 0)
    error_db.add_error('semantic', 0)
    assert(error_db.no_errors == 1)
    assert(error_db.errors[0].error_number == 1)


def test_error_reporting(new_error_store):
    """Test different errors give expected error string."""
    errors_to_report = [
        ('semantic', 0),
        ('semantic', 6),
        ('semantic', 10),
        ('semantic', 12),
        ('syntax', 1),
        ('syntax', 5),
        ('syntax', 10)
    ]
    error_db = new_error_store('empty.bna')
    for error in errors_to_report:
        error_db.add_error(error[0], error[1])
    error_db.report_errors()
    error_report = open('error_report.txt').read()
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, 'errors_test_cases/'
                            + 'expected_report.txt')
    expected_report = open(filename, 'r').read()
    assert(error_report == expected_report)


def test_error_sorting(new_error_store):
    """Test errors get sorted by line number correctly.

    Note error objects directly added to avoid requiring
    a non-tested parser. See test_parse.py for parser
    testing.
    """
    error_db = new_error_store('empty.bna')
    locations = [
        (12, '', 0),
        (2, '', 0),
        (5, '', 0),
        (31, '', 0)
    ]
    i = 1
    for loc in locations:
        new_error = Error(i, loc, 'semantic', 0)
        error_db.errors.append(new_error)
        i += 1

    error_db.sort_errors()
    assert(error_db.errors[0].location == locations[1])
    assert(error_db.errors[0].error_number == 2)

    assert(error_db.errors[1].location == locations[2])
    assert(error_db.errors[1].error_number == 3)

    assert(error_db.errors[2].location == locations[0])
    assert(error_db.errors[2].error_number == 1)

    assert(error_db.errors[3].location == locations[3])
    assert(error_db.errors[3].error_number == 4)


def test_error_querying(new_error_store):
    error_db = new_error_store('empty.bna')
    for i in range(19):
        error_db.add_error('syntax', i)
        error_db.add_error('semantic', i)
        assert(error_db.query_semantics(i) == 1)
        assert(error_db.query_semantics(i) == 1)
    error_db.add_error('syntax', 5)
    error_db.add_error('semantic', 8)
    assert(error_db.query_syntax(5) == 2)
    assert(error_db.query_semantics(8) == 2)
