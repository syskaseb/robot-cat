import unittest
from w5_source_platform_native_r3 import specification
from w5_source_platform_native_r4 import specification as final_specification


class SourcePlatformR3Tests(unittest.TestCase):
    def test_shared_inlets_unchanged_and_two_accessible_mount_axes(self):
        s = specification()
        self.assertEqual(s['insulation_centres'], [[-84, 2, 135.5], [-76.5, 2, 135.5]])
        self.assertEqual(s['bolt_centres'], [[-90.2, 27.5], [-90.2, 40.5]])
        self.assertLessEqual(s['foot'][3], -86.4)
        self.assertEqual(s['foot'][2], s['deck_bearing_pad'][5])
        for x, y in s['bolt_centres']:
            self.assertGreater(x - 1.7, s['foot'][0])
            self.assertLess(x + 1.7, s['foot'][3])
            self.assertGreater(y - 1.7, s['foot'][1])
            self.assertLess(y + 1.7, s['foot'][4])
        self.assertEqual(s['new_M3_washers'], 4)
        self.assertFalse(s['selected'])
        self.assertFalse(s['physical_pass'])

    def test_bolt_and_driver_envelopes_west_of_complete_source_loop(self):
        s = final_specification()
        for x, y in s['bolt_centres']:
            self.assertEqual(x, -94.4)
            self.assertLess(x + 1.5, -92.6)
            self.assertGreater(x - 3.5, s['foot'][0])
        self.assertEqual(s['new_M3x12'], 2)
        self.assertEqual(s['body_bounds'], specification()['body_bounds'])
        self.assertEqual(s['insulation_centres'], specification()['insulation_centres'])


if __name__ == '__main__':
    unittest.main()
