import json,math,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/cad'))
from plan_current_main_pi_wiring import plan,OUT
from open_prototype_source_group import check_path

class MainPi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.p=plan()
    def test_four_pads_and_protected_factory_split(self):
        self.assertEqual(set(self.p['routes']),{'W060','W077','W078','W079','W080'})
        self.assertEqual(set(self.p['bare_pad_parts']),{'W060','W078','W079','W080'})
        for wid,parts in self.p['bare_pad_parts'].items():
            route=self.p['routes'][wid]['parts']
            self.assertEqual(parts[-1]['end'],route[-1]['end'] if wid in ('W060','W078') else route[0]['start'])
            self.assertAlmostEqual(sum(s['length_mm'] for s in parts),3)
    def test_p0_budget_and_no_physical_claim(self):
        r=self.p['routes']
        self.assertLessEqual(r['W078']['guide_mm']+3,150)
        self.assertLessEqual(r['W060']['guide_mm']+3+14,300)
        self.assertTrue(all(r[n]['guide_mm']+3<=250 for n in ('W079','W080')))
        # Existing protected input + factory overlap + full custom/bare.
        old=json.loads((OUT/'source-receiving-plan.json').read_text())
        inp=old['factory_routes']['W043']
        chain=sum(s['length_mm'] for s in inp['parts'])+r['W077']['guide_mm']+8+r['W078']['guide_mm']+3
        self.assertLessEqual(chain,300)
        self.assertFalse(self.p['selected']);self.assertFalse(self.p['W5_complete'])
        self.assertFalse(self.p['physical_pass'])
    def test_south_lap_and_same_ground_rail(self):
        a=self.p['factory_custom_overlap']['factory_tip_mm'];b=self.p['factory_custom_overlap']['custom_tip_mm']
        self.assertAlmostEqual(math.dist(a,b),8)
        self.assertEqual(a,self.p['routes']['W077']['parts'][-1]['end'])
        self.assertEqual(b,self.p['routes']['W078']['parts'][0]['start'])
        self.assertEqual(self.p['routes']['W060']['parts'][0]['start'],[-69.5,-73.75,100.99])
    def test_concentric_output_pair_not_equal_radius_crossing(self):
        a=self.p['routes']['W079']['parts'];b=self.p['routes']['W080']['parts']
        # Shared circle centres at the two paired plan-view turns, with
        # >=3.5mm radial separation. Cheap screen independently rejects crosses.
        for index,direction in [(2,[1,0,0]),(4,[0,-1,0])]:
            centres=[]
            for row in (a,b):
                s=row[index];centres.append([s['start'][i]+direction[i]*s['radius_mm'] for i in range(3)])
            self.assertLess(math.dist(*centres),1e-6)
        self.assertGreaterEqual(abs(a[2]['radius_mm']-b[2]['radius_mm']),3.5-1e-7)

if __name__=='__main__':unittest.main()
