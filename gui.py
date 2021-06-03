"""Implement the graphical user interface for the Logic Simulator.

Used in the Logic Simulator project to enable the user to run the simulation
or adjust the network properties.

Classes:
--------
MyGLCanvas - handles all canvas drawing operations.
Gui - configures the main window and all the widgets.
"""
import wx
from wx.core import Position
import wx.glcanvas as wxcanvas
from OpenGL import GL, GLUT
import os

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser
from errors import Error_Store


class MyGLCanvas(wxcanvas.GLCanvas):
    """Handle all drawing operations.

    This class contains functions for drawing onto the canvas. It
    also contains handlers for events relating to the canvas.

    Parameters
    ----------
    parent: parent window.
    devices: instance of the devices.Devices() class.
    monitors: instance of the monitors.Monitors() class.

    Public methods
    --------------
    init_gl(self): Configures the OpenGL context.

    render(self, text): Handles all drawing operations.

    on_paint(self, event): Handles the paint event.

    on_size(self, event): Handles the canvas resize event.

    on_mouse(self, event): Handles mouse events.

    render_text(self, text, x_pos, y_pos): Handles text drawing
                                           operations.
    """

    def __init__(self, parent, devices, monitors):
        """Initialise canvas properties and useful variables."""
        super().__init__(parent, -1,
                         attribList=[wxcanvas.WX_GL_RGBA,
                                     wxcanvas.WX_GL_DOUBLEBUFFER,
                                     wxcanvas.WX_GL_DEPTH_SIZE, 16, 0])
        GLUT.glutInit()
        self.init = False
        self.context = wxcanvas.GLContext(self)

        self.blank_file = True

        # Initialise variables for panning
        self.pan_x = 0
        self.pan_y = 0
        self.last_mouse_x = 0  # previous mouse x position
        self.last_mouse_y = 0  # previous mouse y position

        # Initialise variables for zooming
        self.zoom = 1

        self.length = 10
        self.outputs = [[4 for i in range(10)]]
        self.output_labels = ['No signal']

        # Bind events to the canvas
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)

    def init_gl(self):
        """Configure and initialise the OpenGL context."""
        size = self.GetClientSize()
        self.SetCurrent(self.context)
        GL.glDrawBuffer(GL.GL_BACK)
        GL.glClearColor(1.0, 1.0, 1.0, 0.0)
        GL.glViewport(0, 0, size.width, size.height)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, size.width, 0, size.height, -1, 1)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        GL.glTranslated(self.pan_x, self.pan_y, 0.0)
        GL.glScaled(self.zoom, self.zoom, self.zoom)

    def render(self, outputs, length):
        """Handle all drawing operations."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        # Draw a sample signal trace
        x_step = (self.GetClientSize().width - 60) / length
        y_spacing = (self.GetClientSize().height) / (2 * len(outputs))
        y_step = 50  # Determines the vertical size of the signal traces

        for j in range(len(outputs)):
            if(len(outputs) > 6):
                self.render_text(
                    self.output_labels[j], 5, y_spacing*(2*j+1)+y_step/2)
            else:
                self.render_text(
                    self.output_labels[j], 50, y_spacing*(2*j+1)+y_step*3/2)
            self.render_text('0', 25, y_spacing * (2 * j + 1))
            self.render_text('1', 25, y_spacing * (2 * j + 1) + y_step)
            GL.glColor3f(0.0, 0.0, 1.0)  # signal trace is blue
            GL.glBegin(GL.GL_LINE_STRIP)
            for i in range(length):
                x = (i * x_step) + 50
                x_next = (i * x_step) + x_step + 50
                y = y_spacing * (2 * j + 1) + y_step * outputs[j][i]
                if(outputs[j][i] != 4):
                    GL.glVertex2f(x, y)
                    GL.glVertex2f(x_next, y)
            GL.glEnd()

        # We have been drawing to the back buffer, flush the graphics pipeline
        # and swap the back buffer to the front
        GL.glFlush()
        self.SwapBuffers()

    def on_paint(self, event):
        """Handle the paint event."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        self.render(self.outputs, len(self.outputs[0]))

    def on_size(self, event):
        """Handle the canvas resize event."""
        # Forces reconfiguration of the viewport, modelview and projection
        # matrices on the next paint event
        self.init = False

    def on_mouse(self, event):
        """Handle mouse events."""
        # Calculate object coordinates of the mouse position
        size = self.GetClientSize()
        ox = (event.GetX() - self.pan_x) / self.zoom
        oy = (size.height - event.GetY() - self.pan_y) / self.zoom
        old_zoom = self.zoom
        if event.ButtonDown():
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
        if event.ButtonUp():
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
        if event.Leaving():
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
        if event.Dragging():
            self.pan_x += event.GetX() - self.last_mouse_x
            self.pan_y -= event.GetY() - self.last_mouse_y
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            self.init = False
        if event.GetWheelRotation() < 0:
            self.zoom *= (1.0 + (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            # Adjust pan so as to zoom around the mouse position
            self.pan_x -= (self.zoom - old_zoom) * ox
            self.pan_y -= (self.zoom - old_zoom) * oy
            self.init = False
        if event.GetWheelRotation() > 0:
            self.zoom /= (1.0 - (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            # Adjust pan so as to zoom around the mouse position
            self.pan_x -= (self.zoom - old_zoom) * ox
            self.pan_y -= (self.zoom - old_zoom) * oy
            self.init = False  # triggers the paint event
        if(not self.blank_file):
            self.Refresh()

    def render_text(self, text, x_pos, y_pos):
        """Handle text drawing operations."""
        GL.glColor3f(0.0, 0.0, 0.0)  # text is black
        GL.glRasterPos2f(x_pos, y_pos)
        font = GLUT.GLUT_BITMAP_HELVETICA_12

        for character in text:
            if character == '\n':
                y_pos = y_pos - 20
                GL.glRasterPos2f(x_pos, y_pos)
            else:
                GLUT.glutBitmapCharacter(font, ord(character))


class Gui(wx.Frame):
    """Configure the main window and all the widgets.

    This class provides a graphical user interface for the Logic Simulator and
    enables the user to change the circuit properties and run simulations.

    Parameters
    ----------
    title: title of the window.

    Public methods
    --------------
    on_menu(self, event): Event handler for the file menu.

    on_spin(self, event): Event handler for when the user changes the spin
                           control value.

    on_run_button(self, event): Event handler for when the user clicks the run
                                button.

    on_continue_button(self, event): Event handler for when the user clicks
                                     the continue button.

    on_remove_monitor(self, event): Event handler for when the user clicks
                                    the zap monitor button.

    on_add_monitor(self, event): Event handler for when the user clicks
                                 the add monitor button.

    open_file_button(self, event): Event handler for when the user clicks
                                   the open file button.

    open_file_dialog(self): Function which opens a new BNA and resets the
                            gui for the new circuit.

    display_errors(self, error_db): Function which displays a dialog box with the
                                    syntax errors if there are any present

    """

    def __init__(self, title="Logic Simulator", path=None,
                 names=None, devices=None, network=None, monitors=None):
        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title, size=(800, 600))

        blank_file = open('startup.bna', 'w')
        blank_file.write(
            'begin devices:\nend devices;\nbegin connections:\nend connections;\nbegin monitors:\nend monitors;')
        blank_file.close()
        pathname = 'startup.bna'

        if(names is None):
            names1 = Names()
            devices1 = Devices(names1)
            network1 = Network(names1, devices1)
            monitors1 = Monitors(names1, devices1, network1)

            scanner = Scanner(pathname, names1)
            error_db = Error_Store(scanner)
            parser = Parser(
                names1,
                devices1,
                network1,
                monitors1,
                scanner,
                error_db)
            if not parser.parse_network():
                self.display_errors(error_db)

            self.network = network1
            self.devices = devices1
            self.names = names1
            self.monitors = monitors1
            self.error_store = error_db
        else:
            # Set up network for running
            self.network = network
            self.devices = devices
            self.names = names
            self.monitors = monitors

        # Store original values of switches
        switches = self.devices.find_devices(self.devices.SWITCH)
        initial_switch_values = [
            self.devices.get_device(
                switches[i]).switch_state for i in range(
                len(switches))]

        self.cycles = 0

        # Configure the file menu
        fileMenu = wx.Menu()
        menuBar = wx.MenuBar()
        fileMenu.Append(wx.ID_OPEN, "&Open")
        fileMenu.Append(wx.ID_ABOUT, "&About")
        fileMenu.Append(wx.ID_EXIT, "&Exit")
        menuBar.Append(fileMenu, "&File")
        self.SetMenuBar(menuBar)

        # Canvas for drawing signals
        self.canvas = MyGLCanvas(self, devices, monitors)

        # Configure the widgets
        self.text = wx.StaticText(self, wx.ID_ANY, " Number of Cycles")
        self.spin = wx.SpinCtrl(self, wx.ID_ANY, "10")
        self.run_button = wx.Button(self, wx.ID_ANY, "Run")
        self.continue_button = wx.Button(self, wx.ID_ANY, "Continue")
        self.remove_monitor = wx.Button(self, wx.ID_ANY, "Zap Monitor")
        self.add_monitor = wx.Button(self, wx.ID_ANY, "Add Monitor")
        self.open_file = wx.Button(self, wx.ID_ANY, "Open file")

        # Bind events to widgets
        self.Bind(wx.EVT_MENU, self.on_menu)
        self.spin.Bind(wx.EVT_SPINCTRL, self.on_spin)
        self.run_button.Bind(wx.EVT_BUTTON, self.on_run_button)
        self.continue_button.Bind(wx.EVT_BUTTON, self.on_continue_button)
        self.remove_monitor.Bind(wx.EVT_BUTTON, self.on_remove_monitor)
        self.add_monitor.Bind(wx.EVT_BUTTON, self.on_add_monitor)
        self.open_file.Bind(wx.EVT_BUTTON, self.open_file_button)

        # Configure sizers for layout
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.side_sizer = wx.FlexGridSizer(1, 5, 10)
        self.run_box = wx.StaticBoxSizer(
            wx.VERTICAL, self, label='Run/Continue')

        main_sizer.Add(self.canvas, 5, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(self.side_sizer, 1, wx.ALL, 5)
        self.side_sizer.Add(self.run_box, 1, wx.ALL, 5)

        self.previous_outputs = []
        for key in self.monitors.monitors_dictionary:
            self.previous_outputs.append([])

        self.spinner_box = wx.BoxSizer(wx.HORIZONTAL)
        self.run_button_box = wx.BoxSizer(wx.HORIZONTAL)

        # Add the run/continue controls
        self.spinner_box.Add(self.text, 1, wx.TOP, 10)
        self.spinner_box.Add(self.spin, 1, wx.ALL, 5)
        self.run_button_box.Add(self.run_button, 1, wx.ALL, 5)
        self.run_button_box.Add(self.continue_button, 1, wx.ALL, 5)

        self.run_box.Add(self.spinner_box)
        self.run_box.Add(self.run_button_box)

        self.radiobuttons = []

        self.switch_box = wx.StaticBoxSizer(
            wx.VERTICAL, self, label='Switches')
        self.side_sizer.Add(self.switch_box, 1, wx.ALL, 5)

        switches = self.devices.find_devices(self.devices.SWITCH)
        self.switch_items = []
        for i in range(len(switches)):
            self.single_switch_box = wx.BoxSizer(wx.HORIZONTAL)
            self.switch_box.Add(self.single_switch_box)
            switch_name = self.names.get_name_string(switches[i])
            self.switch_items.append(
                wx.StaticText(
                    self, wx.ID_ANY, switch_name))
            self.switch_items.append(
                wx.StaticText(
                    self,
                    wx.ID_ANY,
                    "                        "))
            self.single_switch_box.Add(self.switch_items[-2])
            self.single_switch_box.Add(self.switch_items[-1])
            # Add the RadioButton objects to a list so we can access their
            # value
            self.radiobuttons.append(
                wx.RadioButton(
                    self,
                    wx.ID_ANY,
                    label="On",
                    style=wx.RB_GROUP))
            if(initial_switch_values[i]):
                self.radiobuttons[-1].SetValue(True)
            # Adds the RadioButton created in the previous line
            self.single_switch_box.Add(self.radiobuttons[-1])
            self.radiobuttons.append(
                wx.RadioButton(
                    self, wx.ID_ANY, label="Off"))
            if(not initial_switch_values[i]):
                self.radiobuttons[-1].SetValue(True)
            self.single_switch_box.Add(self.radiobuttons[-1])

        # Retrieve initial list of monitored and unmonitored devices
        self.monitored_devices, self.unmonitored_devices = self.monitors.get_signal_names()

        self.add_monitor_box = wx.StaticBoxSizer(
            wx.HORIZONTAL, self, label="Add Monitor")
        self.side_sizer.Add(self.add_monitor_box)

        # Add monitor addition/removal controls
        self.add_monitor_choice = wx.Choice(
            self, wx.ID_ANY, size=wx.Size(
                100, 5), choices=self.unmonitored_devices)
        self.add_monitor_box.Add(self.add_monitor_choice)
        self.add_monitor_box.Add(
            wx.StaticText(
                self,
                wx.ID_ANY,
                "            "))
        self.add_monitor_box.Add(self.add_monitor)

        self.zap_monitor_box = wx.StaticBoxSizer(
            wx.HORIZONTAL, self, label="Zap Monitor")
        self.side_sizer.Add(self.zap_monitor_box)

        self.remove_monitor_choice = wx.Choice(
            self, wx.ID_ANY, size=wx.Size(
                100, 5), choices=self.monitored_devices)
        self.zap_monitor_box.Add(self.remove_monitor_choice)
        self.zap_monitor_box.Add(
            wx.StaticText(
                self,
                wx.ID_ANY,
                "            "))
        self.zap_monitor_box.Add(self.remove_monitor)

        self.open_file_box = wx.StaticBoxSizer(
            wx.HORIZONTAL, self, label="File")
        self.open_file_box.Add(self.open_file)
        self.side_sizer.Add(self.open_file_box)

        os.remove(pathname)

        self.SetSizeHints(600, 600)
        self.SetSizer(main_sizer)

    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        Id = event.GetId()
        if Id == wx.ID_EXIT:
            self.Close(True)
        if Id == wx.ID_ABOUT:
            wx.MessageBox(
                "Boernashly Logic Simulator\nCreated by Reef Boericke, Joe Nash, and Finn Ashley\n2021",
                "About Logsim",
                wx.ICON_INFORMATION | wx.OK)
        if Id == wx.ID_OPEN:
            self.open_file_dialog()

    def on_spin(self, event):
        """Handle the event when the user changes the spin control value."""
        self.canvas.length = self.spin.GetValue()

    def on_run_button(self, event):
        """Handle the event when the user clicks the run button."""
        for i in range(len(self.previous_outputs)):
            self.previous_outputs[i] = []

        self.cycles = 0
        self.monitors.reset_monitors()

        self.devices.cold_startup()

        switch_values = []
        # Assembles the values of the switches set in the GUI. Can be returned
        # to run the logsim with the right settings.
        for i in range(len(self.radiobuttons)):
            if(i % 2 == 0):
                switch_values.append(self.radiobuttons[i].GetValue())

        switch_signals = []  # Convert True/False to 1/0
        for value in switch_values:
            if value:
                switch_signals.append(1)
            else:
                switch_signals.append(0)

        # Set all switches to the value specified in GUI
        switches = self.devices.find_devices(self.devices.SWITCH)
        for i in range(len(switches)):
            self.devices.set_switch(switches[i], switch_signals[i])

        for i in range(self.canvas.length):
            if self.network.execute_network():
                self.monitors.record_signals()

        self.cycles += self.canvas.length

        self.canvas.outputs = [self.monitors.monitors_dictionary[device]
                               for device in self.monitors.monitors_dictionary]

        self.canvas.output_labels = self.monitored_devices

        if self.canvas.outputs != [[4, 4, 4, 4, 4, 4, 4, 4, 4, 4]]:
            self.canvas.render(self.canvas.outputs, self.canvas.length)

    def on_continue_button(self, event):
        """Handle the event when the user clicks the continue button."""
        self.previous_outputs = [self.previous_outputs[i] + [self.monitors.monitors_dictionary[device]
                                                             for device in self.monitors.monitors_dictionary][i] for i in range(len(self.previous_outputs))]

        self.monitors.reset_monitors()

        switch_values = []
        # Assembles the values of the switches set in the GUI. Can be returned
        # to run the logsim with the right settings.
        for i in range(len(self.radiobuttons)):
            if(i % 2 == 0):
                switch_values.append(self.radiobuttons[i].GetValue())

        switch_signals = []  # Convert True/False to 1/0
        for value in switch_values:
            if value:
                switch_signals.append(1)
            else:
                switch_signals.append(0)

        # Set all switches to the value specified in GUI
        switches = self.devices.find_devices(self.devices.SWITCH)
        for i in range(len(switches)):
            self.devices.set_switch(switches[i], switch_signals[i])

        for i in range(self.canvas.length):
            if self.network.execute_network():
                self.monitors.record_signals()

        self.cycles += self.canvas.length

        self.canvas.outputs = [self.previous_outputs[i] + [self.monitors.monitors_dictionary[device]
                                                           for device in self.monitors.monitors_dictionary][i] for i in range(len(self.previous_outputs))]
        self.canvas.output_labels = self.monitored_devices

        if self.canvas.outputs != [[4, 4, 4, 4, 4, 4, 4, 4, 4, 4]]:
            self.canvas.render(
                self.canvas.outputs, len(
                    self.canvas.outputs[0]))

    def on_remove_monitor(self, event):
        """Handle removing the selected monitor."""
        device_index = self.remove_monitor_choice.GetSelection()

        if(device_index != wx.NOT_FOUND):
            device_id = self.names.query(self.monitored_devices[device_index])
            if(len(self.monitored_devices) == 1):
                window = wx.MessageDialog(
                    self, "You must have at least 1 monitor", style=wx.OK)
                window.ShowWindowModal()
                return None
            self.previous_outputs.pop(device_index)
            if(self.devices.get_device(device_id).device_kind != self.devices.D_TYPE):
                self.monitors.remove_monitor(device_id, None)
            else:
                self.monitors.remove_monitor(device_id, self.devices.Q_ID)
            self.unmonitored_devices.append(
                self.monitored_devices[device_index])
            self.monitored_devices.pop(device_index)
            self.add_monitor_choice.Destroy()
            self.add_monitor_choice = wx.Choice(
                self, wx.ID_ANY, size=wx.Size(
                    100, 5), choices=self.unmonitored_devices)
            self.add_monitor_box.Insert(0, self.add_monitor_choice)
            self.remove_monitor_choice.Destroy()
            self.remove_monitor_choice = wx.Choice(
                self, wx.ID_ANY, size=wx.Size(
                    100, 5), choices=self.monitored_devices)
            self.zap_monitor_box.Insert(0, self.remove_monitor_choice)
            self.add_monitor_box.Layout()
            self.zap_monitor_box.Layout()

    def on_add_monitor(self, event):
        """Handle adding the selected monitor."""
        if(len(self.unmonitored_devices) == 0):
            return None

        device_index = self.add_monitor_choice.GetSelection()

        if(device_index != wx.NOT_FOUND):
            device_id = self.names.query(
                self.unmonitored_devices[device_index])
            self.previous_outputs.append([])
            if (self.devices.get_device(
                    device_id).device_kind != self.devices.D_TYPE):
                self.monitors.make_monitor(
                    device_id, None, len(
                        self.canvas.outputs[0]))
            else:
                self.monitors.make_monitor(
                    device_id, self.devices.Q_ID, self.cycles)
            self.monitored_devices.append(
                self.unmonitored_devices[device_index])
            self.unmonitored_devices.pop(device_index)
            self.add_monitor_choice.Destroy()
            self.add_monitor_choice = wx.Choice(
                self, wx.ID_ANY, size=wx.Size(
                    100, 5), choices=self.unmonitored_devices)
            self.add_monitor_box.Insert(0, self.add_monitor_choice)
            self.remove_monitor_choice.Destroy()
            self.remove_monitor_choice = wx.Choice(
                self, wx.ID_ANY, size=wx.Size(
                    100, 5), choices=self.monitored_devices)
            self.zap_monitor_box.Insert(0, self.remove_monitor_choice)
            self.add_monitor_box.Layout()
            self.zap_monitor_box.Layout()

    def open_file_button(self, event):
        """Handle the user pressing the open file button."""
        self.open_file_dialog()

    def open_file_dialog(self):
        """Open a new BNA file via a GUI."""
        self.canvas.blank_file = False
        self.canvas.outputs = [[4 for i in range(10)]]
        self.canvas.length = 10
        self.canvas.output_labels = ['No signal']
        with wx.FileDialog(self, "Open bna file", wildcard="bna files (*.bna)|*.bna",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            pathname = fileDialog.GetPath()

            names1 = Names()
            devices1 = Devices(names1)
            network1 = Network(names1, devices1)
            monitors1 = Monitors(names1, devices1, network1)

            scanner = Scanner(pathname, names1)
            error_db = Error_Store(scanner)
            parser = Parser(
                names1,
                devices1,
                network1,
                monitors1,
                scanner,
                error_db)
            if not parser.parse_network():
                self.display_errors(error_db)

            self.network = network1
            self.devices = devices1
            self.names = names1
            self.monitors = monitors1
            self.error_store = error_db

            self.monitored_devices, self.unmonitored_devices = self.monitors.get_signal_names()

            self.add_monitor_choice.Destroy()
            self.add_monitor_choice = wx.Choice(
                self, wx.ID_ANY, size=wx.Size(
                    100, 5), choices=self.unmonitored_devices)
            self.add_monitor_box.Insert(0, self.add_monitor_choice)
            self.remove_monitor_choice.Destroy()
            self.remove_monitor_choice = wx.Choice(
                self, wx.ID_ANY, size=wx.Size(
                    100, 5), choices=self.monitored_devices)
            self.zap_monitor_box.Insert(0, self.remove_monitor_choice)
            self.add_monitor_box.Layout()
            self.zap_monitor_box.Layout()

            switches = self.devices.find_devices(self.devices.SWITCH)
            initial_switch_values = [
                self.devices.get_device(
                    switches[i]).switch_state for i in range(
                    len(switches))]

            for item in self.switch_items:
                try:
                    item.Destroy()
                except(RuntimeError):
                    continue

            for item in self.radiobuttons:
                item.Destroy()

            self.radiobuttons = []
            for i in range(len(switches)):
                self.single_switch_box = wx.BoxSizer(wx.HORIZONTAL)
                self.switch_box.Add(self.single_switch_box)
                switch_name = self.names.get_name_string(switches[i])
                self.switch_items.append(
                    wx.StaticText(
                        self, wx.ID_ANY, switch_name))
                self.switch_items.append(
                    wx.StaticText(
                        self,
                        wx.ID_ANY,
                        "                        "))
                self.single_switch_box.Add(self.switch_items[-2])
                self.single_switch_box.Add(self.switch_items[-1])
                # Add the RadioButton objects to a list so we can access their
                # value
                self.radiobuttons.append(
                    wx.RadioButton(
                        self,
                        wx.ID_ANY,
                        label="On",
                        style=wx.RB_GROUP))
                if(initial_switch_values[i]):
                    self.radiobuttons[-1].SetValue(True)
                # Adds the RadioButton created in the previous line
                self.single_switch_box.Add(self.radiobuttons[-1])
                self.radiobuttons.append(
                    wx.RadioButton(
                        self, wx.ID_ANY, label="Off"))
                if(not initial_switch_values[i]):
                    self.radiobuttons[-1].SetValue(True)
                self.single_switch_box.Add(self.radiobuttons[-1])
                self.single_switch_box.Layout()
                self.switch_box.Layout()
                self.side_sizer.Layout()

            self.previous_outputs = []
            for i in range(len(self.monitored_devices)):
                self.previous_outputs.append([])

    def display_errors(self, error_db):
        """Create a dialog box with the errors present if there are any."""
        window = wx.MessageDialog(self, error_db.report_errors(command_line=False,file_output=False), style=wx.OK)
        window.Title = "There were errors: logged in error_report.txt"
        window.ShowWindowModal()
