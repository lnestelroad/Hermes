#!/usr/bin/env python3


# System modules
import logging
from typing import Dict, List, Any
from pprint import pprint
import json

# Third party modules
import zmq
from zmq.sugar.context import T

# Relative imports
from Hermes.Node import Node
from Hermes.Message import Message
from Hermes.DBP import commands


class Client(Node):
    """
    A LIAMb node extension to provide a client interface with the bus.
    """

    def __init__(self, name="Gondor", log_level=logging.WARNING):
        super().__init__(name=name, log_level=log_level)

        # A flag variable to determine if the client has made a connection with the broker
        self.connected = False

        # open a socket to the broker
        self.logger.info("Attempting to connect to the bus...")
        rc = self.discover()

        if rc is not None:
            header, ip, port = rc
            self.new_socket('client->bus', zmq.REQ, addr=f'tcp://{ip}:{port}')
            self.connected = True

    def get_services(self, name='') -> Dict[str, Dict[str, Any]]:
        """
        Get a list or entry of registered service(s) information.

        Parameter
        ---------
        name : str, default=None
            A name of a desired service to get information about. If left blank then all services
            will be returned
        """
        if self.connected:
            msg = Message(socket=self.sockets["client->bus"])
            msg.send(command=commands['Info_Req'], body=name)
            msg.recv()

            info = json.loads(msg.body[0].decode('utf-8'))

            if 'Error' in info.keys():
                return None

            if name == '':
                return info
            else:
                return info[name]

        else:
            self.logger.warning("No established connection with CCS.")

    def connect_to_service(self, addr):
        """
        Connects the client to a service at the specified address. One can either be provide or found
        by asking the bus broker node.

        Parameters
        ----------
        addr: str
            An address to connect the client to.
        """
        # TODO: Give this socket a unique name for each service.
        self.new_socket("client->service", zmq.REQ, addr)

    def request_from_service(self, name=None, addr=None) -> Dict[str, Any]:
        if name is None and addr is None:
            raise ValueError(
                "Either the name or addr parameter must have a value")

        if name is not None:

            # TODO: Move null service check to somewhere else
            info = self.get_services(name=name)['interfaces']['router']

            if info is not None:
                self.connect_to_service(
                    addr=f"tcp://{info['ip']}:{info['port']}")
            else:
                self.logger.warning("Service does not exits.")
                return None

        if addr is not None:
            self.connect_to_service(addr=addr)

        msg = Message(self.sockets['client->service'])
        msg.send(command=commands['Ping'], body="Hello!")
        msg.recv()

        return msg.body

    def sub_to_service(self, name, topic):
        pass


if __name__ == "__main__":
    print("Shalom, World!")

    cli = Client(log_level=logging.DEBUG)
    pprint(cli.get_services())
