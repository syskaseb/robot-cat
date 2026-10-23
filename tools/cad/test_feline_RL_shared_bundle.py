"""Guard the received departure without awarding an unfinished whole route."""
import json
import unittest
from check_main_p0_placement import ROOT, sha
from plan_feline_layout import OUT
from plan_feline_RL_shared_bundle import construct
import feline_tangent_routes as ft


class SharedDeparture(unittest.TestCase):
    def test_received_scope_and_geometry(self):
        receipt=json.loads((OUT/'n01-RL-W047-companion-prefix-received.json').read_text())
        parts,_=construct(3)
        self.assertEqual(receipt['parts'],parts)
        self.assertEqual(parts[0]['start'],[97.9,24,66.4])
        self.assertGreaterEqual(ft.min_radius(parts),12.4)
        self.assertFalse(receipt['whole_portion_received'])
        self.assertFalse(receipt['N01_complete'])
        self.assertFalse(receipt['physical_pass'])
        self.assertTrue(receipt['W069_geometry_unchanged'])
        self.assertTrue(receipt['own_cap_fused_one_valid_solid'])
        self.assertEqual(receipt['own_cap_common_mm3'],0)
        self.assertTrue(all(row['ok'] for row in receipt['checks'].values()))
        self.assertEqual(sha(ROOT/receipt['bundle']),receipt['bundle_sha256'])
        for path,digest in receipt['source_sha256'].items():
            self.assertEqual(sha(ROOT/path),digest,path)


if __name__=='__main__':unittest.main()
