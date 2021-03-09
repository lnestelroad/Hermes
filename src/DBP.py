#!/usr/bin/env python3

# System modules
from enum import Enum
from typing import Protocol
import zmq


# class Protocols(Enum):
#     Client = b"DBPCCC01"
#     Service = b"DBPCCS01"


# class Commands(Enum):
#     Registration = b"0x01"
#     Approved = b"0x02"
#     Denied = b"0x03"
#     Heartbeat = b"0x04"
#     Disconnect = b"0x05"

Protocols = [
    b'DBPCCC01',
    b'DBPCCS01'
]
