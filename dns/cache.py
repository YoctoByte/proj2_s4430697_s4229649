#!/usr/bin/env python2

"""A cache for resource records

This module contains a class which implements a cache for DNS resource records,
you still have to do most of the implementation. The module also provides a
class and a function for converting ResourceRecords from and to JSON strings.
It is highly recommended to use these.
"""

import json

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
        self.records = []
        self.ttl = ttl

    def lookup(self, dname, type_, class_):
        """ Lookup resource records in cache

        Lookup for the resource records for a domain name with a specific type
        and class.
        
        Args:
            dname (str): domain name
            type_ (Type): type
            class_ (Class): class
        """
        for record in self.records:
            if dname == record.name and type_ == record.type_ and class_ == record.class_:
                return record

    
    def add_record(self, record):
        """ Add a new Record to the cache
        
        Args:
            record (ResourceRecord): the record added to the cache
        """
        self.records.append(record)
    
    def read_cache_file(self):
        """ Read the cache file from disk """
        with open(self.cache_dir, 'r') as file:
            json_records = file.read()
            records = json.loads(json_records, object_hook=ResourceEncoder.resource_from_json)

    def write_cache_file(self):
        """ Write the cache file to disk """
        with open(self.cache_dir, 'w') as file:
            json_records = json.dumps(self.records, cls=ResourceEncoder, indent=4)
            file.write(json_records)
