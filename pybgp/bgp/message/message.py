# encoding: utf-8
"""
Author: Quentin Loos <contact@quentinloos.be>
"""
from struct import pack


class Message(object):

    """
    BGP message. It defines the header of all BGP messages like OPEN, UPDATE,
    etc.

    Format of the message::

        0                   1                   2                   3
        0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        |                                                               |
        +                                                               +
        |                                                               |
        +                                                               +
        |                       Marker (16 octects)                     |
        +                                                               +
        |                                                               |
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        |        Length  (2 octects)    |      Type     |
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

    Marker:
        All bits are set.

    Length:
        Indicates the total length of the message (including the header).
        This value is >= 19 and <= 4096.

    Type:
        Represents the type of the message.
    """

    marker     = pack('!B', 0xFF) * 16
    type       = 0
    min_length = 19

    class Type(object):
        OPEN         = 1
        UPDATE       = 2
        NOTIFICATION = 3
        KEEPALIVE    = 4

    @property
    def length(self):
        return self.min_length

    def pack(self):
        """
        Return a string representation of the packet to send.
        This string includes marker, length of the packet and type.
        """
        return self.marker + pack('!H', self.length) + pack('!B', self.type)

    def __str__(self):
        return 'BGP Message'
