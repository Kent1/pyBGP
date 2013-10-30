# encoding: utf-8
"""
Author: Quentin Loos <contact@quentinloos.be>
"""
from pybgp.bgp.message import Message, Type
from struct import pack


class Notification(Message):

    """
    A NOTIFICATION message is sent when an error condition is detected.
    The BGP connection is closed immediately after it is sent.

    In addition to the fixed-size BGP header, the NOTIFICATION message
    contains the following fields::

        0                   1                   2                   3
        0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        | Error code    | Error subcode |   Data (variable)             |
        +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

    Error Code:

        This 1-octet unsigned integer indicates the type of
        NOTIFICATION.  The Error Codes are define in the RFC 4271.

    Error subcode:

        This 1-octet unsigned integer provides more specific
        information about the nature of the reported error.  Each Error
        Code may have one or more Error Subcodes associated with it.
        If no appropriate Error Subcode is defined, then a zero
        (Unspecific) value is used for the Error Subcode field.

    Data:

        This variable-length field is used to diagnose the reason for
        the NOTIFICATION.  The contents of the Data field depend upon
        the Error Code and Error Subcode.  See Section 6 in RFC 4271
        for more details.

        Note that the length of the Data field can be determined from
        the message Length field by the formula:

                Message Length = 21 + Data Length

    The minimum length of the NOTIFICATION message is 21 octets
    (including message header).
    """

    MIN_LEN = 21

    def __init__(self, error_code, error_subcode, data=None):
        """
        :param int error_code: The error code.
        :param int error_subcode: The error subcode.
        :param str data: The data.
        """
        self.error_code    = error_code
        self.error_subcode = error_subcode
        self.data          = data if data else ''
        super(Notification, self).__init__(Type.NOTIFICATION)

    def __str__(self):
        result = 'BGP NOTIFICATION Message ('
        result += 'Error code %d, ' % self.error_code
        result += 'Error subcode %d, ' % self.error_subcode
        if self.data:
            result += 'Data %s' % self.data
        result += ')'
        return result

    def __len__(self):
        return self.MIN_LEN + len(self.data)

    def pack(self):
        """
        Return a string representation of the packet to send.
        This string includes header, error code, error subcode
        and data.
        """
        result = super(Notification, self).pack()
        result += pack('!B', self.error_code)
        result += pack('!B', self.error_subcode)
        result += self.data
        return result


class HeaderError(Notification):

    """
    Notification with error code 1, Message Header Error.
    """

    UNSPECIFIC                  = 0
    CONNECTION_NOT_SYNCHRONIZED = 1
    BAD_MESSAGE_LENGTH          = 2
    BAD_MESSAGE_TYPE            = 3

    str_subcode = {
        UNSPECIFIC                  : 'Unspecific.',
        CONNECTION_NOT_SYNCHRONIZED : 'Connection Not Synchronized.',
        BAD_MESSAGE_LENGTH          : 'Bad Message Length.',
        BAD_MESSAGE_TYPE            : 'Bad Message Type.',
    }

    def __init__(self, error_subcode=0, data=None):
        super(HeaderError, self).__init__(1, error_subcode, data)

    def __str__(self):
        result = 'BGP NOTIFICATION Message ('
        result += 'HEADER Error, '
        result += '%s, ' % self.str_subcode[self.error_subcode]
        if self.data:
            result += 'Data %s' % self.data
        result += ')'
        return result


class OpenError(Notification):

    """
    Notification with error code 2, OPEN Message Error.
    """

    UNSPECIFIC                     = 0
    UNSUPPORTED_VERSION_NUMBER     = 1
    BAD_PEER_AS                    = 2
    BAD_BGP_IDENTIFIER             = 3
    UNSUPPORTED_OPTIONAL_PARAMETER = 4
    AUTHENTICATION_NOTIFICATION    = 5
    UNACCEPTABLE_HOLD_TIME         = 6

    str_subcode = {
        UNSPECIFIC                     : 'Unspecific.',
        UNSUPPORTED_VERSION_NUMBER     : 'Unsupported Version Number.',
        BAD_PEER_AS                    : 'Bad Peer AS.',
        BAD_BGP_IDENTIFIER             : 'Bad BGP Identifier.',
        UNSUPPORTED_OPTIONAL_PARAMETER : 'Unsupported Optional Parameter.',
        AUTHENTICATION_NOTIFICATION    : 'Authentication Notification (Deprecated).',
        UNACCEPTABLE_HOLD_TIME         : 'Unacceptable Hold Time.',
    }

    def __init__(self, error_subcode=0, data=None):
        super(OpenError, self).__init__(2, error_subcode, data)

    def __str__(self):
        result = 'BGP NOTIFICATION Message ('
        result += 'OPEN Error, '
        result += '%s, ' % self.str_subcode[self.error_subcode]
        if self.data:
            result += 'Data %s' % self.data
        result += ')'
        return result


