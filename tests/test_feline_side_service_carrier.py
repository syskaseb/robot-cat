import json
import math
from pathlib import Path
import sys
import unittest
import numpy as np
import FreeCAD as A
import Part
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/cad'))
from feline_side_service_carrier import unit,HINGE_Y,HINGE_Z

OUT=Path(__file__).resolve().parents[1]/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure'


class SideCarrier(unittest.TestCase):
    def test_complete_grips_unchanged_R_full_stock_and_self_fit(self):
        stations={s['ref']:s for s in json.loads((OUT/'n01-flat-station-architecture.json').read_text())['stations']}
        outer=Part.Shape();outer.read(str(OUT/'n01-six-source-shared-lanes.outer.brep'))
        for ref,tier in (('D_FL','upper'),('FL_P','upper'),('FL_G','upper'),('G1','upper'),('P_FRONT','lower'),('G_AUX','lower')):
            parts,rows,facts=unit(stations[ref],tier,1,0)
            self.assertTrue(parts['split_common_comb'].isValid());self.assertEqual(len(parts['split_common_comb'].Solids),1)
            self.assertAlmostEqual(parts['head_budget'].Volume,216)
            self.assertGreaterEqual(facts['comb']['common_strap_plane_overlap_mm'],2.5-1e-7)
            self.assertLess(facts['comb']['stock_loop_upper_bound_mm'],100)
            for name,s in parts.items():
                outside=s.cut(outer);self.assertLess(outside.Volume,1e-5,(ref,name,'outside'))
                self.assertGreaterEqual(s.distToShape(outer.Shells[0])[0],3.25-1e-6,(ref,name,'skin'))
            for r in rows:
                length=r['first']+r['after']+r['R']*r['arc_radians_total']
                self.assertAlmostEqual(r['wire_shape'].Volume,math.pi*r['radius']**2*length,places=5)
                self.assertGreaterEqual(r['grip_length'],9)
                for n in ('case','split_common_comb','band_budget','head_budget'):
                    self.assertLess(r['wire_shape'].common(parts[n]).Volume,1e-5,(ref,r['endpoint'],n))
            for i,a in enumerate(rows):
                for b in rows[i+1:]:self.assertGreaterEqual(a['wire_shape'].distToShape(b['wire_shape'])[0],.2-1e-6,(ref,a['endpoint'],b['endpoint']))

    def test_service_corner_bound_not_a_whole_motion_PASS(self):
        minimum=HINGE_Y-math.hypot(HINGE_Y-74.5,30-HINGE_Z)
        self.assertGreater(minimum,67.75+1.25)
        self.assertLessEqual(HINGE_Y+3.3/2+2,96.75)


if __name__=='__main__':unittest.main()
