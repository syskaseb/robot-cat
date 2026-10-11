import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/cad'))
from package_current_aux_power import ready,joint_coverage,FEEDS,OUT
from release_check import verify

class AuxPowerContractTests(unittest.TestCase):
 def test_ready_rejects_partial_or_failed_native(self):
  q={'status':'SHARED_SUPPORT_ALLOCATION_ONLY_NATIVE_OPEN','contacts':[],'errors':[],'insulation_included':True}
  s={'status':'SOLID_CLEARANCE_ONLY_MOUNTS_OPEN','contacts':[],'errors':[],'reservation_conflicts':[]}
  n={'status':'CURRENT_NATIVE_W1_PREPARED','contacts':[],'errors':[],'exports':[1,2,3],
   'native_parameter_restore':True,'fresh_relocated_reopen':True,'removed_retained_material_mm3':{'Foundation':0}}
  self.assertTrue(ready(q,s,n))
  for i in range(3):
   rows=copy.deepcopy([q,s,n]);rows[i]['status']='PENDING';self.assertFalse(ready(*rows))
   rows=copy.deepcopy([q,s,n]);rows[i]['contacts']=[{'contact':1}];self.assertFalse(ready(*rows))
  n['removed_retained_material_mm3']['Foundation']=.01;self.assertFalse(ready(q,s,n))
 def test_all_current_curves_and_factory_sides(self):
  p=json.loads((OUT/'whole-layout-plan.json').read_text());c=json.loads((OUT/'whole-layout-preflight.json').read_text())
  self.assertTrue(set(FEEDS)<=set(p['routes']));self.assertFalse(c['contacts'] or c['errors'])
  self.assertTrue(all(c['minimum_radii_mm'][n]>=15-1e-5 for n in FEEDS))
  self.assertLessEqual(c['unfused_XA01_blank_mm'],50)
  self.assertTrue(all(v['margin_mm']>=0 for v in c['factory_budgets'].values()))
  self.assertEqual('P_REAR.1',p['F_AUX_input_port'])
 def test_actual_opposed_end_strips_and_sleeve_coverage(self):
  p=json.loads((OUT/'whole-layout-plan.json').read_text());q=joint_coverage(p)
  self.assertEqual(18,q['XA02']['raw_sleeve_mm']);self.assertEqual(20,q['XB11']['raw_sleeve_mm'])
  self.assertTrue(all(min(v['nominal_jacket_coverage_mm'])>=3 for v in q.values()))
  p['routes']['XA02']['parts'][0]['start'][2]+=.5
  with self.assertRaises(AssertionError):joint_coverage(p)
 def test_whole_space_and_native(self):
  rows=[json.loads((OUT/name).read_text()) for name in ('grip-checks.json','whole-layout-solid-checks.json','native-checks.json')]
  self.assertTrue(ready(*rows))
  self.assertTrue(all(max(r['size_mm'])+10<256 and not r['print_ready'] for r in rows[-1]['exports']))
  self.assertFalse(rows[-1]['physical_pass'])
 def test_six_complete_end_pairs_and_stock(self):
  s=json.loads((OUT/'selection.json').read_text())
  self.assertEqual(set(FEEDS),{r['wire'] for r in s['feed_ends']})
  self.assertTrue(all(len(r['ends'])==2 for r in s['feed_ends']))
  self.assertEqual(6,len(s['length_stock_rows']))
  for row in s['length_stock_rows']:
   self.assertGreaterEqual(row['procurement_contribution_mm'],row['nominal_fit_blank_mm'])
   self.assertGreater(row['nominal_fit_blank_mm'],row['guided_mm'])
  self.assertEqual(0,s['new_hardware']['M3']);self.assertEqual(16,s['new_hardware']['T18I_11102370'])
  self.assertEqual(2,s['new_hardware']['SJ4570_reused_matched_pairs'])
  self.assertEqual(14,s['additional_source_prefix']['source_strip_mm'])
  self.assertLessEqual(s['additional_source_prefix']['complete_unfused_blank_mm'],50)
  self.assertEqual('HISTORICAL_BANK_REFERENCE_NOT_CURRENT_FIT_PROOF',s['bank_ownership']['status'])
 def test_manifest_prototype_only(self):
  m=json.loads((OUT/'manifest.json').read_text())
  self.assertTrue(verify(ROOT,m)['integrity_ok']);self.assertFalse(verify(ROOT,m,True)['integrity_ok'])
 def test_fixed_twenty_and_actual_complete_result(self):
  s=json.loads((OUT.parent/'current-phase1-score.json').read_text())
  self.assertEqual(20,s['fixed_total']);self.assertIn('W1',s['confirmed_result_ids'])
  self.assertEqual(s['result_count'],len(set(s['confirmed_result_ids'])))
  self.assertEqual(s['result_percent'],5*s['result_count']);self.assertGreaterEqual(s['result_count'],11)
 def test_exact_retained_input_archive(self):
  from restore_current_aux_inputs import replay
  r=replay(True);self.assertGreater(r['verified'],0);self.assertEqual(0,r['missing'])

if __name__=='__main__':unittest.main()
