"""
NowTrade module wrapper for the python logging module.
Allows for independent logging levels of different NowTrade components and
separate configurations for a console and file handler.
"""
import logging
from nowtrade import configuration

CRITICAL = logging.CRITICAL
ERROR = logging.ERROR
WARNING = logging.WARNING
INFO = logging.INFO
DEBUG = logging.DEBUG

class Logger(object):
    """
    A simple wrapper around the python logging module.
    Logs to both a file and the console.
    """
    def __init__(self, name, log_file=configuration.LOG_FILE, \
                 console_lvl=configuration.LOGGING_DEFAULT_CONSOLE, \
                 file_lvl=configuration.LOGGING_DEFAULT_FILE):
        """
        @type name: string
        @param name: The name of the logger object.
        @type log_file: string
        @param log_file: The logger filename.
        @type console_lvl: int
        @param console_lvl: The logging level of the console logger (see python logging module)
        @type file_lvl: int
        @param file_lvl: The logging level of the file logger (see python logging module)
        """
        self.name = name
        self.log_file = log_file
        self.console_lvl = self.get_console_level(name, console_lvl)
        self.file_lvl = self.get_file_level(name, file_lvl)
        self.logger = logging.getLogger(name)
        self.file_formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(name)s: %(message)s')
        self.file_logging_handler = None
        self.console_formatter = logging.Formatter('%(levelname)-8s %(name)s: %(message)s')
        self.console_logging_handler = None
        if len(self.logger.handlers) < 1:
            self.logger.propagate = False # Required to stop root logger
            self.logger.setLevel(logging.DEBUG)
            self.set_file_level(self.file_lvl)
            self.set_console_level(self.console_lvl)
            self.debug('Logger initialized  Log file: %s  \
                                            Log level: %s \
                                            Console Log Level: %s' \
                                            %(self.log_file, \
                                              self.file_lvl, \
                                              self.console_lvl))
    def get_logger_level(self, name, default, out):
        """
        Returns the logger level of a NowTrade object.
        """
        try:
            return getattr(configuration, 'LOGGING_%s_%s' %(name, out))
        except AttributeError:
            return default
    def get_console_level(self, name, default):
        """
        Returns the console logging level of a NowTrade object.
        """
        return self.get_logger_level(name, default, 'CONSOLE')
    def get_file_level(self, name, default):
        """
        Returns the file logging level of a NowTrade object.
        """
        return self.get_logger_level(name, default, 'FILE')
    def set_file_level(self, lvl):
        """
        Sets the file logging level of the current logging object.
        """
        if lvl is None:
            return
        self.logger.removeHandler(self.file_logging_handler)
        self.file_logging_handler = logging.FileHandler(self.log_file)
        self.file_logging_handler.setLevel(lvl)
        self.file_logging_handler.setFormatter(self.file_formatter)
        self.logger.addHandler(self.file_logging_handler)
    def set_console_level(self, lvl):
        """
        Sets the console logging level of the current logging object.
        """
        if lvl is None:
            return
        self.logger.removeHandler(self.console_logging_handler)
        self.console_logging_handler = logging.StreamHandler()
        self.console_logging_handler.setLevel(lvl)
        self.console_logging_handler.setFormatter(self.console_formatter)
        self.logger.addHandler(self.console_logging_handler)
    def debug(self, message):
        """
        Add debug logging statement.
        """
        self.logger.debug(message)
    def info(self, message):
        """
        Add info logging statement.
        """
        self.logger.info(message)
    def warning(self, message):
        """
        Add warning logging statement.
        """
        self.logger.warning(message)
    def error(self, message):
        """
        Add error logging statement.
        """
        self.logger.error(message)
    def critical(self, message):
        """
        Add critical logging statement.
        """
        self.logger.critical(message)
    def exception(self, message):
        """
        Add exception logging statement.
        """
        self.logger.exception(message)
    # Used to enable pickling
    def __getstate__(self):
        values = dict(self.__dict__)
        del values['logger']
        try:
            del values['file_logging_handler']
        except KeyError:
            pass
        try:
            del values['console_logging_handler']
        except KeyError:
            pass
        return values
    def __setstate__(self, data):
        self.__dict__.update(data)
        self.__init__(self.name, self.log_file, self.console_lvl, self.file_lvl)
