import unittest
from parallel_core_candidates import tangent,shifted,west_north_return
from plan_current_moving_looms import exact_quarter
from plan_current_mta_interfaces import line
import math


class ParallelGeometryTest(unittest.TestCase):
    def test_exact_circle_tangent_not_sample_chord(self):
        actual=tangent(dict(kind='arc',start=[10,0,0],mid=[2**.5*5,2**.5*5,0],end=[0,10,0]))
        for a,b in zip(actual,[-1,0,0]):self.assertAlmostEqual(a,b,12)
    def test_shift_preserves_shape_and_length(self):
        p=dict(kind='bezier',start=[0,0,0],end=[3,0,0],poles_mm=[[0,0,0],[1,0,0],[2,0,0],[3,0,0]],length_mm=3)
        q=shifted(p,[0,2.25,-1.299]);self.assertEqual(q['length_mm'],3)
        self.assertEqual(q['poles_mm'][0],[0,2.25,-1.299]);self.assertEqual(p['start'],[0,0,0])
    def test_one_return_preserves_ends_tangents_and_budget(self):
        start=[114.89756646104678,102.5,91];free=[*start[:2],96]
        receiving=[line([105,110,98.5],[105,100,98.5]),exact_quarter([105,100,98.5],[0,-1,0],[0,0,-1],10),line([105,90,88.5],[105,90,79.5])]
        row=dict(wire='W071',source_land=line(start,free),free_end=[105,110,98.5],receiver_outward_axis=[0,1,0],
            receiving_parts=receiving,capacity_before_terminal_mm=197.08213432960827,terminal_allowance_project_mm=11)
        q=west_north_return(row,exact_quarter(free,[0,0,1],[-1,0,0],10));self.assertIsNotNone(q)
        self.assertEqual(q['parts'][0]['start'],start);self.assertEqual(q['parts'][-1]['end'],[105,90,79.5])
        self.assertGreater(q['spare_before_trim_mm'],48);self.assertGreaterEqual(q['minimum_sampled_R_mm'],10)
        for a,b in zip(q['parts'],q['parts'][1:]):self.assertLess(math.dist(a['end'],b['start']),1e-6)


if __name__=='__main__':unittest.main()
