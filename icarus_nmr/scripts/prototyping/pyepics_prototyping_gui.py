

#!/bin/env python
"""
Icarus Client (High Pressure Apparatus Client Level)
dates: Nov 2017 - Sept 2018
by  Valentyn Stadnytskyi @ National Institutes of Health


"""
__version__ = '0.0.0'



import psutil, os
p = psutil.Process(os.getpid())
import platform #https://stackoverflow.com/questions/110362/how-can-i-find-the-current-os-in-python
if platform.system() == 'Windows':
    p.nice(psutil.NORMAL_PRIORITY_CLASS)
elif platform.system() == 'Linux':
    p.nice(0) #source: https://psutil.readthedocs.io/en/release-2.2.1/
# psutil.ABOVE_NORMAL_PRIORITY_CLASS
# psutil.BELOW_NORMAL_PRIORITY_CLASS
# psutil.HIGH_PRIORITY_CLASS
# psutil.IDLE_PRIORITY_CLASS
# psutil.NORMAL_PRIORITY_CLASS
# psutil.REALTIME_PRIORITY_CLASS
from time import time,sleep,clock
import sys

import os.path
import struct
from pdb import pm
import traceback
from time import gmtime, strftime
import logging

#from setting import setting
import wx
import epics
import epics.wx
from logging import debug,warn,info,error
from pdb import pm
import icarus_nmr
print(icarus_nmr.__file__)
from icarus_nmr.pyepics import PVImage, PVToggleButton

import matplotlib
if platform.system() == 'Windows':
    matplotlib.use('TkAgg')
else:
    matplotlib.use('WxAgg')

#threading library manual https://docs.python.org/3/library/threading.html
#def round_sig(x,sig=4):   return round(x,sig-int(floor(log10(abs(x))))-1)

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

