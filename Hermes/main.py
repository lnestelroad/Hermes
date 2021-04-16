#!/usr/bin/env python3

# System modules
import os
import math
import time
import logging
import threading
import concurrent.futures

# Third party modules
import zmq


# Relative imports
from Hermes.Client import Client
from Hermes.Service import Service
# from src.Beacon import Beacon
# from src.LastCachedValue import


# def start_broker(addr="127.0.0.1:5246"):
# beacon_of_gondor  = Broker(addr)


def start_client(name):
    theoden = Service(name)


def start_service(name):
    denethor_II = Client(name)


def main():

    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        # executor.submit(start_broker)
        executor.map(start_client, range(10))
        executor.map(start_service, range(2))


if __name__ == "__main__":

    format = "%(asctime)s| %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
    logging.info("[Main] Basic logger configured")
    print(f"PyZMQ version: {zmq.__version__}")

    main()
