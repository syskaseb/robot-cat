"""Small regression checks for received roof and exact nut-loading hull."""
from pathlib import Path
import json,math,unittest
from w5_source_roof_service_r1 import hull
ROOT=Path(__file__).resolve().parents[2]

class RoofTests(unittest.TestCase):
    def test_hull_removes_collinear_and_duplicate_points(self):
        self.assertEqual(hull([(0,0),(1,0),(2,0),(2,2),(0,2),(0,0)]),[(0,0),(2,0),(2,2),(0,2)])

    def test_hex_translation_sweep_bounds(self):
        points=[(3.175*math.cos(math.pi/6+k*math.pi/3),3.175*math.sin(math.pi/6+k*math.pi/3)+dy) for k in range(6) for dy in (0,12)]
        polygon=hull(points)
        self.assertAlmostEqual(max(y for _,y in polygon)-min(y for _,y in polygon),18.35)
        self.assertLess(max(x for x,_ in polygon)-min(x for x,_ in polygon),6)

    def test_received_roof_fit_and_no_completion_claim(self):
        r=json.loads((ROOT/'hardware/electronics/full-cat/w5-source-roof-native-r3/checks.json').read_text(encoding='utf-8'))
        self.assertEqual(r['hits'],[]);self.assertEqual(r['errors'],[])
        self.assertTrue(r['closed_STLs'] and r['relocated_reopen'])
        for x,y,z in r['dimensions_mm'].values():
            self.assertLessEqual(x+10,256);self.assertLessEqual(y+10,256);self.assertLessEqual(z,256)
        self.assertFalse(r['selected'] or r['W5_complete'] or r['physical_pass'])

    def test_received_service_scope_is_sampled(self):
        r=json.loads((ROOT/'hardware/electronics/full-cat/w5-source-roof-service-r1/assembly.json').read_text(encoding='utf-8'))
        self.assertEqual(r['hits'],[]);self.assertEqual(r['errors'],[])
        self.assertTrue(r['hood_lift']['sampled_not_continuous'])
        self.assertFalse(r['whole_source_assembly_complete'])
        self.assertEqual([q['quantity'] for q in r['allocations']],[4,4,8])

if __name__=='__main__':unittest.main()
