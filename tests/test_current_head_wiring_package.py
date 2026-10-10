import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/cad'))
import package_current_head_wiring as P
class CurrentHeadWiring(unittest.TestCase):
 def test_gate_fail_closed(self):
  q=P.read(P.OUT/'head-final-checks.json');n=P.read(P.OUT/'anchor-release-checks.json');a=P.read(P.OUT/'anchor-space-checks.json')
  self.assertTrue(P.ready(q,n,a));self.assertFalse(P.ready(dict(q,contacts=[{}]),n,a));self.assertFalse(P.ready(q,dict(n,fresh_relocated_reopen=False),a))
 def test_score(self):
  s=P.read(P.BASE/'current-phase1-score.json');self.assertEqual(s['fixed_total'],20);self.assertIn('W2',s['confirmed_result_ids']);self.assertEqual(s['result_percent'],5*len(s['confirmed_result_ids']))
 def test_stock_not_fake_factory_route(self):
  p=P.read(P.OUT/'selection.json');self.assertEqual(len(p['length_stock_rows']),6)
  for f in p['factory_leads']:self.assertAlmostEqual(f['modeled_guide_mm']+f['unallocated_delivery_fit_budget_mm'],250)
  self.assertEqual(p['quantities']['JR_Kamami586761_300mm22AWG'],2);self.assertEqual(len(p['quantities']['RNF100_1_8_raw_mm']),6)
 def test_current_prints(self):
  p=P.read(P.OUT/'selection.json');self.assertEqual(len(p['prints']),2)
  for r in p['prints']:self.assertEqual(P.sha(P.ROOT/r['path']),r['sha256']);self.assertLess(max(r['size_mm'])+10,256)
 def test_no_physical_or_W3_claim(self):
  p=P.read(P.OUT/'selection.json');self.assertTrue(p['W2_complete']);self.assertFalse(p['physical_pass']);self.assertFalse(p['print_ready']);self.assertTrue(p['open_outside_W2'])
 def test_release_integrity(self):
  q=P.read(P.OUT/'manifest.json');self.assertTrue(P.verify(P.ROOT,q)['integrity_ok']);self.assertFalse(P.verify(P.ROOT,q,True)['integrity_ok'])
if __name__=='__main__':unittest.main()
