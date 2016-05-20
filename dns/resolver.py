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
        self.SLIST = ['8.8.8.8', '198.41.0.4']
        self.SBELT = ['198.41.0.4']  # TODO: slist moet eigenlijk geinitialiseerd worden vanuit een config file
        if self.caching:
            self.CACHE = RecordCache(self.ttl)
        self.pending_requests = []
        self.aliases = []
        self.addresses = []
        self.timeout = 10

    def gethostbyname(self, hostname):
        """ Translate a host name to IPv4 address.
        Args:
            hostname (str): the hostname to resolve

        Returns:
            (str, [str], [str]): (hostname, aliaslist, ipaddrlist)
        """
        self.SNAME = hostname

        self.aliases = []
        self.addresses = []

        # Step 1 of rfc 1034 sect 5.3.3:
        if self.caching:
            answer = self.CACHE.lookup(self.SNAME, Type.A, Class.IN)
            if answer:
                return self.SNAME, answer.aliases, answer.addresses

        # step 2:
        self.update_slist()

        # step 3 + 4:
        self.send_queries()

        return self.SNAME, self.aliases, self.addresses

    # step 2:
    def update_slist(self):
        # todo: implement this function
        self.SLIST = ['198.41.0.4']
        # example:
        # if SNAME is Mockapetris.ISI.EDU, first look for a NS RRs
        # for Mockapetris.ISI.EDU, then ISI.EDU, then EDU and then . (root)

    # step 3:
    def send_queries(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(self.timeout)

        # Create and send query
        question = message.Question(self.SNAME, Type.A, Class.IN)
        header = message.Header(9001, 0, 1, 0, 0, 0)
        header.qr = 0
        header.opcode = 0
        header.rd = 1
        query = message.Message(header, [question])
        query_bytes = query.to_bytes()

        for server in self.SLIST:
            sock.sendto(query_bytes, (server, 53))

        # Receive response
        try:
            data = sock.recv(512)
            response = message.Message.from_bytes(data)
            print('--------')
            self.show_response(response)
            self.analyze_response(response)
        except socket.timeout:
            print('timeout')

    # step 4:
    def analyze_response(self, response):
        # step 4:
        self.SLIST = []
        additionals = list()
        for additional in response.additionals:
            rr = ResourceRecord(additional.name, additional.type_, additional.class_, additional.ttl, additional.rdata)
            additionals.append(rr)
        for answer in response.answers:
            rr = ResourceRecord(answer.name, answer.type_, answer.class_, answer.ttl, answer.rdata)
            print('answer: ' + rr.name + ', ' + rr.rdata.data)
            # todo: cache the data
        if response.answers:
            # todo: return stuff (ook de additionals als aliases)
            # self.aliases =
            # self.addresses =
            return
        for authority in response.authorities:
            rr = ResourceRecord(authority.name, authority.type_, authority.class_, authority.ttl, authority.rdata)
            if rr.type_ == Type.NS:
                # found_ip = False
                for additional in additionals:
                    if additional.name == rr.rdata.data and additional.type_ == Type.A:
                        self.SLIST.append(additional.rdata.data)
                #         found_ip = True
                # if not found_ip:
                #     _, addresses, _ = self.gethostbyname(rr.rdata.data)
                #     self.SLIST.append(addresses)

            if rr.type_ == Type.A and rr.class_ == Class.IN:
                pass  # for IN class, data is a 32 bit ip address
            if rr.type_ == Type.CNAME:
                self.gethostbyname(rr.rdata.data)
                return
        self.send_queries()


    @staticmethod
    def show_response(response):
        for question in response.questions:
            print 'question:', question.qname, Type.by_value[question.qtype], Class.by_value[question.qclass]
        for answer in response.answers:
            print 'answer:', answer.rdata.data, Type.by_value[answer.type_], Class.by_value[
                answer.class_], answer.name, answer.ttl
        for authority in response.authorities:
            print 'authority:', authority.rdata.data, Type.by_value[authority.type_], Class.by_value[
                authority.class_], authority.name, authority.ttl
        for additional in response.additionals:
            print 'additional:', additional.rdata.data, Type.by_value[additional.type_], Class.by_value[
                additional.class_], additional.name, additional.ttl


resolver = Resolver(False, 10)
resolver.gethostbyname('ns1.zxcs.nl')
