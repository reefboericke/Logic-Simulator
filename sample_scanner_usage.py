""" For testing usage of scanner before implementation of pytests. """

from scanner import Symbol
from scanner import Scanner
from names import Names
names = Names()

scanner = Scanner('test_BNA_file.txt', names)

while (True):
    sym = scanner.get_symbol()
    #print(sym.type)
    #print(sym.id)
    #print(names.get_name_string((sym.id)))