#!/usr/bin/env python2

""" Tests for your DNS resolver and server """
import unittest

import sys

import unittest
import sys

import time

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
    @classmethod
    def setUpClass(cls):
        cls.ttl = 3
        record_data = RecordData.create(Type.A, "192.168.123.456")
        cls.rr = ResourceRecord("wiki.nl", Type.A, Class.IN, cls.ttl, record_data)

    def setUp(self):
        RecordCache().write_cache_file()  # overwrite the current cache file

    def test_cache_lookup(self):
        """
        Add a record to the cache and look it up
        """
        cache = RecordCache()
        cache.add_record(self.rr)
        lookup_vals = cache.lookup("wiki.nl", Type.A, Class.IN)
        self.assertEqual(len(lookup_vals), 1)
        self.assertEqual(self.rr, lookup_vals[0])

    def test_cache_disk_io(self):
        """
        Add a record to the cache, write to disk, read from disk, do a lookup
        """
        cache = RecordCache()
        # add rr to cache and write to disk
        cache.add_record(self.rr)
        cache.write_cache_file()

        # read from disk again
        new_cache = RecordCache()
        new_cache.read_cache_file()
        lookup_vals = new_cache.lookup("wiki.nl", Type.A, Class.IN)
        self.assertEqual(len(lookup_vals), 1)
        self.assertEqual(self.rr, lookup_vals[0])

    def test_timeout(self):
        """
        cache a record, wait till ttl expires, see if record is removed from cache
        """
        cache = RecordCache()
        cache.add_record(self.rr)

        time.sleep(self.ttl)

        lookup_vals = cache.lookup("wiki.nl", Type.A, Class.IN)
        self.assertFalse(lookup_vals)


class TestResolverCache(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
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
        raise NotImplementedError


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
