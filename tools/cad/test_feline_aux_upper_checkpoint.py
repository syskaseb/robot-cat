"""Scoped geometry isn't whole N01 or proof of every selected tool."""
import json,math,unittest
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT


class UpperAUX(unittest.TestCase):
    def test_complete37_static_and36_gate_not_partial(self):
        p=json.loads((OUT/'n01-AUX-upper-escape-joint-plan.json').read_text())
        r=json.loads((OUT/'n01-AUX-upper-escape-joint-received.json').read_text())
        self.assertEqual(r['status'],'WHOLE_AUX_BOARD_THREE_SOURCE_GRIPS_ROOT_STATIC36_RECEIVED_N01_OPEN')
        self.assertEqual(len(p['geometry']),37)
        self.assertEqual(len(r['completed_static']),37)
        self.assertEqual(len(r['completed_motion']),37)
        self.assertFalse(r['failures']);self.assertFalse(r['N01_complete'])
        self.assertEqual(sha(ROOT/p['bundle']),p['bundle_sha256'])
        self.assertEqual(sha(ROOT/r['pair_rows']),r['pair_rows_sha256'])
        self.assertGreater(p['root_carrier_common_mm3'],1)
        self.assertGreater(p['root_host_common_mm3'],1)
        self.assertLess(max(p['whole_fore_support_envelope_mm']),250)

    def test_all_three_full9_then_real_R15_no_second_land(self):
        p=json.loads((OUT/'n01-AUX-upper-escape-joint-plan.json').read_text())
        self.assertEqual(set(p['source_escapes']),{'XA02','XA03','XA04'})
        for e in p['updates'].values():
            self.assertAlmostEqual(math.dist(*e['jacket_grip9_mm']),9.)
            self.assertEqual(e['received_prefix_R_mm'],15.)
            w=e['prefix_geometry_owner'].split(':')[1]
            self.assertEqual(p['source_escapes'][w]['arc']['start'],e['jacket_grip9_mm'][-1])
            self.assertFalse(p['source_escapes'][w]['extra_mandatory_straight_after9'])

    def test_tooling_hold_is_not_hidden_by_geometry_pass(self):
        r=json.loads((OUT/'n01-AUX-upper-key-configurations-received.json').read_text())
        self.assertEqual(r['status'],'AUX_UPPER_NO_COMPLETE_TOOL_CONFIGURATION')
        self.assertTrue(r['failures']);self.assertFalse(r['N01_complete'])
        self.assertNotIn('M2Driver1',r['selected_tool_configurations'])
        self.assertNotIn('M2Driver3',r['selected_tool_configurations'])


if __name__=='__main__':unittest.main()
