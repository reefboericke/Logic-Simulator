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

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser


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

        # Initialise variables for panning
        self.pan_x = 0
        self.pan_y = 0
        self.last_mouse_x = 0  # previous mouse x position
        self.last_mouse_y = 0  # previous mouse y position

        # Initialise variables for zooming
        self.zoom = 1

        # Initialise variables for rendering signals
        self.outputs = [[0, 10, 10, 10, 10, 0, 0, 10, 0, 0, 10, 0, 0, 10, 10, 10, 10, 0, 0, 0], [0, 0, 0, 0, 10, 0, 0, 10, 0, 0, 0, 0, 0, 0, 10, 10, 10, 10, 10, 10], [0, 10, 10, 10, 10, 0, 0, 10, 0, 0, 10, 0, 0, 10, 10, 10, 10, 0, 0, 0]] # Fake test signal
        self.length = 10

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
        x_step = (self.GetClientSize().width - 20)/length
        y_spacing = (self.GetClientSize().height)/(2*len(outputs))
        y_step = 20 #if the screen is very crowded or empty could adjust this for readability

        for j in range(len(outputs)):
            GL.glColor3f(0.0, 0.0, 1.0)  # signal trace is blue
            GL.glBegin(GL.GL_LINE_STRIP)
            for i in range(length):
                x = (i * x_step) + 10
                x_next = (i * x_step) + x_step + 10
                y = y_spacing*(2*j + 1) + y_step*outputs[j][i]
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

        self.render(self.outputs, self.length)

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
            self.init = False
        self.Refresh()  # triggers the paint event

    #def render_text(self, text, x_pos, y_pos):
    #    """Handle text drawing operations."""
    #    GL.glColor3f(0.0, 0.0, 0.0)  # text is black
    #    GL.glRasterPos2f(x_pos, y_pos)
    #    font = GLUT.GLUT_BITMAP_HELVETICA_12

    #    for character in text:
    #        if character == '\n':
    #            y_pos = y_pos - 20
    #            GL.glRasterPos2f(x_pos, y_pos)
    #        else:
    #            GLUT.glutBitmapCharacter(font, ord(character))


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

    on_text_box(self, event): Event handler for when the user enters text.
    """

    def __init__(self, title, path, names, devices, network, monitors):
        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title, size=(800, 600))

        # Set up network for running
        self.network = network
        self.devices = devices
        self.names = names

        # Configure the file menu
        fileMenu = wx.Menu()
        menuBar = wx.MenuBar()
        fileMenu.Append(wx.ID_OPEN, "&Open")
        fileMenu.Append(wx.ID_ABOUT, "&About")
        fileMenu.Append(wx.ID_EXIT, "&Exit")
        menuBar.Append(fileMenu, "&File")
        self.SetMenuBar(menuBar)

        # Might need to later define the outputs and lengths etc. here first and then pass them to the canvas when the object is defined.
        # For now these variables are defined in the canvas init function

        # Canvas for drawing signals
        self.canvas = MyGLCanvas(self, devices, monitors)

        # Configure the widgets
        self.text = wx.StaticText(self, wx.ID_ANY, " Number of Cycles")
        self.spin = wx.SpinCtrl(self, wx.ID_ANY, "10")
        self.run_button = wx.Button(self, wx.ID_ANY, "Run")
        self.continue_button = wx.Button(self, wx.ID_ANY, "Continue")
        self.remove_monitor = wx.Button(self, wx.ID_ANY, "Zap Monitor")
        self.add_monitor = wx.Button(self, wx.ID_ANY, "Add Monitor")

        # Bind events to widgets
        self.Bind(wx.EVT_MENU, self.on_menu)
        self.spin.Bind(wx.EVT_SPINCTRL, self.on_spin)
        self.run_button.Bind(wx.EVT_BUTTON, self.on_run_button)
        self.continue_button.Bind(wx.EVT_BUTTON, self.on_continue_button)
        self.remove_monitor.Bind(wx.EVT_BUTTON, self.on_remove_monitor)
        self.add_monitor.Bind(wx.EVT_BUTTON, self.on_add_monitor)

        # Configure sizers for layout
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.side_sizer = wx.FlexGridSizer(3, 5, 5)

        main_sizer.Add(self.canvas, 5, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(self.side_sizer, 1, wx.ALL, 5)

        # If (there are errors):
        #       for error in errors:
        #           main_sizer.add(staticText('error'))
        # Then somehow stop the rest of the code from running, because the circuit cant be loaded. How to do this TBC

        self.side_sizer.Add(self.text, 1, wx.TOP, 10) #Add the run/continue controls
        self.side_sizer.Add(self.spin, 1, wx.ALL, 5)
        self.side_sizer.Add(wx.StaticText(self, wx.ID_ANY, ""))
        self.side_sizer.Add(self.run_button, 1, wx.ALL, 5)
        self.side_sizer.Add(self.continue_button, 1, wx.ALL, 5)
        self.side_sizer.Add(wx.StaticText(self, wx.ID_ANY, ""))
        self.radiobuttons = []
        for i in range(3): #Iterate through the switches in the circuit and list them out with on/off. (3) to be replaced with a value loaded from the circuit
            self.side_sizer.Add(wx.StaticText(self, wx.ID_ANY, "Switch " + str(i)))
            self.radiobuttons.append(wx.RadioButton(self, wx.ID_ANY, label = "On", style = wx.RB_GROUP)) # Add the RadioButton objects to a list so we can access their value
            self.side_sizer.Add(self.radiobuttons[-1]) # Adds the RadioButton created in the previous line
            self.radiobuttons.append(wx.RadioButton(self, wx.ID_ANY, label = "Off"))
            self.side_sizer.Add(self.radiobuttons[-1])

        # Define dummy lists of devices
        self.monitored_devices = ["NAND1", "NAND2", "DTYPE1"]
        self.unmonitored_devices = ["NAND3", "NAND4", "DTYPE2"]

        # Add monitor addition/removal controls
        self.add_monitor_choice = wx.Choice(self, wx.ID_ANY, choices=self.unmonitored_devices)
        self.side_sizer.Add(self.add_monitor_choice)
        self.side_sizer.Add(wx.StaticText(self, wx.ID_ANY, ""))
        self.side_sizer.Add(self.add_monitor)

        self.remove_monitor_choice = wx.Choice(self, wx.ID_ANY, choices=self.monitored_devices)
        self.side_sizer.Add(self.remove_monitor_choice)
        self.side_sizer.Add(wx.StaticText(self, wx.ID_ANY, ""))
        self.side_sizer.Add(self.remove_monitor)

        self.SetSizeHints(600, 600)
        self.SetSizer(main_sizer)

    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        Id = event.GetId()
        if Id == wx.ID_EXIT:
            self.Close(True)
        if Id == wx.ID_ABOUT:
            wx.MessageBox("Boernashly Logic Simulator\nCreated by Reef Boericke, Joe Nash, and Finn Ashley\n2021",
                          "About Logsim", wx.ICON_INFORMATION | wx.OK)
        if Id == wx.ID_OPEN:
            with wx.FileDialog(self, "Open txt file", wildcard="txt files (*.txt)|*.txt",
                       style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
                if fileDialog.ShowModal() == wx.ID_CANCEL:
                    return
                pathname = fileDialog.GetPath()
                

    def on_spin(self, event):
        """Handle the event when the user changes the spin control value."""
        self.canvas.length = self.spin.GetValue()

    def on_run_button(self, event):
        """Handle the event when the user clicks the run button."""
        #for specified number of iterations run the simulation and fetch the state of the devices to be monitored
        monitored_ids = [self.names.query(device_name) for device_name in self.monitored_devices]
        for i in range(self.canvas.length):
            self.network.execute_network()
        for device in self.devices.devices_list:
            if device.device_id in monitored_ids:
                self.outputs.append([device.ouputs[output_id] for output_id in device.outputs]) # might be wrong - if device stores one output at a time then need to move this inside the previous loop and store output per step of the network

        self.canvas.render(self.canvas.outputs, self.canvas.length) #probably superfluous

    def on_continue_button(self, event):
        """Handle the event when the user clicks the continue button."""
        switch_values = []
        for i in range(len(self.radiobuttons)): #Assembles the values of the switches set in the GUI. Can be returned to run the logsim with the right settings.
            if(i%2 == 0):
                switch_values.append(self.radiobuttons[i].GetValue())
        self.canvas.render(self.canvas.outputs, self.canvas.length) #probably superfluous

    def on_remove_monitor(self, event):
        """Handle removing the selected monitor"""
        if(self.remove_monitor_choice.GetSelection() != wx.NOT_FOUND):
            self.unmonitored_devices.append(self.monitored_devices[self.remove_monitor_choice.GetSelection()])
            self.monitored_devices.pop(self.remove_monitor_choice.GetSelection())
            self.add_monitor_choice.Destroy()
            self.add_monitor_choice = wx.Choice(self, wx.ID_ANY, choices=self.unmonitored_devices)
            self.side_sizer.Insert(15, self.add_monitor_choice)
            self.remove_monitor_choice.Destroy()
            self.remove_monitor_choice = wx.Choice(self, wx.ID_ANY, choices=self.monitored_devices)
            self.side_sizer.Insert(18, self.remove_monitor_choice)
            self.side_sizer.Layout()

    def on_add_monitor(self, event):
        """Handle adding the selected monitor"""
        if(self.add_monitor_choice.GetSelection() != wx.NOT_FOUND):
            self.monitored_devices.append(self.unmonitored_devices[self.add_monitor_choice.GetSelection()])
            self.unmonitored_devices.pop(self.add_monitor_choice.GetSelection())
            self.add_monitor_choice.Destroy()
            self.add_monitor_choice = wx.Choice(self, wx.ID_ANY, choices=self.unmonitored_devices)
            self.side_sizer.Insert(15, self.add_monitor_choice)
            self.remove_monitor_choice.Destroy()
            self.remove_monitor_choice = wx.Choice(self, wx.ID_ANY, choices=self.monitored_devices)
            self.side_sizer.Insert(18, self.remove_monitor_choice)
            self.side_sizer.Layout()
