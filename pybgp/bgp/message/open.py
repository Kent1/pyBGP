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

    Version           : 1-octect uint. Indicates the protocol version.
    Autonomous System : 2-octect uint. ASN of the sender of this message.
    Hold Time         : 2-octect uint. Seconds between message (KEEPALIVE).
    BGP Identifier    : 4-octect uint. An assigned IP address of the sender.
    Opt. Parm. Length : 1-octect uint. Length of the optional parameters.

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

    List of optional parameters. Each parameters is encoded as a
    <Parameter Type, Parameter Length, Parameter Value> triplet.

    Parm. Type   : 1-octect. Identifies individual parameters.
    Parm. Length : 1-octect. Contains the length of the parameter value
                   in octects.
    Parm. Value  : Parameter interpreted according to the Parm. Type.
    (RFC 3392)

         0                   1
     0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6
     +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-...
     |  Parm. Type   | Parm. Length  |  Parameter Value (variable)
     +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-...
    """

    type   = Message.Type.OPEN
    length = 29

    def __init__(self, asn, hold_time, router_id, version=4, capabilities=None):
        self.version      = version
        self.asn          = asn
        self.hold_time    = hold_time
        self.router_id    = router_id
        self.capabilities = capabilities

    def __str__(self):
        result = 'BGP OPEN Message ('
        result += 'Version %d, ' % self.version
        result += 'AS %d, ' % self.asn
        result += 'Hold Time %d, ' % self.hold_time
        result += 'Router ID %s, ' % self.router_id
        result += 'Capabilities %s)' % self.capabilities
        return result

    def pack(self):
        str = super(Open, self).pack()
        str += chr(self.version)
        str += pack('!H', self.asn)
        str += chr(self.hold_time)
        str += ''.join(chr(int(s)) for s in self.router_id.split('.'))
        str += chr(len(self.capabilities) if self.capabilities else 0)
        return str
