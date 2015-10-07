"""
Tests for the NowTrade Logger object.
"""
import unittest
import logging
from nowtrade.logger import Logger, CRITICAL


class TestLogger(unittest.TestCase):
    """
    Test the Logger object.
    """
    def test_logger(self):
        """
        Simple logger operations.
        """
        root_logger = logging.getLogger()
        logger = Logger(root_logger.name, \
                        log_file='logger.log', \
                        console_lvl=CRITICAL, \
                        file_lvl=None)
        #logger.set_console_level(10)
        #logger.set_file_level(10)
        logger.__getstate__()
        logger.__setstate__({})
        logger = Logger(root_logger.name, \
                        log_file='logger.log', \
                        console_lvl=None, \
                        file_lvl=CRITICAL)
        logger.__getstate__()
        logger.__setstate__({})

if __name__ == "__main__":
    unittest.main()
