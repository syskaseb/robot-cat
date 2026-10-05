"""Exact parallel S connector invariants without CAD startup."""
import math
import unittest
from w5_parallel_connection import connect


class ParallelConnectionTests(unittest.TestCase):
    def test_three_dimensional_target_and_tangency(self):
        start=[120.5,-0.5,93.5];target=[-32.5318889681,30.2850416801,89.9000000809]
        edges=connect(start,target,[-1,0,0],10)
        self.assertLess(math.dist(edges[0]['start'],start),1e-7)
        self.assertLess(math.dist(edges[-1]['end'],target),1e-7)
        self.assertTrue(all(math.dist(a['end'],b['start'])<1e-7 for a,b in zip(edges,edges[1:])))

    def test_bends_use_exact_prescribed_radius(self):
        edges=connect([0,0,0],[100,30,5],[1,0,0],12.4)
        arcs=[e for e in edges if e['kind']=='arc']
        self.assertEqual(len(arcs),2)
        self.assertTrue(all(abs(e['radius_mm']-12.4)<1e-8 for e in arcs))

    def test_full_bus_cable_stays_within_factory_blank(self):
        import json
        from pathlib import Path
        root=Path(__file__).resolve().parents[2]
        row=json.loads((root/'hardware/electronics/full-cat/w5-bus-low-s-plan-r1/intent.json').read_text(encoding='utf-8'))['recipe']
        self.assertLessEqual(row['trial_blank_mm'],row['factory_length_mm'])
        self.assertLessEqual(row['body_mm']+41+30,300)
        self.assertEqual(row['source_straight_mm'],6)


if __name__=='__main__':unittest.main()
