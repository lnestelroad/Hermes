# System modules
import json
import time
import socket
from pprint import pprint

# Third party modules
import netifaces as ni


class Beacon():
    """
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
    broadcast = ''  # Broadcast address

    def __init__(self, port=5246, address=None, broadcast='255.255.255.255'):
        if address is None:
            # TODO: Make finding the actuall IP address more robust than guessing where it is.
            local_addrs = ni.ifaddresses(ni.interfaces()[2])[2][0]['addr']

        self.address = local_addrs
        self.broadcast = broadcast
        self.port = port

        # Create UDP sockets
        self.sender = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

        # Ask operating system to let us do broadcasts from socket and resuse ports
        self.sender.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sender.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

    def send(self):
        """
        Sends a default discovery message with the address, port, and timestamp of current machine
        """
        msg = b'GONDOR_CALLS_FOR_AID'
        # TODO: Send with multicast...not broadcast.
        self.sender.sendto(msg, (self.broadcast, self.port))

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

        # Note: Socket needs to be rebuild otherwise old broadcasts queue up.
        # This way ensures when you call recv you're getting the newest broadcast message.
        self.recver = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.recver.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.recver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

        # Bind UDP socket to local port so we can receive pings
        self.recver.bind(('', self.port))

        # TODO: Add timeouts incase there is no broker up and running
        header, addr = self.recver.recvfrom(n)

        if header == b'GONDOR_CALLS_FOR_AID':
            print("Received beacon message...")

        self.recver.close()
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
