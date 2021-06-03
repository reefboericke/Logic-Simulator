# import pytest
import os

from scanner import Symbol
from scanner import Scanner
from names import Names
from parse import Parser
from network import Network
from devices import Devices
from monitors import Monitors
from errors import Error_Store
import linecache


def run():
    
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    
    scanner = Scanner('/Users/finnashley/Onedrive/University/IIA/GF2/Logic-Simulator/errors_test_cases/empty.bna', names)
    error_db = Error_Store(scanner)
    parser = Parser(names,devices,network,monitors,scanner, error_db)

    errors_to_report = [
        ('semantic', 0),
        ('semantic', 6),
        ('semantic', 10),
        ('semantic', 12),
        ('syntax', 1),
        ('syntax', 5),
        ('syntax', 10)
    ]
    for error in errors_to_report:
        error_db.add_error(error[0], error[1])

    parser.parse_network()

if __name__ == "__main__":
    run()
