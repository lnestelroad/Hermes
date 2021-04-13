#!/usr/bin/env python3

# %%
# System modules
import json
import logging
from typing import Dict, List, Type, Any


# Third party modules
import zmq

# Relative imports
from Message import Message
from Beacon import Beacon
from Timer import Heartbeater
from Logger import Logger
from Reactor import Reactor
from zhelpers import zpipe
from DBP import commands

# %%


class CoreCatalogService():
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

    def __init__(self, name="CoreCatalogService", log_level=logging.WARNING, liveliness=1000):

        self.name = name

        # TODO: Pull socket and handler information from a config file
        sockets = {
            'router': zmq.ROUTER
        }

        handlers = {
            commands['Info_Req']: self.client_handler,
            commands['Registration']: self.service_registration,
            commands['Update']: self.service_update
        }

        self.interface = Reactor(
            name=f'{self.name}_interface',
            socs=sockets,
            msg_handlers=handlers,
            log_level=log_level
        )

        # External service registration storage
        self.services = dict()

    def client_handler(self, msg: Message):
        """
        Handles request messages that come in from clients. 

        Parameters
        ----------
        msg : BrokerMessage
            The passed along message received from the interface socket
        """
        body = bytes.decode(msg.body[0], 'utf-8')
        if body != '':
            if body in self.services:
                msg.send(command=commands['Info_Rep'],
                         body={body: self.services[body]})
            else:
                msg.send(
                    command=commands['Info_Rep'],
                    body=f"No Registered Service With the Name {body}")
        else:
            msg.send(command=commands['Info_Rep'],
                     body=self.services)

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
            # self.logger.info(
            #     f"New Service Registered: {name}")
            # self.logger.debug(
            #     f"Service Registration Information\n:\t{self.services[name]}")

            msg.send(command=commands['Approved'])

        else:
            msg.send(command=commands['Denied'])

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

        # self.logger.info(f"Service Configs Update: {info}")
        msg.send(command=commands['Acknowledged'])

    def start(self):
        self.interface.start(display_incoming=True)

    def stop(self):
        self.interface.stop()


# %%
print("Shalom, World!")

test = CoreCatalogService(log_level=logging.DEBUG)
test.start()
