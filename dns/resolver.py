#!/usr/bin/env python2

""" DNS Resolver

This module contains a class for resolving hostnames. You will have to implement
things in this module. This resolver will be both used by the DNS client and the
DNS server, but with a different list of servers.
"""

import socket
from threading import Thread
from dns.cache import RecordCache
from dns.classes import Class
from dns import message
# from dns.rcodes import RCode
from dns.types import Type


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
        self.SLIST = ['8.8.8.8']

    def gethostbyname(self, hostname, timeout):
        """ Translate a host name to IPv4 address.

        Currently this method contains an example. You will have to replace
        this example with the algorithm described in section
        5.3.3 in RFC 1034.

        Args:
            hostname (str): the hostname to resolve

        Returns:
            (str, [str], [str]): (hostname, aliaslist, ipaddrlist)
        """
        self.SNAME = hostname
        self.STYPE = Type.A
        self.SCLASS = Class.IN
        self.SLIST = []
        self.SBELT = ['8.8.8.8']  # TODO: slist moet eigenlijk geinitialiseerd worden vanuit een config file
        if(self.caching):
            self.CACHE = RecordCache(self.ttl)

        # Step 1 of rfc 1034 sect 5.3.3
        if(self.caching):
            self.CACHE.lookup(hostname, Type.A, Class.IN)


        best_servers = self.find_best_servers()

        # Get data
        aliases = list()
        for additional in response.additionals:
            if additional.type_ == Type.CNAME:
                aliases.append(additional.rdata.data)
        addresses = list()
        for answer in response.answers:
            if answer.type_ == Type.A:
                addresses.append(answer.rdata.data)

        for server in best_servers:
            Thread(target=send_query, args=(server,)).start()

        return hostname, aliases, addresses

    # step 2:
    def find_best_servers(self):
        # todo: implement this function
        return self.SLIST

    # step 3:
    def send_query(self, server_address, timeout):
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

    # step 4:
    def analyze_response(self, response):
        # if response answers question or contains name error: chache data and return back to client

        #
        pass