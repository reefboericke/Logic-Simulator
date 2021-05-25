"""Map variable names and string names to unique integers.

Used in the Logic Simulator project. Most of the modules in the project
use this module either directly or indirectly.

Classes
-------
Names - maps variable names and string names to unique integers.
"""


class Names:

    """Map variable names and string names to unique integers.

    This class deals with storing grammatical keywords and user-defined words,
    and their corresponding name IDs, which are internal indexing integers. It
    provides functions for looking up either the name ID or the name string.
    It also keeps track of the number of error codes defined by other classes,
    and allocates new, unique error codes on demand.

    Parameters
    ----------
    No parameters.

    Public methods
    -------------
    unique_error_codes(self, num_error_codes): Returns a list of unique integer
                                               error codes.

    query(self, name_string): Returns the corresponding name ID for the
                        name string. Returns None if the string is not present.

    lookup(self, name_string_list): Returns a list of name IDs for each
                        name string. Adds a name if not already present.

    get_name_string(self, name_id): Returns the corresponding name string for
                        the name ID. Returns None if the ID is not present.
    """

    def __init__(self):
        """Initialise names list."""

        # how many error codes have been declared
        self.error_code_count = 0
        # Declare the names list
        self.names_list = []

    def unique_error_codes(self, num_error_codes):
        """Return a list of unique integer error codes."""
        if not isinstance(num_error_codes, int):
            raise TypeError("Expected num_error_codes to be an integer.")
        self.error_code_count += num_error_codes
        return range(self.error_code_count - num_error_codes,
                     self.error_code_count)

    def query(self, name_string):
        """Return the corresponding name ID for name_string.

        If the name string is not present in the names list, return None.
        """

        # Check to make sure the name_string is string, raise error if false
        if type(name_string) != str:
            raise TypeError
        else:
            # Check if name_string has ID, return None if false, ID if true
            if name_string not in self.names_list:
                return None
            else:
                return self.names_list.index(name_string)

    def lookup(self, name_string_list):
        """Return a list of name IDs for each name string in name_string_list.

        If the name string is not present in the names list, add it.
        """

        # Initialise the output
        ID_list = []
        # Iterate through each name_string
        for name_string in name_string_list:
            # Check if name_string is string, raise error if false
            if type(name_string) != str:
                # TODO: Maybe add option to still print the list of valid IDs?
                raise TypeError
            else:
                # Check if name_string has ID, add to names_list if false
                if name_string not in self.names_list:
                    self.names_list.append(name_string)
                # Add ID to output
                ID_list.append(self.names_list.index(name_string))
        return ID_list

    def get_name_string(self, name_id):
        """Return the corresponding name string for name_id.

        If the name_id is not an index in the names list, return None.
        """

        # If a valid ID and in range, retun name_string
        if name_id in range(len(self.names_list)):
            return self.names_list[name_id]
        # If not valid, raise error
        elif type(name_id) != int:
            raise TypeError
        elif name_id < 0:
            raise ValueError
        # If valid but not in range, return None
        else:
            return None
