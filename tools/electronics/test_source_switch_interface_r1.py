"""Small contract checks for the one source-switch prototype interface."""
from pathlib import Path
import json,unittest
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'hardware/electronics/full-cat'
def read(folder):return json.loads((BASE/folder/'checks.json').read_text(encoding='utf-8'))

class SourceSwitchContract(unittest.TestCase):
    def test_mount_and_assembly_same_bolts(self):
        mount=read('source-switch-mount-finish-r4');assembly=read('source-switch-assembly-finish-r3')
        self.assertEqual(mount['deck_bolt_xy'],assembly['deck_bolt_xy'])
        self.assertEqual(mount['deck_bolt_xy'],[[-79.5,92],[-29,92]])
        self.assertFalse(mount['hits']);self.assertFalse(assembly['hits'])
        self.assertFalse(mount['errors']);self.assertFalse(assembly['errors'])
    def test_factory_lead_and_endpoints(self):
        layout=read('source-switch-layout-r6')
        self.assertEqual(layout['lengths']['W076']['nominal_candidate_blank_mm'],80)
        self.assertLessEqual(80,layout['lengths']['W076']['supplied_nominal_limit_mm'])
        self.assertEqual(layout['P_SYS_labels_plus_X'],['.1','.2','.3','.4','.5'])
        self.assertEqual(layout['lengths']['W066']['nominal_candidate_blank_mm'],330)
    def test_stock_and_thread_stacks(self):
        mount=read('source-switch-mount-finish-r4');assembly=read('source-switch-assembly-finish-r3')
        self.assertEqual([r['quantity'] for r in mount['actual_nominal_SKUs']],[2,2,4,2,2])
        self.assertEqual(assembly['added_M2'],dict(screws_M2x12=2,washers_DIN125_M2=4,nuts_DIN934_M2=2))
        self.assertEqual(assembly['extra_T18I'],2)
        self.assertGreater(mount['M10_stack']['thread_projection_mm'],0)
    def test_no_partial_w5_or_physical_pass(self):
        for folder in ('source-switch-layout-r6','source-switch-restraints-r2','source-switch-mount-finish-r4','source-switch-assembly-finish-r3'):
            m=read(folder);self.assertFalse(m['selected']);self.assertFalse(m['W5_complete']);self.assertFalse(m['physical_pass'])

if __name__=='__main__':unittest.main()
