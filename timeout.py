# !python3
"""
Module for managing timeouts.
"""

from time import perf_counter

__author__ = 'Scott Pinkham, Byte Arts LLC'
__version__ = '2019.511.0'


def secs_to_hms(secs):
    secs = int(secs)
    hours, remainder = divmod(secs, 3600)
    mins, remainder = divmod(remainder, 60)
    return '{:02d}hrs {:02d}mins {:02d}secs'.format(hours, mins, remainder)
#end def


class Timeout(object):
    """
    Class for checking for a timeout.

    Args:
        duration (float): timeout in secs.
    """
    def __init__(self, duration):
        self._duration = float(duration)
        self.reset(duration)
    #end def

    def is_expired(self):
        """
        Checks if the timer has expired.

        Returns:
            bool -- True if expired.
        """
        return perf_counter() >= self._endtime
    #end def

    def reset(self, new_duration:float=None):
        """
        Resets the timeout counter.

        Arguments:
            new_duration {float} -- new duration (in secs), otherwise uses original value (default: {None})
        """
        if new_duration:
            self._duration = float(new_duration)

        self._starttime = perf_counter()
        self._endtime = self._starttime + self._duration
    #end def

    @property
    def status(self):
        """
        Returns (elapsed time, remaining time), values are in hours:mins:secs
        """
        now = perf_counter()
        elapsed = now - self._starttime
        remaining = self._endtime - now
        if remaining < 0:
            remaining = 0

        elapsed_str = secs_to_hms(elapsed)
        remaining_str = secs_to_hms(remaining)
        return (elapsed_str, remaining_str)
#end class

