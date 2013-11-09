"""
Unit tests for Path Attributes

Author: Quentin Loos <contact@quentinloos.be>
"""
import os
import sys
sys.path.insert(0, os.path.abspath('..'))
import struct
import unittest

from pybgp.bgp.message.update.path_attribute import *


class TestOrigin(unittest.TestCase):

    def setUp(self):
        self.origin = Origin(Origin.IGP)

    def test_pack(self):
        expected = struct.pack(
            '!4B', Flag.TRANSITIVE, TypeCode.ORIGIN, 1, Origin.IGP)
        self.assertEqual(self.origin.pack(), expected)

    def test_unpack(self):
        msg = struct.pack('!4B', Flag.TRANSITIVE, TypeCode.ORIGIN, 1, Origin.IGP)
        origin = Origin.unpack(msg)

        self.assertEquals(self.origin.flags, origin.flags)
        self.assertEquals(self.origin.type_code, origin.type_code)
        self.assertEquals(self.origin.length(), origin.length())
        self.assertEquals(self.origin.value, origin.value)

    def test_create(self):
        msg = struct.pack('!4B', Flag.TRANSITIVE, TypeCode.ORIGIN, 1, Origin.IGP)
        origin = PathAttribute.create(msg)

        self.assertEquals(self.origin.flags, origin.flags)
        self.assertEquals(self.origin.type_code, origin.type_code)
        self.assertEquals(self.origin.length(), origin.length())
        self.assertEquals(self.origin.value, origin.value)


class TestASPath(unittest.TestCase):

    def setUp(self):
        segment = ASPath.ASPathSegment(ASPath.ASPathSegment.AS_SEQUENCE, [10, 4525, 1823])
        segment2 = ASPath.ASPathSegment(ASPath.ASPathSegment.AS_SET, [11, 2334, 1])
        self.aspath = ASPath([segment, segment2])


    def test_pack(self):
        expected = struct.pack('!3B', Flag.TRANSITIVE, TypeCode.ASPATH, 16)
        expected += struct.pack('!BB', ASPath.ASPathSegment.AS_SEQUENCE, 3)
        expected += struct.pack('!3H', 10, 4525, 1823)
        expected += struct.pack('!BB', ASPath.ASPathSegment.AS_SET, 3)
        expected += struct.pack('!3H', 11, 2334, 1)

        self.assertEqual(self.aspath.pack(), expected)

    def test_unpack(self):
        expected = struct.pack('!3B', Flag.TRANSITIVE, TypeCode.ASPATH, 16)
        expected += struct.pack('!BB', ASPath.ASPathSegment.AS_SEQUENCE, 3)
        expected += struct.pack('!3H', 10, 4525, 1823)
        expected += struct.pack('!BB', ASPath.ASPathSegment.AS_SET, 3)
        expected += struct.pack('!3H', 11, 2334, 1)
        aspath = ASPath.unpack(expected)

        self.assertEqual(self.aspath.flags, aspath.flags)
        self.assertEqual(self.aspath.type_code, aspath.type_code)
        self.assertEqual(self.aspath.length(), aspath.length())
        self.assertEqual(self.aspath.value[0].type, aspath.value[0].type)
        self.assertEqual(self.aspath.value[0].value, aspath.value[0].value)
        self.assertEqual(self.aspath.value[1].type, aspath.value[1].type)
        self.assertEqual(self.aspath.value[1].value, aspath.value[1].value)

    def test_create(self):
        expected = struct.pack('!3B', Flag.TRANSITIVE, TypeCode.ASPATH, 16)
        expected += struct.pack('!BB', ASPath.ASPathSegment.AS_SEQUENCE, 3)
        expected += struct.pack('!3H', 10, 4525, 1823)
        expected += struct.pack('!BB', ASPath.ASPathSegment.AS_SET, 3)
        expected += struct.pack('!3H', 11, 2334, 1)
        aspath = PathAttribute.create(expected)

        self.assertEqual(self.aspath.flags, aspath.flags)
        self.assertEqual(self.aspath.type_code, aspath.type_code)
        self.assertEqual(self.aspath.length(), aspath.length())
        self.assertEqual(self.aspath.value[0].type, aspath.value[0].type)
        self.assertEqual(self.aspath.value[0].value, aspath.value[0].value)
        self.assertEqual(self.aspath.value[1].type, aspath.value[1].type)
        self.assertEqual(self.aspath.value[1].value, aspath.value[1].value)


class TestNextHop(unittest.TestCase):

    def setUp(self):
        self.nexthop = NextHop(0x0A000001)

    def test_pack(self):
        expected = struct.pack(
            '!3BI', Flag.TRANSITIVE, TypeCode.NEXTHOP, 4, 0x0A000001)
        self.assertEqual(self.nexthop.pack(), expected)

    def test_unpack(self):
        msg = struct.pack('!3BI', Flag.TRANSITIVE, TypeCode.NEXTHOP, 4, 0x0A000001)
        nexthop = NextHop.unpack(msg)

        self.assertEquals(self.nexthop.flags, nexthop.flags)
        self.assertEquals(self.nexthop.type_code, nexthop.type_code)
        self.assertEquals(self.nexthop.length(), nexthop.length())
        self.assertEquals(self.nexthop.value, nexthop.value)

    def test_create(self):
        msg = struct.pack('!3BI', Flag.TRANSITIVE, TypeCode.NEXTHOP, 4, 0x0A000001)
        nexthop = PathAttribute.create(msg)

        self.assertEquals(self.nexthop.flags, nexthop.flags)
        self.assertEquals(self.nexthop.type_code, nexthop.type_code)
        self.assertEquals(self.nexthop.length(), nexthop.length())
        self.assertEquals(self.nexthop.value, nexthop.value)


