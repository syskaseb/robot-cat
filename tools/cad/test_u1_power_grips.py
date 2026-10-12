import unittest
import FreeCAD as A
import Part
import plan_u1_power_grips as P


class PowerGripPlanTests(unittest.TestCase):
    def test_one_group_three_ties_no_extra_fasteners(self):
        p=P.allocation()
        self.assertEqual(p['new_T18R'],2)
        self.assertEqual(p['lacing_blanks_mm'],[150])
        self.assertEqual(p['new_metal_fasteners'],0)
        self.assertEqual(p['MAIN_common_land_mm'],3)
        self.assertEqual((p['USB_land_mm'],p['GTail_land_mm']),(9,9))
        self.assertGreaterEqual(p['MAIN_nut_protrusion_mm'],.4)
        self.assertFalse(p['selected']);self.assertFalse(p['physical_pass'])

    def test_main_bracket_connected_and_metal_clear(self):
        p=P.allocation();rows=[P.material(r) for r in p['pads'] if r['owner']=='MAINGrip']
        s=rows[0].multiFuse(rows[1:])
        for x,y in P.AXES:s=s.cut(Part.makeCylinder(1.2,15,A.Vector(x,y,45)))
        s=s.removeSplitter()
        self.assertTrue(s.isValid());self.assertEqual(len(s.Solids),1)
        self.assertFalse(s.check(True))
        for n,m in P.main_hardware().items():self.assertLess(s.common(m).Volume,1e-5,n)
        for n,m in p['bands'].items():
            if n.startswith('MAIN'):self.assertLess(s.common(m).Volume,1e-5,n)

    def test_original_native_sources_not_modified(self):
        p=P.allocation()
        self.assertEqual({r['owner'] for r in p['pads']},{'MAINGrip','LowerCarrier001','E2Fixture'})
        self.assertEqual(len(p['MAIN_axes_mm']),2)

    def test_gtail_binding_passage_is_not_filled_by_load_path(self):
        p=P.allocation()
        rows=[P.material(r) for r in p['pads'] if r['owner']=='E2Fixture']
        s=rows[0].multiFuse(rows[1:]).removeSplitter()
        self.assertTrue(s.isValid());self.assertEqual(len(s.Solids),1)
        for n in ('GTailBand','GTailHead'):
            self.assertLess(s.common(p['bands'][n]).Volume,1e-5,n)


if __name__=='__main__':unittest.main()
