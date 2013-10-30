# encoding: utf-8
"""
Author: Quentin Loos <contact@quentinloos.be>
"""
import struct
import ipaddr


class Flag(int):

    """
    The high-order bit (bit 0) of the Attribute Flags octet is the
    Optional bit.  It defines whether the attribute is optional (if
    set to 1) or well-known (if set to 0).

    The second high-order bit (bit 1) of the Attribute Flags octet
    is the Transitive bit.  It defines whether an optional
    attribute is transitive (if set to 1) or non-transitive (if set
    to 0).
    For well-known attributes, the Transitive bit MUST be set to 1.

    The third high-order bit (bit 2) of the Attribute Flags octet
    is the Partial bit.  It defines whether the information
    contained in the optional transitive attribute is partial (if
    set to 1) or complete (if set to 0).  For well-known attributes
    and for optional non-transitive attributes, the Partial bit
    MUST be set to 0.

    The fourth high-order bit (bit 3) of the Attribute Flags octet
    is the Extended Length bit.  It defines whether the Attribute
    Length is one octet (if set to 0) or two octets (if set to 1).

    The lower-order four bits of the Attribute Flags octet are
    unused.  They MUST be zero when sent and MUST be ignored when
    received.    This is an optional non-transitive attribute that is a
    four-octet unsigned integer.  The value of this attribute
    MAY be used by a BGP speaker's Decision Process to
    discriminate among multiple entry points to a neighboring

    """

    OPTIONAL      = 1 << 7
    TRANSITIVE    = 1 << 6
    PARTIAL       = 1 << 5
    EXTEND_LENGTH = 1 << 4


class PathAttribute(object):

    """
    Each path attribute is a triple
    <attribute type, attribute length, attribute value> of variable
    length.

    Attribute Type is a two-octet field that consists of the
    Attribute Flags octet, followed by the Attribute Type Code
    octet::

        0                   1
        0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        |  Attr. Flags  |Attr. Type Code|
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

    The attribute Flags is define in :py:class:`Flag`

    The Attribute Type Code octet contains the Attribute Type Code.

    If the Extended Length bit of the Attribute Flags octet is set
    to 0, the third octet of the Path Attribute contains the length
    of the attribute data in octets.

    If the Extended Length bit of the Attribute Flags octet is set
    to 1, the third and fourth octets of the path attribute contain
    the length of the attribute data in octets.

    The remaining octets of the Path Attribute represent the
    attribute value and are interpreted according to the Attribute
    Flags and the Attribute Type Code.
    """

    def __init__(self, flags, type_code, length, value):
        """
        :param int flags: flags of the Path Attribute.
        :param int type_code: type code of the Path Attribute.
        :param int length: length in octet of the value.
        :param value: value of the Path Attribute.
        """
        self.flags     = flags
        self.type_code = type_code
        self.length    = length
        self.value     = value

    def __len__(self):
        length_octect = 2 if(self.flags & Flag.EXTEND_LENGTH) else 1
        return 2 + length_octect + self.length()

    def pack(self):
        """
        Return a string representing the packet.
        """
        result = struct.pack('!B', self.flags)
        result += struct.pack('!B', self.type_code)

        # Extended Length ?
        if(self.flags & Flag.EXTEND_LENGTH):
            result += struct.pack('!H', self.length())
        else:
            result += struct.pack('!B', self.length())

        # Pack value
        result += self._value_pack()
        return result

    def _value_pack(self):
        """
        Return a string representing the value packed.
        """
        length = self.length()
        if(length == 0):
            return ''
        if(length == 1):
            return struct.pack('!B', self.value)
        elif(length == 2):
            return struct.pack('!H', self.value)
        elif(length == 4):
            return struct.pack('!I', self.value)
        raise Exception


class Origin(PathAttribute):

    """
    ORIGIN is a well-known mandatory attribute that defines the
    origin of the path information. The data octet can assume
    the following values:

    +-------+----------------------------------------------+
    | Value |                   Meaning                    |
    +=======+==============================================+
    |   0   | IGP - Network Layer Reachability Information |
    |       | is interior to the originating AS            |
    +-------+----------------------------------------------+
    |   1   | EGP - Network Layer Reachability Information |
    |       | learned via the EGP protocol [RFC904]        |
    +-------+----------------------------------------------+
    |   2   | INCOMPLETE - Network Layer Reachability      |
    |       | Information learned by some other means      |
    +-------+----------------------------------------------+

    The ORIGIN attribute is generated by the speaker that originates
    the associated routing information. Its value SHOULD NOT be
    changed by any other speaker.
    """

    # Values
    IGP        = 0
    EGP        = 1
    INCOMPLETE = 2

    def __init__(self, value):
        """
        :param int value: Origin.IGP, Origin.EGP or Origin.INCOMPLETE
        """
        super(Origin, self).__init__(Flag.TRANSITIVE, 1, lambda: 1, value)


