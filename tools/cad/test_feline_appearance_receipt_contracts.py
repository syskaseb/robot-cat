"""Regression contracts for this changed extension package, no simulator/CAD."""
import json,unittest
from pathlib import Path

OUT=Path(__file__).resolve().parents[2]/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure'
def read(name):return json.loads((OUT/name).read_text())


class ReceiptContracts(unittest.TestCase):
    def test_baseline_is_not_extension_completion(self):
        r=read('appearance-checkpoint.json')
        self.assertEqual((r['baseline']['result_count'],r['baseline']['fixed_total']),(20,20))
        self.assertFalse(r['stage_completed']);self.assertFalse(r['new_extension']['complete'])
        self.assertFalse(r['new_extension']['percentage_awarded']);self.assertFalse(r['physical_pass'])

    def test_required_land_failure_cannot_be_hidden_by_bend_search(self):
        r=read('receiver-straight-land-gate.json')
        self.assertEqual(r['required_straight_mm'],9);self.assertEqual(len(r['checks']),8)
        self.assertEqual({b['wire'] for b in r['invariant_blockers']},{'W044/custom/start','W052/custom/start'})
        self.assertFalse(r['bend_solver_run']);self.assertTrue(r['full_native_feet_used'])

    def test_closed_STL_is_not_thickness_approval(self):
        r=read('appearance-checkpoint.json');old=read('skin-base-wall-thickness.json');derived=read('skin-end-correction.json')
        self.assertFalse(r['exports']['print_ready']);self.assertEqual(old['exact_lateral_surface_minimum_mm'],0)
        self.assertLess(derived['base_lateral_minimum_mm'],1);self.assertEqual(len(derived['contacts']),4)
        self.assertEqual(derived['leg_poses'],[])

    def test_end_ledger_and_printed_anchor_classification(self):
        e=read('endpoint-current-receivers.json');axes=read('current-mount-axis-inventory.json')
        self.assertEqual(e['logical_nets'],80);self.assertEqual(e['endpoint_records'],178)
        self.assertEqual(len({r['id'] for r in e['endpoints']}),178);self.assertFalse(e['full80net_paths_complete'])
        self.assertEqual(axes['actual_saved_axis_count'],19)
        u=next(g for g in axes['groups'] if g['role']=='PWM1608_U1');self.assertEqual(u['count'],2)
        self.assertTrue(all('Anchor' not in r['object'] for r in u['references']))

    def test_failed_native_constructions_are_not_selected(self):
        for f in ('grounded-spine-plan.json','grounded-spine-integrated-plan.json','true-normal-wall-study.json'):
            r=read(f);self.assertFalse(r['native_built']);self.assertFalse(r['selected']);self.assertFalse(r['physical_pass'])


if __name__=='__main__':unittest.main()
