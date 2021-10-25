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

        self.panel = wx.Panel(self, wx.ID_ANY, style=wx.BORDER_THEME)#, size = (1920,1080))
        self.panel.Bind(wx.EVT_SIZE, self.on_size_change)
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
        ###FIGUREs####
        ###########################################################################

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

        self.sizers[b'server'] = wx.BoxSizer(wx.HORIZONTAL)
        self.labels[b'server'] = wx.StaticText(self.panel, label= "server name", size = (200,-1))
        self.fields[b'server'] = wx.StaticText(self.panel, label= f'{self.caserver_name}', size = (200,-1))
        self.sizers[b'server'].Add(self.labels[b'server'],0)
        self.sizers[b'server'].Add(self.fields[b'server'],0)


        self.sizers[b'pressure'] = wx.BoxSizer(wx.HORIZONTAL)
        self.labels[b'pressure'] = wx.StaticText(self.panel, label= "Pressure [kbar]", size = (400,-1))
        self.sizers[b'pressure'].Add(self.labels[b'pressure'],0)



        self.labels[b'pressure'].SetFont(wx_l_font)

        self.labels[b'pressure_target'] = wx.StaticText(self.panel, label= "Target:", size = (200,-1))
        #
        self.labels[b'pressure_target'].SetFont(wx_l_font)
        self.labels[b'pressure_target'].SetBackgroundColour(wx.Colour(240, 240, 240))
        #
        #
        self.fields[b'pressure_target'] = epics.wx.PVText(self.panel, pv=f'{self.caserver_name}:target_pressure', size = (200,-1))
        #
        self.fields[b'pressure_target'].SetFont(wx_l_font)
        self.fields[b'pressure_target'].SetBackgroundColour(wx.Colour(240, 240, 240))
        #
        self.sizers[b'pressure_target'] = wx.BoxSizer(wx.HORIZONTAL)
        self.sizers[b'pressure_target'].Add(self.labels[b'pressure_target'],0)
        self.sizers[b'pressure_target'].Add(self.fields[b'pressure_target'],0)

        self.labels[b'pressure_sample'] = wx.StaticText(self.panel, label= "Sample:", size = (200,-1))

        self.labels[b'pressure_sample'].SetFont(wx_l_font)
        self.fields[b'pressure_sample'] = epics.wx.PVText(self.panel, pv=f'{self.caserver_name}:sample_pressure', size = (200,-1))
        self.fields[b'pressure_sample'].SetFont(wx_l_font)

        self.sizers[b'pressure_sample'] = wx.BoxSizer(wx.HORIZONTAL)
        self.sizers[b'pressure_sample'].Add(self.labels[b'pressure_sample'],0)
        self.sizers[b'pressure_sample'].Add(self.fields[b'pressure_sample'],0)

        # Measurements pump counter
        self.labels[b'pump_counter'] = wx.StaticText(self.panel, label= "Pump Counter:", size = (200,-1))

        self.labels[b'pump_counter'].SetFont(wx_m_font)
        self.fields[b'pump_counter'] = epics.wx.PVText(self.panel, pv=f'{self.caserver_name}:pump_counter', size = (200,-1))
        self.fields[b'pump_counter'].SetFont(wx_m_font)

        self.sizers[b'pump_counter'] = wx.BoxSizer(wx.HORIZONTAL)
        self.sizers[b'pump_counter'].Add(self.labels[b'pump_counter'],0)
        self.sizers[b'pump_counter'].Add(self.fields[b'pump_counter'],0)

        # Measurements valves_per_pump
        self.labels[b'valves_per_pump_current'] = wx.StaticText(self.panel, label= "Valve opngs per pump stroke", size = (200,-1))

        self.labels[b'valves_per_pump_current'].SetFont(wx_m_font)
        self.fields[b'valves_per_pump_current'] = epics.wx.PVText(self.panel, pv=f'{self.caserver_name}:valves_per_pump_current', size = (200,-1))
        self.fields[b'valves_per_pump_current'].SetFont(wx_m_font)

        self.sizers[b'valves_per_pump_current'] = wx.BoxSizer(wx.HORIZONTAL)
        self.sizers[b'valves_per_pump_current'].Add(self.labels[b'valves_per_pump_current'],0)
        self.sizers[b'valves_per_pump_current'].Add(self.fields[b'valves_per_pump_current'],0)

        self.box_sizer[b'measurements'].Add(self.sizers[b'server'],0)
        self.box_sizer[b'measurements'].Add(self.sizers[b'pressure'],0)
        self.box_sizer[b'measurements'].Add(self.sizers[b'pressure_target'],0)
        self.box_sizer[b'measurements'].Add(self.sizers[b'pressure_sample'],0)
        self.box_sizer[b'measurements'].Add(self.sizers[b'pump_counter'],0)
        self.box_sizer[b'measurements'].Add(self.sizers[b'valves_per_pump_current'],0)

        # CONTROLS RIGHT Panel
        import socket
        digital_ca = f'digital_handler_{socket.gethostname()}:'

        self.fields['operating_mode_rbox_Manual'] = epics.wx.PVRadioButton(self.panel, pv = f"{digital_ca}operating_mode", pvValue = 0, label = 'Manual')
        self.fields['operating_mode_rbox_Pulsed'] = epics.wx.PVRadioButton(self.panel, pv = f"{digital_ca}operating_mode", pvValue = 1, label = 'Pulsed')
        self.fields['operating_mode_rbox_Console'] = epics.wx.PVRadioButton(self.panel, pv = f"{digital_ca}operating_mode", pvValue = 2, label = 'Console')
        self.sizers['operating_mode_rbox'] = wx.BoxSizer(wx.HORIZONTAL)
        self.sizers['operating_mode_rbox'].Add(self.fields['operating_mode_rbox_Manual'],0)
        self.sizers['operating_mode_rbox'].Add(self.fields['operating_mode_rbox_Pulsed'],0)
        self.sizers['operating_mode_rbox'].Add(self.fields['operating_mode_rbox_Console'],0)

        self.fields[b'shutdown_state'] = epics.wx.PVButton(self.panel, pv=f"{digital_ca}shutdown_state", pushValue = 1, size = (200,200),label="Shutdown")

        self.sizers[b'pump_state'] = wx.BoxSizer(wx.VERTICAL)
        self.fields[b'pump_state_low'] = epics.wx.PVButton(self.panel, pv=f"{digital_ca}bit0", pushValue = 0, size = (200,50),label="Pump Low", disablePV=f"{digital_ca}bit0_enable",disableValue=0)
        self.fields[b'pump_state_high'] = epics.wx.PVButton(self.panel, pv=f"{digital_ca}bit0", pushValue = 1, size = (200,50),label="Pump High", disablePV=f"{digital_ca}bit0_enable",disableValue=0)
        self.sizers[b'pump_state'].Add(self.fields[b'pump_state_low'],0)
        self.sizers[b'pump_state'].Add(self.fields[b'pump_state_high'],0)

        self.sizers[b'depre_state'] = wx.BoxSizer(wx.VERTICAL)
        self.fields[b'depre_state_low'] = epics.wx.PVButton(self.panel, pv=f"{digital_ca}bit1", pushValue = 0, size = (200,50),label="Depre Low", disablePV=f"{digital_ca}bit1_enable",disableValue=0)
        self.fields[b'depre_state_high'] = epics.wx.PVButton(self.panel, pv=f"{digital_ca}bit1", pushValue = 1, size = (200,50),label="Depre High", disablePV=f"{digital_ca}bit1_enable",disableValue=0)
        self.sizers[b'depre_state'].Add(self.fields[b'depre_state_low'],0)
        self.sizers[b'depre_state'].Add(self.fields[b'depre_state_high'],0)

        self.sizers[b'pre_state'] = wx.BoxSizer(wx.VERTICAL)
        self.fields[b'pre_state_low'] = epics.wx.PVButton(self.panel, pv=f"{digital_ca}bit2", pushValue = 0, size = (200,50),label="Pre Low", disablePV=f"{digital_ca}bit2_enable",disableValue=0)
        self.fields[b'pre_state_high'] = epics.wx.PVButton(self.panel, pv=f"{digital_ca}bit2", pushValue = 1, size = (200,50),label="Pre High", disablePV=f"{digital_ca}bit2_enable",disableValue=0)
        self.sizers[b'pre_state'].Add(self.fields[b'pre_state_low'],0)
        self.sizers[b'pre_state'].Add(self.fields[b'pre_state_high'],0)

        self.sizers[b'valve_buttons'] = wx.BoxSizer(wx.HORIZONTAL)
        self.sizers[b'valve_buttons'].Add(self.sizers[b'depre_state'],0)
        self.sizers[b'valve_buttons'].Add(self.sizers[b'pre_state'],0)

        self.box_sizer[b'controls'].Add(self.sizers['operating_mode_rbox'],0, wx.ALL | wx.ALIGN_CENTER, 20)
        self.box_sizer[b'controls'].Add(self.fields[b'shutdown_state'],0, wx.ALL | wx.ALIGN_CENTER, 20)
        self.box_sizer[b'controls'].Add(self.sizers[b'pump_state'],0, wx.ALL | wx.ALIGN_CENTER, 20)
        self.box_sizer[b'controls'].Add(self.sizers[b'valve_buttons'],0, wx.ALL | wx.ALIGN_CENTER, 20)

        self.labels[b'warnings_text'] = wx.StaticText(self.panel, label= "Warning/Faults", size = (200,-1))
        self.labels[b'warnings_text'].SetFont(wx_m_font)
        self.fields[b'warnings_text'] = epics.wx.PVText(self.panel, pv=f'{self.caserver_name}:warning_text', size = (400,200))
        self.fields[b'warnings_text'].SetFont(wx_s_font)

        self.sizers[b'warnings_text'] = wx.BoxSizer(wx.VERTICAL)
        self.sizers[b'warnings_text'].Add(self.labels[b'warnings_text'],0)
        self.sizers[b'warnings_text'].Add(self.fields[b'warnings_text'],0)




        ## TABLE with measurements
        ##
        #ROW0
        self.labels[b'table_header'] = wx.StaticText(self.panel, label= "", size = (200,-1))
        self.fields[b'table_header_col1'] = wx.StaticText(self.panel, label= "Pressurization", size = (200,-1))
        self.fields[b'table_header_col2'] = wx.StaticText(self.panel, label= "Depressurization", size = (200,-1))

        self.sizers[b'row0'] = wx.BoxSizer(wx.HORIZONTAL)
        self.sizers[b'row0'].Add(self.labels[b'table_header'],0)
        self.sizers[b'row0'].Add(self.fields[b'table_header_col1'],0)
        self.sizers[b'row0'].Add(self.fields[b'table_header_col2'],0)

        self.box_sizer[b'table'].Add(self.sizers[b'row0'],0)


        #ROW1
        self.labels[b'pressure'] = wx.StaticText(self.panel, label= "P after/before [kbar]", size = (200,-1))
        self.fields[b'pressure_col1'] = epics.wx.PVText(self.panel, pv=f'{self.caserver_name}:table_pressure_after_pre', size = (200,-1))
        self.fields[b'pressure_col2'] = epics.wx.PVText(self.panel, pv=f'{self.caserver_name}:table_pressure_before_depre', size = (200,-1))

        self.sizers[b'row1'] = wx.BoxSizer(wx.HORIZONTAL)
        self.sizers[b'row1'].Add(self.labels[b'pressure'],0)
        self.sizers[b'row1'].Add(self.fields[b'pressure_col1'],0)
        self.sizers[b'row1'].Add(self.fields[b'pressure_col2'],0)

        self.box_sizer[b'table'].Add(self.sizers[b'row1'],0)

        #ROW2
        self.labels[b'time_to_swtich'] = wx.StaticText(self.panel, label= "time to switch [ms]", size = (200,-1))
        self.fields[b'time_to_swtich_col1'] = epics.wx.PVText(self.panel, pv=f'{self.caserver_name}:table_time_to_switch_pre', size = (200,-1))
        self.fields[b'time_to_swtich_col2'] = epics.wx.PVText(self.panel, pv=f'{self.caserver_name}:table_time_to_switch_depre', size = (200,-1))

        self.sizers[b'row2'] = wx.BoxSizer(wx.HORIZONTAL)
        self.sizers[b'row2'].Add(self.labels[b'time_to_swtich'],0)
        self.sizers[b'row2'].Add(self.fields[b'time_to_swtich_col1'],0)
        self.sizers[b'row2'].Add(self.fields[b'time_to_swtich_col2'],0)

        self.box_sizer[b'table'].Add(self.sizers[b'row2'],0)

        #ROW3
        self.labels[b'slope'] = wx.StaticText(self.panel, label= "fall/rise slope [kbar/ms]", size = (200,-1))
        self.fields[b'slope_col1'] = epics.wx.PVText(self.panel, pv=f'{self.caserver_name}:table_rise_slope', size = (200,-1))
        self.fields[b'slope_col2'] = epics.wx.PVText(self.panel, pv=f'{self.caserver_name}:table_fall_slope', size = (200,-1))

        self.sizers[b'row3'] = wx.BoxSizer(wx.HORIZONTAL)
        self.sizers[b'row3'].Add(self.labels[b'slope'],0)
        self.sizers[b'row3'].Add(self.fields[b'slope_col1'],0)
        self.sizers[b'row3'].Add(self.fields[b'slope_col2'],0)

        self.box_sizer[b'table'].Add(self.sizers[b'row3'],0)

        #ROW4
        self.labels[b'pulse_width'] = wx.StaticText(self.panel, label= "pulse width [ms]", size = (200,-1))
        self.fields[b'pulse_width_col1'] = epics.wx.PVText(self.panel, pv=f'{self.caserver_name}:table_pulse_width_pre', size = (200,-1))
        self.fields[b'pulse_width_col2'] = epics.wx.PVText(self.panel, pv=f'{self.caserver_name}:table_pulse_width_depre', size = (200,-1))

        self.sizers[b'row4'] = wx.BoxSizer(wx.HORIZONTAL)
        self.sizers[b'row4'].Add(self.labels[b'pulse_width'],0)
        self.sizers[b'row4'].Add(self.fields[b'pulse_width_col1'],0)
        self.sizers[b'row4'].Add(self.fields[b'pulse_width_col2'],0)

        self.box_sizer[b'table'].Add(self.sizers[b'row4'],0)


        #ROW5
        self.labels[b'delay'] = wx.StaticText(self.panel, label= "delay [ms]", size = (200,-1))
        self.fields[b'delay_col1'] = epics.wx.PVText(self.panel, pv=f'{self.caserver_name}:table_delay', size = (200,-1))

        self.sizers[b'row5'] = wx.BoxSizer(wx.HORIZONTAL)
        self.sizers[b'row5'].Add(self.labels[b'delay'],0)
        self.sizers[b'row5'].Add(self.fields[b'delay_col1'],0)

        self.box_sizer[b'table'].Add(self.sizers[b'row5'],0)

        #ROW6
        self.labels[b'period'] = wx.StaticText(self.panel, label= "period [s]", size = (200,-1))
        self.fields[b'period_col1'] = epics.wx.PVText(self.panel, pv=f'{self.caserver_name}:table_period', size = (200,-1))

        self.sizers[b'row6'] = wx.BoxSizer(wx.HORIZONTAL)
        self.sizers[b'row6'].Add(self.labels[b'period'],0)
        self.sizers[b'row6'].Add(self.fields[b'period_col1'],0)


        self.box_sizer[b'table'].Add(self.sizers[b'row6'],0)

        #ROW7
        self.labels[b'valve_counter'] = wx.StaticText(self.panel, label= "Valve Counter", size = (200,-1))
        self.fields[b'valve_counter_col1'] = epics.wx.PVText(self.panel, pv=f'{self.caserver_name}:table_valve_counter_pre', size = (200,-1))
        self.fields[b'valve_counter_col2'] = epics.wx.PVText(self.panel, pv=f'{self.caserver_name}:table_valve_counter_depre', size = (200,-1))

        self.sizers[b'row7'] = wx.BoxSizer(wx.HORIZONTAL)
        self.sizers[b'row7'].Add(self.labels[b'valve_counter'],0)
        self.sizers[b'row7'].Add(self.fields[b'valve_counter_col1'],0)
        self.sizers[b'row7'].Add(self.fields[b'valve_counter_col2'],0)

        self.box_sizer[b'table'].Add(self.sizers[b'row7'],0)



        self.sizer_left.Add(self.sizers['graph0'],0)
        self.sizer_left.Add(self.sizers['graph1'],0)
        self.sizer_left.Add(self.sizers['graph2'],0)
        self.sizer_left.Add(self.box_sizer[b'table'])

        self.sizer_middle.Add(self.sizers['graph3'],0)


        self.sizer_right.Add(self.box_sizer[b'measurements'])
        self.sizer_right.Add(wx.StaticLine(self.panel), 0, wx.ALL|wx.EXPAND, 5)
        self.sizer_right.Add(self.box_sizer[b'controls'])
        self.sizer_right.Add(wx.StaticLine(self.panel), 0, wx.ALL|wx.EXPAND, 5)
        self.sizer_right.Add(self.sizers[b'warnings_text'])
        self.sizer_right.Add(wx.StaticLine(self.panel), 0, wx.ALL|wx.EXPAND, 5)



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


if __name__ == "__main__":
    from pdb import pm
    import logging
    from tempfile import gettempdir
    import sys
    import socket
    if len(sys.argv)>1:
        caserver_name = sys.argv[2]
    else:
        caserver_name = f'event_handler_{socket.gethostname()}'

    app = wx.App(redirect=False)
    panel = GUI(caserver_name = caserver_name)

    app.MainLoop()
