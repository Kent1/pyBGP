"""
Unit tests for BGP messages

Author: Quentin Loos <contact@quentinloos.be>
"""
import os
import sys
sys.path.insert(0, os.path.abspath('..'))
import struct
import ipaddr
import unittest

from pybgp.bgp.message import Open, Update
from pybgp.bgp.message.update import path_attribute


class TestOpen(unittest.TestCase):

    def setUp(self):
        self.asn       = 65000
        self.hold_time = 3
        self.router_id = ipaddr.IPAddress('10.0.0.1')
        self.open      = Open(self.asn, self.hold_time, self.router_id)

    def test_pack(self):
        # marker
        expected = chr(0xFF) * 16
        # length = 29, 2 bytes
        expected += chr(0)
        expected += chr(29)
        # type = 1 - OPEN
        expected += chr(1)
        # version = 4
        expected += chr(4)
        # asn = 65000, 0xFD 0xE8
        expected += struct.pack('!H', self.asn)
        # hold time = 3
        expected += struct.pack('!H', self.hold_time)
        # bgp identifier
        expected += chr(10)
        expected += chr(0)
        expected += chr(0)
        expected += chr(1)
        # param length
        expected += chr(0)
        self.assertEqual(self.open.pack(), expected)

    def test_len(self):
        self.assertEqual(len(self.open), Open.MIN_LEN)


class TestUpdate(unittest.TestCase):

    def setUp(self):
        self.update = Update()

    def test_len(self):
        self.assertEqual(len(self.update), Update.MIN_LEN)

    def test_pack(self):
        # Marker
        expected = chr(0xFF) * 16
        # length = 23, 2 bytes
        expected += chr(0)
        expected += chr(23)
        # type = 2 - UPDATE
        expected += chr(2)
        # Withdrawn Routes Length (2 octets)
        expected += struct.pack('!H', 0)
        # Withdrawn Routes
        # Total Path Attribute Length (2 octets)
        expected += struct.pack('!H', 0)
        # Path Attributes
        # Network Layer Reachability Information
        self.assertEqual(self.update.pack(), expected)

    def test_pack_path_attr(self):
        origin = path_attribute.Origin(1)
        self.update.path_attr.append(origin)

        as_path = path_attribute.ASPath(
            [path_attribute.ASPath.ASPathSegment(2, [123, 2345])])
        self.update.path_attr.append(as_path)

        next_hop = path_attribute.NextHop('10.16.23.19')
        self.update.path_attr.append(next_hop)

        med = path_attribute.MED(200)
        self.update.path_attr.append(med)

        local_pref = path_attribute.LocalPref(50)
        self.update.path_attr.append(local_pref)

        atomic_aggregate = path_attribute.AtomicAggregate()
        self.update.path_attr.append(atomic_aggregate)

        aggregator = path_attribute.Aggregator(65100, '30.0.1.1')
        self.update.path_attr.append(aggregator)

        # Marker
        expected = chr(0xFF) * 16
        # length = 23, 2 bytes
        expected += chr(0)
        expected += chr(23)
        # type = 2 - UPDATE
        expected += chr(2)
        # Withdrawn Routes Length (2 octets)
        expected += struct.pack('!H', 0)
        # Withdrawn Routes
        # Total Path Attribute Length (2 octets)
        expected += struct.pack('!H', 4+9+7+7+7+3+9)

        # Path Attributes
        ## Origin
        ### flags
        expected += struct.pack('!B', 1 << 6)
        ### type
        expected += struct.pack('!B', 1)
        ### length
        expected += struct.pack('!B', 1)
        ### value
        expected += struct.pack('!B', 1)

        ## AS Path
        ### flags
        expected += struct.pack('!B', 1 << 6)
        ### type
        expected += struct.pack('!B', 2)
        ### length
        expected += struct.pack('!B', 6)
        ### value
        expected += struct.pack('!B', 2)
        expected += struct.pack('!B', 2)
        expected += struct.pack('!H', 123)
        expected += struct.pack('!H', 2345)

        ## Next HOP
        ### flags
        expected += struct.pack('!B', 1 << 6)
        ### type
        expected += struct.pack('!B', 3)
        ### length
        expected += struct.pack('!B', 4)
        ### value
        expected += struct.pack('!B', 10)
        expected += struct.pack('!B', 16)
        expected += struct.pack('!B', 23)
        expected += struct.pack('!B', 19)

        ## MED
        ### flags
        expected += struct.pack('!B', 1 << 7)
        ### type
        expected += struct.pack('!B', 4)
        ### length
        expected += struct.pack('!B', 4)
        ### value
        expected += struct.pack('!B', 0)
        expected += struct.pack('!B', 0)
        expected += struct.pack('!B', 0)
        expected += struct.pack('!B', 200)

        ## Local Pref
        ### flags
        expected += struct.pack('!B', 1 << 6)
        ### type
        expected += struct.pack('!B', 5)
        ### length
        expected += struct.pack('!B', 4)
        ### value
        expected += struct.pack('!B', 0)
        expected += struct.pack('!B', 0)
        expected += struct.pack('!B', 0)
        expected += struct.pack('!B', 50)

        ## Atomic Aggregate
        ### flags
        expected += struct.pack('!B', 1 << 6)
        ### type
        expected += struct.pack('!B', 6)
        ### length
        expected += struct.pack('!B', 0)

        ## Aggregator
        ### flags
        expected += struct.pack('!B', (1 << 7) + (1 << 6))
        ### type
        expected += struct.pack('!B', 7)
        ### length
        expected += struct.pack('!B', 6)
        ### value
        expected += struct.pack('!H', 65100)
        expected += struct.pack('!B', 30)
        expected += struct.pack('!B', 0)
        expected += struct.pack('!B', 1)
        expected += struct.pack('!B', 1)


        # Network Layer Reachability Information
        self.assertEqual(self.update.pack(), expected)


if __name__ == '__main__':
    unittest.main()
