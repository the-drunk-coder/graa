"""

Client to send OSC datagrams to an OSC server via UDP.

To faciliate usage with dirt sampler, source port can be specified.

"""
import socket

class UDPClient(object):
    """OSC client to send OscMessages or OscBundles via UDP."""
    def __init__(self, address, port, src_port):
        """
        
        Initialize the client.
        As this is UDP it will not actually make any attempt to connect to the

        given server at ip:port until the send() method is called.

        """
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.setblocking(0)
        self._address = address
        self._port = port
        self._sock.bind(("127.0.0.1", src_port))
    def send(self, content):
        """Sends an OscBundle or OscMessage to the server."""
        self._sock.sendto(content.dgram, (self._address, self._port))
            