class ASPath(PathAttribute):

    """
    AS_PATH is a well-known mandatory attribute that is composed
    of a sequence of AS path segments.
    """

    class ASPathSegment(object):

        """
        Each AS path segment is represented by a triple
        <path segment type, path segment length, path segment value>.

        The path segment type is a 1-octet length field with the
        following values defined:

        +-------+-----------------------------------------------+
        | Value |                 Segment type                  |
        +=======+===============================================+
        |   1   | AS_SET: unordered set of ASes a route in the  |
        |       | UPDATE message has traversed                  |
        +-------+-----------------------------------------------+
        |   2   | AS_SEQUENCE: ordered set of ASes a route in   |
        |       | the UPDATE message has traversed              |
        +-------+-----------------------------------------------+

        The path segment length is a 1-octet length field,
        containing the number of ASes (not the number of octets) in
        the path segment value field.

        The path segment value field contains one or more AS
        numbers, each encoded as a 2-octet length field.
        """

        AS_SET      = 1
        AS_SEQUENCE = 2

        def __init__(self, type, value=None):
            """
            :param int type: ASPathSegment.AS_SET or ASPathSegment.AS_SEQUENCE
            :param list value: AS numbers
            """
            self.type = type
            self.value = value if value else []
            self.length = len(self.value)

        def __len__(self):
            # len(ASPathSegment) = len(segment_type) + len(segment_length) + len(ASes)
            # = 1 + 1 + 2 * segment_length
            return 2 + 2 * len(self.value)

        def pack(self):
            """
            Return a string representing the packet.
            """
            result = struct.pack('!B', self.type)
            result += struct.pack('!B', len(self.value))
            result += self._as_packed()
            return result

        def _as_packed(self):
            """
            Return a string representing the AS list.
            """
            result = ''
            for asn in self.value:
                result += struct.pack('!H', asn)
            return result

    def __init__(self, value=None):
        """
        :param list value: ASPathSegment list
        """
        length = lambda: sum([len(segment) for segment in self.value])
        super(ASPath, self).__init__(
            Flag.TRANSITIVE, 2, length, value if value else [])

    def _value_pack(self):
        return ''.join([segment.pack() for segment in self.value])


class NextHop(PathAttribute):

    """
    This is a well-known mandatory attribute that defines the
    (unicast) IP address of the router that SHOULD be used as
    the next hop to the destinations listed in the Network Layer
    Reachability Information field of the UPDATE message.
    """

    def __init__(self, value):
        """
        :param int/str value: IPv4 address of the next-hop
        """
        super(NextHop, self).__init__(
            Flag.TRANSITIVE, 3, lambda: 4, ipaddr.IPv4Address(value))

    def _value_pack(self):
        return self.value.packed


class MED(PathAttribute):

    """
    This is an optional non-transitive attribute that is a
    four-octet unsigned integer.  The value of this attribute
    MAY be used by a BGP speaker's Decision Process to
    discriminate among multiple entry points to a neighboring
    """

    def __init__(self, value):
        """
        :param int value: the MED
        """
        super(MED, self).__init__(Flag.OPTIONAL, 4, lambda: 4, value)


class LocalPref(PathAttribute):

    """
    LOCAL_PREF is a well-known attribute that is a four-octet
    unsigned integer.  A BGP speaker uses it to inform its other
    internal peers of the advertising speaker's degree of
    preference for an advertised route.
    """

    def __init__(self, value):
        """
        :param int value: the local preference.
        """
        super(LocalPref, self).__init__(Flag.TRANSITIVE, 5, lambda: 4, value)


class AtomicAggregate(PathAttribute):

    """
    ATOMIC_AGGREGATE is a well-known discretionary attribute of length 0.
    """

    def __init__(self):
        super(AtomicAggregate, self).__init__(Flag.TRANSITIVE, 6, lambda: 0, 0)


class Aggregator(PathAttribute):

    """
    AGGREGATOR is an optional transitive attribute of length 6.
    The attribute contains the last AS number that formed the
    aggregate route (encoded as 2 octets), followed by the IP
    address of the BGP speaker that formed the aggregate route
    (encoded as 4 octets).  This SHOULD be the same address as
    the one used for the BGP Identifier of the speaker.
    """

    def __init__(self, asn, ip):
        """
        :param int asn: The AS number.
        :param int or str ip: The IP Address.
        """
        self.asn   = asn
        self.ip    = ipaddr.IPv4Address(ip)
        self.value = self.asn << 32 + int(self.ip)
        super(Aggregator, self).__init__(
            Flag.OPTIONAL | Flag.TRANSITIVE, 7, lambda: 6, self.value)

    def _value_pack(self):
        return struct.pack('!HI', self.asn, int(self.ip))
