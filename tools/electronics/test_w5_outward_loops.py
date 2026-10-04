from pathlib import Path
import json, math, unittest
from w5_leg_outward_loops_r1 import plan
from w5_leg_outward_loops_r2 import plan as upward_plan
from w5_rounded_path import corner_offsets
ROOT=Path(__file__).resolve().parents[2]


class OutwardLoomPlan(unittest.TestCase):
    def rows(self):
        return json.loads((ROOT/'hardware/electronics/full-cat/w5-leg-fanouts-r5/intent.json').read_text(encoding='utf-8'))['routes']

    def test_all_labels_ports_breakouts_preserved(self):
        old=self.rows(); snapshot=json.dumps(old,sort_keys=True)
        new=plan(old)
        self.assertEqual(len(new),36)
        self.assertEqual(len({r['wire'] for r in new}),36)
        self.assertEqual(snapshot,json.dumps(old,sort_keys=True))
        for a,b in zip(old,new):
            for key in ('wire','loom','role','body_end','servo_end'):
                self.assertEqual(a[key],b[key])
            self.assertEqual(a['waypoints_mm'][-1],b['waypoints_mm'][-1])
            if a['role']=='V': self.assertEqual(a,b)

    def test_loop_is_diameter20_not_a_polygon_reversal(self):
        for r in plan(self.rows()):
            if r['role']=='V': continue
            p=r['waypoints_mm']; recipe=r['real_half_turn']
            self.assertAlmostEqual(math.dist(p[1],p[2]),20)
            self.assertAlmostEqual(math.dist(p[1],recipe['centre']),10)
            self.assertAlmostEqual(math.dist(p[2],recipe['centre']),10)
            self.assertAlmostEqual(math.dist(p[0],p[1]),6)
            corner_offsets(p[2:],10)  # Only the following real polygon, NOT the arc chord.

    def test_parallel_cage_arcs_have_nominal_core_space(self):
        for angle in (22,32):
            self.assertGreater(6.75*math.sin(math.radians(angle)),2.4)
        self.assertGreater(20*(math.sin(math.radians(32))-math.sin(math.radians(22))),2.4)

    def test_upward_family_does_not_descend_through_p0(self):
        rows=self.rows()
        for old,row in zip(rows,upward_plan(rows)):
            if row['role']=='V':
                self.assertEqual(old,row)
                continue
            points=row['waypoints_mm']
            self.assertGreater(points[2][2],points[1][2])
            self.assertGreater(row['real_half_turn']['centre'][2],points[1][2])
            self.assertAlmostEqual(math.dist(points[1],points[2]),20)
            self.assertTrue(all(p[2]>=113.5 for p in points[:-1]))
            corner_offsets(points[2:],10)


if __name__=='__main__': unittest.main()
