import nowtrade.action
import unittest

class TestActions(unittest.TestCase):
    """ Test Actions """
    def test_action_long(self):
        """ Test Long Action """
        self.assertEqual('LONG', nowtrade.action.Long())
        self.assertEqual(nowtrade.action.Long(), 'LONG')
        self.assertEqual('Long', nowtrade.action.Long())
        self.assertEqual(nowtrade.action.Long(), 'Long')
        self.assertEqual('long', nowtrade.action.Long())
        self.assertEqual(nowtrade.action.Long(), 'long')
        self.assertEqual(nowtrade.action.Long(), nowtrade.action.Long())
        self.assertNotEqual(nowtrade.action.Long(), nowtrade.action.Short())
        self.assertNotEqual(nowtrade.action.Long(), nowtrade.action.LongExit())
        self.assertNotEqual(nowtrade.action.Long(), nowtrade.action.ShortExit())
        self.assertNotEqual(nowtrade.action.Long(), nowtrade.action.ExitLong())
        self.assertNotEqual(nowtrade.action.Long(), nowtrade.action.ExitShort())

    def test_action_short(self):
        """ Test Short Action """
        self.assertEqual('SHORT', nowtrade.action.Short())
        self.assertEqual(nowtrade.action.Short(), 'SHORT')
        self.assertEqual('Short', nowtrade.action.Short())
        self.assertEqual(nowtrade.action.Short(), 'Short')
        self.assertEqual('short', nowtrade.action.Short())
        self.assertEqual(nowtrade.action.Short(), 'short')
        self.assertEqual(nowtrade.action.Short(), nowtrade.action.Short())
        self.assertNotEqual(nowtrade.action.Short(), nowtrade.action.Long())
        self.assertNotEqual(nowtrade.action.Short(), nowtrade.action.LongExit())
        self.assertNotEqual(nowtrade.action.Short(), nowtrade.action.ShortExit())
        self.assertNotEqual(nowtrade.action.Short(), nowtrade.action.ExitLong())
        self.assertNotEqual(nowtrade.action.Short(), nowtrade.action.ExitShort())

    def test_action_long_exit(self):
        """ Test Long Exit Action """
        self.assertEqual('LONGEXIT', nowtrade.action.LongExit())
        self.assertEqual(nowtrade.action.LongExit(), 'LONGEXIT')
        self.assertEqual('LongExit', nowtrade.action.LongExit())
        self.assertEqual(nowtrade.action.LongExit(), 'LongExit')
        self.assertEqual('longexit', nowtrade.action.LongExit())
        self.assertEqual(nowtrade.action.LongExit(), 'longexit')
        self.assertEqual('long_exit', nowtrade.action.LongExit())
        self.assertEqual(nowtrade.action.LongExit(), 'long_exit')
        self.assertEqual('long exit', nowtrade.action.LongExit())
        self.assertEqual(nowtrade.action.LongExit(), 'long exit')
        self.assertEqual('EXITLONG', nowtrade.action.LongExit())
        self.assertEqual(nowtrade.action.LongExit(), 'EXITLONG')
        self.assertEqual('ExitLong', nowtrade.action.LongExit())
        self.assertEqual(nowtrade.action.LongExit(), 'ExitLong')
        self.assertEqual('exitlong', nowtrade.action.LongExit())
        self.assertEqual(nowtrade.action.LongExit(), 'exitlong')
        self.assertEqual('exit_long', nowtrade.action.LongExit())
        self.assertEqual(nowtrade.action.LongExit(), 'exit_long')
        self.assertEqual('exit long', nowtrade.action.LongExit())
        self.assertEqual(nowtrade.action.LongExit(), 'exit long')
        self.assertEqual(nowtrade.action.LongExit(), nowtrade.action.LongExit())
        self.assertNotEqual(nowtrade.action.LongExit(), nowtrade.action.Long())
        self.assertNotEqual(nowtrade.action.LongExit(), nowtrade.action.Short())
        self.assertNotEqual(nowtrade.action.LongExit(), nowtrade.action.ShortExit())
        self.assertNotEqual(nowtrade.action.LongExit(), nowtrade.action.ExitShort())

    def test_action_short_exit(self):
        """ Test Short Exit Action """
        self.assertEqual('SHORTEXIT', nowtrade.action.ShortExit())
        self.assertEqual(nowtrade.action.ShortExit(), 'SHORTEXIT')
        self.assertEqual('ShortExit', nowtrade.action.ShortExit())
        self.assertEqual(nowtrade.action.ShortExit(), 'ShortExit')
        self.assertEqual('shortexit', nowtrade.action.ShortExit())
        self.assertEqual(nowtrade.action.ShortExit(), 'shortexit')
        self.assertEqual('short_exit', nowtrade.action.ShortExit())
        self.assertEqual(nowtrade.action.ShortExit(), 'short_exit')
        self.assertEqual('short exit', nowtrade.action.ShortExit())
        self.assertEqual(nowtrade.action.ShortExit(), 'short exit')
        self.assertEqual('EXITSHORT', nowtrade.action.ShortExit())
        self.assertEqual(nowtrade.action.ShortExit(), 'EXITSHORT')
        self.assertEqual('ExitShort', nowtrade.action.ShortExit())
        self.assertEqual(nowtrade.action.ShortExit(), 'ExitShort')
        self.assertEqual('exitshort', nowtrade.action.ShortExit())
        self.assertEqual(nowtrade.action.ShortExit(), 'exitshort')
        self.assertEqual('exit_short', nowtrade.action.ShortExit())
        self.assertEqual(nowtrade.action.ShortExit(), 'exit_short')
        self.assertEqual('exit short', nowtrade.action.ShortExit())
        self.assertEqual(nowtrade.action.ShortExit(), 'exit short')
        self.assertEqual(nowtrade.action.ShortExit(), nowtrade.action.ShortExit())
        self.assertNotEqual(nowtrade.action.ShortExit(), nowtrade.action.Long())
        self.assertNotEqual(nowtrade.action.ShortExit(), nowtrade.action.Short())
        self.assertNotEqual(nowtrade.action.ShortExit(), nowtrade.action.LongExit())
        self.assertNotEqual(nowtrade.action.ShortExit(), nowtrade.action.ExitLong())

if __name__ == "__main__":
    unittest.main()
