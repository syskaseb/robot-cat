import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/cad'))
from package_current_head_supply import ready,FEEDS,OUT
from release_check import verify

class CurrentHeadSupplyTests(unittest.TestCase):
 def fixtures(self):
  return [json.loads((OUT/name).read_text()) for name in ('coupled-checks.json','native-checks.json','boundary-checks.json')]
 def test_complete_and_fail_closed(self):
  q,n,b=self.fixtures();self.assertTrue(ready(q,n,b))
  for i in range(3):
   parts=copy.deepcopy([q,n,b]);parts[i]['status']='PENDING';self.assertFalse(ready(*parts))
  n['contacts']=[{'unexpected':True}];self.assertFalse(ready(q,n,b))
 def test_actual_all_six_continuous_boundaries(self):
  q,n,b=self.fixtures();self.assertEqual(set(FEEDS),{r['wire'] for r in b['boundaries']})
  self.assertEqual(12,len(b['boundaries']))
  self.assertTrue(all(r['gap_mm']<1e-5 and r['continuous'] for r in b['boundaries']))
 def test_no_print_or_physical_claim(self):
  q,n,b=self.fixtures();self.assertFalse(n['physical_pass']);self.assertEqual(2,len(n['exports']))
  self.assertTrue(all(max(r['size_mm'])+10<256 and not r['print_ready'] for r in n['exports']))
 def test_delivery_lengths_and_native_restore(self):
  q,n,b=self.fixtures();self.assertTrue(n['native_parameter_restore'] and n['fresh_relocated_reopen'])
  self.assertTrue(all(q['lengths_mm'][r]<=84.5 for r in ('F_HY_out','F_HP_out')))
  self.assertEqual(12,n['T18I_new']);self.assertEqual(1,n['SJ4570_reused_pairs'])
 def test_manifest_integrity_and_no_print_readiness(self):
  manifest=json.loads((OUT/'manifest.json').read_text());result=verify(ROOT,manifest)
  self.assertTrue(result['integrity_ok']);self.assertFalse(verify(ROOT,manifest,True)['integrity_ok'])
 def test_aggregate_stock_not_double_counted(self):
  s=json.loads((OUT/'selection.json').read_text());self.assertEqual(6,len(s['length_stock_rows']))
  self.assertTrue(all(not r['new_joint_at_boundary'] for r in s['feed_ends']))
  self.assertTrue(all(r['procurement_contribution_mm']>=r['conservative_continuous_fit_blank_mm'] for r in s['length_stock_rows']))
  self.assertEqual([20,20],s['new_hardware']['RNF100_3_16_9_raw_mm'])
 def test_no_unnecessary_yaw_replacement(self):
  s=json.loads((OUT/'selection.json').read_text());self.assertEqual(8,len(s['grips']))
  self.assertEqual(8,len({r['name'] for r in s['grips']}));self.assertNotIn('YawFinal',{r['name'] for r in s['grips']})
  self.assertFalse(any('YawCarrier' in name for name in s['replaces_prints']));self.assertEqual(0,s['new_hardware']['M3'])
 def test_fixed_twenty_result_score(self):
  s=json.loads((OUT.parent/'current-phase1-score.json').read_text())
  self.assertEqual(20,s['fixed_total']);self.assertIn('W3',s['confirmed_result_ids'])
  self.assertEqual(s['result_count'],len(set(s['confirmed_result_ids'])))
  self.assertEqual(5*s['result_count'],s['result_percent']);self.assertGreaterEqual(s['result_count'],10)
if __name__=='__main__':unittest.main()
