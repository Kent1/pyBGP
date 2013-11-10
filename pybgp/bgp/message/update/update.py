# encoding: utf-8
"""
Author: Quentin Loos <contact@quentinloos.be>
"""
import struct

from pybgp.bgp.message import Message, Type


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

    MIN_LEN = 23

    def __init__(self, wd_routes=None, path_attr=None, nlris=None):
        """
        :param wd_routes: list of IPFields to withdraw.
        :param path_attr: list of PathAttributes
        :param nlris: list of IPFields to advertise.
        """
        super(Update, self).__init__(Type.UPDATE)
        self.wd_routes = wd_routes or []
        self.path_attr = path_attr or []
        self.nlris     = nlris or []

    def __len__(self):
        return (
            self.MIN_LEN +
            sum([len(route) for route in self.wd_routes]) +
            sum([len(attr) for attr in self.path_attr]) +
            sum([len(nlri) for nlri in self.nlris])
        )

    def pack(self):
        """
        Return a string representation of the packet to send.
        This string includes header, version, AS number, Hold Time, Router ID,
        the length of capabilities and the list of capabilities.
        """
        result = super(Update, self).pack()
        # Length of withdrawn routes field in octects
        length = sum([len(route) for route in self.wd_routes])
        result += struct.pack('!H', length)
        # 2-tuple IPField
        result += ''.join([route.pack() for route in self.wd_routes])
        # Length of path attr
        length = sum([len(attr) for attr in self.path_attr])
        result += struct.pack('!H', length)
        # Path Attributes
        result += ''.join([attr.pack() for attr in self.path_attr])
        # NLRI
        result += ''.join([nlri.pack() for nlri in self.nlris])
        return result

    @classmethod
    def unpack(cls, msg):
        """
        Factory function. Return a UPDATE object corresponding
        to the msg unpacked.
        """

        length, type = Message.header_unpack(msg)
        msg = msg[19:]

        # Unpack Withdrawn routes
        wd_routes_length, = struct.unpack('!H', msg[:2])
        wd_routes = []
        wr_packed = msg[2:2+wd_routes_length]
        while(wr_packed):
            ipfield = IPField.unpack(wr_packed)
            wd_routes.append(ipfield)
            wr_packed = wr_packed[len(ipfield):]
        msg = msg[2+wd_routes_length:]

        # Unpack Path Attributes
        path_attrs_length, = struct.unpack('!H', msg[:2])
        path_attrs = []
        pa_packed = msg[2:2+path_attrs_length]
        while(pa_packed):
            path_attr = PathAttribute.create(pa_packed)
            path_attrs.append(path_attr)
            pa_packed = pa_packed[len(path_attr):]
        msg = msg[2+path_attrs_length:]

        # Unpack NLRI
        nlris = []
        nlris_packed = msg[:length]
        while(nlris_packed):
            ipfield = IPField.unpack(nlris_packed)
            nlris.append(ipfield)
            nlris_packed = nlris_packed[len(ipfield):]

        return cls(wd_routes, path_attrs, nlris)


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
        """
        :param int length: The length of the prefix.
        :param int prefix: The IP prefix.
        """
        self.length  = length
        self.prefix  = prefix
        self.octects = IPField.number_octets(length)

    def __len__(self):
        return self.octects + 1

    def pack(self):
        """
        Return a string representing the IPField packed.

        :param int/str prefix: The IP prefix.
        """
        packed = struct.pack('!BI', self.length, self.prefix)
        return packed[:1+self.octects]

    @classmethod
    def unpack(cls, packed):
        """
        Given the IPField packed string, return an IPField object.
        """
        length = struct.unpack('!B', packed[0:1])[0]
        number = cls.number_octets(length)
        prefix = struct.unpack('!%ds' % number, packed[1:1+number])
        return IPField(length, prefix)

    @classmethod
    def number_octets(cls, length):
        """
        Return the minimal number of octets is necessary
        to stock the ip prefix.
        """
        return ((length - 1) / 8) + 1
