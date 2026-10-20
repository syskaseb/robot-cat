import json,unittest
import FreeCAD as A
import Part
from plan_feline_layout import OUT
from receive_feline_rrp_shared_height import load
from feline_source_saddles import segment


class W045PierTests(unittest.TestCase):
    def test_channel_preserves_real_bearings_and_whole_root(self):
        p=json.loads((OUT/'n01-W045-printed-pier-channel.json').read_text())
        self.assertEqual(p['status'],'W045_WHOLE_PRINTED_PORTAL_CHANNEL_STATIC36_RECEIVED')
        self.assertFalse(p['failures']);self.assertFalse(p['N01_complete'])
        self.assertTrue(p['R47_bought_parts_and_mount_datum_unchanged'])
        self.assertTrue(p['original_RL_P_full9_restraint_unchanged'])
        shapes=load(p);self.assertEqual(len(shapes),3)
        self.assertTrue(all(s.isValid() and len(s.Solids)==1 for s in shapes.values()))
        whole=shapes['CurrentFoundation:BankPier:4'].fuse(shapes['CurrentFoundation:ClampSeat:4'])
        self.assertTrue(whole.isValid());self.assertEqual(len(whole.Solids),1)
        joint=p['portal_seat_joint'];self.assertGreater(joint['common_mm3'],300)
        self.assertGreater(joint['removed_corner_mm3'],0)
        for r in joint['actual_bearings'].values():self.assertAlmostEqual(r['before_mm2'],r['after_mm2'])
        edge=segment(p['parts'][0]);self.assertAlmostEqual(edge.Curve.Radius,25.2)
        end=p['updates']['W045/custom/end'];self.assertEqual(end['prefix_geometry_owner'],'W045:PierEscape')
        self.assertLess((A.Vector(*end['routing_exit_mm'])-edge.valueAt(edge.LastParameter)).Length,1e-6)
        self.assertEqual(end['routing_exit_axis'],[-1,0,0])
        self.assertTrue(all(v['original_material_unchanged'] for v in p['kept_original_pier_regions'].values()))


if __name__=='__main__':unittest.main()
