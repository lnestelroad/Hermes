#!/usr/bin/env python3

import time
from typing import Dict, List

# NOTE: These objects are examples of handeling events without including zeromq sockets as opposed to how the Message class does things.

# https://stackoverflow.com/questions/52722864/python-periodic-timer-interrupt
# https://github.com/sankalpjonn/timeloop/tree/d3e58dbe3b362d4f08077f570a8cda870875de65
from threading import Timer


class ProgramKilled(Exception):
    pass


def signal_handler(signum, frame):
    raise ProgramKilled

# https://stackoverflow.com/a/38317060


class PeriodicEvent():
    def __init__(self, interval, function, *args, **kwargs):
        self._timer = None
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False


class Peer():
    """
    Struct to hold peer liveliness information and update values
    """

    def __init__(self, liveliness=1000, retries=3):
        self.liveliness: int = liveliness
        self.retries, self.reset_retries = retries

        self.last_recv = time.time()
        self.expect_time = False

    def is_time(self) -> bool:
        """
        Checks to see if it is time to expect a heartbeat from peer

        Returns
        -------
        bool
        """
        if self.liveliness + self.last_recv >= time.time():
            self.expect_time = True

        return self.expect_time

    def received(self):
        """
        Updates last_recv and resets retires and expect_time attributes upon receiving a message
        """
        self.last_recv = time.time()
        self.retries = self.reset_retries
        self.expect_time = False

    def update_liveliness(self, new_val):
        self.liveliness = new_val

    def update_retries(self, new_val):
        self.reset_retries, self.retries = new_val


class Heartbeater():
    """
    A timer to keep track on when to send and when to expect heartbeats for nodes.

    Attributes
    ----------
    tabs : Dict[str, Peer]
        Holds information on all of the peers in which the node is interested in keeping tabs on and send heartbeats to.
    tardy : List[Peer]
        Contains the names of all the peers which have missed their heartbeat interval.
    last_sent : int
        The time stamp the of current nodes last send heartbeat
    liveliness : int
        The interval length for which to send heartbeats
    send_time : bool
        A flag to signify whether its time to send a new heartbeat to peers
    """
    tabs: Dict[str, Peer] = {}
    tardy: List[Peer] = []
    last_sent = 0

    def __init__(self, liveliness=1000):

        # Sends a little earlier to give some buffer room for unexpected stalling
        self.liveliness = liveliness - 10
        self.send_time = False

    def add_peer(self, peer_name, peer_liveliness=1000, peer_retries=3):
        """
        Adds a new peer to keep track of
        """
        self.tabs[peer_name](Peer(peer_liveliness, peer_retries))

    def remove_peer(self, peer_name: str):
        """
        Removes a presumed dead peer
        """
        del self.tabs[peer_name]

    def reset_peers(self, peer_names: List[str]):
        """
        Updates a peers timer values

        Parameters
        ----------
        peer_names : List[str]
            A list of peer names from which messages have been received.
        """
        for peer_name in peer_names:
            self.tabs[peer_name].received()

    def is_time(self) -> bool:
        """
        Check the current epoch to determine if it is time to send and expect heartbeats.

        Returns
        -------
        List[bool, List[Peer]]
        """
        if self.last_sent + self.liveliness >= time.time():
            self.send_time = True

        for peer_name, peer_obj in self.tabs.items():
            if peer_obj.is_time():
                self.tardy.append(peer_name)
                self.send_time = True

        return self.send_time

    def reset(self):
        """
        Updates the send time stamp and resents the send flag.
        """
        self.last_sent = time.time()
        self.send_time = False
