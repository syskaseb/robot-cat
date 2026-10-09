import math,unittest
import open_prototype_ground_current as G

class CurrentGround(unittest.TestCase):
    def test_current_ends_bends_and_two_grip_lands(self):
        p,r=G.build()
        self.assertEqual(r['end_mm'],p['ports']['G1.1']['point_mm'])
        self.assertEqual(r['ends'],['BAT.minus','G1.1'])
        length=G.B.check_path(r['segments'],r['start_mm'],r['end_mm'],12.4)
        self.assertAlmostEqual(length,r['centreline_mm'])
        for grip in r['grips']:
            self.assertGreaterEqual(math.dist(grip['insulation_axis_from_mm'],grip['insulation_axis_to_mm']),9-1e-7)
        self.assertAlmostEqual(G.B.segment_geometry(r['segments'][-1])[0],3)
        self.assertTrue(r['grips'][1]['grip_is_before_hairpin_not_on_final3mm'])
    def test_nominal_is_not_selected_stock(self):
        _,r=G.build()
        self.assertEqual(r['nominal_fit_blank_mm'],223)
        self.assertLess(r['old150mm_blank_margin_mm'],0)
        self.assertFalse(r['selected'])
        self.assertTrue(r['grip_mounts_and_assembly_access_open'])
    def test_saved_scoped_radius_result_and_source_pins(self):
        r=G.B.read(G.PROOF)
        self.assertEqual(r['status'],'CURRENT_GROUND_RADIUS_CLEAR_NATIVE_GRIPS_AND_SOURCE_BAY_OPEN')
        for key in ('conflicts','outside','errors'):self.assertEqual(r[key],[])
        self.assertFalse(r['stage_completed'])
        for name,value in r['source_sha256'].items():self.assertEqual(G.B.sha(G.T.ROOT/name),value)

if __name__=='__main__':unittest.main()
