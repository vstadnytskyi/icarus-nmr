#!/usr/bin/env python3
"""
this is an application level test server that would generate random data to populate the fields in the application level GUI.
"""

import time
from caproto.server import pvproperty, PVGroup, ioc_arg_parser, run
import numpy as np
from caproto import ChannelType
import logging
logging_shape = (1080,768, 3)
pre_shape = (216,768, 3)
depre_shape = (216,768, 3)
period_shape = (216,768, 3)


class softIOC(PVGroup):
    arr_logging = np.zeros(logging_shape).flatten()
    image_logging = pvproperty(value=arr_logging, dtype = int, max_length = logging_shape[0]*logging_shape[1]*logging_shape[2])

    arr_pre = np.zeros(pre_shape).flatten()
    image_pre = pvproperty(value=arr_pre, dtype = int, max_length = pre_shape[0]*pre_shape[1]*pre_shape[2])

    arr_depre = np.zeros(depre_shape).flatten()
    image_depre = pvproperty(value=arr_depre, dtype = int, max_length = depre_shape[0]*depre_shape[1]*depre_shape[2])

    arr_period = np.zeros(period_shape).flatten()
    image_period = pvproperty(value=arr_period, dtype = int, max_length = period_shape[0]*period_shape[1]*period_shape[2])

    t1 = pvproperty(value=1.0)
    dt = pvproperty(value=1.0, precision = 3)

    server_name = pvproperty(value='icarus_AL_test')

    target_pressure = pvproperty(value=10985.0)
    sample_pressure = pvproperty(value=1.0, precision = 3)
    pump_counter = pvproperty(value=1.0)
    valves_per_pump = pvproperty(value=1.0, precision = 3)
    operating_mode = pvproperty(value=1)

    shutdown_state = pvproperty(value=0)
    pump_state = pvproperty(value=0)
    pre_state = pvproperty(value=0)
    depre_state = pvproperty(value=0)


    pressure_after_pre = pvproperty(value=1.0, precision = 3)
    pressure_before_depre = pvproperty(value=1.0, precision = 3)
    time_to_switch_pre = pvproperty(value=1.0, precision = 3)
    time_to_switch_depre = pvproperty(value=1.0, precision = 3)
    rise_slope = pvproperty(value=1.0, precision = 3)
    fall_slope = pvproperty(value=1.0, precision = 3)
    pulse_width_pre = pvproperty(value=1.0, precision = 3)
    pulse_width_depre = pvproperty(value=1.0, precision = 3)
    delay = pvproperty(value=1.0, precision = 3)
    period = pvproperty(value=1.0, precision = 3)
    valve_counter_pre = pvproperty(value=1.0, precision = 3)
    valve_counter_depre = pvproperty(value=1.0, precision = 3)

    warning_text = pvproperty(value='this is a warning/faults field')


    x = [0]
    y1 = [np.nan]
    y2 = [np.nan]


    @t1.startup
    async def t1(self, instance, async_lib):
        # Loop and grab items from the queue one at a time
        while True:

            await self.t1.write(time.monotonic())
            t1 = time.time()

            figure_logging = self.chart_four(np.asarray(self.x),np.asarray(self.y1))
            img_logging = self.figure_to_array(figure_logging).flatten()

            figure_period = self.chart_one(np.asarray(self.x),np.asarray(self.y1))
            img_period = self.figure_to_array(figure_period).flatten()

            figure_depre = self.chart_one(np.asarray(self.x),np.asarray(self.y1))
            img_depre = self.figure_to_array(figure_depre).flatten()

            figure_pre = self.chart_one(np.asarray(self.x),np.asarray(self.y1))
            img_pre = self.figure_to_array(figure_pre).flatten()

            t2 = time.time()
            self.x.append(self.x[-1]+1)
            self.y2.append(np.random.randint(255))
            self.y1.append((t2-t1))

            await self.image_logging.write(value = img_logging)
            await self.image_pre.write(value = img_depre)
            await self.image_depre.write(value = img_pre)
            await self.image_period.write(value = img_period)

            await self.dt.write(value = (t2-t1))
            await async_lib.library.sleep(1)

    def chart_one(self, x,y):
        """
        charting function that takes x and y
        """
        xs_font = 10
        s_font = 12
        m_font = 16
        l_font = 24
        xl_font = 32

        import io
        from matplotlib.figure import Figure
        from matplotlib import pyplot
        from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
        from scipy import stats
        figure = Figure(figsize=(7.68,2.16),dpi=100)#figsize=(7,5))
        axes = figure.add_subplot(1,1,1)

        axes.plot(x,y, color = 'red', marker = 'o', markersize = 3 )

        axes.set_title("Top subplot")
        axes.set_xlabel("x (value)")
        axes.set_ylabel("y (value)")
        axes.tick_params(axis='y', which='both', labelleft=True, labelright=False)
        axes.grid(True)
        figure.tight_layout()
        return figure

    def chart_four(self, x,y):
        """
        charting function that takes x and y
        """
        xs_font = 10
        s_font = 12
        m_font = 16
        l_font = 24
        xl_font = 32

        import io
        from matplotlib.figure import Figure
        from matplotlib import pyplot
        from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
        from scipy import stats
        figure = Figure(figsize=(7.68,10.80),dpi=100)#figsize=(7,5))
        axes = []
        for i in range(4):
            axes.append(figure.add_subplot(4,1,i+1))
            axes[i].plot(x,y, color = 'red', marker = 'o', markersize = 3 )
            axes[i].set_title(f"Logging {i}")
            axes[i].set_xlabel("x (value)")
            axes[i].set_ylabel("y (value)")
            axes[i].tick_params(axis='y', which='both', labelleft=True, labelright=False)
            axes[i].grid(True)
        figure.tight_layout()
        return figure

    def figure_to_array(self, figure):
        from io import BytesIO
        from PIL.Image import open
        from numpy import asarray
        figure_buf = BytesIO()
        figure.savefig(figure_buf, format='jpg')
        figure_buf.seek(0)
        image = asarray(open(figure_buf))
        return image



if __name__ == "__main__":
    from tempfile import gettempdir
    print(f'temp-dir {gettempdir()}')

    from caproto import config_caproto_logging

    config_caproto_logging(file=gettempdir()+'/chart_generator.log', level='DEBUG')

    ioc_options, run_options = ioc_arg_parser(
        default_prefix="icarus_AL_test:",
        desc="SoftIOC generates a matplotlib plot of some data.",
    )


    ioc = softIOC(**ioc_options)

    run(ioc.pvdb, **run_options)
