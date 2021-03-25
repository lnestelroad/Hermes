#!/usr/bin/env python3

# System modules
import time
import logging
from typing import Dict, List, Any, Callable

# Third party modules
import zmq

# Relative imports
from Message import Message
from Timer import Heartbeater, Peer
from Beacon import Beacon
from Reactor import Reactor
from DBP import commands, command_checks


class Service(Reactor):
    def __init__(self, name="Rohan", log_level=logging.INFO):
        super().__init__(name=name, log_level=log_level)

    def connect(self, reconnect=False):
        """
        Connects the service node to the broker. In the event that the service does not 
        receive a heartbeat after some period of time or it screws up updating an important 
        config option, it will try and reconnect.

        Parameters
        ----------
        reconnect : bool, default=False
            A flag to determine if a reconnect is being attempted or if its the initial connect
        """
        # open a socket to the broker
        if reconnect:
            self.closer_socket("service->bus")

        self.new_socket("service->bus", zmq.REQ)

        # TODO: Figure out how to do retries with reconnect flag
        # while self.retries != 0:
        #     self.retries -= 1
        #     self.logger.warning(
        #         f"No Response From Broker. Closing Ports and Trying Again")

        # self.logger.critical(f"Broker Not Responding, Shutting Down.")

    def register(self):
        """
        Sends a registration message as defined in the DBP.
        """
        self.connect()

        info = {
            "name":       self.name,
            "ip_addr":    self.ip,
            "port":       self.port,
            "last_beat":  time.asctime(),
            # TODO: Fix heartbeat stuff here
            # "liveliness": self.liveliness,
            # "retry":      self.retries,
            "topics":     None
        }

        msg = Message(socket=self.sockets["service->bus"])
        msg.send(command=commands['Registration'], body=info)
        msg.recv()

        if msg.command == commands["Approved"]:
            self.continue_loop = True
            self.logger.info("Registration Approved.")
            self.new_socket('interface', zmq.ROUTER)

            # In the event there was a port conflict when creating the new socket
            if self.update:
                self.update_config({'name': self.name, 'port': self.port})

            self.close_socket("service->bus")
            self.logger.info("Beginning Event Loop...")

        elif msg.command == commands['Denied']:
            self.logger.critical(f"Registration Denied, {msg.body}")
            self.close_ctx()

    def update_config(self, config):
        """
        When a config value changes, the service needs to inform the broker so they get back on the same page.

        Parameters
        ----------
        config : dict(config_option: new value)
            A dictionary which will hold the new values.
        """
        msg = Message(socket=self.sockets["service->bus"])
        msg.send(command=commands["Update"], body=config)
        msg.recv()

        if msg.command == commands['Acknowledged']:
            self.logger.info(f"New Config Value Updated!")
        else:
            self.connect(reconnect=True)


if __name__ == "__main__":
    print("Shalom, World!")

    test = Service()
    test.register()
    test.start()
