class Error:

    def __init__(self, error_number, location, error_type, error_id, scanner):
        self.error_number = error_number
        self.location = location
        self.error_type = error_type
        self.error_id = error_id
        self.scanner = scanner

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
        error_text += self.error_type + ' Error on line ' + self.location[0] + ':'
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
        


    
    

