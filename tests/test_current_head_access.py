import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/cad'))
import package_current_head_access as P
class CurrentHeadAccess(unittest.TestCase):
 def test_complete_gate(self):
  a=P.read(P.OUT/'space-checks.json');n=P.read(P.OUT/'native-checks.json')
  self.assertTrue(P.ready(a,n));self.assertFalse(P.ready(dict(a,contacts=[{}]),n))
  self.assertFalse(P.ready(a,dict(n,fresh_relocated_reopen=False)))
 def test_current_score(self):
  s=P.read(P.BASE/'current-phase1-score.json');self.assertIn('W2',s['confirmed_result_ids'])
  self.assertEqual(s['result_percent'],5*len(s['confirmed_result_ids']));self.assertEqual(s['fixed_total'],20)
 def test_access_not_false_W3(self):
  s=P.read(P.OUT/'selection.json');self.assertTrue(s['W2_complete']);self.assertFalse(s['physical_pass'])
  self.assertEqual(s['fixed_tail_y_mm'],[85,94]);self.assertEqual(len(s['receiving_approaches']),3)
  self.assertTrue(s['open_outside_W2']);self.assertIn('external',s['functional_neck'].lower())
 def test_hardware_and_prints(self):
  s=P.read(P.OUT/'selection.json');self.assertEqual(len(s['prints']),2);self.assertEqual(s['quantities']['M3x10'],2)
  for r in s['prints']:self.assertEqual(P.sha(P.ROOT/r['path']),r['sha256']);self.assertLess(max(r['size_mm'])+10,256)
 def test_integrity(self):
  q=P.read(P.OUT/'manifest.json');self.assertTrue(P.verify(P.ROOT,q)['integrity_ok']);self.assertFalse(P.verify(P.ROOT,q,True)['integrity_ok'])
if __name__=='__main__':unittest.main()
