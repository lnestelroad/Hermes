#!/usr/bin/env python3

# System modules
import os
import time
import logging
from typing import Dict, List, Any

# Third party modules
import zmq

# Relative imports
from BaseClasses import BaseNode
from Message import Message
from Timer import Heartbeater


class Service(BaseNode):
    """
    A LIAMb node extension to provide a service interface with the bus.
    """

    def __init__(self, name="Rohan", liveliness=1000, retries=3):
        super().__init__(name=name, log_level=logging.DEBUG)
        self.continue_loop = False

        # Heartbeat stuff
        self.heart = Heartbeater()

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

    def start(self):
        """
        Begins the event loop for the service. Each currently registered socket will be 
        polled and incoming message will be passed along to its respective callback function.
        A message with a body of "Exit" will cause the loop to terminate stop the broker.
        """
        self.register()

        while self.continue_loop:

            # Returns a dictionary of events to be processed
            events = dict(self.poller.poll())

            if self.sockets["interface"] in events:
                msg = Message(protocol='DBPCCS01',
                              socket=self.sockets["interface"])
                msg.recv()
                msg.display_envelope()

                self.logger.info(f"Message received on Interface")

                if not msg.valid:
                    self.logger.info(f"Dropping Invalid Message.")

                elif msg.command == b'<3':
                    self.heartbeats()

                elif msg.body == [b"Exit"]:
                    self.stop(msg)
                    break

                else:
                    msg.send(body="Sup bro.", command='0x06')

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

        msg = Message(protocol='DBPCCS01', socket=self.sockets["service->bus"])
        msg.send(command="0x01", body=info)
        msg.recv()

        if msg.command == b'0x02':
            self.continue_loop = True
            self.logger.info("Registration Approved.")
            self.new_socket('interface', zmq.ROUTER)

            # In the event there was a port conflict when creating the new socket
            if self.update:
                self.update_config({'name': self.name, 'port': self.port})

            self.closer_socket("service->bus")
            self.logger.info("Beginning Event Loop...")

        elif msg.command == b'0x03':
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
        msg = Message(protocol='DBPCCS01', socket=self.sockets["service->bus"])
        msg.send(command="0x07", body=config)
        msg.recv()

        if msg.command == b'0x06':
            self.logger.info(f"New Config Value Updated!")
        else:
            self.connect(reconnect=True)

    def stop(self, msg):
        self.logger.warning(
            "Received exit command, client will stop receiving messages")
        msg.send("Bye!")
        self.continue_loop = False
        self.close_ctx()


if __name__ == "__main__":
    print("Shalom, World!")

    test = Service()
    test.start()
