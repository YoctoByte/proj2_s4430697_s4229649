#!/usr/bin/env python2

""" DNS Resolver

This module contains a class for resolving hostnames. You will have to implement
things in this module. This resolver will be both used by the DNS client and the
DNS server, but with a different list of servers.
"""

import socket
from threading import Thread
# from Queue import Queue
from dns.cache import RecordCache, MockedCache, CacheException
from dns.classes import Class
from dns import message
# from dns.rcodes import RCode
from dns.types import Type
from dns.resource import ResourceRecord
from time import sleep


# todo: implement pending_requests: pending_requests is een lijst met "state blocks" die een tijd, wat parameters en de SLIST bevatten


class Resolver(object):
    """ DNS resolver """
    
    def __init__(self, caching, ttl, cache=None):
        """ Initialize the resolver
        
        Args:
            caching (bool): caching is enabled if True
            ttl (int): ttl of cache entries (if > 0)
        """
        self.ttl = ttl
        self.caching = caching
        if not cache:
            if self.caching:
                self.CACHE = RecordCache(15)
            else:
                self.CACHE = MockedCache(15)
        else:
            self.CACHE = cache
        self.STYPE = Type.A
        self.SCLASS = Class.IN
        self.SLIST = []
        self.SBELT = [('A.ROOT-SERVERS.NET', '198.41.0.4'),
                      ('B.ROOT-SERVERS.NET', '192.228.79.201'),
                      ('C.ROOT-SERVERS.NET', '192.33.4.12'),
                      ('D.ROOT-SERVERS.NET', '199.7.91.13'),
                      ('E.ROOT-SERVERS.NET', '192.203.230.10'),
                      ('F.ROOT-SERVERS.NET', '192.5.5.241'),
                      ('G.ROOT-SERVERS.NET', '192.112.36.4'),
                      ('H.ROOT-SERVERS.NET', '198.97.190.53'),
                      ('I.ROOT-SERVERS.NET', '192.36.148.17'),
                      ('J.ROOT-SERVERS.NET', '192.58.128.30'),
                      ('K.ROOT-SERVERS.NET', '193.0.14.129'),
                      ('L.ROOT-SERVERS.NET', '199.7.83.42'),
                      ('M.ROOT-SERVERS.NET', '202.12.27.33')]
        self.aliases = []
        self.addresses = []
        self.timeout = 3

    def gethostbyname(self, hostname, slist=None):
        """ Translate a host name to IPv4 address.
        Args:
            hostname (str): the hostname to resolve

        Returns:
            (str, [str], [str]): (hostname, aliaslist, ipaddrlist)
        """
        self.SNAME = hostname
        if slist:
            self.SLIST = slist
        else:
            self.CACHE.read_cache_file()

        # Step 1 of rfc 1034 sect 5.3.3:
        answers = self.CACHE.lookup(self.SNAME, Type.A, Class.IN)
        if answers:
            return self.SNAME, answers, []

        # step 2:
        self.update_slist()

        # step 3 + 4:
        self.send_queries()

        if slist is None:
            print('test')
            self.CACHE.write_cache_file()

        return self.SNAME, self.aliases, self.addresses

    # step 2:
    def update_slist(self):
        # todo: implement this function
        if not self.SLIST:
            self.SLIST = self.SBELT
        # example:
        # if SNAME is Mockapetris.ISI.EDU, first look for a NS RRs
        # for Mockapetris.ISI.EDU, then ISI.EDU, then EDU and then . (root)

    # step 3:
    def send_queries(self):
        # Create query
        question = message.Question(self.SNAME, Type.A, Class.IN)
        header = message.Header(42, 0, 1, 0, 0, 0)
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
                    ns_resolver = Resolver(self.caching, self.ttl, self.CACHE)
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
                try:
                    sock.sendto(query_bytes, (server_ip, 53))
                except:
                    print('ERROR: ' + str(server_ip))
                try:
                    results[ind] = {'data': sock.recv(512), 'server': server_data}
                    return
                except socket.timeout:
                    try_count += 1
                    print('timeout ' + str(try_count))
            results[ind] = -1

        results = list()
        for ind, server in enumerate(self.SLIST):
            results.append(None)
            Thread(target=send_query, args=(ind, server)).start()

        while True:
            if not all(r in [None, -1] for r in results):  # if result is found
                response = None
                server_data = None
                for i, r in enumerate(results):
                    if r not in [None, -1]:
                        response = message.Message.from_bytes(r['data'])
                        server_data = r['server']
                        results[i] = -1
                        break
                print('--------\nserver: ' + str(server_data[0]) + ', ' + str(server_data[1]))
                self.show_response(response)
                self.analyze_response(response, server_data)
                if self.addresses:
                    return
            if all(r == -1 for r in results):  # all results timed out or didn't return anything
                raise ResolverException()
            sleep(0.01)

    # step 4:
    def analyze_response(self, response, server_data):
        additionals = list()
        for additional_rr in response.additionals:
            try:
                self.CACHE.add_record(additional_rr)
                additionals.append(additional_rr)
            except CacheException:
                pass

        for answer_rr in response.answers:
            if answer_rr.type_ == Type.A:
                print('answer: ' + answer_rr.name + ', ' + answer_rr.rdata.data)
                self.CACHE.add_record(answer_rr)
                self.addresses.append(answer_rr.rdata.data)
            if answer_rr.type_ == Type.CNAME:
                new_sname = answer_rr.rdata.data
                try:
                    cname_resolver = Resolver(self.caching, self.ttl, self.CACHE)
                    self.SNAME, self.aliases, self.addresses = cname_resolver.gethostbyname(new_sname)
                except ResolverException:
                    pass
                return
        if response.answers:
            self.aliases = additionals
            return

        new_slist = list()
        for authority in response.authorities:
            rr = ResourceRecord(authority.name, authority.type_, authority.class_, authority.ttl, authority.rdata)
            if rr.type_ == Type.NS:
                ip = None
                for additional in additionals:
                    if additional.name == rr.rdata.data and additional.type_ == Type.A:
                        ip = additional.rdata.data
                # todo: if better delegation:
                if ip:
                    new_slist.append((rr.rdata.data, ip))
            if rr.type_ == Type.A and rr.class_ == Class.IN:
                print('authority contained an A type record!')
            if rr.type_ == Type.CNAME:
                print('authority contained an CNAME type record!')
        if new_slist:
            try:
                next_resolver = Resolver(self.caching, self.ttl, self.CACHE)
                self.SNAME, self.aliases, self.addresses = next_resolver.gethostbyname(self.SNAME, new_slist)
            except ResolverException:
                pass
        else:
            return

    @staticmethod
    def show_response(response):
        for question in response.questions:
            print('question:', question.qname, Type.by_value[question.qtype], Class.by_value[question.qclass])
        for answer in response.answers:
            print('answer:', answer.rdata.data, Type.by_value[answer.type_], Class.by_value[
                answer.class_], answer.name, answer.ttl)
        for authority in response.authorities:
            print('authority:', authority.rdata.data, Type.by_value[authority.type_], Class.by_value[
                authority.class_], authority.name, authority.ttl)
        for additional in response.additionals:
            print('additional:', additional.rdata.data, Type.by_value[additional.type_], Class.by_value[
                additional.class_], additional.name, additional.ttl)


class ResolverException(Exception):
    pass


if __name__ == "__main__":  # anders wordt onderstaande gerunt op het moment dat deze klasse wordt geimporteerd
    resolver = Resolver(True, 3600)
    _, ips, als = resolver.gethostbyname('www.google.com')
    for ip in ips:
        print('IP Address resolved: ' + str(ip.rdata.data))
    for alias in als:
        print('Aliases resolved: ' + alias)
