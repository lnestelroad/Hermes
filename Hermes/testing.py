
# %%

# System modules
import socket
from threading import Event, Thread
import time

# Third party modules
import zmq

# Relative imports
from Hermes.Message import Message
from Hermes.Timer import Heartbeater, Peer
from Hermes.Beacon import Beacon
from Hermes.Reactor import Reactor
from Hermes.Service import Service
from Hermes.Client import Client
from Hermes.DBP import commands, command_checks


# %%
###################### Service Test #############################

#################################################################

# %%
###################### Client Test ###############################
cli = Client()
cli.request_from_service(name='Rohan')
##################################################################

# %%

# %%
