#!/usr/bin/env python2

""" Tests for your DNS resolver and server """
import unittest

import sys

import unittest
import sys

from dns.cache import RecordCache
from dns.classes import Class
from dns.resolver import Resolver
from dns.resource import RecordData, ResourceRecord
from dns.types import Type

portnr = 5353
server = "localhost"


class TestResolver(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.resolver = Resolver(False, 0)

    def test_solve_FQDN(self):
        umass_FQDN = 'gaia.cs.umass.edu'
        umass_IP = '128.119.245.12'
        hostname, aliases, addresses = self.resolver.gethostbyname(umass_FQDN, 15)
        self.assertEqual(hostname, umass_FQDN)
        self.assertFalse(aliases)
        self.assertEqual(addresses, [umass_IP])

    def test_invalid_FQDN(self):
        invalid_FQDN = 'wuiefhiwhao.rerttd.nl'
        hostname, aliases, addresses = self.resolver.gethostbyname(invalid_FQDN, 15)
        self.assertEqual(hostname, invalid_FQDN)
        self.assertFalse(aliases)
        self.assertFalse(addresses)


class TestRecordCache(unittest.TestCase):
    def test_cache_lookup(self):
        cache = RecordCache(15)

        record_data = RecordData.create(Type.A, "192.168.123.456")
        rr = ResourceRecord("oppaalstraat.nl", Type.A, Class.IN, 15, record_data)
        cache.add_record(rr)
        lookup_val = cache.lookup("oppaalstraat.nl", Type.A, Class.IN)
        self.assertEqual(rr, lookup_val)

    def test_cache_disk_io(self):
        cache = RecordCache(15)
        cache.write_cache_file()  # overwrite the current cache file

        record_data = RecordData.create(Type.A, "192.168.123.456")
        rr = ResourceRecord("oppaalstraat.nl", Type.A, Class.IN, 15, record_data)
        cache.add_record(rr)
        lookup_val = cache.lookup("oppaalstraat.nl", Type.A, Class.IN)
        self.assertEqual(rr, lookup_val)

        cache.write_cache_file()
        cache.read_cache_file()
        lookup_val = cache.lookup("oppaalstraat.nl", Type.A, Class.IN)
        self.assertEqual(rr, lookup_val)


class TestResolverCache(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """print "setUpClass"
        cls.resolver = Resolver(True, 10)

    def test_solve_FQDN(self):
        umass_FQDN = 'gaia.cs.umass.edu'
        umass_IP = '128.119.245.12'
        hostname, aliases, addresses = self.resolver.gethostbyname(umass_FQDN, 15)
        self.assertEqual(hostname, umass_FQDN)
        self.assertFalse(aliases)
        self.assertEqual(addresses, [umass_IP])

    def test_invalid_cached_FQDN(self):
        raise NotImplementedError

    def test_wait_for_TTL_expiration(self):
        raise NotImplementedError"""


class TestServer(unittest.TestCase):
    pass


if __name__ == "__main__":
    # Parse command line arguments
    import argparse

    parser = argparse.ArgumentParser(description="HTTP Tests")
    parser.add_argument("-s", "--server", type=str, default="localhost")
    parser.add_argument("-p", "--port", type=int, default=5001)
    args, extra = parser.parse_known_args()
    portnr = args.port
    server = args.server

    # Pass the extra arguments to unittest
    sys.argv[1:] = extra

    # Start test suite
    unittest.main()
