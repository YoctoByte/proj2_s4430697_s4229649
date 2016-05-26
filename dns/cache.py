#!/usr/bin/env python2

"""A cache for resource records

This module contains a class which implements a cache for DNS resource records,
you still have to do most of the implementation. The module also provides a
class and a function for converting ResourceRecords from and to JSON strings.
It is highly recommended to use these.
"""

import json

import time

from dns.resource import ResourceRecord, RecordData
from dns.types import Type
from dns.classes import Class


class ResourceEncoder(json.JSONEncoder):
    """ Conver ResourceRecord to JSON
    
    Usage:
        string = json.dumps(records, cls=ResourceEncoder, indent=4)
    """

    def default(self, obj):
        if isinstance(obj, ResourceRecord):
            return {
                "name": obj.name,
                "type": Type.to_string(obj.type_),
                "class": Class.to_string(obj.class_),
                "ttl": obj.ttl,
                "rdata": obj.rdata.data
            }
        return json.JSONEncoder.default(self, obj)

    @staticmethod
    def resource_from_json(dct):
        """ Convert JSON object to ResourceRecord

        Usage:
            records = json.loads(string, object_hook=resource_from_json)
        """
        name = dct["name"]
        type_ = Type.from_string(dct["type"])
        class_ = Class.from_string(dct["class"])
        ttl = dct["ttl"]
        rdata = RecordData.create(type_, dct["rdata"])
        return ResourceRecord(name, type_, class_, ttl, rdata)


class RecordCache(object):
    """ Cache for ResourceRecords """
    cache_dir = "cache\cache.txt"

    def __init__(self, ttl):
        """ Initialize the RecordCache

        Args:
            ttl (int): TTL of cached entries (if > 0)
        """
        self.ttl = ttl
        self.record_time_stored_dict = {}

    def lookup(self, dname, type_, class_):
        """ Lookup resource records in cache

        Lookup for the resource records for a domain name with a specific type
        and class.
        
        Args:
            dname (str): domain name
            type_ (Type): type
            class_ (Class): class
        """
        matches = []

        for record in self.record_time_stored_dict.keys():
            if dname == record.name and type_ == record.type_ and class_ == record.class_:
                if self.record_time_stored_dict[record] + record.ttl > time.time():
                    matches.append(record)
                    # TODO: moet de time_stored hier aangepast worden?
                else:
                    del self.record_time_stored_dict[record]

        return matches

    def add_record(self, record):
        """ Add a new Record to the cache
        
        Args:
            record (ResourceRecord): the record added to the cache
        """
        if record.ttl == 0:
            raise CacheException('RRs with a ttl of 0 may not be cached')  # see rfc 1035 p.11
        elif record.ttl < 0:
            raise CacheException('ttl smaller than 0')
        elif not (record.type_ == Type.A or record.type_ == Type.CNAME):
            raise CacheException('Only A and CNAME-Resource Records may be cached, actual type is ' + Type.to_string(record.type_))  # see assignment

        self.record_time_stored_dict[record] = time.time()

    def read_cache_file(self):
        """ Read the cache file from disk """
        with open(self.cache_dir, 'r') as file:
            json_records = file.read()
            records = json.loads(json_records, object_hook=ResourceEncoder.resource_from_json)

        for record in records:
            self.record_time_stored_dict[record] = time.time()

    def write_cache_file(self):
        """ Write the cache file to disk """
        for record in self.record_time_stored_dict.keys():
            if self.record_time_stored_dict[record] + record.ttl < time.time():
                del self.record_time_stored_dict[record]
        with open(self.cache_dir, 'w') as file:
            json_records = json.dumps(self.record_time_stored_dict.keys(), cls=ResourceEncoder, indent=4)
            file.write(json_records)


class MockedCache:
    """ Mockup cache that does nothing """
    def __init__(self, ttl):
        pass

    def lookup(self, dname, type_, class_):
        return []

    def add_record(self, record):
        pass

    def read_cache_file(self):
        pass

    def write_cache_file(self):
        pass


class CacheException(Exception):
    pass
