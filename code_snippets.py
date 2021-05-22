""" for keeping different implementations of functions in case decide to use them again """

"""
while( self.current_character.isspace() ):
    if self.current_character == '\n':
        self.last_EOL = self.file.tell()
        self.no_EOL += 1
    self.advance()
"""

""" 
if self.current_character == '#':  # comment found
    self.advance()
    while self.current_character != '#':
        self.advance()
    self.advance()
    self.get_symbol()
"""