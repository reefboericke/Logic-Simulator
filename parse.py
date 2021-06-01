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
        self.network_construction = True
        self.curroutputid = None
        self.currvariablevalue = None
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
        self.network_construction = False


    def monitordefinitiongrammar(self):
        if self.currsymb.type == self.scanner.NAME:
            currdevicenameid = self.currsymb.id
            if self.devices.get_device( currdevicenameid) == None:
                self.encounter_error('semantic', 16, recover=False)
            if self.names.get_name_string(currdevicenameid) in self.monitors.get_signal_names()[0]:
                # device already monitored
                self.encounter_error('semantic', 17, recover=False)
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected a name
            self.encounter_error('syntax', 0, recover=True)
            return

        if self.currsymb.type == self.scanner.SEMICOLON:
            self.currsymb = self.scanner.get_symbol()
            # monitor correctly parsed, add it to list
            if self.devices.get_device(currdevicenameid) != None:
                if self.devices.get_device(currdevicenameid).device_kind == self.devices.D_TYPE:
                    self.monitors.make_monitor(currdevicenameid, self.scanner.Q_ID)
                else:
                    self.monitors.make_monitor(currdevicenameid, None)
        else:
            # expected semicolon
            self.encounter_error('syntax', 1, recover=True)
            return

    def assignoutputgrammar(self):
        if self.currsymb.type == self.scanner.DOT:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected dot
            self.encounter_error('syntax', 2, recover=True)
            return

        if self.currsymb.id in self.output_ids:
            self.curroutputid = self.currsymb.id
            if (self.devices.get_device(self.currdevicenameid1) != None 
             and self.devices.get_device(self.currdevicenameid1).device_kind != self.devices.D_TYPE):
                self.encounter_error('semantic', 12, recover=False)
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected Q / QBAR
            self.encounter_error('syntax', 3, recover=True)
            return

    def connectiondefinitiongrammar(self):
        if self.currsymb.type == self.scanner.NAME:
            self.currdevicenameid1 = self.currsymb.id
            if self.devices.get_device(self.currdevicenameid1) == None:
                self.encounter_error('semantic', 16, recover=False)
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected a name
            self.encounter_error('syntax', 0, recover=True)
            return

        if self.currsymb.type == self.scanner.DOT:
            self.assignoutputgrammar()
        elif (self.devices.get_device(self.currdevicenameid1) != None 
             and self.devices.get_device(self.currdevicenameid1).device_kind == self.devices.D_TYPE):
            self.encounter_error('semantic', 11, recover=False)
        if self.error_recovery_mode:
            return

        if self.currsymb.type == self.scanner.ARROW:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected an arrow
            self.encounter_error('syntax', 4, recover=True)
            return

        if self.currsymb.type == self.scanner.NAME:
            currdevicenameid2 = self.currsymb.id
            if self.devices.get_device(currdevicenameid2) == None:
                self.encounter_error('semantic', 16, recover=False)

            self.currsymb = self.scanner.get_symbol()
        else:
            # expected a name
            self.encounter_error('syntax', 0, recover=True)
            return

        if self.currsymb.type == self.scanner.DOT:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected dot
            self.encounter_error('syntax', 2, recover=True)
            return

        inp = self.names.get_name_string(self.currsymb.id)
        # Check that input name is within those allowed by EBNF:
        if (self.currsymb.id  in self.input_ids) or ( (inp[0] == 'I') and (inp[1:].isdigit())):
            if ((self.devices.get_device(currdevicenameid2) != None )
             and (self.currsymb.id not in self.devices.get_device(currdevicenameid2).inputs)):
                self.encounter_error('semantic', 13, recover=False)
            currinputid = self.currsymb.id
            self.currsymb = self.scanner.get_symbol()
        else:
            self.encounter_error('syntax', 5, recover=True)
            return

        if self.currsymb.type == self.scanner.SEMICOLON:
            self.currsymb = self.scanner.get_symbol()
            # connection correctly parsed, if semantically correct, add to network:
            if self.network_construction:
                self.network.make_connection(self.currdevicenameid1, self.curroutputid, 
                                             currdevicenameid2, currinputid)
                self.curroutputid = None
        else:
            # expected semicolon
            self.encounter_error('syntax', 1, recover=True)
            return

    def assignvariablegrammar(self):
        if self.currsymb.type == self.scanner.COLON:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected a colon
            self.encounter_error('syntax', 6, recover=True)
            return

        if self.currsymb.id in self.variable_ids:
            # check variable matches device
            if self.currdevicetypeid in self.gates_with_inputs and self.currsymb.id != self.scanner.inputs_ID:
                self.encounter_error('semantic', 4, recover=False)
            elif self.currdevicetypeid == self.scanner.CLOCK_ID and self.currsymb.id != self.scanner.period_ID:
                self.encounter_error('semantic', 5, recover=False)
            elif self.currdevicetypeid == self.scanner.SWITCH_ID and self.currsymb.id != self.scanner.initial_ID:
                self.encounter_error('semantic', 6, recover=False)

            self.currsymb = self.scanner.get_symbol()
        else:
            # expected variable
            self.encounter_error('syntax', 7, recover=True)
            return
        
        if self.currsymb.type == self.scanner.EQUALS:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected an equals
            self.encounter_error('syntax', 8, recover=True)
            return

        if self.currsymb.type == self.scanner.NUMBER:
            if (self.currdevicetypeid == self.scanner.CLOCK_ID and int(self.currsymb.id) < 1):
                # clock has non-positive frequency
                self.encounter_error('semantic', 1, recover=False)
            elif (self.currdevicetypeid == self.scanner.SWITCH_ID and int(self.currsymb.id) not in [0,1]):
                # switch has invalid initial state
                self.encounter_error('semantic', 2, recover=False)
            elif (self.currdevicetypeid in self.gates_with_inputs and int(self.currsymb.id) not in range(1, 17, 1)):
                # incorrect number of inputs to gate
                self.encounter_error('semantic', 0, recover=False)
            else:
                self.currvariablevalue = int(self.currsymb.id)
            # checking for semantic errors therefore don't need to skip after error detection
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected a number
            self.encounter_error('syntax', 9, recover=True)
            return


    def devicedefinitiongrammar(self):
        if self.currsymb.id in self.device_ids:
            self.network_construction = True
            self.currdevicetypeid = self.currsymb.id
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected a device keyword
            self.encounter_error('syntax', 10, recover=True)
            return

        if self.currsymb.type == self.scanner.NAME:
            if self.currsymb.id in self.device_ids:
                # name is same as device type
                self.encounter_error('semantic', 7, recover=False)
            if self.currsymb.id in self.unique_names: 
                # check to see if name is unique
                self.encounter_error('semantic', 8, recover=False)
            self.unique_names.append(self.currsymb.id)
            currdevicenameid = self.currsymb.id
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected a name
            self.encounter_error('syntax', 0, recover=True)
            return

        if self.currsymb.type == self.scanner.COLON:
            if self.currdevicetypeid in [self.scanner.DTYPE_ID, self.scanner.XOR_ID]:
                self.encounter_error('semantic', 3, recover=False)
            self.assignvariablegrammar()
        elif self.currdevicetypeid not in [self.scanner.DTYPE_ID, self.scanner.XOR_ID]:
            self.encounter_error('semantic', 3, recover=False)
        if self.error_recovery_mode:
            return
        
        if self.currsymb.type == self.scanner.SEMICOLON:
            # device definition correct therefore create with id from names
            if self.network_construction == True:
                self.devices.make_device(currdevicenameid, self.currdevicetypeid,
                                     self.currvariablevalue)
            self.currvariablevalue = None
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected semicolon
            self.encounter_error('syntax', 11, recover=True)
            return

    def monitorblockgrammar(self): 
        if self.currsymb.id == self.scanner.begin_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected begin keyword
            self.encounter_error('syntax', 12, recover=True)
            return
    
        if self.currsymb.id == self.scanner.monitors_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected monitors keyword
            self.encounter_error('syntax', 13, recover=True)
            return

        if self.currsymb.type == self.scanner.COLON:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected colon 
            self.encounter_error('syntax', 6, recover=True)
            return
        
        while self.currsymb.type == self.scanner.NAME:
            self.monitordefinitiongrammar()
            self.error_recovery_mode = False

        if self.currsymb.id == self.scanner.end_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected monitors keyword
            self.encounter_error('syntax', 14, recover=True)
            return

        if self.currsymb.id == self.scanner.monitors_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected monitors keyword
            self.encounter_error('syntax', 13, recover=True)
            return

        if self.currsymb.type == self.scanner.SEMICOLON:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected semicolon
            self.encounter_error('syntax', 1, recover=True)
            return

    def connectionblockgrammar(self):
        if self.currsymb.id == self.scanner.begin_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected being keyword
            self.encounter_error('syntax', 12, recover=True)
            return

        if self.currsymb.id == self.scanner.connections_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected connections keyword
            self.encounter_error('syntax', 16, recover=True)
            return

        if self.currsymb.type == self.scanner.COLON:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected colon
            self.encounter_error('syntax', 6, recover=True)
            return
        
        while self.currsymb.type == self.scanner.NAME:
            self.connectiondefinitiongrammar()
            self.error_recovery_mode = False

        if self.currsymb.id == self.scanner.end_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected end keyword
            self.encounter_error('syntax', 14, recover=True)
            return

        if self.currsymb.id == self.scanner.connections_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected connections keyword
            self.encounter_error('syntax', 16, recover=True)
            return

        if self.currsymb.type == self.scanner.SEMICOLON:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected semicolon
            self.encounter_error('syntax', 1, recover=True)
            return
    
    def deviceblockgrammar(self):
        if self.currsymb.id == self.scanner.begin_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected begin keyword
            self.encounter_error('syntax', 12, recover=True)
            return

        if self.currsymb.id == self.scanner.devices_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected devices keyword
            self.encounter_error('syntax', 17, recover=True)
            return

        if self.currsymb.type == self.scanner.COLON:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected colon
            self.encounter_error('syntax', 6, recover=True)
            return
        
        while self.currsymb.id in self.device_ids:
            self.devicedefinitiongrammar()
            self.error_recovery_mode = False

        if self.currsymb.id == self.scanner.end_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected end keyword
            self.encounter_error('syntax', 18, recover=True)
            return

        if self.currsymb.id == self.scanner.devices_ID:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected devices keyword
            self.encounter_error('syntax', 17, recover=True)
            return

        if self.currsymb.type == self.scanner.SEMICOLON:
            self.currsymb = self.scanner.get_symbol()
        else:
            # expected semicolon
            self.encounter_error('syntax', 1, recover=True)
            return

    def BNAcodegrammar(self):

        self.deviceblockgrammar()
        self.error_recovery_mode = False

        self.connectionblockgrammar()
        self.error_recovery_mode = False

        if self.currsymb.id == self.scanner.begin_ID:
            self.monitorblockgrammar()
            self.error_recovery_mode = False

    def parse_network(self):
        """Parse the circuit definition file."""
        self.currsymb = self.scanner.get_symbol()
        self.BNAcodegrammar()

        if not self.error_db.report_errors():
            return True
        return False

        """ Note that currently, it correctly will allow 
         correct files to be run, but any erros in the file
         will be flagged as several unique errors """

        """ Current known issues:
        1: If a device isn't initialised, we don't want to come up in semantic checks later
        """
        
