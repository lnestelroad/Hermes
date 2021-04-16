#!/usr/bin/env python3

# %%

import os
from pathlib import Path
from pprint import pprint
from typing import Dict, Any

# Third party imports
import yaml

# %%


class ConfigParser():
    """
    Uses the PyYaml file parser to bring in user defined service configuration items. The config object
    attribute will hold all of the necessary information to be accessed by the service code. Yaml files 
    should be stored in the config dir under. Should no file exist, a default one will be made under the
    name 'Hermesfile.yaml'

    Attributes
    ----------
    configs : Dict[str, Dict[str, Any]]
    """

    def __init__(self, filename: str = None) -> Dict[str, Any]:
        self._config_dir = os.getcwd()

        self._config_file = self._config_dir + \
            (filename if filename is not None else '/Hermesfile.yaml')

        print(self._config_dir)

        if 'Hermesfile.yaml' not in os.listdir(self._config_dir):
            self.default()

        with open(self._config_file) as f:
            self.configs = yaml.load(f, Loader=yaml.FullLoader)

        self.validate()

    def validate(self) -> None:
        # TODO: flesh this out
        if {'general', 'handlers', 'sockets', 'timers'} != self.configs.keys():
            raise KeyError(
                "Hermesfile does not contain the proper config items.")

    def default(self) -> None:
        DEFAULT_CONTENT = """---
    #TODO: define what each field means and its expected data type(s)
    #TODO: Give ranges for ports, broadcast ips, and, liveliness
    general:
    # The general section holds all of the information of the service node which will be passed along to the 
    # Core Catalog Service node during registration and uniquely identify itself in the network. Each node should
    # contain the following information:
        # name: ~
        # ip: localhost
        # log_level: [DEBUG, INFO, WARNING, CRITICAL, ERROR]
        # liveliness: 1000

        # Default
        name: ~
        ip: localhost
        log_level: warning
        liveliness: 1000

    
    sockets:
    # The sockets section of the configuration will hold all of the zmq message exchange pattern specific sockets 
    # needed to transport specific information. Socket information should follow the following format:
        # name:
        #     port: 1234
        #     type: [ROUTER, DEALER, REQ, REP, SUB, PUB, DISH, RADIO, PAIR]
        #     verbose: [True, False]

        # Default
        cmd_intake:
            port: 5246
            type: ROUTER
            verbose: false


    handlers:
    # The handlers section holds all of the function callback for any given message command. Message commands are 
    # binary frames of 3-5 bytes and callbacks are callables (closures) defined within the user defined service class.
    # Each entry should consist of key value pairs in the following format:

        # binary_command : callback_function

        # Defaults
        Info_Req: = client_handler
        Registration: = service_registration
        Update: = service_update



    timers:
    # The timers section will hold all of the periodic outgoing message generation functions. After a user given
    # interval, the timer will call a user defined function which either has recurring data to distribute or watches
    # a location for new updates to pass along. Timers information should contain the following attributes:
        # name:
        #     interval: 1000
        #     callback: callback_name
        #     args: 
        #         positional_parameters:
        #             - arg1
        #             - arg2
        #     kwargs: 
        #         keyword_parameters:
        #             kwarg1: value1
        #             kwarg2: value2

        # Defaults
        heartbeats: 
            interval: 1
            callback: = broadcast
            args: 
                - 5245
                - 255.255.255.255
            kwargs: 
                port: 5245
                broadcast_addr: 255.255.255.255
        """

        if 'Hermesfile.yaml' in os.listdir(self._config_dir):
            raise Exception('Hermesfile already exists.')

        else:
            with open(self._config_file, 'x') as f:
                f.write(DEFAULT_CONTENT)


# %%
if __name__ == "__main__":
    print("Shalom, World!")

    test = ConfigParser()
    # pprint(test.configs)

# %%
