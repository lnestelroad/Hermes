#!/usr/bin/env python3

# System modules
import logging
from typing import Dict, List, Any, Callable
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4
import signal

# Third party modules
import zmq

# Relative imports
from Hermes.Node import Node
from Hermes.Message import Message
from Hermes.DBP import commands, command_checks
from Hermes.Timer import ProgramKilled, PeriodicEvent, signal_handler


class Reactor(Node):
    """
    A zmq ROUTER extension to provide an eventloop and persistant interface for services. Includes a command registering
    method for users to define new message and callbacks pairs.
    """

    def __init__(self, socs: Dict[str, zmq.Socket], timers: Dict[str, Dict[str, Any]] = None, msg_handlers: Dict[bytes, Callable[..., Message]] = None, name=f'{uuid4().hex}_reactor', log_level=logging.WARN):
        super().__init__(name=name, log_level=log_level)

        self.continue_loop: bool = True

        # Holds the functions for message handlers.
        # TODO: Add wild card options for commands
        self.msg_handlers: Dict[bytes, Callable[..., Message]] = {}
        self.timers: Dict[str, int] = {}

        # Sets up sockets on which to poll over
        if socs is not None:
            for soc_name, soc_type in socs.items():
                self.new_socket(soc_name, soc_type)

        # Adds any msg_handlers passed in
        if msg_handlers is not None:
            for cmd, closure in msg_handlers.items():
                self.add_msg_handler(cmd, closure)

        # Initiates timer objects for periodic callbacks
        if timers is not None:
            for timer_name, timer_obj in timers.items():
                self.add_timer(
                    timer_name,
                    timer_obj['interval'],
                    timer_obj['callback'],
                    *timer_obj['args'],
                    **timer_obj['kwargs'])

    def start(self, display_incoming=False):
        """
        Begins the eventloop, polls on each registered socket, and passes incoming
        messages off to a child thread.
        """
        # Used to catch Ctl-C and Ctl-Z signal interupts
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)

        self.add_msg_handler(commands['Exit'], self.stop)
        self.logger.info("Beginning Reactor...")

        for timer in self.timers.values():
            timer.start()

        with ThreadPoolExecutor(max_workers=100) as executor:
            try:
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
            except ProgramKilled:
                self.stop()

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

    def add_timer(self, name: str, interval: int, closure: Callable, *args, **kwargs):
        """
        Adds a timer to watch for outside data generating or internal periodic events. On occurrence, 
        said outside data/internal events will be queued up on the appropriate outgoing socket(s)
        """
        periodic_event = PeriodicEvent(interval, closure, *args, **kwargs)
        self.timers[name] = periodic_event
        self.logger.info(f"Registered new timer: {name}")

    def stop(self, msg: Message = None):
        """
        A special callback function to end the reactors main loop when certain messages
        come in.TODO: Authorize these types of messages.
        """
        self.logger.warning(
            "Received exit command, client will stop receiving messages")
        if msg is not None:
            msg.send("Bye!")

        self.continue_loop = False
        self.close_ctx()

        for timer in self.timers.values():
            timer.stop()


if __name__ == "__main__":
    print("Shalom, World!")

    def respond(msg: Message):
        msg.send(command=commands['Acknowledged'], body='Sup.')

    test = Reactor()
    test.add_msg_handler(command=b'<3', closure=respond)
    test.start()
