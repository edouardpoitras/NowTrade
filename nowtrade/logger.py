import logging
from nowtrade import configuration

CRITICAL = logging.CRITICAL
ERROR = logging.ERROR
WARNING = logging.WARNING
INFO = logging.INFO
DEBUG = logging.DEBUG

class Logger:
    """
    A simple wrapper around the python logging module.
    Logs to both a file and the console.
    """
    def __init__(self, name, logFile=configuration.LOG_FILE, consoleLvl=configuration.LOGGING_DEFAULT_CONSOLE, fileLvl=configuration.LOGGING_DEFAULT_FILE):
        """
        @type name: string
        @param name: The name of the logger object.
        @type logFile: string
        @param logFile: The logger filename.
        @type consoleLvl: int
        @param consoleLvl: The logging level of the console logger (see python logging module)
        @type fileLvl: int
        @param fileLvl: The logging level of the file logger (see python logging module)
        """
        self.name = name
        self.logFile = logFile
        self.consoleLvl = self.getConsoleLevel(name, consoleLvl)
        self.fileLvl = self.getFileLevel(name, fileLvl)
        self.logger = logging.getLogger(name)
        self.fileFormatter = logging.Formatter('%(asctime)s %(levelname)-8s %(name)s: %(message)s')
        self.consoleFormatter = logging.Formatter('%(levelname)-8s %(name)s: %(message)s')
        if len(self.logger.handlers) < 1:
            self.logger.propagate = False # Required to stop root logger
            self.logger.setLevel(logging.DEBUG)
            self.setFileLevel(self.fileLvl)
            self.setConsoleLevel(self.consoleLvl)
            self.debug('Logger initialized  Log file: %s  Log level: %s  Console Log Level: %s' %(self.logFile, fileLvl, consoleLvl))
    def getLoggerLevel(self, name, default, out):
        try: return getattr(configuration, 'LOGGING_%s_%s' %(name, out))
        except: return default
    def getConsoleLevel(self, name, default):
        return self.getLoggerLevel(name, default, 'CONSOLE')
    def getFileLevel(self, name, default):
        return self.getLoggerLevel(name, default, 'FILE')
    def setFileLevel(self, lvl):
        if lvl == None: return
        try: self.logger.removeHandler(self.fileLoggingHandler)
        except: pass
        self.fileLoggingHandler = logging.FileHandler(self.logFile)
        self.fileLoggingHandler.setLevel(lvl)
        self.fileLoggingHandler.setFormatter(self.fileFormatter)
        self.logger.addHandler(self.fileLoggingHandler)
    def setConsoleLevel(self, lvl):
        if lvl == None: return
        try: self.logger.removeHandler(self.consoleLoggingHandler)
        except: pass
        self.consoleLoggingHandler = logging.StreamHandler()
        self.consoleLoggingHandler.setLevel(lvl)
        self.consoleLoggingHandler.setFormatter(self.consoleFormatter)
        self.logger.addHandler(self.consoleLoggingHandler)
    def debug(self, message): self.logger.debug(message)
    def info(self, message): self.logger.info(message)
    def warning(self, message): self.logger.warning(message)
    def error(self, message): self.logger.error(message)
    def critical(self, message): self.logger.critical(message)
    def exception(self, message): self.logger.exception(message)
    # Used to enable pickling
    def __getstate__(self):
        d = dict(self.__dict__)
        del d['logger']
        try: del d['fileLoggingHandler']
        except: pass
        try: del d['consoleLoggingHandler']
        except: pass
        return d
    def __setstate__(self, d):
        self.__dict__.update(d)
        self.__init__(self.name, self.logFile, self.consoleLvl, self.fileLvl)
