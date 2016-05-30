# DNS Resolver

The DNS Resolver can be found in dns/resolver.py. A resolver object can be constructed using `Resolver(caching)`, where `caching` is a boolean which indicates if caching is enabled.


# DNS Name Server

**Usage:** `python dns_server.py [-c|--caching] [-t|--ttl time] [-p|--port portNum]`

- `-c`: enables caching
- `-t`: time-to-live of resource records belonging to your zone(klopt dat?), defaults to 0 if not specified
- `-p`: port number, defaults to 5353


Table of Contents
1     Structure
1.1   Libraries Used
2     Control Flow
2.1   Name Server
2.2   Resolver
3     Difficulties


1. Structure

The structure of the project is as following:

proj2_s4430697_s4229649
....dns
........cache.json
........cache.py
........classes.py
........domainname.py
........message.py
........rcodes.py
........resolver.py
........resource.py
........server.py
........types.py
........zone.py
....dns_client.py
....dns_server.py
....dns_tests.py
....documentation.md


1.1 Libraries Used
The most important library used is the socket library. This library enables the easy transport of packages via
the UDP protocol. Other external libraries that where argparse, json and Threading. All other functionality was
provided via modules in the dns directory


2 Control Flow
The main module of this project is dns_server.py. This file can be run from the command line and parameters can be
passed to it. When executed, dns_server.py creates an instance of the Server class in server.py.
Another important module is resolver.py which makes use of cache.py for caching. The cache stores it data in the memory
and on the disk in the cache.json file.

2.1 Name Server
When the Server class is initiated and the serve function is executed within dns_server.py, it starts listening to UDP
packages on the port it receives from dns_server.py (default 5353). When a package of 512 bytes is received it created
a RequestHandler thread which processes the data from the request. The control flow of RequestHandler should follow
section 4.3.2 from RFC 1034, but due to time issues we could not implement this whole section. Only when the RD bit of
the request is 1 it is able to process the data because then it uses the resolver in the resolver class to resolve an
IP address. Otherwise it should consult the zone file to get information for the response. The zone file was not
implemented yet.

2.2 Resolver


3 Difficulties