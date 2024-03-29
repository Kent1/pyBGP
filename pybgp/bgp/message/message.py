# encoding: utf-8
"""
Author: Quentin Loos <contact@quentinloos.be>
"""
import struct


class Type(object):

    """
    Type of a BGP message.
    """

    OPEN         = 1
    UPDATE       = 2
    NOTIFICATION = 3
    KEEPALIVE    = 4


class Message(object):

    """
    Base of a BGP message. It defines the header wich is the same in
    all BGP messages like OPEN, UPDATE, etc.

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
        See :py:class:`pybgp.bgp.message.Type`
    """

    MARKER  = struct.pack('!B', 0xFF) * 16
    MIN_LEN = 19

    def __init__(self, type):
        self.type = type

    def __str__(self):
        return 'BGP Message'

    def __len__(self):
        return self.MIN_LEN

    def pack(self):
        """
        Return a string representation of the packet to send.
        This string includes marker, length of the packet and type.
        """
        return self.MARKER + struct.pack('!HB', len(self), self.type)

    @classmethod
    def header_unpack(cls, msg):
        """
        Return the type and the length of a message, regardless the
        type of the message.
        Verify that marker, length and type are well-formed.
        """

        if len(msg) < 19:
            raise Exception

        marker, length, type = struct.unpack('!16sHB', msg[:19])

        if marker != Message.MARKER:
            raise Exception

        if length < 19 or length > 4096:
            raise Exception

        return length, type

    @classmethod
    def unpack(cls, msg):
        length, type = Message.header_unpack(msg)
        return cls(type)
