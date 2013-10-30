# encoding: utf-8
"""
Author: Quentin Loos <contact@quentinloos.be>
"""
from pybgp.bgp.message import Message, Type


class KeepAlive(Message):

    """
    BGP does not use any TCP-based, keep-alive mechanism to determine if
    peers are reachable.  Instead, KEEPALIVE messages are exchanged
    between peers often enough not to cause the Hold Timer to expire.  A
    reasonable maximum time between KEEPALIVE messages would be one third
    of the Hold Time interval.  KEEPALIVE messages MUST NOT be sent more
    frequently than one per second.  An implementation MAY adjust the
    rate at which it sends KEEPALIVE messages as a function of the Hold
    Time interval.

    If the negotiated Hold Time interval is zero, then periodic KEEPALIVE
    messages MUST NOT be sent.

    A KEEPALIVE message consists of only the message header and has a
    length of 19 octets.
    """

    def __init__(self):
        super(KeepAlive, self).__init__(Type.KEEPALIVE)

    def __str__(self):
        return 'BGP KEEPALIVE Message'
