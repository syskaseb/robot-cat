import unittest
from compose_phase1_assembly import order,stage_for


class WholeSequence(unittest.TestCase):
    def test_cycle_and_future_dependency_rejected(self):
        with self.assertRaises(AssertionError):order([dict(id='upper',requires=['lower']),dict(id='lower',requires=['upper'])])

    def test_duplicate_stage_rejected(self):
        with self.assertRaises(AssertionError):order([dict(id='base',requires=[]),dict(id='base',requires=[])])

    def test_covers_after_wiring_and_battery_separate(self):
        self.assertEqual(stage_for(dict(identity='P0-BASE-COVER-FRONT')),'close')
        self.assertEqual(stage_for(dict(identity='P0-BATTERY-CARRIER-R4')),'battery')


if __name__=='__main__':unittest.main()
