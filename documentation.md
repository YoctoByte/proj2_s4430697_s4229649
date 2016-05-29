# DNS Resolver

The DNS Resolver can be found in dns/resolver.py. A resolver object can be constructed using `Resolver(caching)`, where `caching` is a boolean which indicates if caching is enabled.


# DNS Name Server

**Usage:** `python dns_server.py [-c|--caching] [-t|--ttl time] [-p|--port portNum]`

- `-c`: enables caching
- `-t`: time-to-live of resource records belonging to your zone(klopt dat?), defaults to 0 if not specified
- `-p`: port number, defaults to 5353