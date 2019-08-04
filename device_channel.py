# !python3
"""
Module that defines class for doing communication with a 
device over a channel
"""
from timeout import Timeout


__author__ = 'Scott Pinkham, Byte Arts LLC'
__version__ = '2019.513.0'


class DeviceChannel(object):
    """
    Abstract class that defines a channel used to communicate with a device
    """
    INVALID_HANDLE = -1
    VALID_HANDLE = 0

    def __init__(self):
        self._channel_handle = DeviceChannel.INVALID_HANDLE
        self._open_settings = {}
        self._read_terminator = b'\n'
        self._cmd_terminator = b'\n'
        self._cmd_timeout = 0.3
        self._last_error = ''
        self.flush()
    #end def __init__()


    def close(self):
        """
        Closes the channel
        """
        self._channel_handle = DeviceChannel.INVALID_HANDLE
    #end def 


    def flush(self):
        self._read_buffer = bytearray(0)
        self._write_buffer = bytearray(0)
    #end def 


    def is_open(self):
        """
        Returns True if the channel is open
        """
        return (self._channel_handle != DeviceChannel.INVALID_HANDLE)
    #end def 


    def is_response_in_buffer(self, buffer, response = None):
        """
        Checks if the specified response is in the buffer.

        Args:
            buffer (bytes):
            response (bytes): if None, then the
            current read_terminator value is used.

        Returns: (boolean)
        """
        if len(buffer) <= 0:
            return False
        
        # check if a terminator is in the buffer
        if not response:
            response = self._read_terminator
        return buffer.count(response) > 0
    #end def 


    def open(self, settings):
        """
        Open(settings) -> boolean

        Opens a channel using the specified settings. Returns boolean.
        """            
        self._open_settings = dict(settings)

        # update the local copies of settings
        if 'read_terminator' in settings:
            self._read_terminator = settings['read_terminator']

        if 'cmd_terminator' in settings:
            self._cmd_terminator = settings['cmd_terminator']

        if 'cmd_timeout' in settings:
            self._cmd_timeout = settings['cmd_timeout']

        return True
    #end def open()


    def read(self):
        """
        Reads data from channel. This implementation just
        checks if the channel is open or not -- child class
        should implement the actual read.
        
        Returns (tuple): (isopen, buffer) where isopen (boolean), buffer (bytes)
        """
        return (self.is_open(), bytes(0))
    #end def read()


    def remove_response_from_buffer(self, buffer, terminator=None):
        """
        Parses buffer to get the command response (if any)
        Usage: remove_response_from_buffer(buffer, resp) -> (response, leftover_buffer)
        """
        response = bytearray(0)
        remainder = buffer

        if not terminator:
            terminator = self._read_terminator

        if self.is_response_in_buffer(buffer, terminator):
            response, _, remainder = buffer.partition(terminator)
            pass
        #end if

        return (response, remainder)
    #end def remove_response_from_buffer()


    def send_command(self, cmd):
        """
        Sends a command to the device over the channel.

        Args:
            cmd (bytes): data to write

        Returns: (tuple): (success, response) where success (bool), 
            response (bytes).
        """
        self._last_error = ''
        self._read_buffer = bytearray(0)

        # send the command
        if not self.write(cmd + self._cmd_terminator):
            self._last_error = 'write'
            return (False, [])

        # wait for the response, or timeout
        cmd_timeout = Timeout(self._cmd_timeout)
        while (True):
            # read bytes
            read_result = self.read()
            if read_result[0]:
                self._read_buffer += read_result[1]

            # check if complete response has been received
            if self.is_response_in_buffer(self._read_buffer):
                break

            # check for timeout
            if cmd_timeout.is_expired():
                self._last_error = 'timeout'
                return (False, self._read_buffer)
        #end while

        # parse any command response from the buffer and return it
        parse_result = self.remove_response_from_buffer(self._read_buffer, self._read_terminator)
        return (True, parse_result[0])
    #end def sendcommand()


    def write(self, data):
        """
        Writes data to channel. This implementation just
        checks if the channel is open or not -- child class
        should implement the actual write.
        
        Returns (bool): True if channel is open
        """
        return self.is_open()
    #end def write()


    @property 
    def last_error(self):
        return self._last_error
#end class TDeviceChannel
