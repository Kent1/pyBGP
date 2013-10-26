# encoding: utf-8
"""
Author: Quentin Loos <contact@quentinloos.be
"""
from pybgp.bgp.message import Message
from struct import pack


class Open(Message):

    """
    BGP OPEN message. This is the first message send after the TCP connection
    is etablished.

    Format of the message::

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

    Version:
        Indicates the protocol version.
    Autonomous System:
        ASN of the sender of this message.
    Hold Time:
        Seconds between message (KEEPALIVE).
    BGP Identifier:
        An assigned IP address of the sender.
    Opt. Parm. Length:
        Length of the optional parameters.
    Optional Parameters:
        List of optional parameters. Each parameters is encoded as a
        <Parameter Type, Parameter Length, Parameter Value> triplet::

            0                   1
            0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6
            +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-...
            |  Parm. Type   | Parm. Length  |  Parameter Value (variable)
            +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-...

        Parm. Type:
            Identifies individual parameters.
        Parm. Length:
            Contains the length of the parameter value in octects.
        Parm. Value:
            Parameter interpreted according to the Parm. Type. (RFC 3392)
    """

    type       = Message.Type.OPEN
    min_length = 29

    def __init__(self, asn, hold_time, router_id, version=4, capabilities=None):
        self.version      = version
        self.asn          = asn
        self.hold_time    = hold_time
        self.router_id    = router_id
        self.capabilities = capabilities if capabilities else []

    def __str__(self):
        result = 'BGP OPEN Message ('
        result += 'Version %d, '     % self.version
        result += 'AS %d, '          % self.asn
        result += 'Hold Time %d, '   % self.hold_time
        result += 'Router ID %s, '   % self.router_id
        result += 'Capabilities %s)' % self.capabilities
        return result

    @property
    def length(self):
        return self.min_length + len(self.capabilities)

    def pack(self):
        """
        Return a string representation of the packet to send.
        This string includes header, version, AS number, Hold Time, Router ID,
        the length of capabilities and the list of capabilities.
        """
        str = super(Open, self).pack()
        str += chr(self.version)
        str += pack('!H', self.asn)
        str += chr(self.hold_time)
        str += ''.join(chr(int(s)) for s in self.router_id.split('.'))
        str += chr(len(self.capabilities))
        return str
