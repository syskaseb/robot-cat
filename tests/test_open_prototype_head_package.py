"""Pure package contract checks: no simulator or native rebuild."""
from pathlib import Path
import unittest,json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/cad'))
from release_check import verify
OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/head-mount-checkpoint'
def read(n):return json.loads((OUT/n).read_text(encoding='utf-8'))
class HeadPackage(unittest.TestCase):
 def test_integrity(self):self.assertTrue(verify(ROOT,read('manifest.json'))['integrity_ok'])
 def test_not_print_ready(self):self.assertFalse(verify(ROOT,read('manifest.json'),True)['integrity_ok'])
 def test_inventory(self):
  p=read('selection.json');self.assertEqual(sum(r['quantity'] for r in p['prints']),23)
  self.assertEqual(len(p['prints']),22);self.assertEqual(len(p['internal_hardware_groups']),12)
  self.assertTrue(all(max(r['print_size_mm'])+10<256 for r in p['prints']))
 def test_native(self):
  p=read('head-neck-checks.json');self.assertEqual(p['external_links'],0)
  self.assertTrue(p['all_52_rise_restore'] and p['MAIN_absolute_4_5_4'])
  self.assertEqual(p['head_modeled_identities'],52);self.assertEqual(len(p['neck_hardware']),32)
  self.assertFalse(p['head_washer_changed_interface']['contacts'])
 def test_nominal_only(self):
  p=read('selection.json');self.assertTrue(p['mechanical_M2_complete'])
  self.assertFalse(p['physical_pass'] or p['print_ready'] or p['wiring_complete'] or p['continuous_sweep_qualified'])
 def test_neck_no_old_kit(self):
  p=read('selection.json')['neck_hardware'];self.assertEqual(p['lower_M2x10'],4);self.assertEqual(p['upper_M2x12'],4)
  self.assertNotIn('M2x14',p);self.assertEqual(p['MAIN_board_mount_separate']['M2x12'],2)
  self.assertEqual(p['M2_washers_OD5_ID2p2_t0p3'],16)
if __name__=='__main__':unittest.main()
