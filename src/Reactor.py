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
from DBP import commands, command_checks


class Reactor(Node):
    """
    A zmq ROUTER extension to provide an eventloop and persistant interface for services. Includes a command registering
    method for users to define new message and callbacks pairs.
    """

    def __init__(self, socs: Dict[str, zmq.Socket], msg_handlers: Dict[bytes, Callable[..., Message]] = None, name=f'{uuid4().hex}_reactor', log_level=logging.WARN):
        super().__init__(name=name, log_level=log_level)

        self.continue_loop: bool = True

        # Holds the functions for message handlers.
        # TODO: Add wild card options for commands
        self.msg_handlers: Dict[bytes, Callable[..., Message]] = {}

        # Sets up sockets on which to poll over
        for name, soc_type in socs.items():
            self.new_socket(name, soc_type)

        # Adds any msg_handlers passed in
        for cmd, closure in msg_handlers.items():
            self.add_msg_handler(cmd, closure)

    def start(self, display_incoming=False):
        """
        Begins the eventloop, polls on each registered socket, and passes incoming
        messages off to a child thread.
        """
        self.add_msg_handler(commands['Exit'], self.stop)
        self.logger.info("Beginning Reactor...")

        with ThreadPoolExecutor(max_workers=100) as executor:
            while self.continue_loop:

                ####################### Incoming Message ####################
                events = dict(self.poller.poll())

                # Checks to see if there are events on any created sockets.
                for soc_name, soc_obj in self.sockets.items():
                    if soc_obj in events:
                        self.logger.info(f"Message on {soc_name}.")
                        msg = Message(self.sockets[soc_name], self.logger)
                        msg.recv(display=display_incoming)

                        if msg.command in self.msg_handlers.keys():
                            self.logger.debug("Passing msg to thread.")
                            executor.submit(
                                self.msg_handlers[msg.command], msg)
                        else:
                            # TODO: Add message command for making new command registrations
                            self.logger.debug(
                                f"No message handler with command {msg.command}.")
                            msg.send(
                                "Error: Invalid command type. Please register command callback with the server.")

    def add_msg_handler(self, command: bytes, closure: Callable[..., Message]):
        """
        Adds a new message handler function to the list of callback. Messages
        with the command associated with the passed in function will be executed
        upon arrival in a child thread.

        Parameters
        ----------
        command: bytes
            A command for which to associate a callback function with.
        closure : Callable[..., Message]
            A function which takes a Message as its parameter to handle specific messages.
        """

        # if command not in self.standard_commands.values():
        #     self.logger.info(
        #         "New Command is not apart of the standard list. Adding custom command")

        if command not in self.msg_handlers.keys():
            self.msg_handlers[command] = closure
            self.logger.info(f"Registered new handler: {command}.")
        else:
            print("Command already exists.")

    def stop(self, msg: Message):
        """
        A special callback function to end the reactors main loop when certain messages
        come in.TODO: Authorize these types of messages.
        """
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
