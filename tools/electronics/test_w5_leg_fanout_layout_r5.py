import json
from pathlib import Path
import unittest
from w5_leg_fanout_layout_r5 import changed_plan,GROUND_DX,GROUND_DY
from w5_rounded_path import corner_offsets

ROOT=Path(__file__).resolve().parents[2]


class PreservedFootprintTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old=json.loads((ROOT/'hardware/electronics/full-cat/w5-leg-fanouts-r3/intent.json').read_text())['routes']
        cls.new=changed_plan(cls.old)

    def test_conservation(self):
        for old,new in zip(self.old,self.new):
            for key in ('wire','loom','servo_end','body_end','termination'):self.assertEqual(old[key],new[key])
            if old['role']=='V':self.assertEqual(old,new)

    def test_true_r10_tangent_consumption(self):
        for row in self.new:
            if row['role']!='V':corner_offsets(row['waypoints_mm'],10)

    def test_ground_remains_in_original_bought_footprint(self):
        self.assertEqual((GROUND_DX,GROUND_DY),(0,0))
        for old,new in zip(self.old,self.new):
            if old['role']=='G':
                self.assertEqual(old['waypoints_mm'][0][0],new['waypoints_mm'][0][0])
                self.assertEqual(abs(new['waypoints_mm'][0][1]),49.5)

    def test_separated_bands_and_outer_ground_above_pi_only_outside(self):
        d=[r['waypoints_mm'][2][2] for r in self.new if r['role']=='D']
        g=[r['waypoints_mm'][2][2] for r in self.new if r['role']=='G']
        self.assertGreaterEqual(min(g)-max(d),2.499999)
        for row in self.new:
            if row['role']=='G':self.assertGreater(abs(row['waypoints_mm'][2][1]),76+1.2)


if __name__=='__main__':unittest.main()
