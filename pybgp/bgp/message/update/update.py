# encoding: utf-8
"""
Author: Quentin Loos <contact@quentinloos.be>
"""
from pybgp.bgp.message import Message
from struct import pack


class Update(Message):

    """
    BGP UPDATE Message.
    Use to advertise feasible routes to a peer, or withdraw feasible routes.

    Format of the message::

        +-----------------------------------------------------+
        |   Withdrawn Routes Length (2 octets)                |
        +-----------------------------------------------------+
        |   Withdrawn Routes (variable)                       |
        +-----------------------------------------------------+
        |   Total Path Attribute Length (2 octets)            |
        +-----------------------------------------------------+
        |   Path Attributes (variable)                        |
        +-----------------------------------------------------+
        |   Network Layer Reachability Information (variable) |
        +-----------------------------------------------------+

    Withdrawn Routes Length:
        Indicates the total length of the Withdrawn Routes field in octets.
    Withdrawn Routes:
        Contains a list of IP address prefixes for the routes that are being
        withdrawn
    Total Path Attribute Length:
        Total length of the Path Attributes field in octets.
    Path Attributes:
        A variable-length sequence of path attributes is present in every
        UPDATE message, except for an UPDATE message that carries only the
        withdrawn routes.

    Network Layer Reachability Information:
        Contains a list of IP address prefixes.

    See http://www.ietf.org/rfc/rfc4271.txt for more informations
    """

    type       = Message.Type.UPDATE
    min_length = 23

    def __init__(self, withdrawn_routes=None, path_attr=None, nlris=None):
        """
        :param withdrawn_routes: list of IPFields to withdraw.
        :param path_attr: list of PathAttributes
        :param nlris: list of IPFields to advertise.
        """
        self.withdrawn_routes = withdrawn_routes if withdrawn_routes else []
        self.path_attr        = path_attr if path_attr else []
        self.nlris            = nlris if nlris else []

    @property
    def length(self):
        return self.min_length
        + sum([network.length() for network in self.withdrawn_routes])
        + len(self.path_attr)

    def pack(self):
        """
        Return a string representation of the packet to send.
        This string includes header, version, AS number, Hold Time, Router ID,
        the length of capabilities and the list of capabilities.
        """
        str = super(Update, self).pack()
        # Length of withdrawn routes field in octects
        length = sum([route.length() for route in self.withdrawn_routes])
        str += pack('!H', length)
        # 2-tuple IPField
        str += ''.join([network.pack() for network in self.withdrawn_routes])
        # Length of path attr
        length = sum([attr.length for attr in self.path_attr])
        str += pack('!H', length)
        # Path Attributes
        str += ''.join([attr.pack() for attr in self.path_attr])
        # NLRI
        str += ''.join([network.pack() for network in self.nlris])
        return str


class IPField(object):

    """
    IP address prefix is encoded as a 2-tuple of the form <length, prefix>::

        +---------------------------+
        |   Length (1 octet)        |
        +---------------------------+
        |   Prefix (variable)       |
        +---------------------------+

    Length:
        The Length field indicates the length in bits of the IP
        address prefix.  A length of zero indicates a prefix that
        matches all IP addresses (with prefix, itself, of zero
        octets).

    Prefix:
        The Prefix field contains an IP address prefix, followed by
        the minimum number of trailing bits needed to make the end
        of the field fall on an octet boundary.  Note that the value
        of trailing bits is irrelevant.
    """

    def __init__(self, length, prefix):
        self.length  = length
        self.prefix  = prefix
        self.octects = self._number_octects()

    def _number_octects(self):
        number_octect = 4
        if self.length <= 24:
            number_octect = 3
        if self.length <= 16:
            number_octect = 2
        if self.length <= 8:
            number_octect = 1
        if self.length == 0:
            number_octect = 0
        return number_octect

    def length(self):
        return self.octects + 1

    def pack(self):
        packed = pack('!B', self.length)
        prefix_split = self.prefix.split('.')
        for i in range(self.octects):
            packed += pack('!B', prefix_split[i])
        return packed
