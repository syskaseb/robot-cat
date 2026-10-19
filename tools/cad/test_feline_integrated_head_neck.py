import math,unittest
from feline_integrated_head_neck import candidates,positive_channel_candidates


class IntegratedNeck(unittest.TestCase):
    def test_actual_diagonal_link_is_not_its_axis_aligned_box(self):
        import FreeCAD as A
        from receive_feline_integrated_head_neck import rectangular_link
        s=rectangular_link([0,0,0],[20,10,4])
        self.assertTrue(s.isValid());self.assertEqual(len(s.Solids),1)
        witness=A.Vector(18,0,0)
        self.assertTrue(s.BoundBox.isInside(witness))
        self.assertFalse(s.isInside(witness,1e-7,True))

    def test_nominal_face_bearing_not_lower_dimensional_solid_common(self):
        import FreeCAD as A
        import Part
        from receive_feline_integrated_head_neck import bearing_area
        a=Part.makeBox(10,12,3);b=Part.makeBox(6,8,2,A.Vector(2,2,3))
        self.assertAlmostEqual(bearing_area(a,b,3),48)
        self.assertAlmostEqual(a.common(b).Volume,0)

    def test_positive_trunk_whole_volume_pitch_and_normal_transition(self):
        rows,bounds=positive_channel_candidates()
        self.assertEqual(len(rows),3);self.assertEqual(len(bounds),6)
        self.assertTrue(all(r['ok'] for r in bounds))
        for row in rows:
            self.assertEqual(row['radius_mm'],1.05)
            self.assertEqual(row['end_mm'][2],103.)
            self.assertGreaterEqual(row['transition_curvature']['minimum_radius_mm'],12.4)
            self.assertEqual(len(row['swept_piece_bounds_mm']),10)
            self.assertAlmostEqual(row['shape'].Volume,row['analytic_expected_volume_mm3'],places=3)

    def test_complete_source_to_body_three_wire_recipe(self):
        rows,bounds=candidates()
        self.assertEqual({r['wire'] for r in rows},{'XB22','XB23','XS23'})
        self.assertEqual(len(bounds),3)
        self.assertTrue(all(b['ok'] and b['gap_lower_bound_mm']>.4 for b in bounds))
        for r in rows:
            self.assertEqual(r['radius_mm'],1.05)
            self.assertGreaterEqual(r['transition_curvature']['minimum_radius_mm'],12.4)
            self.assertEqual(r['minimum_wire_R_mm'],12.4)
            self.assertAlmostEqual(math.dist(*r['source_full9_mm']),9)
            self.assertEqual(r['end_mm'][0],-35.)
            self.assertAlmostEqual(r['end_mm'][2],41.75)
            self.assertTrue(r['shape'].isValid());self.assertEqual(len(r['shape'].Solids),1)
            self.assertAlmostEqual(r['shape'].Volume,math.pi*1.05**2*r['path_length_mm'],places=3)


if __name__=='__main__':unittest.main()
