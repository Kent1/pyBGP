# encoding: utf-8
"""
BGP message

Author: Quentin Loos <contact@quentinloos.be>
"""
from struct import pack


class Message(object):

    """

    BGP message. It defines the base of OPEN, UPDATE, KEEPALIVE, etc..
    Based on RFC 4271.

    Marker : 16-octect, all bits are set.
    Length : 2-octect unsigned integer. Indicates the total length of the
             message (including the header). This value is >= 19 and <= 4096.
    Type   : 1-octect unsigned integer representing the type of the message.

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
    length = 19

    class Type(object):
        OPEN = 1
        UPDATE = 2
        NOTIFICATION = 3
        KEEPALIVE = 4

    def __init__(self, length, type_):
        self.length = length
        self.type = type_

    def __str__(self):
        return 'BGP Message'

    def pack(self):
        """
        Return the packet representation.
        """
        return self.marker + pack('!H', self.length) + pack('!B', self.type)


class Open(Message):

    """
    BGP OPEN message. This is the first message send after the TCP connection
    is etablished.

    Version           : 1-octect unsigned integer. Indicates the protocol version number of the message.
    Autonomous System : 2-octect unsigned integer. ASN of the sender of this message.
    Hold Time         : 2-octect unsigned integer. Indicates the number of seconds for the hold timer.
    BGP Identifier    : 4-octect unsigned integer. An assigned IP address of the sender.
    Opt. Parm. Length : 1-octect unsigned integer. Length of the optional parameters.

    0                   1                   2                   3
    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
    +-+-+-+-+-+-+-+-+
    |    Version    |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |     My Autonomous System      |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |           Hold Time           |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |                         BGP Identifier                        |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    | Opt Parm Len  |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |                                                               |
    |             Optional Parameters (variable)                    |
    |                                                               |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+


    Optional Parameters
    -------------------

    List of optional parameters. Each parameters is encoded as a <Parameter Type, Parameter Length, Parameter Value> triplet.

    Parm. Type   : 1-octect. Identifies individual parameters.
    Parm. Length : 1-octect. Contains the length of the parameter value in octects.
    Parm. Value  : Parameter interpreted according to the value of the Parm. Type.
    (RFC 3392)

         0                   1
     0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5
     +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-...
     |  Parm. Type   | Parm. Length  |  Parameter Value (variable)
     +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-...
    """

    TYPE = chr(Message.Type.OPEN)

    def __init__(self, version, asn, hold_time, router_id, capabilities):
        self.version = version
        self.asn = asn
        self.hold_time = hold_time
        self.router_id = router_id
        self.capabilities = capabilities
        super(Message.Type.OPEN)

    def __str__(self):
        'BGP OPEN Message\n\
        \tVersion      %d\n\
        \tAS           %d\n\
        \tHold Time    %d\n\
        \tRouter ID    %s\n\
        \tCapabilities %s\n\
        ' % (
            self.version,
            self.asn,
            self.hold_time,
            self.router_id,
            self.capabilities
        )

    def pack(self):
        return super.pack()
