#!/usr/bin/env python3

# System modules
import os
import time
import json
import logging
from typing import Dict, List, Type, Any


# Third party modules
import zmq

# Relative imports
from BaseClasses import BaseNode
from Message import Message
from Beacon import Beacon
from Timer import Heartbeater


class Broker(BaseNode):
    """
    A LIAMb pseudo-distributed broker protocol implementation instance. Contains a public interface,
    distributive node monitor, beacon, log aggregator, network proxy, and last cache value.

    Attributes
    ----------
    name : str, default="Amon Din"
        A human readable string for identification and log labeling purposes.
    log_level : int, default=logging.WARNING
        The level at which to start display logs generated by the broker
    liveliness : int
        The interval in which to expect/send heartbeats from/to services.
    retries : int
        The number of attempts to try and reconnect to a service that has not sent a heartbeat.
    services : Dict[str: Dict[str, Any]]
        Holds all of the currently registered services information. The information is another dictionary
        of the following form:
        {
            ip_addr:    str,
            port:       int,
            last_beat:  time,
            liveliness: int,
            retry:      int
            topics:     List[]
        }

    Methods
    -------
    start()
        Begins the eventloop
    stop()
        Terminate the eventloop and closes the context.
    """

    def __init__(self, name="Amon Din", log_level=logging.WARNING, liveliness=1000):
        super().__init__(broker=True, ip="*", name=name, log_level=log_level)
        self.continue_loop = True

        # Sets up interface sockets
        self.new_socket("interface", zmq.ROUTER)

        # Only displays if the user sets the log level to debug for verbose mode.
        self.logger.debug("Verbose")

        # Heartbeat stuff
        self.heart = Heartbeater(liveliness)

        # Service registration storage
        self.services = dict()

        # Beaconing Service
        self.beacon = Beacon()

        # TODO: Add internal services
        # self.new_socket("LCVS", zmq.SUB)
        # self.new_socket("NPS", zmq.PAIR)
        # self.new_socket("DLAS", zmq.SUB)

    def start(self):
        """
        Begins the event loop for the broker. Each currently registered socket will be
        polled and incoming message will be passed along to its respective callback function.
        A message with a body of "Exit" will cause the loop to terminate stop the broker.
        """
        self.logger.info("Beginning Event Loop...")
        while self.continue_loop:

            # Sends out a beacon message for discovery
            self.logger.debug("Sending UDP broadcast...")
            self.beacon.broadcast()

            # Returns a dictionary of events to be processed
            events = dict(self.poller.poll(timeout=1000))

            if self.sockets["interface"] in events:

                msg = Message(socket=self.sockets["interface"])
                msg.recv()
                self.logger.info(f"Message received on Interface")

                if not msg.valid:
                    self.logger.info(f"Dropping Invalid Message.")

                elif msg.protocol == b"DBPCCC01":
                    self.logger.debug(f"Passing Message to Client Handler")
                    self.client_handler(msg)

                elif msg.protocol == b'DBPCCS01':
                    if msg.command == b'0x01':
                        self.logger.debug(
                            f"Passing Message to Service Handler")
                        self.service_registration(msg)

                    elif msg.command == b'<3':
                        self.logger.debug(
                            f"Passing Message to Heartbeat Handler")
                        self.heartbeats()

                    elif msg.command == b'0x07':
                        self.logger.debug(
                            f"Passing Message to Service Config Update Handler.")
                        self.service_update(msg)

                    else:
                        self.logger.info("Invalid DBPCCS01 Message.")
                        msg.send('0x03', "Error: Unrecognized Command.")

                elif msg.body == [b"Exit"]:
                    self.stop(msg)
                    break

                else:
                    msg.send(body="Error: Unrecognized Request.")

    # TODO: Implement as thread pool to take over tasks and free up eventloop

    def client_handler(self, msg: Message):
        """
        Handles request messages that come in from clients. 

        Parameters
        ----------
        msg : BrokerMessage
            The passed along message received from the interface socket
        """
        desired = bytes.decode(msg.body[0], 'utf-8')
        if desired != '':
            if desired in self.services:
                msg.send(body=self.services[desired])
            else:
                msg.send(body=f"No Registered Service With the Name {desired}")
        else:
            msg.send(body=self.services)

    # TODO: Implement as thread pool to take over tasks and free up eventloop
    def service_registration(self, msg: Message):
        """
        Handles registration messages that come in from services. 

        Parameters
        ----------
        msg : BrokerMessage
            The passed along message received from the interface socket
        """
        approved = True

        # TODO: Check to make sure info has all the appropriate information
        # TODO: Resolve name conflicts.
        # TODO: Figure out some other way to load json payloads in message class
        info = json.loads(msg.body[0].decode('utf-8'))
        if approved:
            name = info['name']
            # removes duplicate name entry in nested dict
            del info["name"]

            self.services[name] = info
            self.logger.info(
                f"New Service Registered: {name}")
            self.logger.debug(
                f"Service Registration Information\n:\t{self.services[name]}")

            msg.send(command='0x02')

        else:
            msg.send(command='0x03')

    def service_update(self, msg: Message):
        """
        Handles updates to service configurations

        Parameters
        ----------
        msg : BrokerMessage
            The passed along message received from the interface socket
        """
        info = json.loads(msg.body[0].decode('utf-8'))
        name = info['name']
        del info["name"]

        # Incase of multiple update, every value is iterated over.
        for k, v in info.items():
            self.services[name][k] = v

        self.logger.info(f"Service Configs Update: {info}")
        msg.send(command='0x06')

    def heartbeats(self, msg):
        """
        Handles heartbeat messages that come in from services. Times are update and reties are reset

        Parameters
        ----------
        msg : BrokerMessage
            The passed along message received from the interface socket
        """
        pass

    def stop(self, msg):
        """
        Ends the event loop
        """
        self.logger.warning(
            "Received exit command, client will stop receiving messages")
        msg.send("Bye!")
        self.continue_loop = False
        self.close_ctx()


if __name__ == "__main__":
    print("Shalom, World!")

    test = Broker(name="ProofOfConcept", log_level=logging.DEBUG)
    test.start()
