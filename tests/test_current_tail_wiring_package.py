import json,unittest,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/cad'))
import package_current_tail_wiring as P

class CurrentTailWiring(unittest.TestCase):
 def test_complete_gate(self):
  q=P.read(P.OUT/'release-checks.json');self.assertTrue(P.ready(q))
  bad=dict(q,contacts=[{}]);self.assertFalse(P.ready(bad))
 def test_fixed_score(self):
  s=P.read(P.BASE/'current-phase1-score.json');self.assertEqual(s['fixed_total'],20);self.assertIn('W4',s['confirmed_result_ids']);self.assertEqual(s['result_percent'],5*len(s['confirmed_result_ids']))
 def test_full_factory(self):
  p=P.read(P.OUT/'selection.json');f=p['factory'];self.assertAlmostEqual(f['external_with_JR_approach_mm']+f['exit_mm'],250,places=4);self.assertEqual(f['final_JR_approach_mm'],10);self.assertGreaterEqual(f['minimum_sampled_radius_mm'],21)
 def test_stock_and_ends(self):
  p=P.read(P.OUT/'selection.json');self.assertEqual(len(p['length_stock_rows']),3);self.assertEqual(p['quantities']['T18I_11102370_new'],12)
  for r in p['length_stock_rows']:
   self.assertGreaterEqual(r['nominal_fit_blank_mm'],r['guided_total_mm']+r['strip_lap_allowance_mm']);self.assertLessEqual(r['JR_extension_nominal_blank_mm'],300)
 def test_only_one_print_set(self):
  p=P.read(P.OUT/'selection.json');self.assertEqual(len(p['prints']),4)
  for r in p['prints']:self.assertTrue(r['path'].endswith('_selected_x1.stl'));self.assertLess(max(r['size_mm'])+10,256)
 def test_not_physical_acceptance(self):
  p=P.read(P.OUT/'selection.json');self.assertFalse(p['physical_pass']);self.assertFalse(p['print_ready']);self.assertTrue(p['W4_complete']);self.assertTrue(p['open_outside_W4'])
if __name__=='__main__':unittest.main()
