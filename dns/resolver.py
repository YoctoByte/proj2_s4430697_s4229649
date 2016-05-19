#!/usr/bin/env python2

""" DNS Resolver

This module contains a class for resolving hostnames. You will have to implement
things in this module. This resolver will be both used by the DNS client and the
DNS server, but with a different list of servers.
"""

import socket
# from threading import Thread
from dns.cache import RecordCache
from dns.classes import Class
from dns import message
# from dns.rcodes import RCode
from dns.types import Type
from dns.resource import ResourceRecord
# import time


# todo: implement pending_requests: pending_requests is een lijst met "state blocks" die een tijd, wat parameters en de SLIST bevatten


class Resolver(object):
    """ DNS resolver """
    
    def __init__(self, caching, ttl):
        """ Initialize the resolver
        
        Args:
            caching (bool): caching is enabled if True
            ttl (int): ttl of cache entries (if > 0)
        """
        self.caching = caching
        self.ttl = ttl
        self.STYPE = Type.A
        self.SCLASS = Class.IN
        self.SLIST = []
        self.SBELT = ['8.8.8.8']  # TODO: slist moet eigenlijk geinitialiseerd worden vanuit een config file
        if self.caching:
            self.CACHE = RecordCache(self.ttl)
        self.pending_requests = []

    def gethostbyname(self, hostname, timeout):
        """ Translate a host name to IPv4 address.
        Args:
            hostname (str): the hostname to resolve

        Returns:
            (str, [str], [str]): (hostname, aliaslist, ipaddrlist)
        """
        self.SNAME = hostname

        aliases = []
        addresses = []

        # Step 1 of rfc 1034 sect 5.3.3:
        if self.caching:
            answer = self.CACHE.lookup(self.SNAME, Type.A, Class.IN)
            if answer:
                return self.SNAME, answer.aliases, answer.addresses

        # step 2:
        self.update_slist()

        # step 3:
        for server in list(self.SLIST):  # make a copy of SLIST
            response = self.send_query(server, hostname, timeout)
            # step 4:
            for additional in response.additionals:
                rr = ResourceRecord(additional.name, additional.type_, additional.class_, additional.ttl, additional.rdata)
                aliases.append(rr)
            for answer in response.answers:
                rr = ResourceRecord(answer.name, answer.type_, answer.class_, answer.ttl, answer.rdata)
                addresses.append(rr)
            for authority in response.authorities:
                rr = ResourceRecord(authority.name, authority.type_, authority.class_, authority.ttl, authority.rdata)
                data = rr.rdata.data
                if rr.type_ == Type.NS:
                    pass  # data is a host name
                if rr.type_ == Type.A:
                    pass  # for IN class, data is a 32 bit ip address

        return self.SNAME, aliases, addresses

    # step 2:
    def update_slist(self):
        # todo: implement this function
        self.SLIST = ['8.8.8.8']
        # example:
        # if SNAME is Mockapetris.ISI.EDU, first look for a NS RRs
        # for Mockapetris.ISI.EDU, then ISI.EDU, then EDU and then . (root)

    # step 3:
    def send_query(self, server_address, hostname, timeout):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(timeout)

        # Create and send query
        question = message.Question(hostname, Type.A, Class.IN)
        header = message.Header(9001, 0, 1, 0, 0, 0)
        header.qr = 0
        header.opcode = 0
        header.rd = 1
        query = message.Message(header, [question])
        sock.sendto(query.to_bytes(), (server_address, 53))

        # Receive response
        data = sock.recv(512)
        response = message.Message.from_bytes(data)

        return response
