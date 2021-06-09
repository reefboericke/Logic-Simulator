"""Store details of errors encountered in BNA file.

Used by parser in the logic simular project; creates
various error objects to track where encountered and their details.

Classes
-------
Error - stores details of an error including its type and location.
Error_Store - maintains database of errors, providing reporting and
              interfacing.
"""
import gettext
import wx
_ = wx.GetTranslation


class Error:
    """Store details of an error including type and location.

    Errors are found by the parser as it sequentially recieves symbols from
    the scanner and checks them against the BNA EBNF and semantic constraints.
    The error object captures the details of the type of error and where the
    scanner says it occurred.

    Parameters
    ----------
    error_number: unique number identifying this specific error.
    location: touple containing (line number of error, text of this line,
              number of spaces to error). These details returned by
              call to scanner.return_location().
    error_type: string of either 'syntax' or 'semantic'.
    error_id: id of error according to dictionaries in __init__ .

    Public methods
    --------------
    report(self): Prints and returns the relevant error message given
                  attributes of the error object.
    """

    def __init__(self, error_number, location, error_type, error_id):
        """Intialise constants and error table."""
        self.error_number = error_number
        self.location = location
        self.error_type = error_type
        self.error_id = error_id

        self.semantic_errors = {
            0: _('Invalid number of inputs to gate.'),
            1: _('Invalid clock period.'),
            2: _('Invalid initial switch value.'),
            3: _('Incorrect number of arguments supplied for device.'),
            4: _('Incorrect argument provided for gate.'),
            5: _('Incorrect argument provided for clock.'),
            6: _('Incorrect argument provided for switch.'),
            7: _('Invalid device name.'),
            8: _('Two devices assigned same name.'),
            9: _('Left side of a connection must be an output.'),
            10: _('Right side of a connection must be an input.'),
            11: _('Output not specified DTYPE device.'),
            12: _('Unexpected output specified for non-DTYPE device.'),
            13: _('Invalid input name for device.'),
            14: _('Multiple outputs connected to input.'),
            15: _('All gate inputs must be connected.'),
            16: _('No device with specified name.'),
            17: _('Monitor already connected to specified device.'),
            18: _('Specified device doesn\'t exist.')
        }

        self.syntax_errors = {
            0: _('name'),
            1: '";"',  # for monitors and connections
            2: '"."',
            3: ['"Q"', '"QBAR"'],
            4: ['"."', '"->"'],
            5: _('a valid input'),
            6: '":"',
            7: _('device variable'),
            8: '"="',
            9: _('non-negative integer'),
            10: _('a device'),
            11: ['":"', '";"'],  # for devices
            12: _('"begin"'),
            13: _('"monitors"'),
            14: [_('a name'), _('"end"')],
            15: '"->"',
            16: _('"connections"'),
            17: _('"devices"'),
            18: [_('a device'), _('"end"')],
            19: '#',
            20: _('more than just a comment')
        }

    def report(self):
        """Build error message for reporting via terminal or GUI."""
        error_text = ''
        error_text += _(self.error_type.capitalize()) + \
            _(' Error on line ') + str(self.location[0]) + ':'
        if self.error_type == 'semantic':
            specific_error_text = self.semantic_errors[self.error_id]
            error_text += ' ' + specific_error_text
        elif self.error_type == 'syntax':
            specific_error_text = self.syntax_errors[self.error_id]
            error_text += _(' Invalid syntax, expected ')
            if type(specific_error_text) == str:
                error_text += specific_error_text + ':'
            else:  # expect a list now
                for i in range(len(specific_error_text)):
                    if i == (len(specific_error_text) - 1):
                        error_text += specific_error_text[i]
                    else:
                        error_text += specific_error_text[i] + _(' or ')
                error_text += ' :'

        error_text += '\n\n' + str(self.location[1])
        error_text_terminal = error_text
        error_text_txt = error_text
        error_text_gui = error_text
        for i in range(self.location[2]):
            error_text_terminal += ' '
        error_text_terminal += '^'
        for i in range(self.location[3]):
            error_text_txt += ' '
        error_text_txt += '^'

        if self.error_type == 'semantic' and self.error_id == 15:
            msg = _('Semantic Error in file: All inputs must be connected.')
            error_text_txt = msg
            error_text_terminal = msg
            error_text_gui = msg

        if self.error_type == 'syntax' and self.error_id == 19:
            msg = _('Syntax error in file: Comment has not been closed.')
            error_text_txt = msg
            error_text_terminal = msg
            error_text_gui = msg

        return [error_text_terminal, error_text_txt, error_text_gui]


class Error_Store():
    """Store all errors encountered by parser.

    As parser finds errors, calls method of this object
    to add the type of error it has found. Utilises passed
    scanner to infer the location and tag the error with this.

    Parameters
    ----------
    scanner: Instance of scanner class being used by simulator.

    Public methods
    --------------
    add_error(self, error_type, error_id): adds new error to error
                                           list, given input
                                           arguments to the method.
    sort_errors(self): sorts errors in list by their line number.
    query_semantics(self, desired_type): returns number of semantic
                                         errors of id equal to
                                         desired_type.
    query_syntax(self, desired_type): returns number of syntax
                                      errors of id equal to
                                      desired_type.
    report_errors(self, command_line, file_output): returns full text
                                                    of all errors in
                                                    program and their
                                                    details.
    """

    def __init__(self, scanner):
        """Initialise variables."""
        self.scanner = scanner
        self.errors = []
        self.no_errors = 0

    def add_error(self, error_type, error_id):
        """Add new error to error list."""
        loc = self.scanner.return_location()
        self.no_errors += 1
        new_error = Error(self.no_errors, loc, error_type, error_id)
        self.errors.append(new_error)

    def sort_errors(self):
        """Sort errors by line number."""
        self.errors.sort(key=lambda e: e.location[0])

    def query_semantics(self, desired_type):
        """Return number of semantic errors of certain type."""
        count = 0
        for error in self.errors:
            if error.error_type == 'semantic':
                if error.error_id == desired_type:
                    count += 1
        return count

    def query_syntax(self, desired_type):
        """Return number of syntax errors of certain type."""
        count = 0
        for error in self.errors:
            if error.error_type == 'syntax':
                if error.error_id == desired_type:
                    count += 1
        return count

    def report_errors(self, command_line=True, file_output=True):
        """Build full error text of entire BNA file."""
        if self.no_errors == 0:
            return False
        else:
            self.sort_errors()
            total_error_text_terminal = '\n'
            total_error_text_txt = '\n'
            total_error_text_gui = '\n'
            for error in self.errors:
                total_error_text_terminal += error.report()[0] + '\n\n'
                total_error_text_txt += error.report()[1] + '\n\n'
                total_error_text_gui += error.report()[2] + '\n\n'
            if command_line:
                print(total_error_text_terminal)
            if file_output:
                output_file = open('error_report.txt', 'w')
                output_file.write(total_error_text_txt)
            return total_error_text_gui
