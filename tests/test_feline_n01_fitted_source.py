"""Full manufacturing/end contracts for the frame-fitted source candidate."""
import math,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/cad'))
from plan_feline_n01_central_spine_power import build_fitted,build_supported

class FittedSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.p=build_fitted()

    def test_all_source_lengths_and_unchanged_stock(self):
        p=self.p;w={r['wire']:r for r in p['routes']}
        self.assertLess(w['W043']['raw_required_mm'],50);self.assertGreaterEqual(w['W043']['minimum_end_straight_mm'],9)
        self.assertLess(w['W077']['length_mm'],70);self.assertLess(w['W077']['source_draw_required_mm'],84.5)
        self.assertLess(w['W078']['raw_required_mm'],80);self.assertGreaterEqual(w['W078']['parts'][-1]['length_mm'],12)
        s=p['stock_candidate'];self.assertEqual(s['K1474_units'],1)
        self.assertEqual(s['red_remaining_mm']+s['red_W078_candidate_mm']+225,1000)
        self.assertEqual(s['black_remaining_mm']+s['black_W060_retained_candidate_mm']+225,1000)
        self.assertLessEqual(s['positive_path_candidate_mm'],300)

    def test_all_eight_ends_and_whole_clamps(self):
        p=self.p;self.assertEqual(len(p['all_unit_ends']),8);self.assertEqual(len(p['additional_end_prefixes']),6)
        self.assertNotIn('P_SYS.4',{e['role'] for e in p['all_unit_ends']})
        for e in p['all_unit_ends']:
            main=e['role'].startswith('MAIN.');lo,hi=p['shared_relief_reservations']['MAIN_CommonRelief' if main else 'P_SYS_CommonRelief']
            self.assertEqual(e['departure_axis'],[0,0,-1] if main else [-1,0,0])
            for t in (e['initial_mm']-9,e['initial_mm']):
                point=[x+t*d for x,d in zip(e['point_mm'],e['departure_axis'])]
                for i,x in enumerate(point):self.assertGreaterEqual(x+1e-7,lo[i]);self.assertLessEqual(x-1e-7,hi[i])

    def test_no_filled_sleeve_bridge_and_no_added_connector(self):
        s=self.p['splice'];a,b=s['sleeve_x_mm'];first,last=s['jacket_grip16_x_mm'],s['jacket_grip18_x_mm']
        self.assertAlmostEqual(b-a,20);self.assertAlmostEqual(a-first[1],2);self.assertAlmostEqual(last[0]-b,2)
        self.assertAlmostEqual(first[1]-first[0],9);self.assertAlmostEqual(last[1]-last[0],9)
        self.assertEqual(len(s['clip_parts']),3)
        lo,hi=s['clip_parts'][-1];self.assertAlmostEqual(hi[1]-lo[1],2)
        self.assertAlmostEqual(lo[1]-s['centre_mm'][1],2.1)
        self.assertFalse(s['additional_splice_or_connector'])

    def test_curve_continuity_and_exact_endpoints(self):
        p=self.p;w={r['wire']:r for r in p['routes']};e={e['role']:e for e in p['all_unit_ends']}
        self.assertLess(math.dist(w['W043']['end_mm'],e['P_SYS.5']['point_mm']),1e-7)
        self.assertLess(math.dist(w['W077']['end_mm'],p['splice']['tip16_mm']),1e-7)
        self.assertLess(math.dist(w['W078']['end_mm'],e['MAIN.VIN']['point_mm']),1e-7)
        for row in w.values():
            for a,b in zip(row['parts'],row['parts'][1:]):self.assertLess(math.dist(a['end'],b['start']),1e-7)
            for part in row['parts']:
                if part['kind']=='arc':self.assertGreaterEqual(part['radius_mm'],6)
        self.assertFalse(p['selected']);self.assertFalse(p['N01_complete']);self.assertFalse(p['physical_pass'])

class SupportedSourceTests(unittest.TestCase):
    def test_every_main_prefix_is_exact12mm_not_double_translated(self):
        p=build_supported();ends={e['id']:e for e in p['all_unit_ends']}
        for row in p['additional_end_prefixes']:
            e=ends[row['wire'].removeprefix('End:')]
            first,last=row['parts'][0]['start'],row['parts'][-1]['end']
            self.assertLess(math.dist(first,e['point_mm']),1e-7)
            wanted=[x+e['initial_mm']*d for x,d in zip(e['point_mm'],e['departure_axis'])]
            self.assertLess(math.dist(last,wanted),1e-7)
            self.assertLess(math.dist(row['end_mm'],last),1e-7)
            self.assertAlmostEqual(math.dist(first,last),e['initial_mm'])
        self.assertLess(p['routes'][1]['length_mm'],75)
        self.assertLess(p['routes'][2]['raw_required_mm'],80)

    def test_portal_contains_entire_common_clamp_with125_margin(self):
        p=build_supported();a,b=p['backbone_apertures']['UpperStrip-1'][0];lo,hi=p['shared_relief_reservations']['MAIN_CommonRelief']
        for i in (0,1):self.assertGreaterEqual(lo[i]-a[i],1.25-1e-7);self.assertGreaterEqual(b[i]-hi[i],1.25-1e-7)
        lower=p['backbone_changes']['UpperStrip-1'][0];self.assertGreaterEqual(a[1]-lower[1],2.7-1e-7)
        self.assertNotIn('ForeNegativeLowerCrossbar',p['backbone_changes'])
        self.assertFalse(p['selected']);self.assertFalse(p['N01_complete'])

if __name__=='__main__':unittest.main()
