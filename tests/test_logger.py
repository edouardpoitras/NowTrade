import unittest
import logging
from nowtrade.logger import Logger, CRITICAL


class TestLogger(unittest.TestCase):
    def test_logger(self):
        rootLogger = logging.getLogger()
        logger = Logger(rootLogger.name, logFile='logger.log', consoleLvl=CRITICAL, fileLvl=None)
        logger.__getstate__()
        logger.__setstate__({})
        logger = Logger(rootLogger.name, logFile='logger.log', consoleLvl=None, fileLvl=CRITICAL)
        logger.__getstate__()
        logger.__setstate__({})

if __name__ == "__main__":
    unittest.main()
