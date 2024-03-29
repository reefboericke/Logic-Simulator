"""Read the circuit definition file and translate the characters into symbols.

Used in the Logic Simulator project to read the characters in the definition
file and translate them into symbols that are usable by the parser.

Classes
-------
Scanner - reads definition file and translates characters into symbols.
Symbol - encapsulates a symbol and stores its properties.
"""


import linecache
import os


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
    advance(self): Moves file pointer opened in init function on by one
                   character.

    skip_spaces_and_comments(self): Moves onwards until current_character
                                    has first non-whitespace, non-comment
                                    character.

    get_name(self): Returns next name from file, provided current char
                    is a letter.

    get_number(self): Returns next sequence of numbers from file. Assumes
                      file pointer starts on a number.

    get_symbol(self): Scans through the file to return to the next
                      identifiable symbol, stored in the Symbol object,
                      including it's index and type.

    return_location(self): Return location of scanner within file such
                           that error messages can report useful info
                           to the user.
    """

    def __init__(self, path, names):
        """Open specified file and initialise reserved words and IDs."""
        self.path = path
        self.names = names
        self.symbol_type_list = [self.SEMICOLON, self.COLON, self.EQUALS,
                                 self.DOT, self.KEYWORD, self.NUMBER,
                                 self.NAME, self.EOF, self.ARROW,
                                 self.UNEXPECTED] = range(10)
        self.keywords_list = ["begin", "end", "devices", "connections",
                              "monitors", "OR", "NAND", "AND", "NOR",
                              "XOR", "CLOCK", "SWITCH", "DTYPE",
                              "DATA", "CLK", "SET", "CLEAR", "Q",
                              "QBAR", "inputs", "period", "initial",
                              "SIGGEN", "waveform"]

        [self.begin_ID, self.end_ID, self.devices_ID, self.connections_ID,
         self.monitors_ID, self.OR_ID, self.NAND_ID, self.AND_ID,
         self.NOR_ID, self.XOR_ID, self.CLOCK_ID, self.SWITCH_ID,
         self.DTYPE_ID, self.DATA_ID, self.CLK_ID, self.SET_ID,
         self.CLEAR_ID, self.Q_ID, self.QBAR_ID, self.inputs_ID,
         self.period_ID, self.initial_ID, self.SIGGEN_ID,
         self.waveform_ID] = self.names.lookup(self.keywords_list)

        # define variables needed to track where in file
        self.current_character = ""
        self.no_EOL = 1
        self.start_of_file = True
        self.current_char_num_terminal = 0
        self.current_char_num_txt = 0
        self.char_num_last_EOL_terminal = 0
        self.char_num_last_EOL_txt = 0

        # open file
        try:
            self.file = open(path, 'r')
            if (path[-4:] != '.bna'):
                print("Please provide a file with the .bna extension.")
                quit()
            if os.stat(path).st_size == 0:
                print("Please provide a non-empty file.")
                quit()
        except FileNotFoundError:
            print("Cannot find file - please check provided path.")
            quit()

        # perform pass through to check all comments closed
        start_of_file = self.file.tell()
        full_text = self.file.read()
        hashes = 0
        for char in full_text:
            if char == '#':
                hashes += 1
        self.unclosed_comment = False
        if hashes % 2 != 0:
            self.unclosed_comment = True
        self.file.seek(start_of_file)

        self.advance()

    def advance(self):
        """Move file pointer on by one character.

        Reassigns current_character variable.
        """
        self.current_character = self.file.read(1)
        if ((len(self.current_character) == 1 and
             ord(self.current_character) == 9)):
            self.current_char_num_terminal += 8
            self.current_char_num_txt += 4
        else:
            self.current_char_num_terminal += 1
            self.current_char_num_txt += 1

    def skip_spaces_and_comments(self):
        """Pass file pointer over white-space characters and comments."""
        self.inside_comment = False
        while(True):
            if self.current_character.isspace():
                if self.current_character == '\n':
                    self.last_EOL = self.file.tell()
                    self.char_num_last_EOL_txt = self.current_char_num_txt
                    self.char_num_last_EOL_terminal = \
                        self.current_char_num_terminal
                    self.no_EOL += 1
                self.advance()
            elif self.current_character == '#':  # enter / leave comment
                if self.inside_comment is False:  # enter comment
                    self.inside_comment = True
                else:  # end of comment
                    self.inside_comment = False
                self.advance()
            elif self.inside_comment is True:
                self.advance()
            else:
                break
        # current_character now contains non-whitespace and non-comment

    def get_name(self):
        """Return next name from opened file.

        Pointer needs to be at start of name.
        """
        name = ''
        while(self.current_character.isalnum() or
              self.current_character == '_'):
            name = name + self.current_character
            self.advance()
        return name

    def get_number(self):
        """Return next number from opened file.

        Pointer needs to be at start of a number.
        """
        number = ''
        while(self.current_character.isdigit()):
            number += self.current_character
            self.advance()
        # current_character now contains first non-num char
        self.check_point = self.file
        if self.current_character == '.':
            pos = self.file.tell()
            self.advance()
            if (self.current_character.isdigit()):
                # fractional number found
                return None
            else:
                # dot was an error so backtrack
                self.file.seek(pos)
                self.current_char_num_txt -= 1
                self.current_char_num_terminal -= 1

        return number

    def get_symbol(self):
        """Translate next sequence of characters into a symbol."""
        symbol = Symbol()
        self.skip_spaces_and_comments()

        if self.current_character.isalpha():
            name_string = self.get_name()
            if name_string in self.keywords_list:
                symbol.type = self.KEYWORD
            else:
                symbol.type = self.NAME
            [symbol.id] = self.names.lookup([name_string])

        elif self.current_character.isdigit():  # number
            symbol.id = self.get_number()
            if symbol.id is None:
                # non-int found
                symbol.type = self.UNEXPECTED
                symbol.id = self.current_character
            else:
                symbol.type = self.NUMBER

        elif self.current_character == "=":  # punctuation
            symbol.type = self.EQUALS
            self.advance()

        elif self.current_character == "-":
            self.advance()
            if self.current_character == ">":  # -> found
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

        elif self.current_character == "":  # end of file
            symbol.type = self.EOF
            self.file.close()  # close file to avoid corruption

        else:  # not a known character, pass processing onto parser
            symbol.type = self.UNEXPECTED
            symbol.id = self.current_character
            self.advance()

        return symbol

    def return_location(self):
        """Return details of scanner's location in file for error reporting."""
        no_spaces_txt = (self.current_char_num_txt
                         - self.char_num_last_EOL_txt - 2)
        no_spaces_terminal = (self.current_char_num_terminal
                              - self.char_num_last_EOL_terminal - 2)
        line = linecache.getline(self.path, self.no_EOL)
        location = (self.no_EOL, line, no_spaces_terminal, no_spaces_txt)
        return(location)
