import logging
from pathlib import Path


class Logger():
    def __init__(self, name, log_level, fmt='[%(name)s] %(levelname)s - %(message)s', file=None):

        self.logger = logging.getLogger(name)
        # self.log_dir = Path(__file__).parent / 'data/logs'

        # TODO: Put this in config file

        # Create handlers
        c_handler = logging.StreamHandler()
        # f_handler = logging.FileHandler(self.log_dir / f'{name}.log')

        # https://stackoverflow.com/questions/38182177/python-logging-info-debug-logs-not-displayed
        self.logger.setLevel(log_level)
        c_handler.setLevel(log_level)
        # f_handler.setLevel(logging.WARNING)

        # Create formatters and add it to handlers
        c_format = logging.Formatter(fmt)
        f_format = logging.Formatter(f'%(asctime)s - {fmt}')

        c_handler.setFormatter(c_format)
        # f_handler.setFormatter(f_format)

        # Add handlers to the logger
        self.logger.addHandler(c_handler)
        # self.logger.addHandler(f_handler)
