"""

Client to send OSC datagrams to an OSC server via UDP.

"""
import socket
from pythonosc import osc_message_builder

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
    def sendMsg(self, *args):
        """Sends an OscBundle or OscMessage to the server."""
        msg = osc_message_builder.OscMessageBuilder(address = args[0])
        for arg in args[1:]:
            msg.add_arg(arg)
        msg = msg.build()
        self._sock.sendto(msg.dgram, (self._address, self._port))
            
