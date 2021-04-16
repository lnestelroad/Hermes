# System modules
import time
import socket

# Third party modules
import netifaces as ni

from Hermes.Timer import Heartbeater

################################################# RESOURCES ##########################################################
# Basic UDP broadcast: https://gist.github.com/ninedraft/7c47282f8b53ac015c1e326fffb664b5
# Multicast examples: https://stackoverflow.com/questions/603852/how-do-you-udp-multicast-in-python
# Sockets documentation: https://docs.python.org/3/library/socket.html
# Getting IP address in python: https://stackoverflow.com/questions/24196932/how-can-i-get-the-ip-address-from-nic-in-python
#######################################################################################################################


class Beacon():
    """
    NOTE: DEPRECATED
    Sets up vanilla python UDP python sockets to send and receive discovery messages

    Attributes
    ----------
    port : int, default=5246
        Holds the port number on which to send from and receive on
    address : str, default=None
        Holds the address for sending sockets to include in message data
    bradcast : str, default='255.255.255.255'
        Holds the broadcasting address to send messages off too.

    Notes
    -----
    This class will soon be converted to dealing with multicasting rather than broadcasting. 
    (Once I can figure out how that all works.)
    """
    port = 0        # UDP port we work on
    address = ''    # Own address
    broadcast_addr = ''  # Broadcast address

    def __init__(self, port=5246, address=None, broadcast_addr='255.255.255.255'):
        if address is None:
            # TODO: Make finding the actual IP address more robust than guessing where it is.
            local_addrs = ni.ifaddresses(ni.interfaces()[2])[2][0]['addr']

        # self.heartbeater = heartbeater
        # self.logger = logger
        self.address = local_addrs
        self.broadcast_addr = broadcast_addr
        self.port = port

        # Create UDP sockets
        self.sender = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

        # Ask operating system to let us do broadcasts from socket and resuse ports
        self.sender.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sender.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

        self.recver = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.recver.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.recver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

        # Bind UDP socket to local port so we can receive pings
        self.recver.bind(('', self.port))

    def broadcast(self):
        """
        Sends a default discovery message with the address, port, and timestamp of current machine
        """
        msg = b'GONDOR_CALLS_FOR_AID'
        # TODO: Send with multicast...not broadcast.
        self.sender.sendto(msg, (self.broadcast_addr, self.port))

    def heartbeat(self, addr, port, name):
        self.sender.sendto(bytes(name, 'utf-8'), (addr, port))

    def recv(self, n=1024):
        """
        Makes a new receiving UPD socket and receives all new broadcasted messages on the class port.

        Parameters
        ----------
        n : int, default=1024
            Sets the expected size of the incoming broadcast message. Do not mess with unless you know what you're doing

        Returns
        -------
        dict of discovery information from the broadcast origin.
        """
        # TODO: Add timeouts incase there is no broker up and running
        header, addr = self.recver.recvfrom(n)

        if header == b'GONDOR_CALLS_FOR_AID':
            print("Received beacon message...")

        elif b'<3' in header:
            name = header.decode('utf-8').split(' ')[0]
            return name

        return addr


if __name__ == "__main__":
    print("Shalom, World!")
    test = Beacon()
    print("Beginning broadcast beacon...")
    while True:
        try:
            test.send()
            time.sleep(1)
        except KeyboardInterrupt:
            print("Thanks for playing.")
            break
