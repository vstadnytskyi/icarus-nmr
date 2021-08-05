#!/bin/env python
"""
Icarus Client (High Pressure Apparatus Client Level)
dates: Nov 2017 - Sept 2018
by Gabriel Anfinrud, Philip Anfinrud, Valentyn Stadnytskyi @ National Institutes of Health

current version: 4.3.1
last updated: November 16, 2018


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

from icarus_nmr.pyepics import PVImage

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

    def __init__(self, caserver_name = ''):
        self.caserver_name = caserver_name
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
        self.panel = wx.Panel(self, wx.ID_ANY, style=wx.BORDER_THEME)#, size = (1920,1080))
        self.SetBackgroundColour('white')
        self.Bind(wx.EVT_CLOSE, self.onQuit)
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
        self.Bind(wx.EVT_MENU, self.onQuit, file_item[0])


        aboutMenu = wx.Menu()
        about_item[0]= aboutMenu.Append(wx.ID_ANY,  'About')
        self.Bind(wx.EVT_MENU, self._on_about, about_item[0])
        #self.Bind(wx.EVT_MENU, self._on_server_about, about_item[1])

        menubar.Append(fileMenu, '&File')

        #menubar.Append(self.settingMenu, '&Settings')
        menubar.Append(aboutMenu, '&About')


        self.SetMenuBar(menubar)


        self.Centre()
        self.Show(True)
        sizer = wx.GridBagSizer(hgap = 0, vgap = 0)#(13, 11)

        ###########################################################################
        ###MENU ENDS###
        ###########################################################################

        ###########################################################################
        ###FIGURE####
        ###########################################################################
        #import gc
        #gc.set_debug(gc.DEBUG_LEAK)

        self.sizers['graph0'] = wx.BoxSizer(wx.VERTICAL)
        self.labels['graph0']  = wx.StaticText(self.panel, label= 'Field 2 label', style = wx.ALIGN_CENTER)
        self.fields['graph0']  = PVImage(self.panel, pv=f'{self.caserver_name}:image_pre', im_size = (768,216))
        self.sizers['graph0'] .Add(self.labels['graph0']  , 0)
        self.sizers['graph0'] .Add(self.fields['graph0']  , 0)

        self.sizers['graph1'] = wx.BoxSizer(wx.VERTICAL)
        self.labels['graph1']  = wx.StaticText(self.panel, label= 'Field 2 label', style = wx.ALIGN_CENTER)
        self.fields['graph1']  = PVImage(self.panel, pv=f'{self.caserver_name}:image_depre', im_size = (768,216))
        self.sizers['graph1'] .Add(self.labels['graph1']  , 0)
        self.sizers['graph1'] .Add(self.fields['graph1']  , 0)

        self.sizers['graph2'] = wx.BoxSizer(wx.VERTICAL)
        self.labels['graph2']  = wx.StaticText(self.panel, label= 'Field 2 label', style = wx.ALIGN_CENTER)
        self.fields['graph2']  = PVImage(self.panel, pv=f'{self.caserver_name}:image_period', im_size = (768,216))
        self.sizers['graph2'] .Add(self.labels['graph2']  , 0)
        self.sizers['graph2'] .Add(self.fields['graph2']  , 0)

        self.sizers['graph3'] = wx.BoxSizer(wx.VERTICAL)
        self.labels['graph3']  = wx.StaticText(self.panel, label= 'Field 2 label', style = wx.ALIGN_CENTER)
        self.fields['graph3']  = PVImage(self.panel, pv=f'{self.caserver_name}:image_logging', im_size = (768,1080))
        self.sizers['graph3'] .Add(self.labels['graph3']  , 0)
        self.sizers['graph3'] .Add(self.fields['graph3']  , 0)

        ###########################################################################
        ###FIGURE ENDS####
        ###########################################################################


        ###########################################################################
        ###On Button Press###
        ###########################################################################
        ###Sidebar###

        # self.gui_sizers[b'pressure'] = wx.BoxSizer(wx.HORIZONTAL)
        # self.gui_sizers[b'pressure'].Add(self.gui_labels[b'pressure'],0)
        #
        # self.gui_labels[b'pressure'] = wx.StaticText(self.panel, label= "Pressure [kbar]", size = (400,-1))
        #
        # self.gui_labels[b'pressure'].SetFont(wx_l_font)
        #
        # self.gui_labels[b'pressure_target'] = wx.StaticText(self.panel, label= "Target:", size = (200,-1))
        #
        # self.gui_labels[b'pressure_target'].SetFont(wx_l_font)
        # self.gui_labels[b'pressure_target'].SetBackgroundColour(wx.Colour(240, 240, 240))
        #
        #
        # self.gui_fields[b'pressure_target'] = wx.StaticText(self.panel, label= str(nan), size = (200,-1))
        #
        # self.gui_fields[b'pressure_target'].SetFont(wx_l_font)
        # self.gui_fields[b'pressure_target'].SetBackgroundColour(wx.Colour(240, 240, 240))
        #
        # self.gui_sizers[b'pressure_target'] = wx.BoxSizer(wx.HORIZONTAL)
        # self.gui_sizers[b'pressure_target'].Add(self.gui_labels[b'pressure_target'],0)
        # self.gui_sizers[b'pressure_target'].Add(self.gui_fields[b'pressure_target'],0)
        #
        # self.gui_labels[b'pressure_sample'] = wx.StaticText(self.panel, label= "Sample:", size = (200,-1))
        #
        # self.gui_labels[b'pressure_sample'].SetFont(wx_l_font)
        # #self.samplePressureLabel.Hide()
        #
        # self.gui_fields[b'pressure_sample'] = wx.StaticText(self.panel, label= str(nan), size = (200,-1))
        # self.gui_fields[b'pressure_sample'].SetFont(wx_l_font)
        # #self.samplePressure.Hide()
        #
        # self.gui_sizers[b'pressure_sample'] = wx.BoxSizer(wx.HORIZONTAL)
        # self.gui_sizers[b'pressure_sample'].Add(self.gui_labels[b'pressure_sample'],0)
        # self.gui_sizers[b'pressure_sample'].Add(self.gui_fields[b'pressure_sample'],0)
        #
        # self.gui_labels[b'period_duratrion'] = wx.StaticText(self.panel, label= "period (s):", size = (200,25))
        # #sizer.Add(self.gui_labels[b'period_duratrion'] , pos=(5, 8),  span=(1,2), flag=wx.ALIGN_CENTER_VERTICAL, border=5, )
        # self.gui_labels[b'period_duratrion'].SetFont(wx_m_font)
        # period_duration_string = 'nan'
        # self.gui_fields[b'period_duratrion'] = wx.StaticText(self.panel, label= period_duration_string, size = (200,25))
        # #sizer.Add(self.gui_fields[b'period_duratrion'] , pos=(5, 10),  span=(1,2), flag=wx.ALIGN_CENTER_VERTICAL, border=5, )
        # self.gui_fields[b'period_duratrion'].SetFont(wx_m_font)
        # self.gui_fields[b'period_duratrion'].SetBackgroundColour(wx.Colour(240, 240, 240))
        # self.gui_labels[b'period_duratrion'].SetBackgroundColour(wx.Colour(240, 240, 240))
        #
        # self.gui_sizers[b'period_duratrion'] = wx.BoxSizer(wx.HORIZONTAL)
        # self.gui_sizers[b'period_duratrion'].Add(self.gui_labels[b'period_duratrion'],0)
        # self.gui_sizers[b'period_duratrion'].Add(self.gui_fields[b'period_duratrion'],0)
        #
        #
        #
        # self.gui_labels[b'delay_width'] = wx.StaticText(self.panel, label= "delay (ms):", size = (200,25))
        # #sizer.Add(self.gui_labels[b'delay_width']  , pos=(6, 8),  span=(1,2), flag=wx.ALIGN_CENTER_VERTICAL, border=5, )
        # self.gui_labels[b'delay_width'] .SetFont(wx_m_font)
        # delay_width_string = 'nan'
        # self.gui_fields[b'delay_width']  = wx.StaticText(self.panel, label= delay_width_string, size = (200,25))
        # #sizer.Add(self.gui_fields[b'delay_width'] , pos=(6, 10),  span=(1,2), flag=wx.ALIGN_CENTER_VERTICAL, border=5, )
        # self.gui_fields[b'delay_width'].SetFont(wx_m_font)
        #
        # self.gui_sizers[b'delay_width'] = wx.BoxSizer(wx.HORIZONTAL)
        # self.gui_sizers[b'delay_width'].Add(self.gui_labels[b'delay_width'],0)
        # self.gui_sizers[b'delay_width'].Add(self.gui_fields[b'delay_width'],0)
        #
        #
        # self.gui_labels[b'pressurize_width'] = wx.StaticText(self.panel, label= "pressurize (ms):", size = (200,25))
        # #sizer.Add(self.gui_labels[b'pressurize_width'] , pos=(7, 8),  span=(1,2), flag=wx.ALIGN_CENTER_VERTICAL, border=5, )
        # self.gui_labels[b'pressurize_width'].SetFont(wx_m_font)
        # pressurize_width_string = 'nan'
        # self.gui_fields[b'pressurize_width'] = wx.StaticText(self.panel, label= pressurize_width_string, size = (200,25))
        # #sizer.Add(self.gui_fields[b'pressurize_width'] , pos=(7, 10),  span=(1,2), flag=wx.ALIGN_CENTER_VERTICAL, border=5, )
        # self.gui_fields[b'pressurize_width'].SetFont(wx_m_font)
        # self.gui_fields[b'pressurize_width'].SetBackgroundColour(wx.Colour(240, 240, 240))
        # self.gui_labels[b'pressurize_width'].SetBackgroundColour(wx.Colour(240, 240, 240))
        #
        # self.gui_sizers[b'pressurize_width'] = wx.BoxSizer(wx.HORIZONTAL)
        # self.gui_sizers[b'pressurize_width'].Add(self.gui_labels[b'pressurize_width'],0)
        # self.gui_sizers[b'pressurize_width'].Add(self.gui_fields[b'pressurize_width'],0)
        #
        # self.gui_labels[b'depressurize_width'] = wx.StaticText(self.panel, label= "depressurize (ms):", size = (200,25))
        # sizer.Add(self.gui_labels[b'depressurize_width'] , pos=(8, 8),  span=(1,2), flag=wx.ALIGN_CENTER_VERTICAL, border=5, )
        # self.gui_labels[b'depressurize_width'].SetFont(wx_m_font)
        # depressurize_width_string = 'nan'
        # self.gui_fields[b'depressurize_width'] = wx.StaticText(self.panel, label= depressurize_width_string)
        # sizer.Add(self.gui_fields[b'depressurize_width'] , pos=(8, 10),  span=(1,2), flag=wx.ALIGN_CENTER_VERTICAL, border=5, )
        # self.gui_fields[b'depressurize_width'].SetFont(wx_m_font)
        #
        # self.gui_sizers[b'depressurize_width'] = wx.BoxSizer(wx.HORIZONTAL)
        # self.gui_sizers[b'depressurize_width'].Add(self.gui_labels[b'depressurize_width'],0)
        # self.gui_sizers[b'depressurize_width'].Add(self.gui_fields[b'depressurize_width'],0)
        #
        # self.box_sizer[b'measurements'].Add(self.gui_sizers[b'pressure'],0)
        # self.box_sizer[b'measurements'].Add(self.gui_sizers[b'pressure_target'],0)
        # self.box_sizer[b'measurements'].Add(self.gui_sizers[b'pressure_sample'],0)
        # self.box_sizer[b'measurements'].Add(self.gui_sizers[b'period_duratrion'],0)
        # self.box_sizer[b'measurements'].Add(self.gui_sizers[b'delay_width'],0)
        # self.box_sizer[b'measurements'].Add(self.gui_sizers[b'pressurize_width'],0)
        # self.box_sizer[b'measurements'].Add(self.gui_sizers[b'depressurize_width'],0)
        #
        # lblList = ['Manual', 'Pulsed', 'Console']
        #
        # self.gui_fields[b'operating_mode_rbox'] = wx.RadioBox(self.panel, label = 'Operating Mode', choices = lblList,
        #                         majorDimension = 1, style = wx.RA_SPECIFY_ROWS|wx.ALIGN_CENTER_HORIZONTAL, size = (400,-1))
        #
        # self.gui_sizers[b'operating_mode_rbox'] = wx.BoxSizer(wx.HORIZONTAL)
        # self.gui_sizers[b'operating_mode_rbox'].Add(self.gui_fields[b'operating_mode_rbox'],0)
        # try:
        #     flag = icarus_AL.ctrls.trigger_mode
        # except:
        #     flag = -1
        #     error(traceback.format_exc())
        #
        # if flag!= None and flag >=0:
        #     self.gui_fields[b'operating_mode_rbox'].SetSelection(icarus_AL.trigger_mode)
        #     self.gui_fields[b'operating_mode_rbox'].Enable()
        # else:
        #     self.gui_fields[b'operating_mode_rbox'].SetSelection(0)
        #     self.gui_fields[b'operating_mode_rbox'].Disable()
        #
        # sizer.Add(self.gui_fields[b'operating_mode_rbox'] , pos=(9, 8), span=(2,4), flag=wx.TOP|wx.RIGHT|wx.ALIGN_CENTER_HORIZONTAL, border=5)
        # self.gui_fields[b'operating_mode_rbox'].Bind(wx.EVT_RADIOBOX,self.onRadioBox)
        # self.gui_fields[b'operating_mode_rbox'].SetFont(wx_m_font)
        #
        #
        # self.image_red = wx.Image(resource_path('images/shutdown_red.png'), wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        # self.image_yellow = wx.Image(resource_path('images/shutdown_yellow.png'), wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        #
        # self.gui_fields[b'shutdown_button'] = wx.StaticBitmap(self.panel, -1,self.image_red, (1, 1), (self.image_red.GetWidth(), self.image_red.GetHeight()))
        #
        # sizer.Add(self.gui_fields[b'shutdown_button'] , pos=(13, 8), flag=wx.ALIGN_CENTER, border=1, span = (2,4))
        # self.gui_fields[b'shutdown_button'].Bind(wx.EVT_LEFT_DOWN, self.onShutdownButton)
        #
        # self.gui_sizers[b'shutdown_button'] = wx.BoxSizer(wx.HORIZONTAL)
        # #self.gui_sizers[b'shutdown_button'].Add(self.gui_labels[b'shutdown_button'],0)
        # self.gui_sizers[b'shutdown_button'].Add(self.gui_fields[b'shutdown_button'],0)
        #
        # self.gui_fields[b'pump_button']  = wx.ToggleButton(self.panel, label="Pump: Turn On", size = (300,50))
        # sizer.Add(self.gui_fields[b'pump_button'] , pos=(15, 8), span = (2,4), flag=wx.ALIGN_CENTER, border=5)
        # self.gui_fields[b'pump_button'].Bind(wx.EVT_TOGGLEBUTTON, self.on_pump_state)
        # self.gui_fields[b'pump_button'].SetBackgroundColour((243,122,123))
        # self.gui_fields[b'pump_button'].SetFont(wx_m_font)
        # #self.PumpButton.Hide()
        # #self.PumpButton.SetForegroundColour('white')
        #
        # self.gui_sizers[b'pump_button'] = wx.BoxSizer(wx.HORIZONTAL)
        # #self.gui_sizers[b'shutdown_button'].Add(self.gui_labels[b'shutdown_button'],0)
        # self.gui_sizers[b'pump_button'].Add(self.gui_fields[b'pump_button'],0)
        #
        # self.gui_fields[b'pressurize_button']  = wx.ToggleButton(self.panel, label="Pressurize: \n    Open", size = (145,100))
        # sizer.Add(self.gui_fields[b'pressurize_button'] , pos=(18, 8), span = (2,2), flag=wx.ALIGN_CENTER_HORIZONTAL, border=5)
        # self.gui_fields[b'pressurize_button'].Bind(wx.EVT_TOGGLEBUTTON, self.on_pressurize_state)
        # self.gui_fields[b'pressurize_button'].SetBackgroundColour((243,122,123))
        # self.gui_fields[b'pressurize_button'].SetFont(wx_m_font)
        # #self.PreToggleButton.Hide()
        # #self.PumpButton.SetForegroundColour('white')
        #
        # self.gui_sizers[b'pressurize_button'] = wx.BoxSizer(wx.HORIZONTAL)
        # #self.gui_sizers[b'shutdown_button'].Add(self.gui_labels[b'shutdown_button'],0)
        # self.gui_sizers[b'pressurize_button'].Add(self.gui_fields[b'pressurize_button'],0)
        #
        #
        # self.gui_fields[b'depressurize_button']  = wx.ToggleButton(self.panel, label="Depressurize: \n     Open", size = (145,100))
        #
        # self.gui_fields[b'depressurize_button'].Bind(wx.EVT_TOGGLEBUTTON, self.on_depressurize_state)
        # self.gui_fields[b'depressurize_button'].SetBackgroundColour((243,122,123))
        # self.gui_fields[b'depressurize_button'].SetFont(wx_m_font)
        # #self.DepreToggleButton.Hide()
        # #self.PumpButton.SetForegroundColour('white')
        #
        # self.gui_sizers[b'depressurize_button'] = wx.BoxSizer(wx.HORIZONTAL)
        # #self.gui_sizers[b'shutdown_button'].Add(self.gui_labels[b'shutdown_button'],0)
        # self.gui_sizers[b'depressurize_button'].Add(self.gui_fields[b'depressurize_button'],0, wx.EXPAND | wx.ALL, 20)
        #
        # self.gui_sizers[b'acknowledge_faults'] = wx.BoxSizer(wx.HORIZONTAL)
        # self.gui_fields[b'acknowledge_faults']  = wx.Button(self.panel, label="Acknowledge \n Faults", size = (145,100))
        # self.gui_fields[b'acknowledge_faults'].Bind(wx.EVT_BUTTON, self.on_acknowledge_faults)
        # #self.gui_fields[b'acknowledge_faults'].SetBackgroundColour((243,122,123))
        # self.gui_fields[b'acknowledge_faults'].SetFont(wx_m_font)
        # try:
        #     length = len(icarus_AL.inds.faults)
        # except:
        #     length = 0
        # if length == 0:
        #     self.gui_fields[b'acknowledge_faults'].Hide()
        #
        #
        # self.box_sizer[b'controls'].Add(self.gui_sizers[b'operating_mode_rbox'],0, wx.ALL | wx.ALIGN_CENTER, 20)
        # self.box_sizer[b'controls'].Add(self.gui_sizers[b'shutdown_button'],0, wx.ALL | wx.ALIGN_CENTER , 20)
        # self.box_sizer[b'controls'].Add(self.gui_sizers[b'pump_button'],0, wx.ALL | wx.ALIGN_CENTER, 20)
        # self.button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        # self.button_sizer.Add(self.gui_fields[b'pressurize_button'],0, wx.ALL | wx.ALIGN_CENTER, 20)
        # self.button_sizer.Add(self.gui_fields[b'depressurize_button'],0, wx.ALL | wx.ALIGN_CENTER, 20)
        # self.button_sizer.Add(self.gui_fields[b'acknowledge_faults'],0, wx.ALL | wx.ALIGN_CENTER, 20)
        # self.box_sizer[b'controls'].Add(self.button_sizer,0, wx.ALL | wx.ALIGN_CENTER, 20)
        #
        #
        #
        #
        # self.gui_labels[b'faults_warnings_header'] = wx.StaticText(self.panel, label= "Fault/Warning" )
        # #sizer.Add(self.gui_labels[b'faults_warnings_header'] , pos=(20, 8),  span=(1,4), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL, border=5)
        # self.gui_labels[b'faults_warnings_header'].SetFont(wx_m_font)
        # self.gui_sizers[b'faults_warnings_header'] = wx.BoxSizer(wx.HORIZONTAL)
        # #self.gui_sizers[b'shutdown_button'].Add(self.gui_labels[b'shutdown_button'],0)
        # self.gui_sizers[b'faults_warnings_header'].Add(self.gui_labels[b'faults_warnings_header'],0)
        #
        # try:
        #     msg = str(icarus_al.warnings)
        # except:
        #     msg = 'Nothing to report'
        #
        # self.gui_fields[b'warnings'] = wx.StaticText(self.panel)
        # self.gui_fields[b'warnings'].SetFont(wx_m_font)
        # self.gui_fields[b'warnings'].SetLabel(msg)
        # self.gui_fields[b'warnings'].Wrap(500)
        # self.gui_sizers[b'warnings'] = wx.BoxSizer(wx.HORIZONTAL)
        # self.gui_sizers[b'warnings'].Add(self.gui_fields[b'warnings'],0)
        #
        # try:
        #     msg = str(icarus_al.faults)
        # except:
        #     msg = 'Nothing to report'
        #
        # self.gui_fields[b'faults'] = wx.StaticText(self.panel)
        # self.gui_fields[b'faults'].SetFont(wx_m_font)
        # self.gui_fields[b'faults'].SetLabel(msg)
        # self.gui_fields[b'faults'].Wrap(500)
        # self.gui_sizers[b'faults'] = wx.BoxSizer(wx.HORIZONTAL)
        # self.gui_sizers[b'faults'].Add(self.gui_fields[b'faults'],0)
        #
        #
        # self.box_sizer[b'faults_warnings'].Add(self.gui_sizers[b'faults_warnings_header'],0)
        # self.box_sizer[b'faults_warnings'].Add(self.gui_sizers[b'warnings'],0)
        # self.box_sizer[b'faults_warnings'].Add(self.gui_sizers[b'faults'],0)
        #
        # self.graphs_hidden = False
        # self.gui_fields[b'graphs_hidden'] = wx.Button(self.panel, label="Show/Hide")
        # #sizer.Add(self.ResetButton , pos=(23, 10), flag=wx.TOP|wx.RIGHT|wx.EXPAND, border=1, span = (1,1))
        # self.gui_fields[b'graphs_hidden'].Bind(wx.EVT_BUTTON, self.on_add_remove_widget)
        # self.gui_fields[b'graphs_hidden'].SetFont(wx_xs_font)
        # #self.ResetButton.SetBackgroundColour((243,122,123))
        # #self.ResetButton.Hide()
        # self.gui_sizers[b'graphs_hidden'] = wx.BoxSizer(wx.HORIZONTAL)
        # #self.gui_sizers[b'shutdown_button'].Add(self.gui_labels[b'shutdown_button'],0)
        # self.gui_sizers[b'graphs_hidden'].Add(self.gui_fields[b'graphs_hidden'],0)
        #
        # self.gui_labels[b'last_N_history']  = wx.StaticText(self.panel, label= "show last N history log points")
        # self.gui_fields[b'last_N_history'] = wx.TextCtrl(self.panel,-1, style = wx.TE_PROCESS_ENTER, size = (40,-1), value = str(self.lastN_history))
        # self.gui_sizers[b'last_N_history'] = wx.BoxSizer(wx.HORIZONTAL)
        # self.gui_sizers[b'last_N_history'].Add(self.gui_labels[b'last_N_history'],0)
        # self.gui_sizers[b'last_N_history'].Add(self.gui_fields[b'last_N_history'],0)
        #
        #
        # self.gui_labels[b'last_M_history']  = wx.StaticText(self.panel, label= "to")
        # self.gui_fields[b'last_M_history'] = wx.TextCtrl(self.panel,-1, style = wx.TE_PROCESS_ENTER, size = (40,-1), value = str(self.lastM_history))
        # self.gui_sizers[b'last_M_history'] = wx.BoxSizer(wx.HORIZONTAL)
        # self.gui_sizers[b'last_M_history'].Add(self.gui_labels[b'last_M_history'],0)
        # self.gui_sizers[b'last_M_history'].Add(self.gui_fields[b'last_M_history'],0)
        #
        # self.Bind(wx.EVT_TEXT_ENTER, self.on_lastN_history_input, self.gui_fields[b'last_N_history'])
        # self.Bind(wx.EVT_TEXT_ENTER, self.on_lastM_history_input, self.gui_fields[b'last_M_history'])
        #
        #
        #
        #
        # self.gui_labels[b'last_M_history'].Hide()
        # self.gui_fields[b'last_M_history'].Hide()
        #
        # self.box_sizer[b'auxiliary'].Add(self.gui_sizers[b'last_N_history'],0)
        # self.box_sizer[b'auxiliary'].Add(self.gui_sizers[b'last_M_history'],0)
        # self.box_sizer[b'auxiliary'].Add(self.gui_sizers[b'graphs_hidden'],0)
        #
        # ###Graph Labels###
        # # Depressurize
        #
        #
        # self.gui_labels[b'pressurize_counter'] = wx.StaticText(self.panel, label= 'pres.', size = (120,-1))
        # #sizer.Add(self.gui_labels[b'pressurize_counter'] , pos=(24, 1),  span=(1,1), flag=wx.RIGHT|wx.EXPAND, border=5)
        # self.gui_labels[b'pressurize_counter'].SetFont(wx_m_font)
        #
        # self.gui_labels[b'depressurize_counter'] = wx.StaticText(self.panel, label= 'depres.', size = (120,-1))
        # #sizer.Add(self.gui_labels[b'depressurize_counter'] , pos=(24, 2),  span=(1,1), flag=wx.RIGHT|wx.EXPAND, border=5)
        # self.gui_labels[b'depressurize_counter'].SetFont(wx_m_font)
        #
        # self.gui_labels[b'pump_stroke_counter'] = wx.StaticText(self.panel, label= 'pump', size = (120,-1))
        # #sizer.Add(self.gui_labels[b'pump_stroke_counter'] , pos=(24, 3),  span=(1,1), flag=wx.RIGHT|wx.EXPAND, border=5)
        # self.gui_labels[b'pump_stroke_counter'].SetFont(wx_m_font)
        #
        # self.gui_labels[b'empty_couter'] = wx.StaticText(self.panel, label= " ", size = (120,-1))
        # #sizer.Add(self.gui_labels[b'empty_couter'] , pos=(25, 0),  span=(1,1), flag=wx.TOP|wx.ALIGN_CENTER|wx.EXPAND, border=5)
        # self.gui_labels[b'empty_couter'].SetFont(wx_m_font)
        #
        # self.gui_labels[b'valve_per_pump'] = wx.StaticText(self.panel, label= "\u0394valve/\u0394pump", size = (120,-1))
        # #sizer.Add(self.gui_labels[b'empty_couter'] , pos=(25, 0),  span=(1,1), flag=wx.TOP|wx.ALIGN_CENTER|wx.EXPAND, border=5)
        # self.gui_labels[b'valve_per_pump'].SetFont(wx_s_font)
        # self.gui_labels[b'valve_per_pump'].Wrap(100)
        #
        # self.gui_sizers[b'counters_labels'] = wx.BoxSizer(wx.HORIZONTAL)
        # #self.gui_sizers[b'shutdown_button'].Add(self.gui_labels[b'shutdown_button'],0)
        # self.gui_sizers[b'counters_labels'].Add(self.gui_labels[b'empty_couter'],0)
        # self.gui_sizers[b'counters_labels'].Add(self.gui_labels[b'pressurize_counter'],0)
        # self.gui_sizers[b'counters_labels'].Add(self.gui_labels[b'depressurize_counter'],0)
        # self.gui_sizers[b'counters_labels'].Add(self.gui_labels[b'pump_stroke_counter'],0)
        # self.gui_sizers[b'counters_labels'].Add(self.gui_labels[b'valve_per_pump'],0)
        #
        # self.gui_labels[b'counters'] = wx.StaticText(self.panel, label= "Valve Counter", size = (120,-1))
        # #sizer.Add(self.gui_labels[b'counters'] , pos=(25, 0),  span=(1,1), flag=wx.TOP|wx.ALIGN_CENTER|wx.EXPAND, border=5)
        # self.gui_labels[b'counters'].SetFont(wx_m_font)
        # try:
        #     number = icarus_AL.pulse_pressure_counter
        # except:
        #     number = nan
        #
        # self.gui_fields[b'pressurize_counter'] = wx.StaticText(self.panel, label= str(number), size = (120,-1))
        # #sizer.Add(self.gui_fields[b'pressurize_counter'] , pos=(25, 1),  span=(1,1), flag=wx.RIGHT|wx.EXPAND, border=5)
        # self.gui_fields[b'pressurize_counter'].SetFont(wx_m_font)
        # try:
        #     number = icarus_AL.pulse_depressure_counter
        # except:
        #     number = nan
        # self.gui_fields[b'depressurize_counter'] = wx.StaticText(self.panel, label= str(number), size = (120,-1))
        # #sizer.Add(self.gui_fields[b'depressurize_counter'] , pos=(25, 2),  span=(1,1), flag=wx.RIGHT|wx.EXPAND, border=5)
        # self.gui_fields[b'depressurize_counter'].SetFont(wx_m_font)
        # try:
        #     number = icarus_AL.pump_stroke_counter
        # except:
        #     number = nan
        # self.gui_fields[b'pump_stroke_counter'] = wx.StaticText(self.panel, label= str(number), size = (120,-1))
        # #sizer.Add(self.gui_fields[b'pump_stroke_counter'] , pos=(25, 3),  span=(1,1), flag=wx.RIGHT|wx.EXPAND, border=5)
        # self.gui_fields[b'pump_stroke_counter'].SetFont(wx_m_font)
        # try:
        #     number = icarus_AL.valve_per_pump
        # except:
        #     number = nan
        # self.gui_fields[b'valve_per_pump'] = wx.StaticText(self.panel, label= str(number), size = (120,-1))
        # #sizer.Add(self.gui_fields[b'pump_stroke_counter'] , pos=(25, 3),  span=(1,1), flag=wx.RIGHT|wx.EXPAND, border=5)
        # self.gui_fields[b'valve_per_pump'].SetFont(wx_m_font)
        #
        #
        # self.gui_sizers[b'depressurize_button'] = wx.BoxSizer(wx.HORIZONTAL)
        # #self.gui_sizers[b'shutdown_button'].Add(self.gui_labels[b'shutdown_button'],0)
        # self.gui_sizers[b'depressurize_button'].Add(self.gui_fields[b'depressurize_button'],0)
        #
        # self.gui_sizers[b'counters_fields'] = wx.BoxSizer(wx.HORIZONTAL)
        # #self.gui_sizers[b'shutdown_button'].Add(self.gui_labels[b'shutdown_button'],0)
        # self.gui_sizers[b'counters_fields'].Add(self.gui_labels[b'counters'],0)
        # self.gui_sizers[b'counters_fields'].Add(self.gui_fields[b'pressurize_counter'],0)
        # self.gui_sizers[b'counters_fields'].Add(self.gui_fields[b'depressurize_counter'],0)
        # self.gui_sizers[b'counters_fields'].Add(self.gui_fields[b'pump_stroke_counter'],0)
        # self.gui_sizers[b'counters_fields'].Add(self.gui_fields[b'valve_per_pump'],0)
        #
        # self.box_sizer[b'counters'].Add(self.gui_sizers[b'counters_labels'],0)
        # self.box_sizer[b'counters'].Add(self.gui_sizers[b'counters_fields'],0)

        self.sizer_left.Add(self.sizers['graph0'],0)
        self.sizer_left.Add(self.sizers['graph1'],0)
        self.sizer_left.Add(self.sizers['graph2'],0)
        #self.sizer_left.Add(self.box_sizer[b'counters'])

        self.sizer_middle.Add(self.sizers['graph3'],0)

        # self.sizer_right.Add(self.box_sizer[b'status'])
        # self.sizer_right.Add(wx.StaticLine(self.panel), 0, wx.ALL|wx.EXPAND, 5)
        # self.sizer_right.Add(self.box_sizer[b'measurements'])
        # self.sizer_right.Add(wx.StaticLine(self.panel), 0, wx.ALL|wx.EXPAND, 5)
        # self.sizer_right.Add(self.box_sizer[b'controls'])
        # self.sizer_right.Add(wx.StaticLine(self.panel), 0, wx.ALL|wx.EXPAND, 5)
        # self.sizer_right.Add(self.box_sizer[b'auxiliary'])
        # self.sizer_right.Add(wx.StaticLine(self.panel), 0, wx.ALL|wx.EXPAND, 5)
        # self.sizer_right.Add(self.box_sizer[b'faults_warnings'])

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



    def _on_about(self,event):
        message = str(__doc__)
        wx.MessageBox(message,'About', wx.OK | wx.ICON_INFORMATION)

    def onQuit(self,event):
        #FIXIT uncomment all
        #icarus_AL.GUI_running = False
        #icarus_AL.kill()
        del self
        os._exit(1)


if __name__ == "__main__":
    from pdb import pm
    import logging
    from tempfile import gettempdir
    import sys
    if len(sys.argv)>1:
        caserver_name = sys.argv[2]
    else:
        caserver_name = 'icarus_AL_test'

    app = wx.App(redirect=False)
    panel = GUI(caserver_name = caserver_name)

    app.MainLoop()
