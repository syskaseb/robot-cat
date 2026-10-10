"""Current E2 only; fullW5/E3/physical release deliberately not inferred."""
from pathlib import Path
import sys,unittest,copy
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/cad'))
from package_current_pwm_branch import OUT,read,ready
from release_check import verify

class PWMBranch(unittest.TestCase):
 def test_integrity(self):self.assertTrue(verify(ROOT,read(OUT/'manifest.json'))['integrity_ok'])
 def test_not_print_release(self):self.assertFalse(verify(ROOT,read(OUT/'manifest.json'),True)['integrity_ok'])
 def test_complete_current_only(self):
  p=read(OUT/'selection.json');self.assertTrue(p['selected'] and p['E2_complete']);self.assertFalse(p['physical_pass'] or p['print_ready'] or p['full_phase1_complete'])
  self.assertEqual(p['P_REAR_centre_mm'],[18,0,138]);self.assertEqual(p['quantities']['T18I_11102370'],10)
  self.assertEqual(p['fuse']['XP01_nominal_fit_blank_mm'],34);self.assertLessEqual(p['fuse']['conservative_unfused_mm'],50)
 def test_lengths(self):
  p=read(OUT/'selection.json');self.assertTrue(all(b['margin_mm']>=0 and b['minimum_factory_mm']==220 for b in p['budgets'].values()))
  self.assertEqual(p['quantities']['Molex2147632113'],1);self.assertEqual(p['quantities']['Molex2147631113'],1)
 def test_fail_closed(self):
  q=read(OUT/'complete-checks.json');self.assertTrue(ready(q));bad=copy.deepcopy(q);bad['contacts']=[{'a':'synthetic'}];self.assertFalse(ready(bad))
 def test_all_failed_gates_preserved(self):
  self.assertEqual(len(read(OUT/'final-checks.json')['contacts']),5);self.assertEqual(len(read(OUT/'current-checks.json')['contacts']),3)
  self.assertFalse(read(OUT/'received-checks.json')['contacts']);self.assertFalse(read(OUT/'complete-checks.json')['contacts'])
if __name__=='__main__':unittest.main()
