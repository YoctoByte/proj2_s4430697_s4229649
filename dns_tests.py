#!/usr/bin/env python2

""" Tests for your DNS resolver and server """

import unittest
import sys

import time

from dns.cache import RecordCache
from dns.classes import Class
from dns.resolver import Resolver, ResolverException
from dns.resource import RecordData, ResourceRecord
from dns.types import Type

portnr = 5353
server = "localhost"


class TestResolver(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.resolver = Resolver(False)

    def test_solve_FQDN(self):
        umass_FQDN = 'gaia.cs.umass.edu'
        umass_IP = '128.119.245.12'
        hostname, addresses, aliases = self.resolver.gethostbyname(umass_FQDN)
        self.assertEqual(hostname, umass_FQDN)
        self.assertFalse(aliases)
        self.assertEqual(addresses, [umass_IP])

    def test_invalid_FQDN(self):
        invalid_FQDN = 'wuiefhiwhao.rerttd.nl'
        try:
            hostname, addresses, aliases = self.resolver.gethostbyname(invalid_FQDN)
        except ResolverException:
            hostname, addresses, aliases = invalid_FQDN, [], []
        self.assertEqual(hostname, invalid_FQDN)
        self.assertFalse(aliases)
        self.assertFalse(addresses)


class TestRecordCache(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ttl = 3
        rr = ResourceRecord("wiki.nl", Type.A, Class.IN, cls.ttl, RecordData.create(Type.A, "192.168.123.456"))

    def test_cache_lookup(self):
        """
        Add a record to the cache and look it up
        """
        rr = ResourceRecord("wiki.nl", Type.A, Class.IN, self.ttl, RecordData.create(Type.A, "192.168.123.456"))
        cache = RecordCache()
        cache.add_record(rr)
        lookup_vals = cache.lookup("wiki.nl", Type.A, Class.IN)
        self.assertEqual([rr], lookup_vals)

    def test_cache_disk_io(self):
        """
        Add a record to the cache, write to disk, read from disk, do a lookup
        """
        rr = ResourceRecord("wiki.nl", Type.A, Class.IN, self.ttl, RecordData.create(Type.A, "192.168.123.456"))
        cache = RecordCache()
        cache.write_cache_file() # overwrite the current cache file

        # add rr to cache and write to disk
        cache.add_record(rr)
        cache.write_cache_file()

        # read from disk again
        new_cache = RecordCache()
        new_cache.read_cache_file()
        lookup_vals = new_cache.lookup("wiki.nl", Type.A, Class.IN)
        self.assertEqual([rr], lookup_vals)

    def test_TTL_expiration(self):
        """
        cache a record, wait till ttl expires, see if record is removed from cache
        """
        rr = ResourceRecord("wiki.nl", Type.A, Class.IN, self.ttl, RecordData.create(Type.A, "192.168.123.456"))
        cache = RecordCache()
        cache.add_record(rr)

        time.sleep(rr.ttl)

        lookup_vals = cache.lookup("wiki.nl", Type.A, Class.IN)
        self.assertFalse(lookup_vals)


class TestResolverCache(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.resolver = Resolver(True)

    def setUp(self):
        # put invalid record in cache file
        record_data = RecordData.create(Type.A, "192.168.123.456")
        self.rr = ResourceRecord("invalid.invalid", Type.A, Class.IN, 3, record_data)

        cache = RecordCache()
        cache.add_record(self.rr)
        cache.write_cache_file()

    def test_solve_FQDN(self):
        umass_FQDN = 'gaia.cs.umass.edu'
        umass_IP = '128.119.245.12'
        hostname, addresses, aliases = self.resolver.gethostbyname(umass_FQDN)
        self.assertEqual(hostname, umass_FQDN)
        self.assertFalse(aliases)
        self.assertEqual(addresses, [umass_IP])

    def test_invalid_cached_FQDN(self):
        hostname,  addresses, aliases = self.resolver.gethostbyname(self.rr.name)
        self.assertEqual(hostname, self.rr.name)
        self.assertFalse(aliases)
        self.assertEqual(addresses[0], self.rr.rdata.data)

    def test_wait_for_TTL_expiration(self):
        time.sleep(self.rr.ttl)
        hostname, addresses, aliases = self.resolver.gethostbyname(self.rr.name)
        self.assertEqual(hostname, self.rr.name)
        self.assertFalse(aliases)
        self.assertFalse(addresses)


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
