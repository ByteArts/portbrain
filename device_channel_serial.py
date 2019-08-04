# !python3
"""
This module implements the DeviceChannel class over a serial connection.
"""

from device_channel import DeviceChannel
import serial_utils

__author__ = 'Scott Pinkham, Byte Arts LLC'
__version__ = '2019.511.0'


class SerialChannel(DeviceChannel):
    """
    Class for handling serial port i/o.
    """

    def __init__(self):
        self._serial_port = None
        self._serial_port_name = ''
        self._serial_port_settings = 'baud=9600 data size=8 parity=n stop bits=1'
        super(SerialChannel, self).__init__()
    #end def

    def _on_connected(self):
        pass
    #end def


    def _on_disconnected(self):
        pass
    #end def


    def close(self):
        if self._serial_port:
            self._serial_port.close()
            self._serial_port = None

        super(SerialChannel, self).close() # invalidates the handle
    #end def


    def flush(self):
        super(SerialChannel, self).flush()
        serial_utils.flush_port(self._serial_port)
    #end def


    def open(self, settings):
        """
        Opens a serial port.

        Args:
            settings = {portname: <com port name>, portsettings:'baud=<v> databits=<v> parity=<v> stopbits=<v>'}

        Returns: bool
        """
        # TODO: check that a channel isn't already open
        super(SerialChannel, self).open(settings)

        if 'portsettings' in settings:
            self._serial_port_settings = settings['portsettings']

        if 'portname' in settings:
            self._serial_port_name = settings['portname']

        self._serial_port = serial_utils.open_serial_port(self._serial_port_name, self._serial_port_settings)

        if self._serial_port:
            self._channel_handle = DeviceChannel.VALID_HANDLE
            self.flush()
        else:
            self._channel_handle = DeviceChannel.INVALID_HANDLE
        #end if

        return (self._channel_handle != None)
    #end def


    def read(self, count=1):
        """
        Read data from serial port.

        Returns: (tuple) - (success, data), where success (bool), data (bytes)
        """
        if not self.is_open():
            return (False, bytes(0))

        try:
            data = self._serial_port.read(count)
            return (len(data) > 0, data)
        except:
            return (False, data)
        #end try..except
    #end def


    def write(self, data):
        """
        Write to serial port.

        Args:
            data (bytes)
        """
        if not self.is_open():
            return False
        
        try:
            self._serial_port.write(data)
            return True
        except:
            return False
    #end def    


    @property
    def name(self):
        return self._open_settings['portname']
#end class