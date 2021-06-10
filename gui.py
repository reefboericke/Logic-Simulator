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
from wx.core import LANGUAGE_GERMAN
import wx.glcanvas as wxcanvas
from OpenGL import GL, GLU, GLUT
import os
import numpy as np
import math
from os import sys
import platform

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser
from errors import Error_Store
import gettext
import builtins
_ = wx.GetTranslation


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

    reset_camera(self): Resets the rotation and position of the
                        camera.
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

        # Constants for OpenGL materials and lights
        self.mat_diffuse = [0.0, 0.0, 0.0, 1.0]
        self.mat_no_specular = [0.0, 0.0, 0.0, 0.0]
        self.mat_no_shininess = [0.0]
        self.mat_specular = [0.5, 0.5, 0.5, 1.0]
        self.mat_shininess = [50.0]
        self.top_right = [1.0, 1.0, 1.0, 0.0]
        self.straight_on = [0.0, 0.0, 1.0, 0.0]
        self.no_ambient = [0.0, 0.0, 0.0, 1.0]
        self.dim_diffuse = [0.5, 0.5, 0.5, 1.0]
        self.bright_diffuse = [1.0, 1.0, 1.0, 1.0]
        self.med_diffuse = [0.75, 0.75, 0.75, 1.0]
        self.full_specular = [0.5, 0.5, 0.5, 1.0]
        self.no_specular = [0.0, 0.0, 0.0, 1.0]

        self.blank_file = True
        self.is_3d = False

        # Initialise variables for panning
        self.pan_x = 0
        self.pan_y = 0
        self.last_mouse_x = 0  # previous mouse x position
        self.last_mouse_y = 0  # previous mouse y position

        # Initialise the scene rotation matrix
        self.scene_rotate = np.identity(4, 'f')

        # Initialise variables for zooming
        self.zoom = 1

        # Offset between viewpoint and origin of the scene
        self.depth_offset = 1000

        self.length = 10
        self.outputs = [[4 for i in range(10)]]
        self.output_labels = [_('No signal')]

        # Bind events to the canvas
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)

    def init_gl(self):
        """Configure and initialise the OpenGL context."""
        size = self.GetClientSize()
        self.SetCurrent(self.context)

        GL.glViewport(0, 0, size.width, size.height)

        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GLU.gluPerspective(45, size.width / size.height, 10, 10000)

        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()  # lights positioned relative to the viewer
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_AMBIENT, self.no_ambient)
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_DIFFUSE, self.med_diffuse)
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_SPECULAR, self.no_specular)
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_POSITION, self.top_right)
        GL.glLightfv(GL.GL_LIGHT1, GL.GL_AMBIENT, self.no_ambient)
        GL.glLightfv(GL.GL_LIGHT1, GL.GL_DIFFUSE, self.dim_diffuse)
        GL.glLightfv(GL.GL_LIGHT1, GL.GL_SPECULAR, self.no_specular)
        GL.glLightfv(GL.GL_LIGHT1, GL.GL_POSITION, self.straight_on)

        GL.glMaterialfv(GL.GL_FRONT, GL.GL_SPECULAR, self.mat_specular)
        GL.glMaterialfv(GL.GL_FRONT, GL.GL_SHININESS, self.mat_shininess)
        GL.glMaterialfv(GL.GL_FRONT, GL.GL_AMBIENT_AND_DIFFUSE,
                        self.mat_diffuse)
        GL.glColorMaterial(GL.GL_FRONT, GL.GL_AMBIENT_AND_DIFFUSE)

        GL.glClearColor(0.0, 0.0, 0.0, 0.0)
        GL.glDepthFunc(GL.GL_LEQUAL)
        GL.glShadeModel(GL.GL_SMOOTH)
        GL.glDrawBuffer(GL.GL_BACK)
        GL.glCullFace(GL.GL_BACK)
        GL.glEnable(GL.GL_COLOR_MATERIAL)
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_LIGHTING)
        GL.glEnable(GL.GL_LIGHT0)
        GL.glEnable(GL.GL_LIGHT1)
        GL.glEnable(GL.GL_NORMALIZE)

        # Viewing transformation - set the viewpoint back from the scene
        GL.glTranslatef(0.0, 0.0, -self.depth_offset)

        # Modelling transformation - pan, zoom and rotate
        GL.glTranslatef(self.pan_x, self.pan_y, 0.0)
        GL.glMultMatrixf(self.scene_rotate)
        GL.glScalef(self.zoom, self.zoom, self.zoom)

    def render(self, outputs, length):
        """Handle all drawing operations."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        # Clear everything
        GL.glClearColor(1, 1, 1, 0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        # Draw a sample signal trace
        x_step = (self.GetClientSize().width * 0.7) / length
        y_spacing = (self.GetClientSize().height) / (2.5 * len(outputs))
        if(len(outputs) > 7):
            y_step = self.GetClientSize().height/20
        else:
            y_step = 50  # Determines the vertical size of the signal traces

        for p in range(len(outputs)):
            j = p - len(outputs)//2
            GL.glColor3f(0, 0, 0)
            if(len(outputs) > 6):
                self.render_text(
                    self.output_labels[j], -self.GetClientSize().width/2.5 + 5,
                    y_spacing*(2*j)+y_step/2, 5)
            else:
                self.render_text(
                    self.output_labels[j],
                    -self.GetClientSize().width/2.5 + 50,
                    y_spacing*(2*j)+y_step*3/2, 5)
            self.render_text('0', -self.GetClientSize().width/2.5,
                             y_spacing * (2 * j), 5)
            self.render_text('1', -self.GetClientSize().width/2.5,
                             y_spacing * (2 * j) + y_step, 5)
            if(self.is_3d):
                GL.glColor3f(1.0, 0.7, 0.5)  # signal trace is beige
                for i in range(length):
                    # i = q - length//2
                    x = (i * x_step) + 50 - self.GetClientSize().width/2.5
                    x_next = x + x_step
                    y = y_spacing * (2 * j)
                    # - self.GetClientSize().height/len(outputs)
                    if(outputs[j][i] != 4):
                            if(outputs[j][i] == 1):
                                self.draw_cuboid(x, y, 5, x_step/2, 25, y_step)
                            else:
                                self.draw_cuboid(x, y, 5, x_step/2, 25, 1)
            else:
                GL.glColor3f(0, 0, 1)
                GL.glBegin(GL.GL_LINE_STRIP)
                for i in range(length):
                    # i = q - length//2
                    x = (i * x_step) + 50 - self.GetClientSize().width/2.5
                    x_next = x + x_step
                    y = y_spacing * (2 * j) + y_step * outputs[j][i]
                    # - self.GetClientSize().height/len(outputs)
                    if(outputs[j][i] != 4):
                        GL.glVertex2f(x, y)
                        GL.glVertex2f(x_next, y)
                GL.glEnd()

        # We have been drawing to the back buffer, flush the graphics pipeline
        # and swap the back buffer to the front
        GL.glFlush()
        self.SwapBuffers()

    def draw_cuboid(self, x_pos, y_pos, z_pos, half_width, half_depth, height):
        """Draw a cuboid.

        Draw a cuboid at the specified position, with the specified
        dimensions.
        """
        GL.glBegin(GL.GL_QUADS)
        GL.glNormal3f(0, -1, 0)
        GL.glVertex3f(x_pos, y_pos, z_pos - half_depth)
        GL.glVertex3f(x_pos + 2*half_width, y_pos, z_pos - half_depth)
        GL.glVertex3f(x_pos + 2*half_width, y_pos, z_pos + half_depth)
        GL.glVertex3f(x_pos, y_pos, z_pos + half_depth)
        GL.glNormal3f(0, 1, 0)
        GL.glVertex3f(x_pos + 2*half_width, y_pos + height, z_pos - half_depth)
        GL.glVertex3f(x_pos, y_pos + height, z_pos - half_depth)
        GL.glVertex3f(x_pos, y_pos + height, z_pos + half_depth)
        GL.glVertex3f(x_pos + 2*half_width, y_pos + height, z_pos + half_depth)
        GL.glNormal3f(-1, 0, 0)
        GL.glVertex3f(x_pos, y_pos + height, z_pos - half_depth)
        GL.glVertex3f(x_pos, y_pos, z_pos - half_depth)
        GL.glVertex3f(x_pos, y_pos, z_pos + half_depth)
        GL.glVertex3f(x_pos, y_pos + height, z_pos + half_depth)
        GL.glNormal3f(1, 0, 0)
        GL.glVertex3f(x_pos + 2*half_width, y_pos, z_pos - half_depth)
        GL.glVertex3f(x_pos + 2*half_width, y_pos + height, z_pos - half_depth)
        GL.glVertex3f(x_pos + 2*half_width, y_pos + height, z_pos + half_depth)
        GL.glVertex3f(x_pos + 2*half_width, y_pos, z_pos + half_depth)
        GL.glNormal3f(0, 0, -1)
        GL.glVertex3f(x_pos, y_pos, z_pos - half_depth)
        GL.glVertex3f(x_pos, y_pos + height, z_pos - half_depth)
        GL.glVertex3f(x_pos + 2*half_width, y_pos + height, z_pos - half_depth)
        GL.glVertex3f(x_pos + 2*half_width, y_pos, z_pos - half_depth)
        GL.glNormal3f(0, 0, 1)
        GL.glVertex3f(x_pos, y_pos + height, z_pos + half_depth)
        GL.glVertex3f(x_pos, y_pos, z_pos + half_depth)
        GL.glVertex3f(x_pos + 2*half_width, y_pos, z_pos + half_depth)
        GL.glVertex3f(x_pos + 2*half_width, y_pos + height, z_pos + half_depth)
        GL.glEnd()

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
            GL.glMatrixMode(GL.GL_MODELVIEW)
            GL.glLoadIdentity()
            x = event.GetX() - self.last_mouse_x
            y = event.GetY() - self.last_mouse_y
            if event.RightIsDown():
                if(self.is_3d):
                    GL.glRotatef(math.sqrt((x * x) + (y * y)), y, x, 0)
            if event.MiddleIsDown():
                if(self.is_3d):
                    GL.glRotatef((x + y), 0, 0, 1)
            if event.LeftIsDown():
                self.pan_x += x
                self.pan_y -= y
            GL.glMultMatrixf(self.scene_rotate)
            GL.glGetFloatv(GL.GL_MODELVIEW_MATRIX, self.scene_rotate)
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

    def render_text(self, text, x_pos, y_pos, z_pos):
        """Handle text drawing operations."""
        GL.glDisable(GL.GL_LIGHTING)
        GL.glRasterPos3f(x_pos, y_pos, z_pos)
        font = GLUT.GLUT_BITMAP_HELVETICA_10

        for character in text:
            if character == '\n':
                y_pos = y_pos - 20
                GL.glRasterPos3f(x_pos, y_pos, z_pos)
            else:
                GLUT.glutBitmapCharacter(font, ord(character))

        GL.glEnable(GL.GL_LIGHTING)

    def reset_camera(self):
        """Reset the rotation and position of the camera."""
        self.zoom = 1
        self.pan_x = 0
        self.pan_y = 0
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        GL.glGetFloatv(GL.GL_MODELVIEW_MATRIX, self.scene_rotate)
        self.init = False
        self.Refresh()


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

    display_errors(self, error_db): Function which displays a dialog box with
                                    the syntax errors if there are any present

    toggle_3d(self, event): Event handler for when the user clicks the toggle
                            3d button.

    reset_display(self, event): Event handler for when the user clicks the
                                reset display button.

    """

    def __init__(self, title=_("Logic Simulator"), path=None,
                 names=None, devices=None, network=None, monitors=None):
        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title, size=(800, 600))

        blank_file = open('startup.bna', 'w')
        blank_file.write(
            'begin devices:\nend devices;\nbegin connections:\nend' +
            ' connections;\nbegin monitors:\nend monitors;')
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
        fileMenu.Append(wx.ID_OPEN, _("&Open"))
        fileMenu.Append(wx.ID_ABOUT, _("&About"))
        fileMenu.Append(wx.ID_EXIT, _("&Exit"))
        menuBar.Append(fileMenu, _("&File"))
        self.SetMenuBar(menuBar)

        # Canvas for drawing signals
        self.canvas = MyGLCanvas(self, devices, monitors)

        # Configure the widgets
        self.text = wx.StaticText(self, wx.ID_ANY, _(" Number of Cycles"))
        self.spin = wx.SpinCtrl(self, wx.ID_ANY, "10")
        self.run_button = wx.Button(self, wx.ID_ANY, _("Run"))
        self.continue_button = wx.Button(self, wx.ID_ANY, _("Continue"))
        self.remove_monitor = wx.Button(self, wx.ID_ANY, _("Zap Monitor"))
        self.add_monitor = wx.Button(self, wx.ID_ANY, _("Add Monitor"))
        self.open_file = wx.Button(self, wx.ID_ANY, _("Open file"))
        self.display_toggle = wx.Button(self, wx.ID_ANY,
                                        _("Toggle 3D Display"))
        self.reset_display_button = wx.Button(self, wx.ID_ANY,
                                              _("Reset Display"))

        # Bind events to widgets
        self.Bind(wx.EVT_MENU, self.on_menu)
        self.spin.Bind(wx.EVT_SPINCTRL, self.on_spin)
        self.run_button.Bind(wx.EVT_BUTTON, self.on_run_button)
        self.continue_button.Bind(wx.EVT_BUTTON, self.on_continue_button)
        self.remove_monitor.Bind(wx.EVT_BUTTON, self.on_remove_monitor)
        self.add_monitor.Bind(wx.EVT_BUTTON, self.on_add_monitor)
        self.open_file.Bind(wx.EVT_BUTTON, self.open_file_button)
        self.display_toggle.Bind(wx.EVT_BUTTON, self.toggle_3d)
        self.reset_display_button.Bind(wx.EVT_BUTTON, self.reset_display)

        # Configure sizers for layout
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.side_sizer = wx.FlexGridSizer(1, 5, 10)
        self.run_box = wx.StaticBoxSizer(
            wx.VERTICAL, self, label=_('Run/Continue'))

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
            wx.VERTICAL, self, label=_('Switches'))
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
                    label=_("On"),
                    style=wx.RB_GROUP))
            if(initial_switch_values[i]):
                self.radiobuttons[-1].SetValue(True)
            # Adds the RadioButton created in the previous line
            self.single_switch_box.Add(self.radiobuttons[-1])
            self.radiobuttons.append(
                wx.RadioButton(
                    self, wx.ID_ANY, label=_("Off")))
            if(not initial_switch_values[i]):
                self.radiobuttons[-1].SetValue(True)
            self.single_switch_box.Add(self.radiobuttons[-1])

        # Retrieve initial list of monitored and unmonitored devices
        self.monitored_devices, self.unmonitored_devices = \
            self.monitors.get_signal_names()

        self.add_monitor_box = wx.StaticBoxSizer(
            wx.HORIZONTAL, self, label=_("Add Monitor"))
        self.side_sizer.Add(self.add_monitor_box)

        # Add monitor addition/removal controls
        self.add_monitor_choice = wx.Choice(
            self, wx.ID_ANY, size=wx.Size(
                100, 20), choices=self.unmonitored_devices)
        self.add_monitor_box.Add(self.add_monitor_choice)
        self.add_monitor_box.Add(
            wx.StaticText(
                self,
                wx.ID_ANY,
                "            "))
        self.add_monitor_box.Add(self.add_monitor)

        self.zap_monitor_box = wx.StaticBoxSizer(
            wx.HORIZONTAL, self, label=_("Zap Monitor"))
        self.side_sizer.Add(self.zap_monitor_box)

        self.remove_monitor_choice = wx.Choice(
            self, wx.ID_ANY, size=wx.Size(
                100, 20), choices=self.monitored_devices)
        self.zap_monitor_box.Add(self.remove_monitor_choice)
        self.zap_monitor_box.Add(
            wx.StaticText(
                self,
                wx.ID_ANY,
                "            "))
        self.zap_monitor_box.Add(self.remove_monitor)

        self.open_file_box = wx.StaticBoxSizer(
            wx.HORIZONTAL, self, label=_("File"))
        self.open_file_box.Add(self.open_file)
        self.side_sizer.Add(self.open_file_box)

        self.toggle_display_box = wx.StaticBoxSizer(
            wx.HORIZONTAL, self, label=_('Display Options'))
        self.toggle_display_box.Add(self.display_toggle)
        self.toggle_display_box.Add(wx.StaticText(self, wx.ID_ANY, "    "))
        self.toggle_display_box.Add(self.reset_display_button)
        self.side_sizer.Add(self.toggle_display_box)

        if(len(self.monitored_devices)):
            self.canvas.blank_file = False

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
                _("Boernashly Logic Simulator\nCreated by Reef Boericke,") +
                _(" Joe Nash, and Finn Ashley\n2021"),
                _("About Logsim"),
                wx.ICON_INFORMATION | wx.OK)
        if Id == wx.ID_OPEN:
            self.open_file_dialog()

    def on_spin(self, event):
        """Handle the event when the user changes the spin control value."""
        self.canvas.length = self.spin.GetValue()

    def on_run_button(self, event):
        """Handle the event when the user clicks the run button."""
        if(self.canvas.blank_file):
            return None
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
        if(self.canvas.blank_file):
            return None
        self.previous_outputs = [self.previous_outputs[i] +
                                 [self.monitors.monitors_dictionary[device]
                                  for device in
                                  self.monitors.monitors_dictionary][i]
                                 for i in range(len(self.previous_outputs))]

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

        self.canvas.outputs = [self.previous_outputs[i] +
                               [self.monitors.monitors_dictionary[device]
                                for device in
                                self.monitors.monitors_dictionary][i]
                               for i in range(len(self.previous_outputs))]
        self.canvas.output_labels = self.monitored_devices

        if self.canvas.outputs != [[4, 4, 4, 4, 4, 4, 4, 4, 4, 4]]:
            self.canvas.render(self.canvas.outputs,
                               len(self.canvas.outputs[0]))

    def on_remove_monitor(self, event):
        """Handle removing the selected monitor."""
        device_index = self.remove_monitor_choice.GetSelection()

        if(device_index != wx.NOT_FOUND):
            device_name = self.monitored_devices[device_index]
            if('.' in device_name):
                device_id = self.names.query(device_name.split('.')[0])
            else:
                device_id = self.names.query(device_name)
            if(len(self.monitored_devices) == 1):
                window = wx.MessageDialog(
                    self, _("You must have at least 1 monitor"), style=wx.OK)
                window.ShowWindowModal()
                return None
            self.previous_outputs.pop(device_index)
            if(self.devices.get_device(device_id).device_kind
               != self.devices.D_TYPE):
                self.monitors.remove_monitor(device_id, None)
            else:
                output = device_name.split('.')[1]
                if(output == "QBAR"):
                    self.monitors.remove_monitor(
                        device_id, self.devices.QBAR_ID)
                else:
                    self.monitors.remove_monitor(
                        device_id, self.devices.Q_ID)
            self.unmonitored_devices.append(
                self.monitored_devices[device_index])
            self.monitored_devices.pop(device_index)
            self.add_monitor_choice.Destroy()
            self.add_monitor_choice = wx.Choice(
                self, wx.ID_ANY, size=wx.Size(
                    100, 20), choices=self.unmonitored_devices)
            self.add_monitor_box.Insert(0, self.add_monitor_choice)
            self.remove_monitor_choice.Destroy()
            self.remove_monitor_choice = wx.Choice(
                self, wx.ID_ANY, size=wx.Size(
                    100, 20), choices=self.monitored_devices)
            self.zap_monitor_box.Insert(0, self.remove_monitor_choice)
            self.add_monitor_box.Layout()
            self.zap_monitor_box.Layout()

    def on_add_monitor(self, event):
        """Handle adding the selected monitor."""
        if(len(self.unmonitored_devices) == 0):
            return None

        device_index = self.add_monitor_choice.GetSelection()

        if(device_index != wx.NOT_FOUND):
            device_name = self.unmonitored_devices[device_index]
            if('.' in device_name):
                device_id = self.names.query(device_name.split('.')[0])
            else:
                device_id = self.names.query(device_name)
            self.previous_outputs.append([])
            if (self.devices.get_device(
                    device_id).device_kind != self.devices.D_TYPE):
                self.monitors.make_monitor(
                    device_id, None, len(
                        self.canvas.outputs[0]))
            else:
                output = device_name.split('.')[1]
                if(output == "QBAR"):
                    self.monitors.make_monitor(
                        device_id, self.devices.QBAR_ID, self.cycles)
                else:
                    self.monitors.make_monitor(
                        device_id, self.devices.Q_ID, self.cycles)

            self.monitored_devices.append(
                self.unmonitored_devices[device_index])
            self.unmonitored_devices.pop(device_index)
            self.add_monitor_choice.Destroy()
            self.add_monitor_choice = wx.Choice(
                self, wx.ID_ANY, size=wx.Size(
                    100, 20), choices=self.unmonitored_devices)
            self.add_monitor_box.Insert(0, self.add_monitor_choice)
            self.remove_monitor_choice.Destroy()
            self.remove_monitor_choice = wx.Choice(
                self, wx.ID_ANY, size=wx.Size(
                    100, 20), choices=self.monitored_devices)
            self.zap_monitor_box.Insert(0, self.remove_monitor_choice)
            self.add_monitor_box.Layout()
            self.zap_monitor_box.Layout()

    def open_file_button(self, event):
        """Handle the user pressing the open file button."""
        self.open_file_dialog()

    def open_file_dialog(self):
        """Open a new BNA file via a GUI."""
        self.canvas.outputs = [[4 for i in range(10)]]
        self.canvas.length = 10
        self.canvas.output_labels = [_('No signal')]
        with wx.FileDialog(self, _("Open bna file"),
                           wildcard="bna files (*.bna)|*.bna",
                           style=wx.FD_OPEN |
                           wx.FD_FILE_MUST_EXIST)as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            pathname = fileDialog.GetPath()

            if(os.path.getsize(pathname) == 0):
                wx.MessageBox("Please choose a non-empty file",
                              caption='Empty File')
                return

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

            self.canvas.blank_file = False

            self.network = network1
            self.devices = devices1
            self.names = names1
            self.monitors = monitors1
            self.error_store = error_db

            self.monitored_devices, self.unmonitored_devices = \
                self.monitors.get_signal_names()

            self.add_monitor_choice.Destroy()
            self.add_monitor_choice = wx.Choice(
                self, wx.ID_ANY, size=wx.Size(
                    100, 20), choices=self.unmonitored_devices)
            self.add_monitor_box.Insert(0, self.add_monitor_choice)
            self.remove_monitor_choice.Destroy()
            self.remove_monitor_choice = wx.Choice(
                self, wx.ID_ANY, size=wx.Size(
                    100, 20), choices=self.monitored_devices)
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
                        label=_("On"),
                        style=wx.RB_GROUP))
                if(initial_switch_values[i]):
                    self.radiobuttons[-1].SetValue(True)
                # Adds the RadioButton created in the previous line
                self.single_switch_box.Add(self.radiobuttons[-1])
                self.radiobuttons.append(
                    wx.RadioButton(
                        self, wx.ID_ANY, label=_("Off")))
                if(not initial_switch_values[i]):
                    self.radiobuttons[-1].SetValue(True)
                self.single_switch_box.Add(self.radiobuttons[-1])
                self.single_switch_box.Layout()
                self.switch_box.Layout()
                self.side_sizer.Layout()

            self.previous_outputs = []
            for i in range(len(self.monitored_devices)):
                self.previous_outputs.append([])

        self.canvas.reset_camera()

    def display_errors(self, error_db):
        """Create a dialog box with the errors present if there are any."""
        error_report = error_db.report_errors(command_line=False,
                                              file_output=False)
        translated_report = wx.GetTranslation(error_report)
        window = wx.MessageBox(error_report,
                               caption='Errors logged in error_report.txt')

    def toggle_3d(self, event):
        """Toggle whether the signal traces are rendered in 2d or 3d."""
        self.canvas.is_3d = not self.canvas.is_3d
        self.canvas.Refresh()

    def reset_display(self, event):
        """Reset the pan zoom and rotation of the view."""
        self.canvas.reset_camera()
