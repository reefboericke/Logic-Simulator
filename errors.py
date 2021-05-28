"""Store details of error encountered in BNA file.

Used by parser in the logic simular project; creates
error objects to track where encountered and their details.

Classes
-------
Error - stores details of an error including its type and location.
"""


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
    error_id: id of semantic error or string of what triggered syntax error.

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
            0: 'Invalid number of inputs to gate.',
            1: 'Invalid clock period.',
            2: 'Invalid intial switch value.',
            3: 'Incorrect number of arguments supplied for device.',
            4: 'Incorrect argument provided for gate.',
            5: 'Incorrect argument provided for clock.',
            6: 'Incorrect argument provided for switch.',
            7: 'Invalid device name.',
            8: 'Two devices assigned same name.',
            9: 'Left side of a connection must be an output.',
            10: 'Right side of a connection must be an input.',
            11: 'Output not specified DTYPE device.',
            12: 'Unexpected output specified for DTYPE device.',
            13: 'Invalid input name.',
            14: 'Multiple outputs connected to input.',
            15: 'All gate inputs must be connected.',
            16: 'No device with specified name.',
            17: 'Monitor already connected to specified device.'
        }

    def report(self):
        """Build error message for reporting via terminal or GUI."""
        error_text = ''
        error_text += self.error_type + \
            ' Error on line ' + self.location[0] + ':'
        if self.error_type == 'semantic':
            error_text += self.semantic_errors[self.error_id]
        elif self.error_type == 'syntax':
            error_text += 'Invalid syntax, expected "' + self.error_id + '"'
        error_text += '\n' + self.location[1] + '\n'
        for i in range(self.location[2]):
            error_text += ' '
        error_text += '^'
        print(error_text)
        return(error_text)

class Error_Store():

    def __init__(self, scanner):
        self.scanner = scanner

        self.errors = []
        self.no_errors = 0

    def add_error(self, error_type, error_id):
        loc = self.scanner.return_location()
        self.no_errors += 1
        new_error  = Error(self.no_errors, loc, error_type, error_id)
        self.errors.append(new_error)

        # move the file pointer onto next semicolon as current line contains error
        sym = self.scanner.get_symbol()
        while sym != self.scanner.SEMICOLON:
            sym = self.scanner.get_symbol()
        self.currsymb = self.scanner.get_symbol()

    def sort_errors(self):
        self.errors.sort(key=lambda e: e.location[0])

    def report_errors(self):
        total_error_text =''
        for error in self.errors:
            total_error_text += error.report() + '\n'
        return total_error_text


