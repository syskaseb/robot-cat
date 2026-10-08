import math
import unittest
from open_prototype_direct_mta_plan import build, inside, samples, section_screen


class DirectMtaPlan(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.plan=build()

    def test_all_eight_routes_and_both_exits(self):
        self.assertEqual(len(self.plan['rows']),8)
        for leg in ('FL','FR','RL','RR'):
            rows=[r for r in self.plan['rows'] if r['leg']==leg]
            self.assertEqual({r['side'] for r in rows},{'source','output'})
            self.assertEqual(rows[0]['recipe']['segments'][0]['start'][0],
                             rows[1]['recipe']['segments'][0]['start'][0])

    def test_circle_sampling_and_length_gates(self):
        for row in self.plan['rows']:
            r=row['recipe']; pts=samples(r['segments'],.1)
            self.assertLess(math.dist(pts[0],r['segments'][0]['start']),1e-7)
            self.assertLess(math.dist(pts[-1],r['segments'][-1]['end']),1e-7)
            total=sum(math.dist(a,b) for a,b in zip(pts,pts[1:]))
            self.assertAlmostEqual(total,r['centreline_mm'],places=3)
            self.assertTrue(row['length_fits_assumption'])
            self.assertGreaterEqual(r['first_straight_mm'],3-1e-7)
            self.assertEqual(r['grip_straight_mm'],9)
            for a,b in zip(r['segments'],r['segments'][1:]):
                self.assertLess(math.dist(a['end'],b['start']),1e-7)

    def test_no_fake_selection_or_new_stock(self):
        self.assertFalse(self.plan['selected'])
        self.assertFalse(self.plan['stage_completed'])
        self.assertTrue(self.plan['conditional_reductions']['stock_not_reduced'])
        self.assertEqual(len(set(self.plan['candidate_lower_left_roles']+
                                 self.plan['candidate_lower_right_roles'])),10)
        self.assertGreaterEqual(len(self.plan['before_next_CAD']),5)

    def test_shared_port_permutation_preserves_electrical_identity(self):
        b=self.plan['port_binding'];p=b['same_bus_permutation']
        self.assertEqual(len(set(p)),len(set(p.values())))
        for old,new in p.items():self.assertEqual(old.split('.')[0],new.split('.')[0])
        self.assertEqual(len(b['ports']),100)
        self.assertEqual(sum(r['occupied'] for r in b['ports']),86)
        self.assertEqual(len(b['body_ends']),160)
        self.assertEqual(len(b['unallocated_upper_roles']),8)
        for port in b['ports']:
            if port['role'].split('.')[0] in b['unallocated_upper_roles']:
                self.assertIsNone(port['datum'])

    def test_even_odd_contours_keep_holes(self):
        outer=[[0,0],[10,0],[10,10],[0,10]]
        hole=[[3,3],[7,3],[7,7],[3,7]]
        self.assertTrue(inside([1,1],[outer,hole]))
        self.assertFalse(inside([5,5],[outer,hole]))
        self.assertFalse(inside([12,5],[outer,hole]))

    def test_coplanar_routes_are_not_silently_omitted(self):
        space={'sections':[{'z_mm':120,'contours':[
            {'part':'TorsoEnvelope','kind':'retained','xy_mm':[[-5,-5],[5,-5],[5,5],[-5,5]]},
            {'part':'block','kind':'retained','xy_mm':[[-1,-1],[1,-1],[1,1],[-1,1]]}]}]}
        r={'id':'test','recipe':{'segments':[{'kind':'line','start':[-2,0,120],'end':[2,0,120]}]}}
        result=section_screen([r],space)
        self.assertGreater(result['events'],0)
        self.assertEqual([h['part'] for h in result['centreline_planning_overlaps']],['block'])


if __name__=='__main__':unittest.main()