class UpdateError(Notification):

    """
    Notification with error code 3, UPDATE Message Error.
    """

    UNSPECIFIC                        = 0
    MALFORMED_ATTRIBUTE_LIST          = 1
    UNRECOGNIZED_WELL_KNOWN_ATTRIBUTE = 2
    MISSING_WELL_KNOWN_ATTRIBUTE      = 3
    ATTRIBUTE_FLAGS_ERROR             = 4
    ATTRIBUTE_LENGTH_ERROR            = 5
    INVALID_ORIGIN_ATTRIBUTE          = 6
    AS_ROUTING_LOOP                   = 7
    INVALID_NEXT_HOP_ATTRIBUTE        = 8
    OPTIONAL_ATTRIBUTE_ERROR          = 9
    INVALID_NETWORK_FIELD             = 10
    MALFORMED_AS_PATH                 = 11

    str_subcode = {
        UNSPECIFIC                        : 'Unspecific.',
        MALFORMED_ATTRIBUTE_LIST          : 'Malformed Attribute List',
        UNRECOGNIZED_WELL_KNOWN_ATTRIBUTE : 'Unrecognized Well-known Attribute',
        MISSING_WELL_KNOWN_ATTRIBUTE      : 'Missing Well-known Attribute',
        ATTRIBUTE_FLAGS_ERROR             : 'Attribute Flags Error',
        ATTRIBUTE_LENGTH_ERROR            : 'Attribute Length Error',
        INVALID_ORIGIN_ATTRIBUTE          : 'Invalid ORIGIN Attribute',
        AS_ROUTING_LOOP                   : 'AS Routing Loop',
        INVALID_NEXT_HOP_ATTRIBUTE        : 'Invalid NEXT_HOP Attribute',
        OPTIONAL_ATTRIBUTE_ERROR          : 'Optional Attribute Error',
        INVALID_NETWORK_FIELD             : 'Invalid Network Field',
        MALFORMED_AS_PATH                 : 'Malformed AS_PATH',

    }

    def __init__(self, error_subcode=0, data=None):
        super(UpdateError, self).__init__(3, error_subcode, data)

    def __str__(self):
        result = 'BGP NOTIFICATION Message ('
        result += 'UPDATE Error, '
        result += '%s, ' % self.str_subcode[self.error_subcode]
        if self.data:
            result += 'Data %s' % self.data
        result += ')'
        return result


class HoldTimerExpired(Notification):

    """
    Notification with error code 4, Hold Timer Expired.
    """

    UNSPECIFIC = 0

    str_subcode = {
        UNSPECIFIC : 'Unspecific.',
    }

    def __init__(self, error_subcode=0, data=None):
        super(HoldTimerExpired, self).__init__(4, error_subcode, data)

    def __str__(self):
        result = 'BGP NOTIFICATION Message ('
        result += 'Hold Timer Expired, '
        result += '%s, ' % self.str_subcode[self.error_subcode]
        if self.data:
            result += 'Data %s' % self.data
        result += ')'
        return result


class FSMError(Notification):

    """
    Notification with error code 5, Finite State Machine Error.
    """

    UNSPECIFIC = 0

    str_subcode = {
        UNSPECIFIC : 'Unspecific.',
    }

    def __init__(self, error_subcode=0, data=None):
        super(FSMError, self).__init__(5, error_subcode, data)

    def __str__(self):
        result = 'BGP NOTIFICATION Message ('
        result += 'Finite State Machine Error, '
        result += '%s, ' % self.str_subcode[self.error_subcode]
        if self.data:
            result += 'Data %s' % self.data
        result += ')'
        return result


class FSMError(Notification):

    """
    Notification with error code 5, Cease.
    """

    UNSPECIFIC = 0

    str_subcode = {
        UNSPECIFIC : 'Unspecific.',
    }

    def __init__(self, error_subcode=0, data=None):
        super(FSMError, self).__init__(6, error_subcode, data)

    def __str__(self):
        result = 'BGP NOTIFICATION Message ('
        result += 'Cease, '
        result += '%s, ' % self.str_subcode[self.error_subcode]
        if self.data:
            result += 'Data %s' % self.data
        result += ')'
        return result
