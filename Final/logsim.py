#!/usr/bin/env python3
"""Parse command line options and arguments for the Logic Simulator.

This script parses options and arguments specified on the command line, and
runs either the command line user interface or the graphical user interface.

Usage
-----
Show help: logsim.py -h
Command line user interface: logsim.py -c <file path>
Graphical user interface: logsim.py <file path>
"""
import getopt
from os import error
import os
import sys
import linecache

import wx
from wx.core import LANGUAGE_GERMAN

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser
from userint import UserInterface
from gui import Gui
from errors import Error_Store
from internationalization import set_language
import wx
import builtins
# _ = wx.GetTranslation


def main(arg_list):
    """Parse the command line options and arguments specified in arg_list.

    Run either the command line user interface, the graphical user interface,
    or display the usage message.
    """
    usage_message = ("Usage:\n"
                     "Show help: logsim.py -h\n"
                     "Command line user interface: logsim.py -c <file path>\n"
                     "Graphical user interface: logsim.py <file path>")
    try:
        options, arguments = getopt.getopt(arg_list, "hc:")
    except getopt.GetoptError:
        print("Error: invalid command line arguments\n")
        print(usage_message)
        sys.exit()

    # Initialise instances of the four inner simulator classes
    names = Names()
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    # names = None
    # devices = None
    # network = None
    # monitors = None

    for option, path in options:
        if option == "-h":  # print the usage message
            print(usage_message)
            sys.exit()
        elif option == "-c":  # use the command line user interface
            scanner = Scanner(path, names)
            error_db = Error_Store(scanner)
            parser = Parser(names, devices, network,
                            monitors, scanner, error_db)
            if parser.parse_network():
                # Initialise an instance of the userint.UserInterface() class
                userint = UserInterface(names, devices, network, monitors)
                userint.command_interface()

    if not options:  # no option given, use the graphical user interface

        if len(arguments) == 0:  # No arguments
            app = wx.App()

            locale = set_language(app)

            gui = Gui(_("Logic Simulator"))
            gui.Show(True)
            app.MainLoop()
        elif len(arguments) > 1:
            print("Error: two many arguments provided\n")
            print(usage_message)
            sys.exit()
        elif len(arguments) == 1:  # File provided
            [path] = arguments
            scanner = Scanner(path, names)
            error_db = Error_Store(scanner)
            parser = Parser(names, devices, network,
                            monitors, scanner, error_db)
            if parser.parse_network():
                # Initialise an instance of the gui.Gui() class
                app = wx.App()
                locale = set_language(app)

                gui = Gui("Logic Simulator", path, names, devices, network,
                          monitors)
                gui.Show(True)
                app.MainLoop()


if __name__ == "__main__":
    main(sys.argv[1:])
