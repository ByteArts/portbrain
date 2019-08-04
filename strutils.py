# !python3
"""
Basic string utilities
"""

__author__ = 'Scott Pinkham, Byte Arts LLC'
__version__ = '2019.511.0'


def str_after(substr, valuestr):
    """
    Searches for the first occurance of a sub string and returns everything after that.

    Args:
        substr (string): sub-string to search for
        valuestr (string): string to be searched

    Returns:
        everything after the substring, or "" if not found.
    """
    result = valuestr.split(substr)
    if (len(result) > 1):
        return result[1]
    else:
        return ''
#end def str_after()


def str_before(substr, valuestr):
    """
    Searches for the first occurance of a sub string and returns everything before that.

    Args:
        substr (string): sub-string to search for
        valuestr (string): string to be searched

    Returns:
        everything before the substring, or "" if not found.
    """
    result = valuestr.split(substr)
    if (len(result) > 1):
        return result[0]
    else:
        return ''
#end str_before()
        
