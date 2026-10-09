"""Current south-of-ATO common family, not native or physical acceptance."""
import math,unittest
import test_open_prototype_rear_face as Base
import open_prototype_source_south_ato as G

class SouthAto(Base.RearFace):
    @classmethod
    def setUpClass(cls):cls.p=G.build_geometry();cls.old=G.G.T.build()

    def test_south_transfer_keeps_all_four_sources_and_no_metal_rotation_change(self):
        self.assertEqual(self.p['s1_module'],G.B.read(G.Above.PRIOR_PLAN)['family']['s1_module'])
        self.assertEqual(len(self.p['s1_routes']),4)
        self.assertEqual(self.p['rear_level_allocation']['entry_level_mm'],138)
        self.assertAlmostEqual(self.p['rear_level_allocation']['transfer_direction'][1],-.5)
        self.assertFalse(self.p['s1_geometry_changed'])
        w=next(r for r in self.p['s1_routes'] if r['wire']=='W065')
        self.assertGreater(G.B.segment_geometry(w['segments'][-1])[0],2)
        self.assertTrue(w['short_entry_is_not_grip'])

    def test_north_face_slot_labels_match_rotated_nominal_model(self):
        c=next(s for s in self.p['stations'] if s['role']=='P_REAR')
        self.assertEqual(c['rotation'],'180')
        for i in range(1,6):
            d=self.p['ports'][f'P_REAR.{i}'];self.assertEqual(d['rotated_model_cavity_index'],6-i)
            self.assertAlmostEqual(d['point_mm'][1],22.5)
        for wire in ('W044','W052'):
            w=next(r for r in self.p['tails'] if r['wire']==wire)
            self.assertGreaterEqual(G.B.segment_geometry(w['segments'][0])[0],9-1e-7)
            self.assertGreaterEqual(len(w['independent_grip_lands']),2)
            self.assertAlmostEqual(G.B.segment_geometry(w['segments'][-1])[0],3)

if __name__=='__main__':unittest.main()
