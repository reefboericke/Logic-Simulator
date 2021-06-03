"""Test parse module"""

import os
import pytest
from scanner import Scanner
from names import Names
from errors import Error_Store
from parse import Parser
from network import Network
from devices import Devices
from monitors import Monitors
import os


@pytest.fixture
def parsed_network():
    """Return parser and error objects operating on passed file
       present in test cases folder."""
    def _method(file):
        names = Names()
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, 'parse_test_cases/' + file)
        scanner = Scanner(filename, names)
        error_db = Error_Store(scanner)
        devices = Devices(names)
        network = Network(names, devices)
        monitors = Monitors(names, devices, network)

        parser = Parser(names, devices, network, monitors, scanner, error_db)
        parser.parse_network()
        return error_db

    return _method


def test_parse_correct_file(parsed_network):
    """Test parser raises no errors on a valid file"""
    error_db = parsed_network('valid.bna')
    error_report = error_db.report_errors()
    assert(error_report is False)


def test_device_semantic_errors(parsed_network):
    """Test parser finds all device definition semantics errs."""
    error_db = parsed_network('device_semantic_errors.bna')
    expected_semantic_error_counts = [
        1,  # error type 0
        1,  # type 1
        1,  # type 2
        11,  # type 3
        2,  # type 4
        2,  # type 5
        2,  # type 6
        3,  # type 7
        1   # type 8
    ]
    for i in range(9):
        assert(error_db.query_semantics(i) ==
               expected_semantic_error_counts[i])


def test_connection_semantic_errors(parsed_network):
    """Test parser picks up semantic errors in connection block."""
    error_db = parsed_network('connection_semantic_errors.bna')
    expected_error_types = [11, 12, 13, 15]
    for i in expected_error_types:
        assert(error_db.query_semantics(i) == 1)


def test_connection_double_connection_error(parsed_network):
    """Check specific case of double connections."""
    error_db = parsed_network('double_connection.bna')
    assert(error_db.query_semantics(14) == 1)  # error 14
    assert(error_db.query_semantics(15) == 1)  # error 15


def test_monitor_semantic_errors(parsed_network):
    """Test parser finds semantic errors related to monitor block."""
    error_db = parsed_network('monitor_semantic_errors.bna')
    assert(error_db.query_semantics(16) == 1)
    assert(error_db.query_semantics(17) == 1)


@pytest.mark.parametrize("file, error_id", [
    ('no_devices.bna', 17),
    ('no_connections.bna', 16),
    ('no_monitors.bna', 13),
    ('no_begin.bna', 12),
    ('missing_name.bna', 0),
    ('missing_semicolon.bna', 1),
    ('missing_dot.bna', 2),
    ('missing_DTYPE_output.bna', 3),
    ('missing_arrow.bna', 4),
    ('invalid_input.bna', 5),
    ('missing_colon.bna', 6),
    ('invalid_device_variable.bna', 7),
    ('missing_equals.bna', 8),
    ('missing_number.bna', 9),
    ('missing_device.bna', 18),
    ('missing_colon_semicolon.bna', 11),
    ('missing_name_end.bna', 14),
    ('missing_device_end.bna', 18)
])
def test_single_syntax_error_detection(parsed_network, file, error_id):
    """Test every syntax error and that parser picks it up."""
    error_db = parsed_network(file)
    assert(error_db.query_syntax(error_id) == 1)
    """
    for i in range(19):
        if (i not in [error_id, 15]):
            assert(error_db.query_syntax(i) == 0)
        assert(error_db.query_semantics(i) == 0)
    """


def test_realistic_error_set_detection(parsed_network):
    """Test parser behaves as expected on a feasible file."""
    error_db = parsed_network('multiple_errors.bna')
    for i in range(1, 19):
        if (i in [4, 7, 15]):
            assert(error_db.query_semantics(i) == 1)
            assert(error_db.query_syntax(i) == 0)
        elif (i in [2, 13]):
            assert(error_db.query_syntax(i) == 1)
            assert(error_db.query_semantics(i) == 0)
        else:
            assert(error_db.query_syntax(i) == 0)
            assert(error_db.query_semantics(i) == 0)
