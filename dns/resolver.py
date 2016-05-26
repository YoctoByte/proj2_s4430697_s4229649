#!/usr/bin/env python2

""" DNS Resolver

This module contains a class for resolving hostnames. You will have to implement
things in this module. This resolver will be both used by the DNS client and the
DNS server, but with a different list of servers.
"""

import socket
from threading import Thread
# from Queue import Queue
from dns.cache import RecordCache, MockedCache
from dns.classes import Class
from dns import message
# from dns.rcodes import RCode
from dns.types import Type
from dns.resource import ResourceRecord
from time import sleep


# todo: implement pending_requests: pending_requests is een lijst met "state blocks" die een tijd, wat parameters en de SLIST bevatten


class Resolver(object):
    """ DNS resolver """
    
    def __init__(self, caching, ttl):
        """ Initialize the resolver
        
        Args:
            caching (bool): caching is enabled if True
            ttl (int): ttl of cache entries (if > 0)
        """
        self.ttl = ttl
        self.caching = caching
        if self.caching:
            self.CACHE = RecordCache(self.ttl)
        else:
            self.CACHE = MockedCache(self.ttl)
        self.STYPE = Type.A
        self.SCLASS = Class.IN
        self.SLIST = [(None, '8.8.8.8'), (None, '198.41.0.4')]
        self.SBELT = [(None, '8.8.8.8'), (None, '198.41.0.4')]  # TODO: slist moet eigenlijk geinitialiseerd worden vanuit een config file
        self.aliases = []
        self.addresses = []
        self.timeout = 3

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
        self.SLIST = [(None, '198.41.0.4')]  # 198.41.0.4
        # example:
        # if SNAME is Mockapetris.ISI.EDU, first look for a NS RRs
        # for Mockapetris.ISI.EDU, then ISI.EDU, then EDU and then . (root)

    # step 3:
    def send_queries(self):
        # Create query
        question = message.Question(self.SNAME, Type.A, Class.IN)
        header = message.Header(9001, 0, 1, 0, 0, 0)
        header.qr = 0
        header.opcode = 0
        header.rd = 1
        query = message.Message(header, [question])
        query_bytes = query.to_bytes()

        def send_query(ind, server_data):
            server_name = server_data[0]
            server_ip = server_data[1]
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(self.timeout)
            if not server_ip:
                if server_name:
                    ns_resolver = Resolver(self.caching, self.ttl)
                    _, addresses, _ = ns_resolver.gethostbyname(server_name)
                    if addresses:
                        server_ip = addresses[0]
                    else:
                        results[ind] = -1
                        return
                else:
                    results[ind] = -1
                    return

            try_count = 0
            max_tries = 3
            while try_count < max_tries:
                print(server_ip)
                sock.sendto(query_bytes, (server_ip, 53))
                try:
                    results[ind] = (sock.recv(512), server_data)
                    return
                except socket.timeout:
                    print('timeout ' + str(try_count))
                    try_count += 1
            results[ind] = -1

        results = list()
        for ind, server in enumerate(self.SLIST):
            results.append(None)
            Thread(target=send_query, args=(ind, server)).start()

        while True:
            if not all(r in [None, -1] for r in results):  # if result is found
                response = None
                server_data = None
                for r in results:
                    if r not in [None, -1]:
                        response = message.Message.from_bytes(r[0])
                        server_data = r[1]
                        break
                print('--------\nserver:' + str(server_data[0]))
                self.show_response(response)
                self.analyze_response(response, server_data)
            if all(r == -1 for r in results):  # all results timed out
                # todo: do something here
                pass
            sleep(0.01)

    # step 4:
    def analyze_response(self, response, server_data):
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
                found_ip = False
                for additional in additionals:
                    if additional.name == rr.rdata.data and additional.type_ == Type.A:
                        self.SLIST.append((rr.rdata.data, additional.rdata.data))
                        found_ip = True
                if not found_ip:
                    self.SLIST.append((rr.rdata.data, None))
            if rr.type_ == Type.A and rr.class_ == Class.IN:
                pass  # for IN class, data is a 32 bit ip address
            if rr.type_ == Type.CNAME:
                new_sname = rr.rdata.data
                return self.gethostbyname(new_sname)
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

if __name__ == "__main__":  # anders wordt onderstaande gerunt op het moment dat deze klasse
    # wordt geimporteerd
    resolver = Resolver(False, 3600)
    resolver.gethostbyname('www.google.com')
