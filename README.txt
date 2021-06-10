GF2: Logic Simulator Project

This project develops a novel HDL, known as BNA, for use in a digital logic simulator program.

To run program, run logsim.py.

Possible options:
-c runs the command line interface
-h displays the help message

Software prerequisites:
pyOpenGL 3.1.5
numpy 1.20.3
wxPython 4.11

There is a current issue with the GitHub actions service due to a conflict with wxpython on the VM it is using.
This stops it from running the pytest command, but pytest run locally will pass all checks.
