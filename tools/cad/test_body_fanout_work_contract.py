import copy,json,unittest
import prepare_body_fanout_work_contract as P

class ContractTest(unittest.TestCase):
    def inputs(self):
        return [json.loads((P.OUT/n).read_text()) for n in ('leg-source-near-member-plan.json','leg-extension-budget-plan.json','remaining-retention-entry.json')]

    def test_current_ends_and_donors_not_double_counted(self):
        family,budget,retention=self.inputs();rows=P.combine(family,budget,retention)
        self.assertEqual(len(rows),36)
        self.assertEqual(len({r['existing_fixed_support'] for r in rows}),4)
        self.assertEqual(sum(r['source_extension_candidate'] is not None for r in rows),12)
        self.assertTrue(all(r['actual_route'] is None and r['receiving_restraint'] is None for r in rows))
        for r in rows:
            hip=next(h for h in family['hips'] if h['loom']==r['loom'])
            self.assertEqual(r['bundle_root_world_mm'],hip['fixed_anchor_world_mm'])
            self.assertEqual(r['bodyward_bundle_tangent'],[-v for v in hip['fixed_tangent_world']])

    def test_stale_guide_or_electrical_role_rejected(self):
        inputs=self.inputs();bad=copy.deepcopy(inputs);bad[1]['rows'][0]['guide_to_body_grip_mm']+=1
        with self.assertRaises(AssertionError):P.combine(*bad)
        bad=copy.deepcopy(inputs);bad[1]['rows'][0]['body_cores'][0]['role']='WRONG.1'
        with self.assertRaises(AssertionError):P.combine(*bad)

    def test_impossible_budget_rejected_before_routing(self):
        inputs=self.inputs();inputs[1]['rows'][0]['remaining_after_guide_mm']=0
        with self.assertRaises(AssertionError):P.combine(*inputs)

if __name__=='__main__':unittest.main()
