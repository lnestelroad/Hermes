#!/usr/bin/env python3

# %%
# System modules
import time
import logging
from typing import Dict, List, Any, Callable

# Third party modules
import zmq

# Relative imports
from Hermes.Node import Node
from Hermes.Message import Message
from Hermes.Timer import Heartbeater, Peer
from Hermes.Beacon import Beacon
from Hermes.Reactor import Reactor
from Hermes.DBP import commands, command_checks

# %%


class Service(Node):
    def __init__(self, name="Rohan", log_level=logging.WARNING, config_file: str = None):
        super().__init__(name=name, log_level=log_level)

        # TODO: Pull socket and handler information from a config file
        sockets = {
            'router': zmq.ROUTER
        }

        handlers = {
            b'ping': self.pong,
        }

        self.loop = Reactor(
            name=f'{self.name}_reactor',
            socs=sockets,
            msg_handlers=handlers,
            log_level=log_level
        )

    def connect(self, reconnect=False):
        """
        Connects the service node to the core catalog service. In the event that the service does not 
        receive a heartbeat after some period of time or it screws up updating an important 
        config option, it will try and reconnect.

        Parameters
        ----------
        reconnect : bool, default=False
            A flag to determine if a reconnect is being attempted or if its the initial connect
        """
        # open a socket to the CCS
        _, ip, port = self.discover()
        self.new_socket("service->bus", zmq.REQ, addr=f'tcp://{ip}:{port}')

        # TODO: Figure out how to do retries with reconnect flag
        # while self.retries != 0:
        #     self.retries -= 1
        #     self.logger.warning(
        #         f"No Response From Broker. Closing Ports and Trying Again")

        # self.logger.critical(f"Broker Not Responding, Shutting Down.")

    def register(self) -> bool:
        """
        Sends a registration message as defined in the DBP.
        """
        self.connect()

        info = {
            "name":       self.name,
            "interfaces": {
                name: sockets for name, sockets in self.loop.interfaces.items()
            },
            "reg_time":  time.asctime(),

            # TODO: Fix heartbeat stuff here
            # "liveliness": self.liveliness,
            # "retry":      self.retries,
            "topics":     None
        }

        msg = Message(socket=self.sockets["service->bus"])
        msg.send(command=commands['Registration'], body=info)
        msg.recv(display=True)

        if msg.command == commands["Approved"]:
            self.continue_loop = True
            self.logger.info("Registration Approved.")
            self.close_socket("service->bus")
            return True

        elif msg.command == commands['Denied']:
            self.logger.critical(f"Registration Denied, {msg.body}")
            self.close_ctx()

        return False

    def update_config(self, config: Dict[str, Any]):
        """
        When a config value changes, the service needs to inform the broker so they get back on the same page.

        Parameters
        ----------
        config : dict(config_option: new value)
            A dictionary which will hold the new values.
        """
        self.connect()
        msg = Message(socket=self.sockets["service->bus"])
        msg.send(command=commands["Update"], body=config)
        msg.recv()

        if msg.command == commands['Acknowledged']:
            self.logger.info(f"New Config Value Updated!")
            self.close_socket('service->bus')
        else:
            #TODO: this
            self.connect(reconnect=True)

    def start(self, display_incoming=False):
        """
        Attempts to register with the Core Catalog Service and on success begins the reactors main loop.
        """
        if self.register():
            self.loop.start(display_incoming=display_incoming)
        else:
            self.logger.critical('Could not start service.')

    def pong(self, msg: Message):
        """
        Used to see if the service is alive. To Be Replaced with heartbeats....
        """
        msg.send(command=b'pong', body=self.name)


# %%
if __name__ == "__main__":
    print("Shalom, World!")

    test = Service(log_level=logging.INFO)
    test.start(display_incoming=True)
