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
    scanner = Scanner('test_devicesblock.txt', names)
    error_store = Error_Store(scanner)
    devices = Devices(names, error_store)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    
    
    error_db = Error_Store(scanner)

    parser = Parser(names,devices,network,monitors,scanner, error_db)

    parser.parse_network()

    # error_db.report_errors()

if __name__ == "__main__":
    run()
