"""Parse the definition file and build the logic network.

Used in the Logic Simulator project to analyse the syntactic and semantic
correctness of the symbols received from the scanner and then builds the
logic network.

Classes
-------
Parser - parses the definition file and builds the logic network.
"""


from names import Names
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

    def __init__(self, names, devices, network, monitors, scanner, error_db):
        """Initialise constants."""
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors
        self.scanner = scanner
        self.error_db = error_db
        self.device_ids = [self.scanner.CLOCK_ID, self.scanner.SWITCH_ID, 
         self.scanner.DTYPE_ID, self.scanner.AND_ID, self.scanner.NAND_ID,
         self.scanner.OR_ID, self.scanner.NOR_ID, self.scanner.XOR_ID]
        self.variable_ids = [self.scanner.inputs_ID, self.scanner.period_ID, 
         self.scanner.initial_ID]
        self.output_ids = [self.scanner.Q_ID, self.scanner.QBAR_ID]

    def skip_to_semicolon(self):
        #print("error encountered on symbol:", self.names.names_list[self.currsymb.id])
        while self.currsymb.type != self.scanner.SEMICOLON:
            self.currsymb = self.scanner.get_symbol()
        self.currsymb = self.scanner.get_symbol()

    def monitordefinitiongrammar(self):
        if self.currsymb.type == self.scanner.NAME:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected a name
            self.error_db.add_error('syntax', 'name')
            self.skip_to_semicolon()

        if self.currsymb.type == self.scanner.SEMICOLON:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected semicolon
            self.error_db.add_error('syntax', ';')
            self.skip_to_semicolon()

    def assignoutputgrammar(self):
        if self.currsymb.type == self.scanner.DOT:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected dot
            self.error_db.add_error('syntax', '.')
            self.skip_to_semicolon()

        if self.currsymb.id in self.output_ids:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected Q / QBAR
            self.error_db.add_error('syntax', 'Q / QBAR')
            self.skip_to_semicolon()

    def connectiondefinitiongrammar(self):
        if self.currsymb.type == self.scanner.NAME:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected a name
            self.error_db.add_error('syntax', 'name')
            self.skip_to_semicolon()

        if self.currsymb.type == self.scanner.DOT:
            self.assignoutputgrammar()

        if self.currsymb.type == self.scanner.ARROW:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected an arrow
            self.error_db.add_error('syntax', '->')
            self.skip_to_semicolon()

        if self.currsymb.type == self.scanner.NAME:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected a name
            self.error_db.add_error('syntax', 'name')
            self.skip_to_semicolon()

        if self.currsymb.type == self.scanner.DOT:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected dot
            self.error_db.add_error('syntax', '.')
            self.skip_to_semicolon()

        if self.currsymb.type == self.scanner.NAME: # Can we refine this to only allow inputs?
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected a name
            self.error_db.add_error('syntax', 'name')
            self.skip_to_semicolon()

        if self.currsymb.type == self.scanner.SEMICOLON:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected semicolon
            self.error_db.add_error('syntax', ';')
            self.skip_to_semicolon()

    def assignvariablegrammar(self):
        if self.currsymb.type == self.scanner.COLON:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected a colon
            self.error_db.add_error('syntax', ':')
            self.skip_to_semicolon()

        if self.currsymb.id in self.variable_ids:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected variable
            self.error_db.add_error('syntax', 'device variable')
            self.skip_to_semicolon()
        
        if self.currsymb.type == self.scanner.EQUALS:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected an equals
            self.error_db.add_error('syntax', '=')
            self.skip_to_semicolon()

        if self.currsymb.type == self.scanner.NUMBER:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected a number
            self.error_db.add_error('syntax', 'number')
            self.skip_to_semicolon()


    def devicedefinitiongrammar(self):
        if self.currsymb.id in self.device_ids:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected device keyword
            self.error_db.add_error('syntax', 'devices')
            self.skip_to_semicolon()

        if self.currsymb.type == self.scanner.NAME:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected a name
            self.error_db.add_error('syntax', 'name')
            self.skip_to_semicolon()

        if self.currsymb.type == self.scanner.COLON:
            self.assignvariablegrammar()
        
        if self.currsymb.type == self.scanner.SEMICOLON:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected semicolon
            self.error_db.add_error('syntax', ';')
            self.skip_to_semicolon()

    def monitorblockgrammar(self): 
        if self.currsymb.id == self.scanner.begin_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected begin keyword
            self.error_db.add_error('syntax', 'begin')
            self.skip_to_semicolon()
    
        if self.currsymb.id == self.scanner.monitors_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected monitors keyword
            self.error_db.add_error('syntax', 'monitors')
            self.skip_to_semicolon()

        if self.currsymb.type == self.scanner.COLON:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected colon 
            self.error_db.add_error('syntax', ':')
            self.skip_to_semicolon()
        
        while self.currsymb.type == self.scanner.NAME:
            self.monitordefinitiongrammar()

        if self.currsymb.id == self.scanner.end_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected monitors keyword
            self.error_db.add_error('syntax', 'end')
            self.skip_to_semicolon()

        if self.currsymb.id == self.scanner.monitors_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected monitors keyword
            self.error_db.add_error('syntax', 'monitors')
            self.skip_to_semicolon()

        if self.currsymb.type == self.scanner.SEMICOLON:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected semicolon
            self.error_db.add_error('syntax', ';')
            self.skip_to_semicolon()

    def connectionblockgrammar(self):
        if self.currsymb.id == self.scanner.begin_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected being keyword
            self.error_db.add_error('syntax', 'begin')
            self.skip_to_semicolon()

        if self.currsymb.id == self.scanner.connections_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected connections keyword
            self.error_db.add_error('syntax', 'connections')
            self.skip_to_semicolon()

        if self.currsymb.type == self.scanner.COLON:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected colon
            self.error_db.add_error('syntax', ':')
            self.skip_to_semicolon()
        
        while self.currsymb.type == self.scanner.NAME:
            self.connectiondefinitiongrammar()

        if self.currsymb.id == self.scanner.end_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected end keyword
            self.error_db.add_error('syntax', 'end')
            self.skip_to_semicolon()

        if self.currsymb.id == self.scanner.connections_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected connections keyword
            self.error_db.add_error('syntax', 'connections')
            self.skip_to_semicolon()

        if self.currsymb.type == self.scanner.SEMICOLON:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected semicolon
            self.error_db.add_error('syntax', ';')
            self.skip_to_semicolon()
    
    def deviceblockgrammar(self):
        if self.currsymb.id == self.scanner.begin_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected begin keyword
            self.error_db.add_error('syntax', 'begin')
            self.skip_to_semicolon()


        if self.currsymb.id == self.scanner.devices_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected devices keyword
            self.error_db.add_error('syntax', 'devices')
            self.skip_to_semicolon()

        if self.currsymb.type == self.scanner.COLON:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected colon
            self.error_db.add_error('syntax', ':')
            self.skip_to_semicolon()
        
        while self.currsymb.id in self.device_ids:
            self.devicedefinitiongrammar()

        if self.currsymb.id == self.scanner.end_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected end keyword
            self.error_db.add_error('syntax', 'end')
            self.skip_to_semicolon()

        if self.currsymb.id == self.scanner.devices_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected devices keyword
            self.error_db.add_error('syntax', 'devices')
            self.skip_to_semicolon()

        if self.currsymb.type == self.scanner.SEMICOLON:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected semicolon
            self.error_db.add_error('syntax', ';')
            self.skip_to_semicolon()

    def BNAcodegrammar(self):

        self.deviceblockgrammar()

        self.connectionblockgrammar()

        if self.currsymb.id == self.scanner.begin_ID:
            self.monitorblockgrammar()


    def semantic_error_check(self):
        pass

    def parse_network(self):
        """Parse the circuit definition file."""
        self.currsymb = self.scanner.get_symbol()
        self.BNAcodegrammar()
        self.semantic_error_check()

        """ Note that currently, it correctly will allow 
         correct files to be run, but any erros in the file
         will be flagged as several unique errors """
        
