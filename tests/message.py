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

from pybgp.bgp.message import Message, Open


class TestMessage(unittest.TestCase):

    def setUp(self):
        self.message = Message()

    def test_pack(self):
        # marker
        expected = chr(0xFF) * 16
        # length = 19, 2 bytes
        expected += chr(0)
        expected += chr(19)
        # type
        expected += chr(0)
        self.assertEqual(self.message.pack(), expected)


class TestOpen(unittest.TestCase):

    def setUp(self):
        asn       = 65000
        hold_time = 3
        router_id = ipaddr.IPAddress('10.0.0.1')
        self.open = Open(asn, hold_time, router_id)

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
        expected += struct.pack('!H', 65000)
        # hold time = 3
        expected += chr(3)
        # bgp identifier
        expected += chr(10)
        expected += chr(0)
        expected += chr(0)
        expected += chr(1)
        # param length
        expected += chr(0)
        self.assertEqual(self.open.pack(), expected)
        print self.open


if __name__ == '__main__':
    unittest.main()
