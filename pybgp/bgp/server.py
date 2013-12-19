# Python import
import sys

# Twisted import
from twisted.internet import reactor, protocol, task
from twisted.python import log
log.startLogging(sys.stdout)

# My import
from pybgp.bgp import message
from pybgp.bgp import State


class BGP(protocol.Protocol):

    def __init__(self, asn, hold_time, router_id):
        log.msg('Initializing new BGP connection.')
        self.state = State.IDLE
        self.status = None
        self.buffer = ''
        self.asn = asn
        self.hold_time = hold_time
        self.router_id = router_id
        self.keepalive_timer = task.LoopingCall(self.keepalive)
        self.hold_timer = None
        # ACTIVE state consists to listen for TCP connections
        self.state = State.ACTIVE

    def connectionMade(self):
        log.msg('Connection made.')
        if self.state == State.ACTIVE:
            # Send Open message
            self.open()
            # Set hold_time to a large value (4 minutes)
            self.hold_timer = reactor.callLater(4 * 60, self.hold_timer_expired)
            self.state = State.OPENSENT

    def connectionLost(self, reason):
        pass

    def dataReceived(self, data):
        self.buffer += data

        if len(self.buffer) < 19:
            return

        # We received at least the header, we can parse it
        length, type = message.Message.header_unpack(self.buffer[:19])

        if len(self.buffer) < length:
            return

        # We received the entire packet
        msg = self.buffer[:length]
        self.buffer = self.buffer[length:]

        # TODO Call when running
        if type == message.Type.OPEN:
            self.handle_open(msg)
        elif type == message.Type.UPDATE:
            self.handle_update(msg)
        elif type == message.Type.KEEPALIVE:
            self.handle_keepalive(msg)
        elif type == message.Type.NOTIFICATION:
            self.handle_notification(msg)
        else:
            pass

    def handle_open(self, msg):
        log.msg('OPEN message received.')

        msg = message.Open.unpack(msg)
        print msg

        if self.state == State.OPENSENT:
            # Check correctness of the OPEN message
            try:
                msg = message.OpenFactory(msg)
            except:
                pass

            # Send KeepAlive
            self.keepalive()
            # Set Hold Time to the negotiated value
            if self.hold_time > msg.hold_time:
                self.hold_time = msg.hold_time
            # If hold_time is not 0
            if self.hold_time:
                # Set keepalive timer and the hold timer
                self.keepalive_timer.start(1.0)  # call every second
                self.hold_timer.reset(self.hold_time)
            if self.asn == msg.asn:
                self.status = 'internal'
            else:
                self.status = 'external'
            self.state = State.OPENCONFIRM
        else:
            pass

    def handle_update(self, msg):
        log.msg('UPDATE message received.')
        msg = message.Update.unpack(msg)

    def handle_keepalive(self, msg):
        log.msg('KEEPALIVE message received.')
        msg = message.KeepAlive.unpack(msg)

    def handle_notification(self, msg):
        log.msg('NOTIFICATION message received.')
        msg = message.Notification.unpack(msg)
        print msg
        self.hold_timer.cancel()
        self.keepalive_timer.stop()
        self.transport.loseConnection()

    def hold_timer_expired(self):
        log.msg('Hold Timer expired !')
        if self.state == State.OPENSENT:
            self.send(message.HoldTimerExpired())
            self.transport.loseConnection()

    def send(self, msg):
        self.transport.write(msg.pack())

    def open(self):
        log.msg('Send OPEN message.')
        self.send(message.Open(self.asn, self.hold_time, self.router_id))

    def keepalive(self):
        log.msg('Send KEEPALIVE message.')
        self.send(message.KeepAlive())


class BGPFactory(protocol.Factory):

    # protocol = BGP

    def __init__(self):
        self.peers = []

    def buildProtocol(self, addr):
        log.msg('Create new BGP connection.')
        return BGP(65100, 3, 0x0A000002)

reactor.listenTCP(179, BGPFactory())
# for (host, port) in peers:
# reactor.connectTCP(host, port, BGPFactory(), timeout=30, bindAddress=None)
reactor.run()
