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
import re


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
        self.input_ids = [self.scanner.DATA_ID, self.scanner.CLK_ID,
         self.scanner.SET_ID, self.scanner.CLEAR_ID]
        self.unique_names = []
        self.monitored_devices = []

        [self.NO_ERROR, self.INVALID_QUALIFIER, self.NO_QUALIFIER,
         self.BAD_DEVICE, self.QUALIFIER_PRESENT,
         self.DEVICE_PRESENT] = self.names.unique_error_codes(6) # DO WE NEED THIS HERE?????

    def error_recovery(self):
        while self.currsymb.type != self.scanner.SEMICOLON:
            self.currsymb = self.scanner.get_symbol()
        self.currsymb = self.scanner.get_symbol()
        self.error_recovery_mode = True

    def encounter_error(self, type, id, recover):
        self.error_db.add_error(type, id)
        if recover:
            self.error_recovery()


    def monitordefinitiongrammar(self):
        if self.currsymb.type == self.scanner.NAME:
            if self.names.get_name_string(self.currsymb.id) == None: 
                # check to see if monitor exists
                self.encounter_error('semantic', 16, recover=False)
            if self.names.get_name_string(self.currsymb.id) in self.monitored_devices:
                # device already monitored
                self.encounter_error('semantic', 17, recover=False)
            parsing_device = self.names.get_name_string(self.currsymb.id)
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected a name
            self.encounter_error('syntax', 'name', recover=True)
            return

        if self.currsymb.type == self.scanner.SEMICOLON:
            self.currsymb = self.scanner.get_symbol()
            # monitor correctly parsed, add it to list
            self.monitors.get_monitor_signal(parsing_device, None)
            # Need to add way of changing None to Q for DTYPE
        else:
            # expected semicolon
            self.encounter_error('syntax', ';', recover=True)
            return

    def assignoutputgrammar(self):
        if self.currsymb.type == self.scanner.DOT:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected dot
            self.encounter_error('syntax', '.', recover=True)
            return

        if self.currsymb.id in self.output_ids:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected Q / QBAR
            self.encounter_error('syntax', ['Q', 'QBAR'], recover=True)
            return

    def connectiondefinitiongrammar(self):
        if self.currsymb.type == self.scanner.NAME:
            if self.currsymb.id not in self.unique_names:
                # device doesn't exist
                self.encounter_error('semantic', 18, recover=False)
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected a name
            self.encounter_error('syntax', 'name', recover=True)
            return

        if self.currsymb.type == self.scanner.DOT:
            self.assignoutputgrammar()
        if self.error_recovery_mode:
            return

        if self.currsymb.type == self.scanner.ARROW:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected an arrow
            self.encounter_error('syntax', ['.', '->'], recover=True)
            return

        if self.currsymb.type == self.scanner.NAME:
            if self.currsymb.id not in self.unique_names:
                # device doesn't exist
                self.encounter_error('semantic', 18, recover=False)
            currdeviceid = self.currsymb.id
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected a name
            self.encounter_error('syntax', 'name', recover=True)
            return

        if self.currsymb.type == self.scanner.DOT:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected dot
            self.encounter_error('syntax', '.', recover=True)
            return

        inp = self.names.get_name_string(self.currsymb.id)
        # Check that input name is within those allowed by EBNF:
        if (self.currsymb.id  in self.input_ids) or ( (inp[0] == 'I') and (inp[1:].isdigit())):
            # Fail semantic if DTYPE takes non-DTYPE inputs or vice versa
            if (((currdeviceid in self.devices.find_devices(self.devices.D_TYPE)) == 
             (self.currsymb.id not in self.input_ids))
             # or fail semantic if input number too high
             or ((currdeviceid not in self.devices.find_devices(self.devices.D_TYPE))
             and int(inp[1:]) > len(self.devices.get_device(currdeviceid).inputs))):
                self.encounter_error('semantic', 13, recover=False)

            self.currsymb = self.scanner.get_symbol()
        else:
            self.encounter_error('syntax', 'a valid input', recover=True)
            return

        if self.currsymb.type == self.scanner.SEMICOLON:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected semicolon
            self.encounter_error('syntax', ';', recover=True)
            return

    def assignvariablegrammar(self):
        if self.currsymb.type == self.scanner.COLON:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected a colon
            self.encounter_error('syntax', ':', recover=True)
            return

        if self.currsymb.id in self.variable_ids:
            # check variable matches device
            if self.parsing_device.id == self.gates_with_inputs and self.currsymb.id != self.scanner.inputs_ID:
                self.encounter_error('semantic', 4, recover=False)
            elif self.parsing_device.id == self.scanner.CLOCK_ID and self.currsymb.id != self.scanner.period_ID:
                self.encounter_error('semantic', 5, recover=False)
            elif self.parsing_device.id == self.scanner.SWITCH_ID and self.currsymb.id != self.scanner.initial_ID:
                self.encounter_error('semantic', 6, recover=False)
                
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected variable
            self.encounter_error('syntax', 'device variable', recover=True)
            return
        
        if self.currsymb.type == self.scanner.EQUALS:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected an equals
            self.encounter_error('syntax', '=', recover=True)
            return

        if self.currsymb.type == self.scanner.NUMBER:
            if (self.parsing_device.id == self.scanner.CLOCK_ID and int(self.currsymb.id) < 1):
                # clock has non-positive frequency
                self.encounter_error('semantic', 1, recover=False)
            elif (self.parsing_device.id == self.scanner.SWITCH_ID and int(self.currsymb.id) not in [0,1]):
                # switch has invalid initial state
                self.encounter_error('semantic', 2, recover=False)
            elif (self.parsing_device.id in self.gates_with_inputs and int(self.currsymb.id) not in range(1, 17, 1)):
                # incorrect number of inputs to gate
                self.encounter_error('semantic', 0, recover=False)
            else:
                self.variable_value = int(self.currsymb.id)
            # checking for semantic errors therefore don't need to skip after error detection
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected a number
            self.encounter_error('syntax', 'number', recover=True)
            return


    def devicedefinitiongrammar(self):
        if self.currsymb.id in self.device_ids:
            self.parsing_device = self.currsymb
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected a device keyword
            self.encounter_error('syntax', 'a device', recover=True)
            return

        if self.currsymb.type == self.scanner.NAME:
            if self.currsymb.id in self.device_ids:
                # name is same as device type
                self.encounter_error('semantic', 7, recover=False)
            if self.currsymb.id in self.unique_names: 
                # check to see if name is unique
                self.encounter_error('semantic', 8, recover=False)
            self.unique_names.append(self.currsymb.id)
            creating_name = self.currsymb
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected a name
            self.encounter_error('syntax', 'name', recover=True)
            return

        if self.currsymb.type == self.scanner.COLON:
            self.assignvariablegrammar()
        if self.error_recovery_mode:
            return
        
        if self.currsymb.type == self.scanner.SEMICOLON:
            # device definition correct therefore create with id from names
            err = self.devices.make_device(creating_name.id, 
                                           self.parsing_device.id,
                                           self.variable_value)
            self.variable_value = None
            if (err == self.DEVICE_PRESENT):
                self.encounter_error('semantic', 8, recover=False)

            self.currsymb = self.scanner.get_symbol()
        else:
            # expected semicolon
            self.encounter_error('syntax', [':', ';'], recover=True)
            return

    def monitorblockgrammar(self): 
        if self.currsymb.id == self.scanner.begin_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected begin keyword
            self.encounter_error('syntax', 'begin', recover=True)
            return
    
        if self.currsymb.id == self.scanner.monitors_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected monitors keyword
            self.encounter_error('syntax', 'monitors', recover=True)
            return

        if self.currsymb.type == self.scanner.COLON:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected colon 
            self.encounter_error('syntax', ':', recover=True)
            return
        
        while self.currsymb.type == self.scanner.NAME:
            self.monitordefinitiongrammar()
            self.error_recovery_mode = False

        if self.currsymb.id == self.scanner.end_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected monitors keyword
            self.encounter_error('syntax', ['a name', 'end'], recover=True)
            return

        if self.currsymb.id == self.scanner.monitors_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected monitors keyword
            self.encounter_error('syntax', 'monitors', recover=True)
            return

        if self.currsymb.type == self.scanner.SEMICOLON:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected semicolon
            self.encounter_error('syntax', ';', recover=True)
            return

    def connectionblockgrammar(self):
        if self.currsymb.id == self.scanner.begin_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected being keyword
            self.encounter_error('syntax', 'begin', recover=True)
            return

        if self.currsymb.id == self.scanner.connections_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected connections keyword
            self.encounter_error('syntax', 'connections', recover=True)
            return

        if self.currsymb.type == self.scanner.COLON:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected colon
            self.encounter_error('syntax', ':', recover=True)
            return
        
        while self.currsymb.type == self.scanner.NAME:
            self.connectiondefinitiongrammar()
            self.error_recovery_mode = False

        if self.currsymb.id == self.scanner.end_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected end keyword
            self.encounter_error('syntax', ['a name', 'end'], recover=True)
            return

        if self.currsymb.id == self.scanner.connections_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected connections keyword
            self.encounter_error('syntax', 'connections', recover=True)
            return

        if self.currsymb.type == self.scanner.SEMICOLON:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected semicolon
            self.encounter_error('syntax', ';', recover=True)
            return
    
    def deviceblockgrammar(self):
        if self.currsymb.id == self.scanner.begin_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected begin keyword
            self.encounter_error('syntax', 'begin', recover=True)
            return

        if self.currsymb.id == self.scanner.devices_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected devices keyword
            self.encounter_error('syntax', 'devices', recover=True)
            return

        if self.currsymb.type == self.scanner.COLON:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected colon
            self.encounter_error('syntax', ':', recover=True)
            return
        
        while self.currsymb.id in self.device_ids:
            self.devicedefinitiongrammar()
            self.error_recovery_mode = False

        if self.currsymb.id == self.scanner.end_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected end keyword
            self.encounter_error('syntax', ['a device', 'end'], recover=True)
            return

        if self.currsymb.id == self.scanner.devices_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected devices keyword
            self.encounter_error('syntax', 'devices', recover=True)
            return

        if self.currsymb.type == self.scanner.SEMICOLON:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected semicolon
            self.encounter_error('syntax', ';', recover=True)
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

        """ Current known issues:

        """
        
