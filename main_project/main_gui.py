#!/usr/bin/env python3
"""Implement the graphical user interface for the Logic Simulator.

Used in the Logic Simulator project to enable the user to run the simulation
or adjust the network properties.

Classes:
--------
MyGLCanvas - handles all canvas drawing operations.
Gui - configures the main window and all the widgets.
"""
import wx
import wx.stc
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

        # Bind events to the canvas
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)

    def init_gl(self):
        """Configure and initialise the OpenGL context."""
        size = self.GetClientSize()
        self.SetCurrent(self.context)
        GL.glDrawBuffer(GL.GL_BACK)
        GL.glClearColor(0.73, 0.83, 1.0, 0.0)
        GL.glViewport(0, 0, size.width, size.height)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, size.width, 0, size.height, -1, 1)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        GL.glTranslated(self.pan_x, self.pan_y, 0.0)

    def render(self, text):
        """Handle all drawing operations."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        # Draw specified text at position (10, 10)
        self.render_text(text, 10, 10)

        # Draw a sample signal trace
        GL.glColor3f(0.0, 0.0, 1.0)  # signal trace is blue
        GL.glBegin(GL.GL_LINE_STRIP)
        for i in range(10):
            x = (i * 20) + 10
            x_next = (i * 20) + 30
            if i % 2 == 0:
                y = 75
            else:
                y = 100
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

        size = self.GetClientSize()
        text = "".join(["Canvas redrawn on paint event, size is ",
                        str(size.width), ", ", str(size.height)])
        self.render(text)

    def on_size(self, event):
        """Handle the canvas resize event."""
        # Forces reconfiguration of the viewport, modelview and projection
        # matrices on the next paint event
        self.init = False

    def on_mouse(self, event):
        """Handle mouse events."""
        text = ""
        if event.ButtonDown():
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            text = "".join(["Mouse button pressed at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.ButtonUp():
            text = "".join(["Mouse button released at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.Leaving():
            text = "".join(["Mouse left canvas at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.Dragging():
            self.pan_x += event.GetX() - self.last_mouse_x
            self.pan_y -= event.GetY() - self.last_mouse_y
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            self.init = False
            text = "".join(["Mouse dragged to: ", str(event.GetX()),
                            ", ", str(event.GetY()), ". Pan is now: ",
                            str(self.pan_x), ", ", str(self.pan_y)])
        if event.GetWheelRotation() < 0:

            self.init = False

        if event.GetWheelRotation() > 0:

            self.init = False

        if text:
            self.render(text)
        else:
            self.Refresh()  # triggers the paint event

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

    def __init__(self, title):
        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title)

        self.SetIcon(wx.Icon('GUI/CUED Software.png'))
        # Canvas for drawing signals
        self.Maximize(True)

        self.SetBackgroundColour((186, 211, 255))
        self.header_font = wx.Font(
            25, wx.FONTFAMILY_SWISS, wx.NORMAL, wx.FONTWEIGHT_BOLD, False)
        self.label_font = wx.Font(
            10, wx.FONTFAMILY_SWISS, wx.NORMAL, wx.NORMAL, False)

        self.makeLeftSizer()
        self.makeMiddleSizer()
        self.makeRightSizer()

        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.main_sizer.Add(self.left_panel, 3, wx.ALL, 30)
        self.main_sizer.Add(self.middle_panel, 3, wx.ALL, 30)
        self.main_sizer.Add(self.right_panel, 4, wx.ALL, 30)
        self.SetSizer(self.main_sizer)

    def makeLeftSizer(self):
        self.left_panel = wx.Panel(self)
        self.left_panel.SetBackgroundColour((37, 103, 209))
        self.load_btn = wx.Button(self.left_panel, wx.ID_ANY, "Browse Files")
        self.check_btn = wx.Button(self.left_panel, wx.ID_ANY, 'Verify Code')

        left_heading = wx.StaticText(self.left_panel, -1, label="Editor")
        left_heading = self.style(left_heading, self.header_font)

        editor_font = wx.Font(14, wx.MODERN, wx.NORMAL,
                              wx.NORMAL, False, u'Consolas')
        self.input_text = wx.stc.StyledTextCtrl(
            self.left_panel, size=(-1, wx.ALL))
        self.input_text.SetMarginType(1, wx.stc.STC_MARGIN_NUMBER)
        self.input_text.SetMarginWidth(3, 15)
        self.input_text.SetUseHorizontalScrollBar(False)
        self.input_text.StyleSetFont(0, editor_font)
        self.input_text.AppendText("DEVICES {\n\n}\nCONNECTIONS {\n\n}")

        self.error_text = wx.TextCtrl(self.left_panel, wx.ID_ANY, size=(
            -1, wx.ALL), style=wx.TE_MULTILINE | wx.TE_READONLY, value="Click run to check for errors")
        self.error_text.SetFont(editor_font)
        self.error_text.SetStyle(0, -1, wx.TextAttr(wx.RED))

        self.left_sizer = wx.BoxSizer(wx.VERTICAL)

        self.left_sizer.Add(left_heading, 0, wx.ALL | wx.ALIGN_CENTER, 10)
        row = wx.BoxSizer(wx.HORIZONTAL)
        row.Add(self.load_btn, 1, wx.ALIGN_LEFT, 5)
        row.Add(self.check_btn, 1, wx.ALIGN_RIGHT, 5)
        self.left_sizer.Add(row, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        self.left_sizer.Add(self.input_text, 6, wx.EXPAND | wx.ALL, 10)
        self.left_sizer.Add(self.error_text, 1, wx.EXPAND | wx.ALL, 10)

        self.left_panel.SetSizer(self.left_sizer)

        self.load_btn.Bind(wx.EVT_BUTTON, self.LoadFile)
        self.check_btn.Bind(wx.EVT_BUTTON, self.CheckText)

    def makeMiddleSizer(self):
        self.middle_panel = wx.Panel(self)
        self.middle_panel.SetBackgroundColour((37, 103, 209))

        self.middle_sizer = wx.BoxSizer(wx.VERTICAL)
        self.middle_panel.SetSizer(self.middle_sizer)
    
        self.middle_panel.Hide()
        self.Layout()

    def makeRightSizer(self):
        self.right_panel = wx.Panel(self)
        self.right_panel.SetBackgroundColour((37, 103, 209))
        self.right_sizer = wx.BoxSizer(wx.VERTICAL)

        right_heading = wx.StaticText(self.right_panel, -1, label="Output")
        right_heading.SetFont(self.header_font)
        right_heading.SetForegroundColour((255, 255, 255))
        self.right_sizer.Add(right_heading, 0, wx.ALL | wx.ALIGN_CENTER, 10)

        self.right_panel.SetSizer(self.right_sizer)
        self.right_panel.Hide()
        self.Layout()

    def CheckText(self, event):
        self.names = Names()
        self.devices = Devices(self.names)
        self.network = Network(self.names, self.devices)
        self.monitors = Monitors(self.names, self.devices, self.network)
        self.scanner = Scanner(self.input_text.GetValue(), self.names, True)
        self.parser = Parser(self.names, self.devices,
                             self.network, self.monitors, self.scanner)
        status = None
        try:
            status = self.parser.parse_network()
        except:
            pass

        self.error_text.Clear()
        if self.scanner.total_error_string == "":
            self.error_text.AppendText("No errors found")
        else:
            self.error_text.AppendText(self.scanner.total_error_string)
            self.error_text.SetStyle(0, -1, wx.TextAttr(wx.RED))

            self.middle_sizer.Clear()
            self.middle_panel.Hide()
            self.right_panel.Hide()
            self.Layout()
            return

        if status == True and len(self.devices.devices_list) > 0:
        
            middle_heading = wx.StaticText(self.middle_panel, label="Options")
            middle_heading = self.style(middle_heading, self.header_font)
            self.middle_sizer.Add(middle_heading, 0, wx.ALL | wx.ALIGN_CENTER, 10)

            self.toggle_right_panel = wx.ToggleButton(self.middle_panel, label="show circuit (experimental)")
            self.toggle_right_panel.Bind(wx.EVT_TOGGLEBUTTON, self.OnRightPanelToggle)
            self.middle_sizer.Add(self.toggle_right_panel, 0, wx.ALL | wx.ALIGN_RIGHT, 5)
        
            self.device_info = wx.FlexGridSizer(4, 0, 15)
            # ------------- HEADINGS ------------- #
            label = wx.StaticText(self.middle_panel, label="Name")
            label = self.style(label, self.label_font)
            self.device_info.Add(label, 0,
                                 wx.EXPAND | wx.ALL, 0)

            label = wx.StaticText(self.middle_panel, label="Type")
            label = self.style(label, self.label_font)
            self.device_info.Add(label, 0,
                                 wx.EXPAND | wx.ALL, 0)

            label = wx.StaticText(self.middle_panel, label="Inputs")
            label = self.style(label, self.label_font)
            self.device_info.Add(label, 0,
                                 wx.EXPAND | wx.ALL, 0)
                                 
            label = wx.StaticText(self.middle_panel, label="Outputs")
            label = self.style(label, self.label_font)
            self.device_info.Add(label, 0,
                                 wx.EXPAND | wx.ALL, 0)

            for device in self.devices.devices_list:

                name = self.devices.names.get_name_string(device.device_id)

                label = wx.StaticText(
                    self.middle_panel, label=self.devices.names.get_name_string(device.device_id))
                label = self.style(label, self.label_font)
                self.device_info.Add(label, 0,
                                     wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
                label = wx.StaticText(
                    self.middle_panel, label=self.devices.names.get_name_string(device.device_kind))
                label = self.style(label, self.label_font)
                self.device_info.Add(label, 0,
                                     wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
                label = wx.StaticText(self.middle_panel, label=name)
                label = self.style(label, self.label_font)
                self.device_info.Add(label, 0,
                                     wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)

                device.monitor_btn = wx.ToggleButton(
                    self.middle_panel, label="monitor {}".format(name))
                device.monitor_btn.Bind(
                    wx.EVT_TOGGLEBUTTON, self.OnToggleClick)
                device.monitor_btn.SetForegroundColour('white')

                if name in self.monitors.get_signal_names()[0]:
                    device.monitor_btn.SetValue(True)
                    device.monitor_btn.SetBackgroundColour('#3ac10d')
                else:
                    device.monitor_btn.SetBackgroundColour('#e0473a')

                self.device_info.Add(device.monitor_btn, 1,
                                     wx.ALL | wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL, 5)

            # ----------- SET INITIAL SWITCH STATES ------------ #
            self.switch_options = wx.FlexGridSizer(2)
            for device in self.devices.devices_list:
                if device.device_kind != self.devices.SWITCH:
                    continue
                name = self.devices.names.get_name_string(device.device_id)

                label = wx.StaticText(self.middle_panel, 1, label=name)
                label = self.style(label,self.label_font)
                self.switch_options.Add(label, 1,
                                        wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)

                device.switch_btn = wx.ToggleButton(
                    self.middle_panel, label="initial switch state")
                device.switch_btn.Bind(wx.EVT_TOGGLEBUTTON, self.OnToggleClick)
                device.switch_btn.SetForegroundColour('white')
                if device.switch_state:
                    device.switch_btn.SetValue(True)
                    device.switch_btn.SetBackgroundColour('#3ac10d')
                else:
                    device.switch_btn.SetBackgroundColour('#e0473a')

                self.switch_options.Add(device.switch_btn, 1,
                                        wx.ALL, 5)

            self.middle_sizer.Insert(1, self.switch_options, 0,
                                     wx.ALL | wx.ALIGN_CENTER, 30)
            self.middle_sizer.Insert(1, self.device_info, 0,
                                     wx.ALL | wx.ALIGN_CENTER, 30)
                        
            simulate_btn = wx.Button(self.middle_panel, label="Simulate!")
            self.middle_sizer.Add(simulate_btn, 0,
                                     wx.ALL | wx.EXPAND, 30)
            self.middle_panel.Show()
            self.Layout()
            
    def OnRightPanelToggle(self, event):
        obj = event.GetEventObject()
        if obj.GetValue():
            self.right_panel.Show()
        else:
            self.right_panel.Hide()
        self.Layout()


    def OnToggleClick(self, event):
        obj = event.GetEventObject()
        if obj.GetValue():
            obj.SetBackgroundColour('#3ac10d')
        else:
            obj.SetBackgroundColour('#e0473a')

    def style(self, obj, font, fgcolour='white', bgcolour=None):
        obj.SetForegroundColour(fgcolour)
        obj.SetBackgroundColour(bgcolour)
        obj.SetFont(font)
        return obj


    def LoadFile(self, event):

        # otherwise ask the user what new file to open
        with wx.FileDialog(self, "Open file", wildcard="TXT files (*.txt)|*.txt",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            fileDialog.SetSize((120,80))

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind

            # Proceed loading the file chosen by the user
            pathname = fileDialog.GetPath()
            try:
                with open(pathname, 'r') as f:
                    self.input_text.ClearAll()
                    self.input_text.AppendText(f.read())
            except IOError:
                wx.LogError("Cannot open file '%s'." % pathname)