#!/usr/bin/env python3

# System modules
import logging
import uuid
from typing import Dict, List, Any, Callable
from concurrent.futures import ThreadPoolExecutor

# Third party modules
import zmq

# Relative imports
from BaseClasses import BaseNode
from Message import Message
from Timer import Heartbeater, Peer
from Beacon import Beacon


class Reactor(BaseNode):
    """
    A LIAMb node extension to provide an eventloop and interface for the bus.
    """

    def __init__(self, name=uuid.uuid4().hex, liveliness=1000, retries=3):
        super().__init__(name=name, log_level=logging.DEBUG)

        # Main timer to determine flow of execution on each iteration
        self.heart = Heartbeater()

        self.continue_loop: bool = True

        # Only displays if the user sets the log level to debug for verbose mode.
        self.logger.debug("Verbose")

        # Sets up interface sockets
        self.new_socket("interface", zmq.ROUTER)

        # Holds the functions for message handlers.
        self.msg_handlers: Dict[str, Callable[..., Message]] = {}

    def start(self):
        self.logger.info("Beginning Event Loop...")
        with ThreadPoolExecutor(max_workers=100) as executor:
            while self.continue_loop:

                ####################### Incoming Message ####################
                events = dict(self.poller.poll())

                if self.sockets["interface"] in events:
                    self.logger.info("Message on interface.")
                    msg = Message(self.sockets["interface"])
                    try:
                        self.logger.debug("Passing msg to thread.")
                        executor.submit(self.msg_handlers[msg.command], msg)
                    except:
                        msg.send(
                            "Error: Invalid command type. Please register command callback with the server.")

                ######################### Timer Events ######################
                timer_event = self.heart.is_time()
                if (timer_event):
                    # executor.submit(self.beacon.broadcast())
                    executor.map(self.stall, self.heart.tardy)

    def add_msg_handler(self, command: str, closure: Callable[..., Message]):
        # TODO: Validate if command is defined
        if command not in self.msg_handlers.keys():
            self.msg_handlers[command] = closure
            self.logger.info("Registered new handler.")
        else:
            print("Command already exists.")

    def stall(self, peer_name: Peer):
        #TODO: This
        print(peer_name)

    def stop(self, msg: Message):
        self.logger.warning(
            "Received exit command, client will stop receiving messages")
        msg.send("Bye!")
        self.continue_loop = False
        self.close_ctx()


if __name__ == "__main__":
    print("Shalom, World!")

    test = Reactor()
    test.start()
