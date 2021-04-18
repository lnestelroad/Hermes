#!/usr/bin/env python3

# System modules
import argparse
import os

# Third party modules
import zmq
from zmq.sugar.context import T

# Relative imports
from Hermes.Message import Message
from Hermes.Timer import Heartbeater, Peer
from Hermes.Beacon import Beacon
from Hermes.Reactor import Reactor
from Hermes.Service import Service
from Hermes.Client import Client
from Hermes.DBP import commands, command_checks


def main():
    parser = argparse.ArgumentParser(prog='hermes',
                                     description='Hermes cli for interactive bus connections.')
    parser.add_argument(
        'broker', help='A bool flag to signify if instance should be a broker',
        type=bool, default=False)
    parser.add_argument(
        '--config_file',
        help='Filepath for a custom configuration file',

    )
    args = parser.parse_args()

    os.system('cls' if os.name == 'nt' else 'clear')
    print(args)
