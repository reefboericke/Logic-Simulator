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
        self.device_ids = [self.scanner.CLOCK_ID, self.scanner.SWITCH_ID, 
         self.scanner.DTYPE_ID, self.scanner.AND_ID, self.scanner.NAND_ID,
         self.scanner.OR_ID, self.scanner.NOR_ID, self.scanner.XOR_ID]
        self.variable_ids = [self.scanner.inputs_ID, self.scanner.period_ID, 
         self.scanner.initial_ID]
        # self.output_ids = [self.scanner.Q, self.scanner.QBAR]

    def error(self):
        print("error encountered on symbol type: ", self.currsymb.type, " and ID: ", self.currsymb.id)
        while self.currsymb.type != self.scanner.SEMICOLON:
            self.currsymb = self.scanner.get_symbol()
        self.currsymb = self.scanner.get_symbol()

    def monitordefinitiongrammar(self):
        if self.currsymb.type == self.scanner.NAME:
            self.currsymb = self.scanner.get_symbol()
        else:
            self.error()

        if self.currsymb.type == self.scanner.SEMICOLON:
            self.currsymb = self.scanner.get_symbol()
        else:
            self.error()

    def assignoutputgrammar(self):
        if self.currsymb.type == self.scanner.DOT:
            self.currsymb = self.scanner.get_symbol()
        else:
            self.error()

        if self.currsymb.type == self.scanner.NAME: # Add Q/QBAR IDs to scanner
            self.currsymb = self.scanner.get_symbol()
        else:
            self.error()

    def connectiondefinitiongrammar(self):
        if self.currsymb.type == self.scanner.NAME:
            self.currsymb = self.scanner.get_symbol()
        else:
            self.error()

        if self.currsymb.type == self.scanner.DOT:
            self.assignoutputgrammar()

        if self.currsymb.type == self.scanner.ARROW:
            self.currsymb = self.scanner.get_symbol()
        else:
            self.error()

        if self.currsymb.type == self.scanner.NAME:
            self.currsymb = self.scanner.get_symbol()
        else:
            self.error()

        if self.currsymb.type == self.scanner.DOT:
            self.currsymb = self.scanner.get_symbol()
        else:
            self.error()

        if self.currsymb.type == self.scanner.NAME: # Can we refine this to only allow inputs?
            self.currsymb = self.scanner.get_symbol()
        else:
            self.error()

        if self.currsymb.type == self.scanner.SEMICOLON:
            self.currsymb = self.scanner.get_symbol()
        else:
            self.error()

    def assignvariablegrammar(self):
        if self.currsymb.type == self.scanner.COLON:
            self.currsymb = self.scanner.get_symbol()
        else:
            self.error()

        if self.currsymb.id in self.variable_ids:
            self.currsymb = self.scanner.get_symbol()
        else:
            self.error()
        
        if self.currsymb.type == self.scanner.EQUALS:
            self.currsymb = self.scanner.get_symbol()
        else:
            self.error()

        if self.currsymb.type == self.scanner.NUMBER:
            self.currsymb = self.scanner.get_symbol()
        else:
            self.error()


    def devicedefinitiongrammar(self):
        if self.currsymb.id in self.device_ids:
            self.currsymb = self.scanner.get_symbol()
        else:
            self.error()

        if self.currsymb.type == self.scanner.NAME:
            self.currsymb = self.scanner.get_symbol()
        else:
            self.error()

        if self.currsymb.type == self.scanner.COLON:
            self.assignvariablegrammar()
        
        if self.currsymb.type == self.scanner.SEMICOLON:
            self.currsymb = self.scanner.get_symbol()
        else:
            self.error()

    def monitorblockgrammar(self): 
        if self.currsymb.id == self.scanner.begin_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            self.error()
    
        if self.currsymb.id == self.scanner.monitors_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            self.error()

        if self.currsymb.type == self.scanner.COLON:
            self.currsymb = self.scanner.get_symbol()
        else:
            self.error()
        
        while self.currsymb.type == self.scanner.NAME:
            self.monitordefinitiongrammar()

        if self.currsymb.id == self.scanner.end_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            self.error()

        if self.currsymb.id == self.scanner.monitors_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            self.error()

        if self.currsymb.type == self.scanner.SEMICOLON:
            self.currsymb = self.scanner.get_symbol()
        else:
            self.error()

    def connectionblockgrammar(self):
        if self.currsymb.id == self.scanner.begin_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            self.error()   

        if self.currsymb.id == self.scanner.connections_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            self.error()

        if self.currsymb.type == self.scanner.COLON:
            self.currsymb = self.scanner.get_symbol()
        else:
            self.error()
        
        while self.currsymb.type == self.scanner.NAME:
            self.connectiondefinitiongrammar()

        if self.currsymb.id == self.scanner.end_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            self.error()

        if self.currsymb.id == self.scanner.connections_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            self.error()

        if self.currsymb.type == self.scanner.SEMICOLON:
            self.currsymb = self.scanner.get_symbol()
        else:
            self.error()
    
    def deviceblockgrammar(self):
        if self.currsymb.id == self.scanner.begin_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            self.error()   

        if self.currsymb.id == self.scanner.devices_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            self.error()

        if self.currsymb.type == self.scanner.COLON:
            self.currsymb = self.scanner.get_symbol()
        else:
            self.error()
        
        while self.currsymb.id in self.device_ids:
            self.devicedefinitiongrammar()

        if self.currsymb.id == self.scanner.end_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            self.error()

        if self.currsymb.id == self.scanner.devices_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            self.error()

        if self.currsymb.type == self.scanner.SEMICOLON:
            self.currsymb = self.scanner.get_symbol()
        else:
            self.error()

    def BNAcodegrammar(self):

        self.deviceblockgrammar()

        self.connectionblockgrammar()

        if self.currsymb.id == self.scanner.begin_ID:
            self.monitorblockgrammar()

    def parse_network(self):
        """Parse the circuit definition file."""
        self.currsymb = self.scanner.get_symbol()
        self.BNAcodegrammar()

        """ Note that currently, it correctly will allow 
         correct files to be run, but any erros in the file
         will be flagged as several unique errors """
        
