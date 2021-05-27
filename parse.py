"""Parse the definition file and build the logic network.

Used in the Logic Simulator project to analyse the syntactic and semantic
correctness of the symbols received from the scanner and then builds the
logic network.

Classes
-------
Parser - parses the definition file and builds the logic network.
"""


from attr import s


class Parser:

    """Parse the definition file and build the logic network.

    The parser deals with error handling. It analyses the syntactic and
    semantic correctness of the symbols it receives from the scanner, and
    then builds the logic network. If there are errors in the definition file,
    the parser detects this and tries to recover from it, giving helpful
    error messages.

    Parameters
    ----------
    names: instance of the names.Names() class.
    devices: instance of the devices.Devices() class.
    network: instance of the network.Network() class.
    monitors: instance of the monitors.Monitors() class.
    scanner: instance of the scanner.Scanner() class.

    Public methods
    --------------
    parse_network(self): Parses the circuit definition file.
    """

    def __init__(self, names, devices, network, monitors, scanner):
        """Initialise constants."""
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors
        self.scanner = scanner

    def error(self):
        print("error encountered")

    def deviceblockgrammar(self):
        currsymb = self.scanner.get_symbol()
        if currsymb.id != self.scanner.begin_ID:
            self.error()
        currsymb = self.scanner.get_symbol()
        if currsymb.id != self.scanner.devices_ID:
            self.error()
        currsymb = self.scanner.get_symbol()
        if currsymb.type != self.scanner.COLON:
            self.error()
        currsymb = self.scanner.get_symbol()
        # self.devicedefintiongrammar()
        if currsymb.id != self.scanner.end_ID:
            self.error()
        currsymb = self.scanner.get_symbol()
        if currsymb.id != self.scanner.devices_ID:
            self.error()
        currsymb = self.scanner.get_symbol()
        if currsymb.type != self.scanner.SEMICOLON:
            self.error()
            

    def BNAcodegrammar(self):
        self.deviceblockgrammar()
        # self.connectionblockgrammar()
        # self.monitorblockgrammar()

    def parse_network(self):
        """Parse the circuit definition file."""
        self.BNAcodegrammar()
        
