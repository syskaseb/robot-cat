"""Whole numerical gate and unchanged-SKU geometry, not robot clearance."""
import math,unittest
import FreeCAD as A
import Part
from test_feline_coupled_rear_power import fixture
from plan_feline_central_power_pod import plan,bodies


class CentralPod(unittest.TestCase):
    def test_both_short_feeds_and_all_four_factory_units_before_geometry(self):
        _,ends=fixture();p=plan(ends)
        self.assertEqual(set(p['feeds']),{'XA01','XP01'})
        self.assertAlmostEqual(p['feeds']['XA01']['total_nominal_unfused_mm'],46.48893722612836)
        self.assertAlmostEqual(p['feeds']['XP01']['total_nominal_unfused_mm'],39.69601685880785)
        self.assertTrue(p['feeds']['XA01']['internal_allowance_NOT_manufacturer_guarantee'])
        self.assertTrue(p['feeds']['XA01']['internal_must_be_measured_before_energizing'])
        self.assertEqual(len(p['routes']),4)
        for r in p['routes'].values():
            self.assertGreaterEqual(r['margin_mm'],0.)
            self.assertTrue(all(v.get('radius_mm',math.inf)>=12.4 for v in r['parts']))
        self.assertFalse(p['selected']);self.assertFalse(p['N01_complete'])

    def test_portal_outside_printed_battery_plate_and_existing_straps(self):
        _,ends=fixture();p=plan(ends);ys=p['portal']['shaft_Y_mm']
        self.assertGreater(min(ys)-.925-26.7,1.25)
        self.assertGreater(min(ys)-.925-27.25,.2)
        self.assertGreater(ys[1]-ys[0]-2*.925,.2)
        self.assertTrue(p['portal']['battery_straps_bolt_bearings_and_frame_connectivity_NOT_yet_received'])

    def test_all_bought_cases_retained_and_full_E2_heads_close_below(self):
        fixed,ends=fixture()
        fixed['Ref_Material_F_AUX_candidate_case_0_0']=Part.makeBox(22,51,20.25,A.Vector(132,-25.5,-25.125))
        p=plan(ends);actors,metadata,groups,mates,retired=bodies(fixed,ends,p)
        self.assertEqual(len(actors),19)
        for new,old in [('CentralPod:P_REAR:case','Station:P_REAR:case'),
            ('CentralPod:F_PWM:case','Station:F_PWM_whole:F_PWM:case'),
            ('CentralPod:F_AUX:case','Ref_Material_F_AUX_candidate_case_0_0')]:
            self.assertAlmostEqual(actors[new].Volume,fixed[old].Volume)
        self.assertAlmostEqual(actors['JPWMSource:XP02.source'].BoundBox.XMax,103.77)
        self.assertAlmostEqual(actors['JPWMSource:XP02.module'].BoundBox.XMin,55.17)
        self.assertLess(actors['JPWMGrip:module:head'].BoundBox.ZMax,90.)
        self.assertEqual(len(mates),7)


if __name__=='__main__':unittest.main()
