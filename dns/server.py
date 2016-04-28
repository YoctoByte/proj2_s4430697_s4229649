#!/usr/bin/env python2

""" A recursive DNS server

This module provides a recursive DNS server. You will have to implement this
server using the algorithm described in section 4.3.2 of RFC 1034.
"""

import socket
from threading import Thread


class RequestHandler(Thread):
    """ A handler for requests to the DNS server """

    def __init__(self, conn_socket):
        """ Initialize the handler thread """
        Thread.__init__(self)
        self.daemon = True
        self.run()
        
    def run(self):
        """ Run the handler thread """
        # TODO: Handle DNS request

        # 1. Set or clear value of recursion. If recursive, goto 5. Otherwise 2.

        # 2. Search for available zones for the zone which is nearest ancestor to QNAME. If found go to 3 else go to 4.

        # 3.
        #   a. if QNAME is matched; node is found.
        #   b. if match takes us out of authoritative data; referral. Goto 4.
        #   c. if match is impossible; ... Goto 6

        # 4. Start matching down the cache. If QNAME found in the cache, copy all Resource Records (RRs) attached to it
        #    that match QTYPE into the answer section

        # 5.

        # 6.
        pass


class Server(object):
    """ A recursive DNS server """

    def __init__(self, port, caching, ttl):
        """ Initialize the server
        
        Args:
            port (int): port that server is listening on
            caching (bool): server uses resolver with caching if true
            ttl (int): ttl for records (if > 0) of cache
        """
        self.done = False
        self.caching = caching
        self.ttl = ttl
        self.port = port
        self.server_socket = socket.socket()
        self.server_socket.bind(('localhost', self.port))

    def serve(self):
        """ Start serving request """
        self.server_socket.listen(20)
        while not self.done:
            (client_socket, address) = self.server_socket.accept()
            print '=== client address ===\n', address, '\n'
            RequestHandler(client_socket).start()
        self.server_socket.close()

    def shutdown(self):
        """ Shutdown the server """
        self.done = True
        # TODO: shutdown socket