class TestMED(unittest.TestCase):

    def setUp(self):
        self.med = MED(150)

    def test_pack(self):
        expected = struct.pack(
            '!3BI', Flag.OPTIONAL, TypeCode.MED, 4, 150)
        self.assertEqual(self.med.pack(), expected)

    def test_unpack(self):
        msg = struct.pack('!3BI', Flag.OPTIONAL, TypeCode.MED, 4, 150)
        med = MED.unpack(msg)

        self.assertEquals(self.med.flags, med.flags)
        self.assertEquals(self.med.type_code, med.type_code)
        self.assertEquals(self.med.length(), med.length())
        self.assertEquals(self.med.value, med.value)

    def test_create(self):
        msg = struct.pack('!3BI', Flag.OPTIONAL, TypeCode.MED, 4, 150)
        med = MED.create(msg)

        self.assertEquals(self.med.flags, med.flags)
        self.assertEquals(self.med.type_code, med.type_code)
        self.assertEquals(self.med.length(), med.length())
        self.assertEquals(self.med.value, med.value)


class TestLocalPref(unittest.TestCase):

    def setUp(self):
        self.localpref = LocalPref(150)

    def test_pack(self):
        expected = struct.pack(
            '!3BI', Flag.TRANSITIVE, TypeCode.LOCALPREF, 4, 150)
        self.assertEqual(self.localpref.pack(), expected)

    def test_unpack(self):
        msg = struct.pack('!3BI', Flag.TRANSITIVE, TypeCode.LOCALPREF, 4, 150)
        localpref = LocalPref.unpack(msg)

        self.assertEquals(self.localpref.flags, localpref.flags)
        self.assertEquals(self.localpref.type_code, localpref.type_code)
        self.assertEquals(self.localpref.length(), localpref.length())
        self.assertEquals(self.localpref.value, localpref.value)

    def test_create(self):
        msg = struct.pack('!3BI', Flag.TRANSITIVE, TypeCode.LOCALPREF, 4, 150)
        localpref = PathAttribute.create(msg)

        self.assertEquals(self.localpref.flags, localpref.flags)
        self.assertEquals(self.localpref.type_code, localpref.type_code)
        self.assertEquals(self.localpref.length(), localpref.length())
        self.assertEquals(self.localpref.value, localpref.value)


class TestAtomicAggregate(unittest.TestCase):

    def setUp(self):
        self.atomic_aggregate = AtomicAggregate()

    def test_pack(self):
        expected = struct.pack(
            '!3B', Flag.TRANSITIVE, TypeCode.ATOMICAGGREGATE, 0)
        self.assertEqual(self.atomic_aggregate.pack(), expected)

    def test_unpack(self):
        msg = struct.pack('!3B', Flag.TRANSITIVE, TypeCode.ATOMICAGGREGATE, 0)
        atomic_aggregate = AtomicAggregate.unpack(msg)

        self.assertEquals(self.atomic_aggregate.flags, atomic_aggregate.flags)
        self.assertEquals(self.atomic_aggregate.type_code, atomic_aggregate.type_code)
        self.assertEquals(self.atomic_aggregate.length(), atomic_aggregate.length())
        self.assertEquals(self.atomic_aggregate.value, atomic_aggregate.value)

    def test_create(self):
        msg = struct.pack('!3B', Flag.TRANSITIVE, TypeCode.ATOMICAGGREGATE, 0)
        atomic_aggregate = PathAttribute.create(msg)

        self.assertEquals(self.atomic_aggregate.flags, atomic_aggregate.flags)
        self.assertEquals(self.atomic_aggregate.type_code, atomic_aggregate.type_code)
        self.assertEquals(self.atomic_aggregate.length(), atomic_aggregate.length())
        self.assertEquals(self.atomic_aggregate.value, atomic_aggregate.value)


class TestAggregator(unittest.TestCase):

    def setUp(self):
        self.aggregator = Aggregator(1500, 0x0A000001)

    def test_pack(self):
        expected = struct.pack(
            '!3BHI', Flag.OPTIONAL | Flag.TRANSITIVE, TypeCode.AGGREGATOR, 6, 1500, 0x0A000001)
        self.assertEqual(self.aggregator.pack(), expected)

    def test_unpack(self):
        msg = struct.pack('!3BHI', Flag.OPTIONAL | Flag.TRANSITIVE, TypeCode.AGGREGATOR, 6, 1500, 0x0A000001)
        aggregator = Aggregator.unpack(msg)

        self.assertEquals(self.aggregator.flags, aggregator.flags)
        self.assertEquals(self.aggregator.type_code, aggregator.type_code)
        self.assertEquals(self.aggregator.length(), aggregator.length())
        self.assertEquals(self.aggregator.value, aggregator.value)
        self.assertEquals(self.aggregator.ip, aggregator.ip)
        self.assertEquals(self.aggregator.asn, aggregator.asn)

    def test_create(self):
        msg = struct.pack('!3BHI', Flag.OPTIONAL | Flag.TRANSITIVE, TypeCode.AGGREGATOR, 6, 1500, 0x0A000001)
        aggregator = PathAttribute.create(msg)

        self.assertEquals(self.aggregator.flags, aggregator.flags)
        self.assertEquals(self.aggregator.type_code, aggregator.type_code)
        self.assertEquals(self.aggregator.length(), aggregator.length())
        self.assertEquals(self.aggregator.value, aggregator.value)
        self.assertEquals(self.aggregator.ip, aggregator.ip)
        self.assertEquals(self.aggregator.asn, aggregator.asn)


if __name__ == '__main__':
    unittest.main()
