import unittest,json
from w5_source_platform_native_r1 import specification,TIE

class SourcePlatformTests(unittest.TestCase):
    def test_real_body_and_same_inlet_centres(self):
        s=specification()
        self.assertEqual(s['body_bounds'],[-87.5,7,131,-50.5,29,142])
        self.assertEqual(s['insulation_centres'],[[-84,2,135.5],[-76.5,2,135.5]])
        self.assertEqual(s['body_ties']+s['shared_inlet_ties'],2)
        self.assertFalse(s['selected']);self.assertFalse(s['physical_pass'])

    def test_exact_tie_and_mount_stack(self):
        s=specification();r=json.loads(TIE.read_text(encoding='utf-8'))
        self.assertEqual(s['strap_length_mm'],r['length_mm'])
        self.assertEqual(s['strap_band_mm'],[r['band_width_mm'],r['band_thickness_mm']])
        self.assertEqual(s['new_M3x12'],len(s['bolt_centres']))
        self.assertEqual(s['foot'][2],s['deck_bearing_pad'][5])
        self.assertEqual(s['new_M3_washers'],2*s['new_M3x12'])

if __name__=='__main__':unittest.main()
