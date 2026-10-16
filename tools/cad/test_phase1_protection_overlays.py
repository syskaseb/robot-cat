import json,unittest
from pathlib import Path
from confirm_phase1_result import validate_score
BASE=Path(__file__).resolve().parents[2]/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype'
def read(n):return json.loads((BASE/n).read_text())
class ProtectionOverlays(unittest.TestCase):
 def test_no_obsolete_E1_prints_or_duplicate_quantities(self):
  k=read('phase1-current-print-selection-r2.json');rows={r['identity']:r for r in k['prints']}
  self.assertEqual((len(rows),sum(r['quantity'] for r in rows.values())),(84,117))
  for n in ('PwmInsulatingWasher','U1TopInsulator','U1InsulatingSpacer'):self.assertNotIn(n,rows)
  self.assertEqual(rows['drive:MG92BPrintedHorn20T-R2']['quantity'],3)
 def test_source_hardware_replaces_not_adds(self):
  q=read('phase1-current-purchased-selection-r4.json');c=q['installed_hardware']
  self.assertEqual((c['M3x45'],c['M3x50 DIN965'],q['drive_count']),(3,1,15))
  self.assertNotIn('M5 current boards:M2x10',{r['id'] for r in q['roles']})
  nuts=next(r for r in q['hardware_products'] if r['size']=='M10 nut');self.assertEqual(nuts['factory_included_credit'],2)
 def test_current_insulation_and_supply(self):
  q=read('phase1-material-selection-r2.json');s={r['sku']:r for r in q['sleeve_stock']}
  self.assertEqual(s['RNF100-3/32-0']['cut_mm'],92);self.assertNotIn('RNF100-3/8-0',s)
  self.assertEqual(len(q['sleeves']),46)
  self.assertEqual(next(r['nominal_fit_blank_mm'] for r in q['wire_blanks'] if r['id']=='W003/factory_BUS_core'),310)
  self.assertEqual(q['factory_units']['SR900']['installed_cables'],17)
 def test_fixed_score_W5_refresh_only(self):
  s=dict(fixed_total=20,confirmed_result_ids=['W5'],result_count=1,result_percent=5)
  self.assertEqual(validate_score(s,'W5',True),['W5'])
  with self.assertRaises(AssertionError):validate_score(dict(fixed_total=20,confirmed_result_ids=[],result_count=0,result_percent=0),'W5')
if __name__=='__main__':unittest.main()
