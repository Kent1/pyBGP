# encoding: utf-8
"""
BGP message

Author: Quentin Loos <contact@quentinloos.be>
"""
from struct import pack


class Message(object):

    """

    BGP message. It defines the base of OPEN, UPDATE, KEEPALIVE, etc..

    0                   1                   2                   3
    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |                                                               |
    +                                                               +
    |                                                               |
    +                                                               +
    |                           Marker                              |
    +                                                               +
    |                                                               |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |          Length               |      Type     |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    """

    MARKER = chr(0xFF) * 16
    HEADER_LENGTH = 19
    MAX_LENGTH = 4096

    class Type(object):
        OPEN = 1
        UPDATE = 2
        NOTIFICATION = 3
        KEEPALIVE = 4

    def __init__(self, length, type_):
        self.length = length
        self.type = type_

    def __str__(self):
        return '%s' % self.type

    def blabla(self):
        """
        Return the packets representation.
        """
        return self.MARKER + pack('!H', self.length) + pack('!B', self.type)
