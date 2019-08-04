# !python3
"""
Utilities for serial port I/O
"""

__author__ = 'Scott Pinkham, Byte Arts LLC'
__version__ = '2019.511.0'


import glob
import logging
import sys
from time import sleep
from builtins import input

import serial

import strutils

SER_TIMEOUT=0.3

def ask_for_serial_port():
    """
    Ask the user to select a serial port.

    Returns:
        Name of the serial port selected by the user
    """
    result = None
    portnames = available_serial_ports()
    logging.debug('available portnames={}'.format(portnames))
    if len(portnames) <= 0:
        logging.warning('No serial ports available.')
        return result

    print('Available serial ports:')
    index = 0
    for pn in portnames:
        print('({0}) = {1}'.format(index, pn))
        index += 1

    while True:
        portnum = 0
        if len(portnames) > 1:
            index = input('Enter index of port to use [0]: ').rstrip('\r\n')
            if index != '':
                portnum = int(index)
        else:
            portnum = 0

        if portnum in range(len(portnames)):
            break
        else:
            print('Invalid port number entered. Try again.')
            #sys.exit(-2)
    #end while

    return portnames[portnum]
#end def ask_for_serial_port()


def available_serial_ports():
    """ Lists serial port names

        Raises: 
            EnvironmentError: On unsupported or unknown platforms
        Returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    # try to open a port to see if it's really available or not
    result = []
    for port in ports:
        # ignore bluetooth ports
        if port.__contains__('Bluetooth'):
            continue

        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result
#end def available_serial_ports()


def flush_port(port):
    if not port:
        return

    port.flushOutput()
    port.flushInput()
#end def


def open_serial_port(Portname, Settings, ReadTimeout=0.2, WriteTimeout=0.2):
    """
    Try to open a port with the specified baud rate.

    Args:
        Portname (string): name of serial port (full path)
        Settings (string): port settings in format 'baud=<baudrate>,parity=<E,O, or N>,databits=<datasize>,stopbits=<stopsize>'
    Returns Serial object or None
    """    
    try:
        baud_setting = strutils.str_after('baud=', Settings)
        baud_setting = int(strutils.str_before(',', baud_setting))

        data_setting = strutils.str_after('databits=', Settings)
        data_setting = int(strutils.str_before(',', data_setting))

        parity_setting = strutils.str_after('parity=', Settings)
        parity_setting = strutils.str_before(',', parity_setting)

        stop_setting = strutils.str_after('stopbits=', Settings)
        stop_setting = int(stop_setting)

        result = serial.Serial(Portname, baudrate=baud_setting, bytesize=data_setting, parity=parity_setting, \
        stopbits=stop_setting, timeout=ReadTimeout, writeTimeout=WriteTimeout)
        result.flush()
        
    except serial.SerialException as err:
        result = None
        serr = str(err)
        # suppress the 'no such file' error
        if (serr.find('No such file') < 0):
            logging.warning('OpenPort() failed: %s' % serr)

    return result
# end def open_serial_port()
