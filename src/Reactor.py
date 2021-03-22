#!/usr/bin/env python3

# System modules
import logging
from typing import Dict, List, Any, Callable
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

# Third party modules
import zmq

# Relative imports
from Node import Node
from Message import Message
from DBP import commands


class Reactor(Node):
    """
    A zmq ROUTER extension to provide an eventloop and persistant interface for services. Includes a command registering
    method for users to define new message and callbacks pairs.
    """

    def __init__(self, name=uuid4().hex, pipe: zmq.Socket = None):
        super().__init__(name=name, log_level=logging.DEBUG)

        self.continue_loop: bool = True

        self.standard_commands: Dict[str, bytes] = commands

        # Sets up interface sockets
        self.new_socket("interface", zmq.ROUTER)

        # Registers the pipe socket if one is passed.
        if pipe is not None:
            self.new_pipe(pipe)

        # Holds the functions for message handlers.
        # TODO: Add wild card options for commands
        self.msg_handlers: Dict[str, Callable[..., Message]] = {}

    def start(self):
        self.logger.info("Beginning Event Loop...")
        self.add_msg_handler(commands['Exit'], self.stop)

        with ThreadPoolExecutor(max_workers=100) as executor:
            while self.continue_loop:

                ####################### Incoming Message ####################
                events = dict(self.poller.poll(timeout=1000))

                # Checks to see if there are events on any created sockets.
                for soc_name, soc_obj in self.sockets.items():
                    if soc_obj in events:
                        self.logger.info(f"Message on {soc_name}.")
                        msg = Message(self.sockets[soc_name], self.logger)
                        msg.recv(display=True)

                        try:
                            self.logger.debug("Passing msg to thread.")
                            executor.submit(
                                self.msg_handlers[msg.command], msg)
                        except:
                            # TODO: Add message command for making new command registrations
                            self.logger.debug(
                                f"No message handler with command {msg.command}.")
                            msg.send(
                                "Error: Invalid command type. Please register command callback with the server.")

    def add_msg_handler(self, command: str, closure: Callable[..., Message]):
        if command not in self.standard_commands.keys():
            self.logger.info(
                "New Command is not apart of the standard list. Adding custom command")

        if command not in self.msg_handlers.keys():
            self.msg_handlers[command] = closure
            self.logger.info("Registered new handler.")
        else:
            print("Command already exists.")

    def stop(self, msg: Message):
        self.logger.warning(
            "Received exit command, client will stop receiving messages")
        msg.send("Bye!")
        self.continue_loop = False
        self.close_ctx()


if __name__ == "__main__":
    print("Shalom, World!")

    def respond(msg: Message):
        msg.send(command=commands['Acknowledged'], body='Sup.')

    test = Reactor()
    test.add_msg_handler(command=b'<3', closure=respond)
    test.start()
