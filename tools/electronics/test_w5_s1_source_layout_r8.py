import math,unittest
from w5_s1_source_layout_r8 import layout
from w5_s1_source_layout_r7 import layout as previous

class DiagonalApproach(unittest.TestCase):
    def test_no_other_interface_changes(self):
        for row,old in zip(layout(),previous()):
            for key in ('wire','a','b','start','end','OD_mm','wire_sku'):self.assertEqual(row[key],old[key])
            if row['wire']!='W067':self.assertEqual(row,old)

    def test_complete_length_continuity(self):
        for row in layout():
            for a,b in zip(row['edges'],row['edges'][1:]):self.assertLess(math.dist(a['end'],b['start']),1e-7)
            for e in row['edges']:
                self.assertGreater(e['length_mm'],0)
                if e['kind']=='arc':self.assertGreaterEqual(e['radius_mm'],row['minimum_static_radius_mm'])
            self.assertGreaterEqual(row['nominal_trial_blank_mm'],row['exposed_path_mm']+row['strip_allowance_mm']+row['trial_reserve_mm'])

if __name__=='__main__':unittest.main()
