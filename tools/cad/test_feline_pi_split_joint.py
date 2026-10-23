import json,unittest
import FreeCAD as A
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from receive_feline_rrp_shared_height import load
from plan_feline_pi_split_joint import cradle,independent

class Joint(unittest.TestCase):
    def test_rebuild(self):
        r=json.loads((OUT/'n01-Pi-open-cradle-joint.json').read_text());saved=load(r)
        p=json.loads((OUT/'n01-Pi-split-service-space.json').read_text());old=load(p)
        tf=A.Placement(A.Vector(*r['frame']['position']),A.Rotation(*r['frame']['rotation']))
        rebuilt=cradle(tf,old['PiRootRetained'],old['PiCarrierRemovable'])
        for n,s in rebuilt.items():
            self.assertTrue(s.isValid() and len(s.Solids)==1,n)
            self.assertLess(independent(s).cut(independent(saved[n])).Volume,1e-5,n)
            self.assertLess(independent(saved[n]).cut(independent(s)).Volume,1e-5,n)

    def test_scope(self):
        r=json.loads((OUT/'n01-Pi-open-cradle-joint.json').read_text())
        for p,h in r['source_sha256'].items():self.assertEqual(sha(ROOT/p),h,p)
        for c in r['checks'].values():self.assertFalse(c['errors'] or c['failures'])
        self.assertFalse(r['selected'] or r['N01_complete'] or r['physical_pass'])
        self.assertFalse(r['strength_and_fit_qualified'])
        self.assertTrue(all(sum(v.values())>0 for v in r['twist_stops_at_15degrees'].values()))

if __name__=='__main__':unittest.main()
