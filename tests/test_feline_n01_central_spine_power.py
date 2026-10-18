"""Pure dimensional contracts of one full source chain, not CAD acceptance."""
import importlib.util,math,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/cad'))
import plan_feline_n01_central_spine_power as P

class CentralPowerPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.p=P.build()

    def test_full_three_routes_and_source_draws(self):
        p=self.p;w={r['wire']:r for r in p['routes']}
        self.assertEqual(w['W043']['end_mm'],[-106,0,30.9])
        self.assertLess(math.dist(w['W077']['end_mm'],p['splice']['tip16_mm']),1e-7)
        self.assertLess(math.dist(w['W078']['end_mm'],[-38.1,0,94.2]),1e-7)
        self.assertEqual(w['W078']['end_direction'],[0,0,1])
        self.assertLessEqual(w['W043']['source_draw_required_mm'],84.5)
        self.assertLessEqual(w['W077']['source_draw_required_mm'],84.5)
        self.assertLessEqual(w['W078']['raw_required_mm'],115)
        self.assertTrue(all(p['necessary_length_gate'][k] for k in ('W043','W077','W078','exact_endpoint_match')))

    def test_sleeve_and_both_jacket_lands(self):
        s=self.p['splice'];a,b=s['sleeve_x_mm'];l=s['jacket_grip18_x_mm'];r=s['jacket_grip16_x_mm']
        self.assertAlmostEqual(b-a,20);self.assertAlmostEqual(l[1]-l[0],9);self.assertAlmostEqual(r[1]-r[0],9)
        self.assertAlmostEqual(a-l[1],2);self.assertAlmostEqual(r[0]-b,2)
        self.assertAlmostEqual(s['bare_overlap_x_mm'][1]-s['bare_overlap_x_mm'][0],8)
        self.assertFalse(s['additional_splice_or_connector'])

    def test_all_eight_ends_in_whole_shared_restraints(self):
        p=self.p;self.assertEqual(len(p['all_unit_ends']),8);self.assertEqual(len(p['additional_end_prefixes']),6)
        self.assertNotIn('P_SYS.4',{e['role'] for e in p['all_unit_ends']})
        for e in p['all_unit_ends']:
            main=e['role'].startswith('MAIN.');lo,hi=p['shared_relief_reservations']['MAIN_CommonRelief' if main else 'P_SYS_CommonRelief']
            self.assertEqual(e['departure_axis'],[0,0,-1] if main else [1,0,0])
            for offset in (e['initial_mm']-9,e['initial_mm']):
                point=[x+offset*d for x,d in zip(e['point_mm'],e['departure_axis'])]
                for i,x in enumerate(point):
                    self.assertGreaterEqual(x+1e-7,lo[i]);self.assertLessEqual(x-1e-7,hi[i])

    def test_continuity_radius_stock_and_no_claims(self):
        p=self.p
        for row in p['routes']:
            for a,b in zip(row['parts'],row['parts'][1:]):self.assertLess(math.dist(a['end'],b['start']),1e-7)
            for part in row['parts']:
                if part['kind']=='arc':self.assertGreaterEqual(part['radius_mm'],9 if row['wire']=='W077' else 11.1)
        s=p['stock_candidate'];self.assertEqual(s['K1474_units'],1)
        self.assertEqual(s['red_remaining_mm']+s['red_W078_candidate_mm']+225,1000)
        self.assertEqual(s['black_remaining_mm']+s['black_W060_retained_candidate_mm']+225,1000)
        self.assertLessEqual(s['positive_path_candidate_mm'],300)
        self.assertFalse(p['selected']);self.assertFalse(p['N01_complete']);self.assertFalse(p['physical_pass'])
        self.assertFalse(p['unit_world_pose_pending'])

if __name__=='__main__':unittest.main()
