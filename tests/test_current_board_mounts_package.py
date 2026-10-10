"""Current board mount package contract, no simulation or native rebuild."""
from pathlib import Path
import sys,unittest,json
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/cad'))
from release_check import verify
OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/mounting-checkpoint'
def read(n):return json.loads((OUT/n).read_text())
class BoardMounts(unittest.TestCase):
 def test_integrity(self):self.assertTrue(verify(ROOT,read('current-M5-manifest.json'))['integrity_ok'])
 def test_no_physical_release(self):self.assertFalse(verify(ROOT,read('current-M5-manifest.json'),True)['integrity_ok'])
 def test_kit(self):
  p=read('current-M5-selection.json');self.assertEqual(len(p['print_parts']),8)
  self.assertEqual(sum(r['quantity'] for r in p['print_parts']),20);self.assertEqual(p['fastener_total'],27)
  self.assertNotIn('M3x30',p['quantities'])
  self.assertTrue(all(max(r['bounds_with_5mm_brim_mm'])<256 for r in p['print_parts']))
 def test_changed_interfaces(self):
  p=read('current-M5-checks.json');self.assertFalse(p['contacts'])
  self.assertEqual(len(p['supplier_axis_bearing_checks']),17)
  self.assertTrue(p['fresh_relocated_reopen'] and p['native_U1_hole_parameter_restore'])
 def test_scope(self):
  p=read('current-M5-selection.json');self.assertTrue(p['M5_complete'] and p['selected'])
  self.assertFalse(p['physical_pass'] or p['print_ready'] or p['full_wiring_complete'])
  self.assertTrue(p['delivered_U1_map_required_before_local_print'])
  self.assertIn('Original R31 M5',p['fixed_criterion_basis'])
if __name__=='__main__':unittest.main()
