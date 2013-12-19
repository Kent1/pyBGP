# encoding: utf-8
"""
Author: Quentin Loos <contact@quentinloos.be>
"""
import struct

from pybgp.bgp.message import Message, Type


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
        An assigned IPv4 address of the sender.
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

    MIN_LEN = 29

    def __init__(self, asn, hold_time, router_id, capabilities=None):
        """
        :param int asn: The AS number of the sender.
        :param int hold_time: The hold_time of the sender.
        :param int router_id: The router_id of the sender.
        :param int version: Version of BGP (default=4).
        :param list capabilities: List of capabilities (default=None).
        """
        super(Open, self).__init__(Type.OPEN)
        self.version      = 4
        self.asn          = asn
        self.hold_time    = hold_time
        self.router_id    = router_id
        self.capabilities = capabilities or []

    def __str__(self):
        result = 'BGP OPEN Message ('
        result += 'AS %d, '          % self.asn
        result += 'Hold Time %d, '   % self.hold_time
        result += 'Router ID %s, '   % self.router_id
        result += 'Capabilities %s)' % self.capabilities
        return result

    def __len__(self):
        return self.MIN_LEN + len(self.capabilities)

    def pack(self):
        """
        Return a string representation of the packet to send.
        This string includes header, version, AS number, Hold Time, Router ID,
        the length of capabilities and the list of capabilities.
        """
        result = super(Open, self).pack()
        result += struct.pack('!BHH', self.version, self.asn, self.hold_time)
        result += struct.pack('!IB', self.router_id, len(self.capabilities))
        #TODO Support capabilities
        return result

    @classmethod
    def unpack(cls, msg):
        """
        Factory function.
        Return a OPEN object corresponding to the given packed msg.
        """
        length, type = Message.header_unpack(msg)
        if type != Type.OPEN:
            raise Exception

        version, asn, hold_time, router_id = struct.unpack('!BHHI', msg[19:28])
        length_capabilities = struct.unpack('!B', msg[28:29])
        if length_capabilities:
            pass
        return cls(asn, hold_time, router_id)
