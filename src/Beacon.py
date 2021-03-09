#System modules
import os
import math
import time
import logging
import threading
import concurrent.futures

# Third party modules
import tqdm
import zmq
import matplotlib.pyplot as plt


class Beacon():
    def __init__(self):
        print("Shalom, World!")