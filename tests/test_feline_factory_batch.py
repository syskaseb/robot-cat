import json
import sys
import unittest
from pathlib import Path
import numpy as np
from scipy.interpolate import RegularGridInterpolator
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/cad'))
from plan_feline_full_factory_domains import full_profile_points,OUT
from feline_factory_field_domains import evaluate


class FactoryBatch(unittest.TestCase):
    def test_same_current_source_domains_not_relaxed_geometry(self):
        data=json.loads((OUT/'n01-global-full-factory-domains.json').read_text());field=np.load(OUT/'n01-global-current-case-field.npz',allow_pickle=False)
        axes=[field[k] for k in ('x','y','z')]
        interpolators={k:RegularGridInterpolator(axes,field[k+'_distance'],bounds_error=False,fill_value=0) for k in ('material','reservation','motion36','curve_hold','outer')}
        for side in ('in','out'):
            end=next(r for r in data['first_lands'] if r['case_id']==2 and r['side']==side)
            old=next(r for r in data['domains'] if r['case_id']==2 and r['side']==side)
            q=np.array(end['point_mm']);d=np.array(end['departure_axis']);u=np.eye(3)[int(np.argmin(abs(d)))];u-=d*np.dot(u,d);u/=np.linalg.norm(u);v=np.cross(d,u)
            rows,count=evaluate(q,d,u,v,interpolators,full_profile_points)
            self.assertEqual(count,224);self.assertEqual(len(rows),old['numeric_eligible'])
            rows.sort(key=lambda r:(-r[0],r[1]))
            for row,source in zip(rows,old['candidates']):
                margin,first,b,arc,tip=row
                self.assertEqual(first,source['first_mm']);self.assertAlmostEqual(margin,source['numeric_min_surface_margin_mm'],places=10)
                np.testing.assert_allclose(b,source['bend_unit'],atol=1e-12)
                np.testing.assert_allclose(arc,source['factory_arc_end_mm'],atol=1e-12)
                np.testing.assert_allclose(tip,source['factory_tip_mm'],atol=1e-12)

    def test_nonfinite_field_is_not_a_pass(self):
        q=np.zeros(3);d=np.array([1.,0,0]);u=np.array([0.,1,0]);v=np.array([0.,0,1])
        with self.assertRaises(AssertionError):evaluate(q,d,u,v,{'material':lambda p:np.full(len(p),np.nan)},full_profile_points)


if __name__=='__main__':unittest.main()
