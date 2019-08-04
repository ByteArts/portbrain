# PortBrain module

import logging

import serial_utils
from device_channel_serial import SerialChannel

DEFAULT_PORT_SETTINGS = 'baud=115200,databits=8,parity=N,stopbits=1'


def enumerate_portbrains(max_count):
    """
    Searches serial ports for port brains(s)

    Arguments:
        max_count (int) -- max number of units to search for.

    Returns:
        (list) -- list of portbrain objects.
    """

    portnames = _search_serial_ports_for_portbrain(max_count)

    portbrains = []

    # now assign each unit
    for index in range(len(portnames)):
        settings = {'portname': portnames[index], 'portsettings': DEFAULT_PORT_SETTINGS,
            'read_terminator': b'\r',
            'cmd_terminator': b'\r',
            'cmd_timeout': 0.5
        }
        portbrain = PortBrainController(SerialChannel())

        if portbrain._channel.open(settings):
            if portbrain.check_for_device():
                portbrains.append(portbrain)
        #end if
    #end if

    return portbrains
#end def


def _search_serial_ports_for_portbrain(max_count):
    """
    Searches all available serial ports on the system for a PortBrain controller.

    Args:
        max_count (int) - max number of units to find.

    Returns: list of port names where a portbrain was found.
    """

    result = []
    portnames = serial_utils.available_serial_ports()

    for portname in portnames:
        settings =  {'portname': portname, 'portsettings': DEFAULT_PORT_SETTINGS,
            'read_terminator': b'\r',
            'cmd_terminator': b'\r',
            'cmd_timeout': 0.3
        }
        channel = SerialChannel()

        logger.debug('Checking %s for PortBrain..' % portname)

        if channel.open(settings):
            try:
                portbrain = PortBrainController(channel)
                if portbrain.check_for_device():
                    logger.debug('PortBrain V{} found on {}'.format(portbrain.device_info['version'], portbrain.device_info['channel name']))
                    result.append(portname)

                    if len(result) >= max_count:
                        break
                #end if
            finally:
                channel.close()
        #end if
    #end for

    return result
#end def


class PortBrainController(object):
    def __init__(self, channel = None):
        """
        Args:
            channel: device channel object
        """
        self._version = ''
        self._channel = channel
        self._initialize_data()
    #end def


    def _initialize_data(self):
        # init data to defaults
        pass
    #end def


    def _is_connection_open(self) -> bool:
        result = False
        if self._channel:
            result = self._channel.is_open()
        return result
    #end def


    def _send_command(self, cmd) -> (bool, bytes):
        """
        Sends a command to the laser.

        Arguments:
            cmd {bytes} -- command string

        Returns:
            tuple -- (<success (bool)>, <response (bytes)>)
        """

        if self._is_connection_open():
            success, response = self._channel.send_command(cmd)

            if success:
                # if command was a query, strip off the echoed command and return the value
                return (True, response)
            #end if
        #end if

        return (False, bytes(0))
    #end def


    def check_for_device(self) -> bool:
        result = False
        success, response = self._send_command(b'VER')

        if success:
            # check that response is the form of <major>.<minor>
            try:
                self._version = response.decode()
                result = self._version.count('.') == 1
            except:
                pass
        #end if

        return result
    #end def


    def get_port_direction(self, portnumber: int) -> (bool, int):
        cmd = b'DIRRD' + str(portnumber).encode()
        success, value = self._send_command(cmd)
        return (success, int(value))
    #end def


    def read_analog_input(self, inputnumber: int) -> (bool, int):
        """
        Read from an analog input

        Args:
            self (object): PortBrain class
            int (int): input number (0-4)

        Returns:
            tuple: (success, value)
        """
        cmd = b'ADC' + str(inputnumber).encode()
        success, value = self._send_command(cmd)
        return (success, int(value))
    #end def


    def read_port(self, portnumber: int) -> (bool, int):
        """
        Reads a digital port

        Args:
            self (object): PortBrain class
            portnumber (int): portnumber to read (0-5)

        Returns:
            tuple: (success, value)
        """
        cmd = b'PRTRD' + str(portnumber).encode()
        success, response = self._send_command(cmd)

        if success:
            return (True, int(response))
        else:
            return (False, 0)
    #end def


    def set_port_direction(self, portnumber: int, dirbits: int) -> bool:
        cmd = b'DIRWR' + str(portnumber).encode() + str(dirbits).encode()
        success, _ = self._send_command(cmd)
        return success
    #end def


    def write_port(self, portnumber: int, value: int) -> bool:
        """
        Write to a port

        Args:
            portnumber (int): Port to write to (0-5)
            value (int): Port value

        Returns:
            bool: True if successful
        """
        cmd = b'PRTWR' + str(portnumber).encode()
        success, response = self._send_command(cmd)
        return success
    #end def


    @property
    def device_info(self):
        if self._channel:
            cn = self._channel.name
        else:
            cn = 'None'
        return {'version': self._version, 'channel name': cn}
    #end def
#end class


if __name__ == '__main__':
    #logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s:%(filename)s, line %(lineno)d:%(levelname)s:%(message)s')
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    logger.info('Searching for PortBrains..')
    portbrains = enumerate_portbrains(1)
    if len(portbrains):
        portbrain = portbrains[0]
    else:
        portbrain = None

    if portbrain:
        print('get_port_direction(0)={}'.format(portbrain.get_port_direction(0)))
        print('read_port(0)={}'.format(portbrain.read_port(0)))
        print('write_port(0)={}'.format(portbrain.write_port(0, 0)))
        print('read_analog_input(3)={}'.format(portbrain.read_analog_input(3)))
    #end if
#end if