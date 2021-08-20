#!/bin/env python
"""
"""

class Client():
    def __init__(self,device_ca_server_prefix = 'device_mock:'):
        """
        ToDo: rewrite the function to include the list of PVs.
        - restructure subscription to PVs to be saved as a dictionary. this will allow potential future expansions.
        """
        from caproto.threading.client import Context
        self.ctx = Context()
        self.ca_name = device_ca_server_prefix
        self.dio, = self.ctx.get_pvs(f'{self.ca_name}dio',)

    def get_dio(self):
        """
        a wrapper to get digital state from the device handler process

        Parameters
        ----------

        Returns
        -------
        value :: integer

        Examples
        --------
        >>> value = client.get_dio()
        """
        return self.dio.read().data[0]

    def set_dio(self, value):
        """
        a wrapper to get digital state from the device handler process

        Parameters
        ----------
        value :: integer

        Returns
        -------

        Examples
        --------
        >>> client.set_dio(127)
        """
        result = self.dio.write(value)
