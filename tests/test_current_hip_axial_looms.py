import sys,json,math,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/cad'))
from plan_current_hip_axial_looms import s_offset,flex,OUT
from open_prototype_source_group import segment_geometry


class AxialHipGeometry(unittest.TestCase):
    def test_s_offset_is_exact_circular_geometry_not_chord_length(self):
        parts=s_offset([0,0,0],[51,20,0],[1,0,0])
        self.assertEqual(len(parts),2)
        for p in parts:
            length,t0,t1,radius=segment_geometry(p)
            self.assertAlmostEqual(radius,p['radius_mm'],places=7)
            self.assertAlmostEqual(length,p['length_mm'],places=7)
        self.assertLess(math.dist(parts[0]['end'],parts[1]['start']),1e-8)
        self.assertGreater(segment_geometry(parts[0])[1][0],.999999)
        self.assertGreater(segment_geometry(parts[-1])[2][0],.999999)

    def test_four_arcs_keep_slack_length_and_radius(self):
        parts=flex([0,0,0],[102,0,0],[1,0,0],1)
        self.assertIsNotNone(parts)
        self.assertAlmostEqual(sum(p['length_mm'] for p in parts),108,places=7)
        self.assertGreaterEqual(min(p['radius_mm'] for p in parts),31)

    def test_rejected_common_layout_cannot_be_accepted_as_w5(self):
        plan=json.loads((OUT/'hip-axial-loom-plan.json').read_text())
        self.assertEqual(plan['status'],'REJECTED_AXIAL_HIP_SHARED_WIRES')
        self.assertEqual(len(plan['rejected']),6)
        self.assertFalse(plan['selected']);self.assertFalse(plan['native_changed'])
        self.assertFalse(plan['W5_complete']);self.assertFalse(plan['physical_pass'])


if __name__=='__main__':unittest.main()