"""Graphical User Interface"""
import platform
class GUI(wx.Frame):

    def __init__(self,server_name = ''):
        self.server_name = server_name

        self.name = platform.node() + '_'+'GUI'
        self.lastN_history = 0
        self.lastM_history = 10000
        self.labels = {}
        self.fields = {}
        self.sizers = {}
        self.box_sizer = {}
        self.sizer_main = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_left = wx.BoxSizer(wx.VERTICAL)
        self.sizer_middle = wx.BoxSizer(wx.VERTICAL)
        self.sizer_right = wx.BoxSizer(wx.VERTICAL)

        self.box_sizer[b'graph0'] = wx.BoxSizer(wx.VERTICAL)
        self.box_sizer[b'graph1'] = wx.BoxSizer(wx.VERTICAL)
        self.box_sizer[b'graph2'] = wx.BoxSizer(wx.VERTICAL)
        self.box_sizer[b'graph3'] = wx.BoxSizer(wx.VERTICAL)

        self.box_sizer[b'counters'] = wx.BoxSizer(wx.VERTICAL)
        self.box_sizer[b'table'] = wx.BoxSizer(wx.VERTICAL)
        self.box_sizer[b'status'] = wx.BoxSizer(wx.VERTICAL)
        self.box_sizer[b'controls'] = wx.BoxSizer(wx.VERTICAL)
        self.box_sizer[b'measurements'] = wx.BoxSizer(wx.VERTICAL)
        self.box_sizer[b'auxiliary'] = wx.BoxSizer(wx.VERTICAL)
        self.box_sizer[b'faults_warnings'] = wx.BoxSizer(wx.VERTICAL)

        self.create_GUI()

    def create_GUI(self):

        #self.selectedPressureUnits = 'kbar'
        self.xs_font = 10
        self.s_font = 12
        self.m_font = 16
        self.l_font = 24
        self.xl_font = 32
        self.xl_font = 60
        self.wx_xs_font = wx_xs_font=wx.Font(self.xs_font,wx.DEFAULT,wx.NORMAL,wx.NORMAL)
        self.wx_s_font = wx_s_font=wx.Font(self.s_font,wx.DEFAULT,wx.NORMAL,wx.NORMAL)
        self.wx_m_font = wx_m_font=wx.Font(self.m_font,wx.DEFAULT,wx.NORMAL,wx.NORMAL)
        self.wx_l_font = wx_l_font=wx.Font(self.l_font,wx.DEFAULT,wx.NORMAL,wx.NORMAL)
        self.wx_xl_font = wx_xl_font=wx.Font(self.xl_font,wx.DEFAULT,wx.NORMAL,wx.NORMAL)
        self.wx_xxl_font = wx_xxl_font=wx.Font(self.xl_font,wx.DEFAULT,wx.NORMAL,wx.NORMAL)



        frame = wx.Frame.__init__(self, None, wx.ID_ANY, "High Pressure Control Panel")#, size = (192,108))#, style= wx.SYSTEM_MENU | wx.CAPTION)

        self.panel = wx.Panel(self, wx.ID_ANY, style=wx.BORDER_THEME, size = (400,200))
        #self.panel.Bind(wx.EVT_SIZE, self.on_size_change)
        self.SetBackgroundColour('white')
        self.Bind(wx.EVT_CLOSE, self.on_quit)
        self.statusbar = self.CreateStatusBar() # Will likely merge the two fields unless we can think of a reason to keep them split
        self.statusbar.SetStatusText('This goes field one')
        #self.statusbar.SetStatusText('Field 2 here!', 1)
        self.statusbar.SetBackgroundColour('green')


        ###########################################################################
        ##MENU for the GUI
        ###########################################################################
        file_item = {}
        about_item = {}

        self.setting_item = {}



        menubar = wx.MenuBar()
        fileMenu = wx.Menu()
        file_item[0] = fileMenu.Append(wx.ID_EXIT, 'Quit', 'Quit application')
        self.Bind(wx.EVT_MENU, self.on_quit, file_item[0])

        self.settingMenu = wx.Menu()
        #self.setting_item[0] = settingMenu.Append(wx.NewId(),  'server settings')
        self.Bind(wx.EVT_MENU_OPEN, self.on_server_settings)#3self.setting_item[0])


        aboutMenu = wx.Menu()
        about_item[0]= aboutMenu.Append(wx.ID_ANY,  'About')
        self.Bind(wx.EVT_MENU, self._on_about, about_item[0])
        #self.Bind(wx.EVT_MENU, self._on_server_about, about_item[1])

        menubar.Append(fileMenu, '&File')

        menubar.Append(self.settingMenu, '&Settings')
        menubar.Append(aboutMenu, '&About')


        self.SetMenuBar(menubar)


        self.Centre()
        self.Show(True)
        sizer = wx.GridBagSizer(hgap = 0, vgap = 0)#(13, 11)

        ###########################################################################
        ###MENU ENDS###
        ###########################################################################

        ###########################################################################
        ###FIGUREs####
        ###########################################################################

        self.labels[b'button1'] = wx.StaticText(self.panel, label= "button1 (press to disable)", size = (200,-1))
        self.labels[b'button1'].SetFont(wx_s_font)
        self.labels[b'button1'].SetBackgroundColour(wx.Colour(240, 240, 240))
        self.fields[b'button1_1'] = epics.wx.PVButton(self.panel, pv=f"{self.server_name}:button1", pushValue = 1, size = (200,-1),label="1")
        self.fields[b'button1_0'] = epics.wx.PVButton(self.panel, pv=f"{self.server_name}:button1", pushValue = 0, size = (200,-1),label="0")
        self.fields[b'button1_ind'] = epics.wx.PVText(self.panel, pv=f"{self.server_name}:button1", size = (200,-1))

        self.sizers[b'button1'] = wx.BoxSizer(wx.HORIZONTAL)
        self.sizers[b'button1'].Add(self.labels[b'button1'],0)
        self.sizers[b'button1'].Add(self.fields[b'button1_0'],0)
        self.sizers[b'button1'].Add(self.fields[b'button1_1'],0)
        self.sizers[b'button1'].Add(self.fields[b'button1_ind'],0)

        self.labels[b'toggle_button1_old'] = wx.StaticText(self.panel, label= "old_toggle_button1", size = (200,-1))
        self.labels[b'toggle_button1_old'].SetFont(wx_m_font)
        self.labels[b'toggle_button1_old'].SetBackgroundColour(wx.Colour(240, 240, 240))
        self.fields[b'toggle_button1_old_1'] = epics.wx.PVButton(self.panel, pv=f"{self.server_name}:toggle_button1", disablePV = f"{self.server_name}:button1",pushValue = 1, size = (200,-1),label="1")
        self.fields[b'toggle_button1_old_0'] = epics.wx.PVButton(self.panel, pv=f"{self.server_name}:toggle_button1", disablePV = f"{self.server_name}:button1",pushValue = 0, size = (200,-1),label="0")
        self.fields[b'toggle_button1_old_ind'] = epics.wx.PVText(self.panel, pv=f"{self.server_name}:toggle_button1", size = (200,-1))

        self.sizers[b'toggle_button1_old'] = wx.BoxSizer(wx.HORIZONTAL)
        self.sizers[b'toggle_button1_old'].Add(self.labels[b'toggle_button1_old'],0)
        self.sizers[b'toggle_button1_old'].Add(self.fields[b'toggle_button1_old_0'],0)
        self.sizers[b'toggle_button1_old'].Add(self.fields[b'toggle_button1_old_1'],0)
        self.sizers[b'toggle_button1_old'].Add(self.fields[b'toggle_button1_old_ind'],0)

        self.labels[b'toggle_button1'] = wx.StaticText(self.panel, label= "new_toggle_button1", size = (200,-1))
        self.labels[b'toggle_button1'].SetFont(wx_m_font)
        self.labels[b'toggle_button1'].SetBackgroundColour(wx.Colour(240, 240, 240))
        self.fields[b'toggle_button1'] = PVToggleButton(self.panel, pv=f"{self.server_name}:toggle_button1", disablePV = f"{self.server_name}:button1", size = (200,-1), buttonLabels = ['Change PV to 1','Change PV to 0'], stateColors = [(0,255,0),(255,0,0)])
        self.fields[b'toggle_button1_ind'] = epics.wx.PVText(self.panel, pv=f"{self.server_name}:toggle_button1", size = (200,-1))

        self.sizers[b'toggle_button1'] = wx.BoxSizer(wx.HORIZONTAL)
        self.sizers[b'toggle_button1'].Add(self.labels[b'toggle_button1'],0)
        self.sizers[b'toggle_button1'].Add(self.fields[b'toggle_button1'],0)
        self.sizers[b'toggle_button1'].Add(self.fields[b'toggle_button1_ind'],0)



        self.sizer_left.Add(self.sizers[b'button1'],0)
        self.sizer_left.Add(self.sizers[b'toggle_button1_old'],0)
        self.sizer_left.Add(self.sizers[b'toggle_button1'],0)

        #self.sizer_middle.Add(self.sizers['graph3'],0)


        #self.sizer_right.Add(self.sizers[b'digital_indicators'])




        self.sizer_main.Add(self.sizer_left,0)
        self.sizer_main.Add(self.sizer_middle,0)
        self.sizer_main.Add(self.sizer_right,0)

        self.Center()
        self.Show()

        self.panel.SetSizer(self.sizer_main)
        self.sizer_main.Fit(self)
        self.Layout()
        self.panel.Layout()
        self.panel.Fit()
        self.Fit()
        self.Update()
    #----------------------------------------------------------------------


    def on_size_change(self,event):
        """
        method called when user changes the size of the window and underlying panel.
        """
        self.panel_width,self.panel_height = event.GetSize()
        print ("Width =",self.panel_width,"Height =",self.panel_height)
        w = self.panel_width
        h = self.panel_height
        try:
            self.fields['graph0'].im_size_show = (int((w-384)/2),int(h/5))
            self.fields['graph1'].im_size_show = (int((w-384)/2),int(h/5))
            self.fields['graph2'].im_size_show = (int((w-384)/2),int(h/5))
            self.fields['graph3'].im_size_show = (int((w-384)/2),int(h))
        except:
            pass

        #self.panel.SetSizer(self.sizer_main)
        #self.sizer_main.Fit(self)
        self.Layout()
        self.panel.Layout()
        #self.panel.Fit()


    def _on_about(self,event):
        """
        method executed when a user click on "About" button in the menu.
        """
        message = str(__doc__)
        wx.MessageBox(message,'About', wx.OK | wx.ICON_INFORMATION)

    def on_quit(self,event):
        """
        method executed when a user closes the window.
        """
        del self
        os._exit(1)

    def on_server_settings(self,event):
        print("on_server_settings Clicked")
        pass


if __name__ == "__main__":
    from pdb import pm
    import logging
    from tempfile import gettempdir
    import sys
    import socket
    server_name = f'pyepics_prototyping'


    print(server_name)

    app = wx.App(redirect=False)
    panel = GUI(server_name = server_name)

    app.MainLoop()
