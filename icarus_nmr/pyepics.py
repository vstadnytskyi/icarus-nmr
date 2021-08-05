"""
PyEpics additional functionality
"""
from epics.wx.wxlib import PVMixin, EpicsFunction
import wx
import epics.wx

class PVImage(wx.StaticBitmap, PVMixin):
    """ Static text for displaying a PV value,
        with callback for automatic updates
        By default the text colour will change on alarm states.
        This can be overriden or disabled as constructor
        parameters
        """
    def __init__(self, parent, pv=None, style=None, im_size = None,
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
        from PIL import Image
        from time import time
        import io
        if value is not None:
            # I do all the stuff below to convert the array to the right format. It seems to be transmitted as 32bit instead of 8, even though i tried created it as 8 on the server. This needs to be investigated.

            raw_image = value
            im_mode = 'RGB'
            im_size = self.im_size
            img = Image.frombuffer(im_mode, im_size, raw_image, 'raw', im_mode, 0, 1)
            width, height = img.size
            bit_img = wx.Bitmap.FromBuffer(width, height, img.tobytes())
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
