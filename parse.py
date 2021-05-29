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
        self.error_recovery_mode = False
        self.device_ids = [self.scanner.CLOCK_ID, self.scanner.SWITCH_ID, 
         self.scanner.DTYPE_ID, self.scanner.AND_ID, self.scanner.NAND_ID,
         self.scanner.OR_ID, self.scanner.NOR_ID, self.scanner.XOR_ID]
        self.variable_ids = [self.scanner.inputs_ID, self.scanner.period_ID, 
         self.scanner.initial_ID]
        self.gates_with_inputs = [self.scanner.AND_ID, self.scanner.NOR_ID,
         self.scanner.NAND_ID]
        self.output_ids = [self.scanner.Q_ID, self.scanner.QBAR_ID]
        self.unique_names = []

    def error_recovery(self):
        while self.currsymb.type != self.scanner.SEMICOLON:
            self.currsymb = self.scanner.get_symbol()
        self.currsymb = self.scanner.get_symbol()
        self.error_recovery_mode = True


    def monitordefinitiongrammar(self):
        if self.currsymb.type == self.scanner.NAME:
            if self.names.get_name_string(self.currsymb.id) == None: 
                # check to see if monitor exists
                self.error_db.add_error('semantic', 16)
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected a name
            self.error_db.add_error('syntax', 'name')
            self.error_recovery()
            return

        if self.currsymb.type == self.scanner.SEMICOLON:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected semicolon
            self.error_db.add_error('syntax', ';')
            self.error_recovery()
            return

    def assignoutputgrammar(self):
        if self.currsymb.type == self.scanner.DOT:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected dot
            self.error_db.add_error('syntax', '.')
            self.error_recovery()
            return

        if self.currsymb.id in self.output_ids:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected Q / QBAR
            self.error_db.add_error('syntax', ['Q', 'QBAR'])
            self.error_recovery()
            return

    def connectiondefinitiongrammar(self):
        if self.currsymb.type == self.scanner.NAME:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected a name
            self.error_db.add_error('syntax', 'name')
            self.error_recovery()
            return

        if self.currsymb.type == self.scanner.DOT:
            self.assignoutputgrammar()
        if self.error_recovery_mode:
            return

        if self.currsymb.type == self.scanner.ARROW:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected an arrow
            self.error_db.add_error('syntax', ['.', '->'])
            self.error_recovery()
            return

        if self.currsymb.type == self.scanner.NAME:
            self.currsymb = self.scanner.get_symbol()
            # CHECK HERE IS AN INPUT
        else:
            # expected a name
            self.error_db.add_error('syntax', 'name')
            self.error_recovery()
            return

        if self.currsymb.type == self.scanner.DOT:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected dot
            self.error_db.add_error('syntax', '.')
            self.error_recovery()
            return

        if self.currsymb.type == self.scanner.NAME: # Can we refine this to only allow inputs?
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected a name
            self.error_db.add_error('syntax', 'name')
            self.error_recovery()
            return

        if self.currsymb.type == self.scanner.SEMICOLON:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected semicolon
            self.error_db.add_error('syntax', ';')
            self.error_recovery()
            return

    def assignvariablegrammar(self):
        if self.currsymb.type == self.scanner.COLON:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected a colon
            self.error_db.add_error('syntax', ':')
            self.error_recovery()
            return

        if self.currsymb.id in self.variable_ids:
            # check variable matches device
            if self.parsing_device.id == self.gates_with_inputs and self.currsymb.id != self.scanner.inputs_ID:
                self.error_db.add_error('semantic', 4)
            elif self.parsing_device.id == self.scanner.CLOCK_ID and self.currsymb.id != self.scanner.period_ID:
                self.error_db.add_error('semantic', 5)
            elif self.parsing_device.id == self.scanner.SWITCH_ID and self.currsymb.id != self.scanner.initial_ID:
                self.error_db.add_error('semantic', 6)
                
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected variable
            self.error_db.add_error('syntax', 'device variable')
            self.error_recovery()
            return
        
        if self.currsymb.type == self.scanner.EQUALS:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected an equals
            self.error_db.add_error('syntax', '=')
            self.error_recovery()
            return

        if self.currsymb.type == self.scanner.NUMBER:
            if (self.parsing_device.id == self.scanner.CLOCK_ID and int(self.currsymb.id) < 1):
                # clock has non-positive frequency
                self.error_db.add_error('semantic', 1)
            elif (self.parsing_device.id == self.scanner.SWITCH_ID and int(self.currsymb.id) not in [0,1]):
                # switch has invalid initial state
                self.error_db.add_error('semantic', 2)
            elif (self.parsing_device.id in self.gates_with_inputs and int(self.currsymb.id) not in range(1, 17, 1)):
                # incorrect number of inputs to gate
                self.error_db.add_error('semantic', 0)

            # checking for semantic errors therefore don't need to skip after error detection
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected a number
            self.error_db.add_error('syntax', 'number')
            self.error_recovery()
            return


    def devicedefinitiongrammar(self):
        if self.currsymb.id in self.device_ids:
            self.parsing_device = self.currsymb
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected a device keyword
            self.error_db.add_error('syntax', 'a device')
            self.error_recovery()
            return

        if self.currsymb.type == self.scanner.NAME:
            if self.currsymb.id in self.device_ids:
                # name is same as device type
                self.error_db.add_error('semantic', 7)
            if self.currsymb.id in self.unique_names: 
                # check to see if name is unique
                self.error_db.add_error('semantic', 8)
            self.unique_names.append(self.currsymb.id)
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected a name
            self.error_db.add_error('syntax', 'name')
            self.error_recovery()
            return

        if self.currsymb.type == self.scanner.COLON:
            self.assignvariablegrammar()
        if self.error_recovery_mode:
            return
        
        if self.currsymb.type == self.scanner.SEMICOLON:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected semicolon
            self.error_db.add_error('syntax', [':', ';'])
            self.error_recovery()
            return

    def monitorblockgrammar(self): 
        if self.currsymb.id == self.scanner.begin_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected begin keyword
            self.error_db.add_error('syntax', 'begin')
            self.error_recovery()
            return
    
        if self.currsymb.id == self.scanner.monitors_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected monitors keyword
            self.error_db.add_error('syntax', 'monitors')
            self.error_recovery()
            return

        if self.currsymb.type == self.scanner.COLON:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected colon 
            self.error_db.add_error('syntax', ':')
            self.error_recovery()
            return
        
        while self.currsymb.type == self.scanner.NAME:
            self.monitordefinitiongrammar()
            self.error_recovery_mode = False

        if self.currsymb.id == self.scanner.end_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected monitors keyword
            self.error_db.add_error('syntax', ['a name', 'end'])
            self.error_recovery()
            return

        if self.currsymb.id == self.scanner.monitors_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected monitors keyword
            self.error_db.add_error('syntax', 'monitors')
            self.error_recovery()
            return

        if self.currsymb.type == self.scanner.SEMICOLON:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected semicolon
            self.error_db.add_error('syntax', ';')
            self.error_recovery()
            return

    def connectionblockgrammar(self):
        if self.currsymb.id == self.scanner.begin_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected being keyword
            self.error_db.add_error('syntax', 'begin')
            self.error_recovery()
            return

        if self.currsymb.id == self.scanner.connections_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected connections keyword
            self.error_db.add_error('syntax', 'connections')
            self.error_recovery()
            return

        if self.currsymb.type == self.scanner.COLON:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected colon
            self.error_db.add_error('syntax', ':')
            self.error_recovery()
            return
        
        while self.currsymb.type == self.scanner.NAME:
            self.connectiondefinitiongrammar()
            self.error_recovery_mode = False

        if self.currsymb.id == self.scanner.end_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected end keyword
            self.error_db.add_error('syntax', ['a name', 'end'])
            self.error_recovery()
            return

        if self.currsymb.id == self.scanner.connections_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected connections keyword
            self.error_db.add_error('syntax', 'connections')
            self.error_recovery()
            return

        if self.currsymb.type == self.scanner.SEMICOLON:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected semicolon
            self.error_db.add_error('syntax', ';')
            self.error_recovery()
            return
    
    def deviceblockgrammar(self):
        if self.currsymb.id == self.scanner.begin_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected begin keyword
            self.error_db.add_error('syntax', 'begin')
            self.error_recovery()
            return

        if self.currsymb.id == self.scanner.devices_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected devices keyword
            self.error_db.add_error('syntax', 'devices')
            self.error_recovery()
            return

        if self.currsymb.type == self.scanner.COLON:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected colon
            self.error_db.add_error('syntax', ':')
            self.error_recovery()
            return
        
        while self.currsymb.id in self.device_ids:
            self.devicedefinitiongrammar()
            self.error_recovery_mode = False

        if self.currsymb.id == self.scanner.end_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected end keyword
            self.error_db.add_error('syntax', ['a device', 'end'])
            self.error_recovery()
            return

        if self.currsymb.id == self.scanner.devices_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected devices keyword
            self.error_db.add_error('syntax', 'devices')
            self.error_recovery()
            return

        if self.currsymb.type == self.scanner.SEMICOLON:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected semicolon
            self.error_db.add_error('syntax', ';')
            self.error_recovery()
            return

    def BNAcodegrammar(self):

        self.deviceblockgrammar()
        self.error_recovery_mode = False

        self.connectionblockgrammar()
        self.error_recovery_mode = False

        if self.currsymb.id == self.scanner.begin_ID:
            self.monitorblockgrammar()
            self.error_recovery_mode = False


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
        
