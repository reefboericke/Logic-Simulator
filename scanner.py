"""Read the circuit definition file and translate the characters into symbols.

Used in the Logic Simulator project to read the characters in the definition
file and translate them into symbols that are usable by the parser.

Classes
-------
Scanner - reads definition file and translates characters into symbols.
Symbol - encapsulates a symbol and stores its properties.
"""


class Symbol:

    """Encapsulate a symbol and store its properties.

    Parameters
    ----------
    No parameters.

    Public methods
    --------------
    No public methods.
    """

    def __init__(self):
        """Initialise symbol properties."""
        self.type = None
        self.id = None


class Scanner:

    """Read circuit definition file and translate the characters into symbols.

    Once supplied with the path to a valid definition file, the scanner
    translates the sequence of characters in the definition file into symbols
    that the parser can use. It also skips over comments and irrelevant
    formatting characters, such as spaces and line breaks.

    Parameters
    ----------
    path: path to the circuit definition file.
    names: instance of the names.Names() class.

    Public methods
    -------------
    advance(self): Moves file pointer opened in init function on by one character.

    skip_spaces_and_comments(self): Moves onwards until current_character has first non-whitespace, non-comment character.

    get_word(self): Returns next combination of alphanumeric characters separated by whitespace.

    get_name(self): Returns next name from file, accounting for two-word names that start BNA logic blocks.

    get_number(self): Returns next sequence of numbers from file. Assumes file pointer starts on a number.

    get_symbol(self): Scans through the file to return to the next identifiable symbol,
                      stored in the Symbol object, including it's index and type.

    output_error_line(self, error_code, error_index=False): Prints out to terminal the current line the scanner is on,
                                                            and an arrow to the current location of the file pointer. Used
                                                            for when an error has been detected and grabs correct error message
                                                            according to error_code.
    """

    def __init__(self, path, names):
        """Open specified file and initialise reserved words and IDs."""
        self.path = path
        self.names = names
        self.symbol_type_list = [self.SEMICOLON, self.COLON, self.EQUALS, self.DOT,
        self.KEYWORD, self.NUMBER, self.NAME, self.EOF, self.ARROW] = range(9)
        self.keywords_list = ["begindevices", "enddevices", "beginconnections", "endconnections",
                "beginmonitors", "endmonitors", "NAND", "AND", "NOR", "XOR", "CLOCK", "SWITCH",
                "DTYPE", "DATA", "CLK", "SET", "CLEAR", "inputs", "period", "intial"]
        [self.begindevices_ID, self.enddevices_ID, self.beginconnections_ID, self.endconnections_ID,
            self.beginmonitors_ID, self.endmonitors_ID, self.NAND_ID, self.AND_ID, self.NOR_ID,
            self.XOR_ID, self.SWITCH_ID, self.DTYPE_ID, self.DATA_ID, self.CLK_ID, self.SET_ID, self.CLEAR_ID,
            self.period_ID, self.initial_ID] = self.names.lookup(self.keywords_list)
        self.current_character = ""
        self.no_EOL = 0
        # open file
        try:
            self.file = open(path, 'r')
        except FileNotFoundError:
            print("Incorrect file - check provided path!")
            sys.exit()
    
    def advance(self):
        """Moves file pointer on by one character and assigns to current_character variable."""
        self.current_character = self.file.read(1)
    
    def skip_spaces_and_comments(self):
        """Passes the file pointer over white-space characters and comments, whilst tracking where the last EOL is."""
        self.advance()
        inside_comment = False
        while( True ):
            if self.current_character.isspace():
                if self.current_character == '\n':
                    self.last_EOL = self.file.tell()
                    self.no_EOL += 1
                self.advance()
            elif self.current_character == '#': # enter / leave comment
                if inside_comment is False:  # enter comment
                    inside_comment = True
                else:  # end of comment
                    inside_comment = False
                self.advance()
            elif inside_comment is True:
                self.advance()
            else:
                break
        # current_character now contains non-whitespace and non-comment

    def get_word(self):
        """Returns next word (alphanumeric characters between whitespace) when called. Assumes current_character is a letter."""
        word = ''
        while(self.current_character.isalnum()):
            word += self.current_character
            self.advance()
        # current_character now contains first non-alnum char
        return word

    def get_name(self):
        """Returns the next name from the opened file, checking if it's single or two word."""
        name = self.get_word()
        if (name in ['begin', 'end']):  # could be two word name
            pos_pre_check = self.file.tell() 
            self.skip_spaces_and_comments()
            next_word = self.get_word()
            if (next_word in ['devices', 'monitors', 'connections']):  # two word name found
                name = name + next_word
            else:  # not a two word name and need to go back
                self.file.seek(pos_pre_check)
        return name

    def get_number(self):
        """Returns next number from opened file, provided pointer currently at start of a number."""
        number = ''
        while(self.current_character.isnum()):
            number += self.current_character
            self.advance()
        # current_character now contains first non-num char
        return number

    def get_symbol(self):
        """Translate the next sequence of characters into a symbol."""
        symbol = Symbol()
        self.skip_spaces_and_comments() 

        if self.current_character.isalpha():
            name_string = self.get_name()
            if name_string in self.keywords_list:
                symbol.type = self.KEYWORD
            else:
                symbol.type = self.NAME
            [symbol.id] = self.names.lookup([name_string])

        elif self.current_character.isdigit(): # number
            symbol.id = self.get_number()
            symbol.type = self.NUMBER

        elif self.current_character == "=": # punctuation
            symbol.type = self.EQUALS
            self.advance()

        elif self.current_character == "->":
            symbol.type = self.ARROW
            self.advance()

        elif self.current_character == ":":
            symbol.type = self.COLON
            self.advance()

        elif self.current_character == ";":
            symbol.type = self.SEMICOLON
            self.advance()

        elif self.current_character == ".":
            symbol.type = self.DOT
            self.advance()

        elif self.current_character == "": # end of file
            symbol.type = self.EOF

        else: # not a valid character
            self.advance()

        return symbol

    def output_error_line(self, error_code, error_index=False):
        """Outputs current line and arrow to indicate location of file pointer. Called when parser detects a syntax error."""
        if error_index is False: # no provided index, default to current position
            error_index = self.file.tell()
        current_line = linecache.getline(self.path, self.no_EOL)
        print(current_line)
        no_spaces = error_index - self.last_EOL
        for i in range(no_spaces):
            print(" ", end='')
        print("^\n")


        
