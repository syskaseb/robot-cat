import json,unittest
import FreeCAD
import Part
from receive_feline_pi_split_service_space import DEST,independent
from receive_feline_rrp_shared_height import load
from check_main_p0_placement import ROOT,sha

class SplitServiceSpace(unittest.TestCase):
    def test_saved_split_geometry_and_unchanged_parent(self):
        r=json.loads(DEST.read_text());parts=load(r)
        self.assertTrue(all(s.isValid() and s.Solids for s in parts.values()))
        parent=parts['ReferenceOriginalCarrier'];root=parts['PiRootRetained'];mobile=parts['PiCarrierRemovable']
        before=parent.exportBrepToString()
        self.assertLess(independent(root).cut(independent(parent)).Volume,1e-5)
        self.assertLess(independent(mobile).cut(independent(parent)).Volume,1e-5)
        removed=independent(parent).cut(Part.makeCompound([independent(root),independent(mobile)]))
        self.assertTrue(removed.isValid())
        self.assertAlmostEqual(removed.Volume,r['removed_rod_mm3'],places=5)
        self.assertLess(independent(parts['PiCarrierLift40Sweep']).common(independent(root)).Volume,1e-7)
        self.assertEqual(before,parent.exportBrepToString());self.assertTrue(parent.isValid())

    def test_scope_and_pins_not_complete_service(self):
        r=json.loads(DEST.read_text())
        for p,h in r['source_sha256'].items():self.assertEqual(sha(ROOT/p),h,p)
        for key in ('static_budget_checks','pi_external_lift_checks','upper_carrier_external_checks','retained_root_checks','key_vs_lifted_unit'):
            self.assertTrue(all(c['ok'] for c in r[key].values()),key)
        self.assertFalse(r['selected']);self.assertFalse(r['N01_complete'])
        self.assertFalse(r['complete_service_received']);self.assertFalse(r['physical_pass'])
        self.assertGreaterEqual(len(r['open']),5)
        self.assertEqual(r['recipe']['head_upper_local_mm'],[5.3,4.3,5])

if __name__=='__main__':unittest.main()
