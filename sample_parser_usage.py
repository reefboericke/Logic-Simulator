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
    
    scanner = Scanner('/Users/finnashley/Onedrive/University/IIA/GF2/Logic-Simulator/empty.bn', names)
    error_db = Error_Store(scanner)
    parser = Parser(names,devices,network,monitors,scanner, error_db)

    parser.parse_network()

if __name__ == "__main__":
    run()
