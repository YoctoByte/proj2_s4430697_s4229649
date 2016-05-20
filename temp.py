import socket
from dns import message
from dns.types import Type
from dns.classes import Class


def gethostbyname(hostname, timeout):
    """ Translate a host name to IPv4 address.

    Currently this method contains an example. You will have to replace
    this example with the algorithm described in section
    5.3.3 in RFC 1034.

    Args:
        hostname (str): the hostname to resolve

    Returns:
        (str, [str], [str]): (hostname, aliaslist, ipaddrlist)
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)

    # Create and send query
    question = message.Question(hostname, Type.A, Class.IN)
    header = message.Header(9001, 0, 1, 0, 0, 0)
    header.qr = 0
    header.opcode = 0
    header.rd = 1
    query = message.Message(header, [question])
    sock.sendto(query.to_bytes(), ('198.41.0.4', 53))
    # 198.41.0.4

    # Receive response
    data = sock.recv(512)
    response = message.Message.from_bytes(data)
    # for byte in data:
    #     print [byte]

    # Get data
    for question in response.questions:
        print 'question:', question.qname, Type.by_value[question.qtype], Class.by_value[question.qclass]

    addresses = list()
    for answer in response.answers:
        if answer.type_ == Type.A:
            addresses.append(answer.rdata.data)
        print 'answer:', answer.rdata.data, Type.by_value[answer.type_], Class.by_value[answer.class_], answer.name, answer.ttl

    for authority in response.authorities:
        print 'authority:', authority.rdata.data, Type.by_value[authority.type_], Class.by_value[authority.class_], authority.name, authority.ttl

    aliases = list()
    for additional in response.additionals:
        if additional.type_ == Type.CNAME:
            aliases.append(additional.rdata.data)
        print 'additional:', additional.rdata.data, Type.by_value[additional.type_], Class.by_value[additional.class_], additional.name, additional.ttl


    # print('aliases:')
    # for alias in aliases:
    #     print(alias)
    # print('addresses:')
    # for address in addresses:
    #     print(address)

    return hostname, aliases, addresses

gethostbyname('opaalstraat.nl', 10)
