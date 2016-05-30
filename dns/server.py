#!/usr/bin/env python2

""" A recursive DNS server

This module provides a recursive DNS server. You will have to implement this
server using the algorithm described in section 4.3.2 of RFC 1034.
"""

import socket
from threading import Thread
import message
from resolver import Resolver, ResolverException
from classes import Class
from types import Type
# from rcodes import RCode


class RequestHandler(Thread):
    """ A handler for requests to the DNS server """

    def __init__(self, received_data, ip_address):
        """ Initialize the handler thread """
        Thread.__init__(self)
        self.daemon = True
        self.ip_address = ip_address
        self.received_message = message.Message.from_bytes(received_data)
        self.run()
        
    def run(self):
        """ Run the handler thread """

        recv_header = self.received_message.header

        try:
            questions = self.received_message.questions[0]
            qd_count = len(questions)
        except IndexError:
            return

        # if recv_header.rd:
        try:
            resolver = Resolver(True)
            answer_sname, addresses, aliasses = resolver.gethostbyname(questions[0].rdata.data)
        except ResolverException as e:
            print e
            return

        answers = list()
        for address in addresses:
            answer = message.Section(answer_sname, Type.A, Class.IN, 86400, len(address), address)
            answers.append(answer)

        send_header = message.Header(recv_header.ident, 0, qd_count, len(addresses), 0, 0)
        send_header.qr = 1
        send_header.opcode = 0
        send_header.rd = recv_header.rd
        response_message = message.Message(send_header, questions, answers)
        response_bytes = response_message.to_bytes()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(3)
        sock.send(response_bytes, (self.ip_address, 53))

    def search_local_data(self):
        pass


class Server(object):
    """ A recursive DNS server """

    def __init__(self, port, caching, ttl):
        """ Initialize the server:

        Args:
            port (int): port that server is listening on i
            caching (bool): server uses resolver with caching if true
            ttl (int): ttl for records (if > 0) of cache
        """
        self.done = False
        self.caching = caching
        self.ttl = ttl
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind(('localhost', self.port))

    def serve(self):
        """ Start serving request """
        while not self.done:
            received_data, ip_address = self.server_socket.recvfrom(512)
            print '=== recieved address ===\n', ip_address, '\n'
            RequestHandler(received_data, ip_address).start()
        self.server_socket.close()

    def shutdown(self):
        """ Shutdown the server """
        self.done = True
        self.server_socket.shutdown(socket.SHUT_RDWR)
        self.server_socket.close()
