"""
PyEpics additional functionality
"""
from epics.wx.wxlib import PVMixin, EpicsFunction, PVCtrlMixin,DelayedEpicsCallback
import wx
import epics.wx

import six

class PVImage(wx.StaticBitmap, PVMixin):
    """ A Dynamic Bitmap where the image is transmitted as a PV value.

        The size of the image has to be hard coded on the GUI size to convert 1-D array to an image.
        """
    def __init__(self, parent, pv=None, style=None, im_size = None,
                 im_size_show = None,
                 minor_alarm="DARKRED", major_alarm="RED",
                 invalid_alarm="ORANGERED", **kw):
        self.im_size = im_size
        wstyle = wx.ALIGN_LEFT
        if style is not None:
            wstyle = style

        wx.StaticBitmap.__init__(self, parent, wx.ID_ANY,
                               style=wstyle, **kw)
        PVMixin.__init__(self, pv=pv)
        self._fg_colour_alarms = {
            epics.MINOR_ALARM : minor_alarm,
            epics.MAJOR_ALARM : major_alarm,
            epics.INVALID_ALARM : invalid_alarm }

    def _SetValue(self, value):
        "set widget label"
        import wx
        from PIL import Image
        from time import time
        import io
        if value is not None:
            # I do all the stuff below to convert the array to the right format. It seems to be transmitted as 32bit instead of 8, even though i tried created it as 8 on the server. This needs to be investigated.

            raw_image = value
            im_mode = 'RGB'
            im_size = self.im_size
            im_size_show = self.im_size_show
            img = Image.frombuffer(im_mode, im_size, raw_image, 'raw', im_mode, 0, 1)
            width, height = img.size
            bit_img = wx.Bitmap.FromBuffer(width, height, img.tobytes())
            image = wx.Bitmap.ConvertToImage(bit_img)
            image = image.Scale(im_size_show[0], im_size_show[1], wx.IMAGE_QUALITY_HIGH)
            bit_img = wx.Bitmap(image)
            t1 = time()
            self.SetBitmap(bit_img)
        else:
            print('_SetValue',value)

    @EpicsFunction
    def OnPVChange(self, value):
        "called by PV callback"
        import traceback
        from numpy import array
        self.pv.auto_monitor = True
        try:
            # I don't know how to work with value correctly.
            # the value of value is <array size=30000, type=ctrl_long>
            # the type of value is <class 'str'>
            if self.pv is not None:
                value = array(self.pv.get(), dtype = 'int8')
                self._SetValue(value)
        except:
            print(traceback.format_exc())


class PVToggleButton(wx.Button, PVCtrlMixin):
    """ A Toggle Button linked to a PV. The button supports two states/values. When the button is pressed, a certain value is written to the PV.  The color of the button represents its' current state and the test on the button describes action that will happen when the button is pressed
    """
    def __init__(self, parent, pv=None, pushValues=[0,1],
                 disablePV=None, disableValue=1, stateColor = [(0,255,0),(255,0,0)], actionText = ['default 1','default 0'], **kw):
        """
        pv = pv to write back to
        pushValue = value to write when button is pressed
        disablePV = read this PV in order to disable the button
        disableValue = disable the button if/when the disablePV has this value
        """
        wx.Button.__init__(self, parent, **kw)
        PVCtrlMixin.__init__(self, pv=pv, font="", fg=None, bg=None)
        self.state = 0
        self.actionText = actionText
        self.stateColor = stateColor
        self.pushValues = pushValues
        self.pushValue = pushValues[self.state]
        wx.Button.SetLabel(self,self.actionText[self.state])
        self.Bind(wx.EVT_BUTTON, self.OnPress)
        if isinstance(disablePV, six.string_types):
            disablePV = epics.get_pv(disablePV)
            disablePV.connect()
        self.disablePV = disablePV
        self.disableValue = disableValue
        if disablePV is not None:
            ncback = len(self.disablePV.callbacks) + 1
            self.disablePV.add_callback(self._disableEvent, wid=self.GetId(),
                                        cb_info=ncback)
        self.maskedEnabled = True

    # def Enable(self, value=None):
    #     "enable button"
    #     if value is not None:
    #         self.maskedEnabled = value
    #     self._UpdateEnabled()

    @EpicsFunction
    def _UpdateEnabled(self):
        "epics function, called by event handler"
        enableValue = self.maskedEnabled
        if self.disablePV is not None and \
           (self.disablePV.get() == self.disableValue):
            enableValue = False
        if self.pv is not None:
            self.state = self.pv.get()
            wx.Button.SetLabel(self,self.actionText[self.state])
            r = self.stateColor[self.state][0]
            g = self.stateColor[self.state][1]
            b = self.stateColor[self.state][2]
            wx.Button.SetBackgroundColour(self,wx.Colour(r, g, b))
            wx.Button.SetForegroundColour(self,wx.Colour(r, g, b))

    @DelayedEpicsCallback
    def _disableEvent(self, **kw):
        "disable event handler"
        self._UpdateEnabled()

    def _SetValue(self, event):
        "set value"
        self._UpdateEnabled()

    @EpicsFunction
    def OnPress(self, event):
        "button press event handler"
        self.pushValue = self.pushValues[not self.state]
        self.pv.put(self.pushValue)
        self.state = not self.state
