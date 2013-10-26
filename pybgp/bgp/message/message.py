# encoding: utf-8
"""
Author: Quentin Loos <contact@quentinloos.be>
"""
from struct import pack


class Message(object):

    """

    BGP message. It defines the base of OPEN, UPDATE, KEEPALIVE, etc..
    Based on RFC 4271.

    Marker : 16-octect, all bits are set.
    Length : 2-octect uint. Indicates the total length of the
             message (including the header). This value is >= 19 and <= 4096.
    Type   : 1-octect uint. Represents the type of the message.

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

    marker = chr(0xFF) * 16
    type   = 0
    length = 19

    class Type(object):
        OPEN         = 1
        UPDATE       = 2
        NOTIFICATION = 3
        KEEPALIVE    = 4

    def __str__(self):
        return 'BGP Message'

    def pack(self):
        """
        Return the packet representation.
        """
        return self.marker + pack('!H', self.length) + pack('!B', self.type)
