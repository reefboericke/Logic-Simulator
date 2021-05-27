# import pytest
import os

from scanner import Symbol
from scanner import Scanner
from names import Names
from parse import Parser
from network import Network
from devices import Devices
from monitors import Monitors



def run():
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    scanner = Scanner('test_devicesblock.txt', names)

    parser = Parser(names,devices,network,monitors,scanner)

    parser.parse_network()

if __name__ == "__main__":
    run()
