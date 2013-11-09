# encoding: utf-8
"""
Author: Quentin Loos <contact@quentinloos.be>
"""
import struct


class Flag(object):

    """
    Attribute Flag.

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
    unused. They MUST be zero when sent and MUST be ignored when
    received.
    """

    OPTIONAL      = 1 << 7
    TRANSITIVE    = 1 << 6
    PARTIAL       = 1 << 5
    EXTEND_LENGTH = 1 << 4


class TypeCode(object):

    """
    Constants type code of Path Attributes.
    """

    ORIGIN          = 1
    ASPATH          = 2
    NEXTHOP         = 3
    MED             = 4
    LOCALPREF       = 5
    ATOMICAGGREGATE = 6
    AGGREGATOR      = 7


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
        :param function length:
            function returning the length in octet of the value.
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
        result = struct.pack('!BB', self.flags, self.type_code)

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
        if(self.length() == 0):
            return ''
        if(self.length() == 1):
            return struct.pack('!B', self.value)
        elif(self.length() == 2):
            return struct.pack('!H', self.value)
        elif(self.length() == 4):
            return struct.pack('!I', self.value)
        raise Exception

    @classmethod
    def unpack(cls, path_attr):
        """
        Unpack the string given in parameter and return a PathAttribute
        object (or a child of it).
        """
        flags, type_code, value_length = cls.header_unpack(path_attr)
        header_length = 2 + (2 if flags & Flag.EXTEND_LENGTH else 1)
        value = cls.value_unpack(path_attr[header_length:header_length+value_length])
        return cls(*value)

    @classmethod
    def header_unpack(cls, path_attr):
        """
        Return the flags, type_code and length of a
        PathAttribute string packed.
        """
        flags, type_code = struct.unpack('!BB', path_attr[:2])
        if flags & Flag.EXTEND_LENGTH:
            length, = struct.unpack('!H', path_attr[2:4])
        else:
            length, = struct.unpack('!B', path_attr[2:3])

        return flags, type_code, length

    @classmethod
    def value_unpack(cls, value):
        """
        Return a string representing the value packed.
        """
        if(len(value) == 0):
            return ''
        if(len(value) == 1):
            return struct.unpack('!B', value)
        elif(len(value) == 2):
            return struct.unpack('!H', value)
        elif(len(value) == 4):
            return struct.unpack('!I', value)
        return struct.unpack('!%ds' % len(value), value)

    @classmethod
    def create(cls, path_attr):
        """
        Create the right PathAttribute Child object, given the
        packed string.
        """
        flags, type_code, length = cls.header_unpack(path_attr)

        if type_code == TypeCode.ORIGIN:
            return Origin.unpack(path_attr[:len(path_attr)])
        elif type_code == TypeCode.ASPATH:
            return ASPath.unpack(path_attr[:len(path_attr)])
        elif type_code == TypeCode.NEXTHOP:
            return NextHop.unpack(path_attr[:len(path_attr)])
        elif type_code == TypeCode.MED:
            return MED.unpack(path_attr[:len(path_attr)])
        elif type_code == TypeCode.LOCALPREF:
            return LocalPref.unpack(path_attr[:len(path_attr)])
        elif type_code == TypeCode.ATOMICAGGREGATE:
            return AtomicAggregate.unpack(path_attr[:len(path_attr)])
        elif type_code == TypeCode.AGGREGATOR:
            return Aggregator.unpack(path_attr[:len(path_attr)])
        else:
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
        super(Origin, self).__init__(
            Flag.TRANSITIVE, TypeCode.ORIGIN, lambda: 1, value)


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
            self.value = value or []

        def __len__(self):
            # len(ASPathSegment) = len(segment_type) + len(segment_length) + len(ASes)
            # = 1 + 1 + 2 * segment_length
            return 2 + 2 * len(self.value)

        def pack(self):
            """
            Return a string representing the ASPathSegment.
            """
            result = struct.pack('!BB', self.type, len(self.value))
            result += ''.join([struct.pack('!H', asn) for asn in self.value])
            return result

        @classmethod
        def unpack(cls, segment_packed):
            """
            Return an ASPathSegment object corresponding
            to the string in parameter.
            """
            type, length = struct.unpack('!BB', segment_packed[:2])
            asn = struct.unpack('!%dH' % length, segment_packed[2:2+2*length])
            return cls(type, value=list(asn))

    def __init__(self, value):
        """
        :param list value: ASPathSegment list
        """
        length = lambda: sum([len(segment) for segment in self.value])
        super(ASPath, self).__init__(
            Flag.TRANSITIVE, TypeCode.ASPATH, length, value or [])

    def _value_pack(self):
        """
        Pack all the segment in a string and return it.
        """
        return ''.join([segment.pack() for segment in self.value])

    @classmethod
    def value_unpack(cls, value):
        """
        Return the list of the segment unpacked include in the value param.
        """
        segments = []
        while(value):
            segment = cls.ASPathSegment.unpack(value)
            segments.append(segment)
            value = value[len(segment):]
        return [segments]


class NextHop(PathAttribute):

    """
    This is a well-known mandatory attribute that defines the
    (unicast) IP address of the router that SHOULD be used as
    the next hop to the destinations listed in the Network Layer
    Reachability Information field of the UPDATE message.
    """

    def __init__(self, value):
        """
        :param int value: IPv4 address of the next-hop
        """
        super(NextHop, self).__init__(
            Flag.TRANSITIVE, TypeCode.NEXTHOP, lambda: 4, value)


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
        super(MED, self).__init__(
            Flag.OPTIONAL, TypeCode.MED, lambda: 4, value)


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
        super(LocalPref, self).__init__(
            Flag.TRANSITIVE, TypeCode.LOCALPREF, lambda: 4, value)


class AtomicAggregate(PathAttribute):

    """
    ATOMIC_AGGREGATE is a well-known discretionary attribute of length 0.
    """

    def __init__(self):
        super(AtomicAggregate, self).__init__(
            Flag.TRANSITIVE, TypeCode.ATOMICAGGREGATE, lambda: 0, None)


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
        :param int ip: The IP Address.
        """
        self.asn   = asn
        self.ip    = ip
        self.value = self.asn << 32 + self.ip
        super(Aggregator, self).__init__(
            Flag.OPTIONAL | Flag.TRANSITIVE,
            TypeCode.AGGREGATOR, lambda: 6, self.value)

    def _value_pack(self):
        """
        Return a string representing the value packed.
        """
        return struct.pack('!HI', self.asn, self.ip)

    @classmethod
    def value_unpack(cls, value):
        """
        Return a string representing the value unpacked.
        """
        return struct.unpack('!HI', value)
