import unittest
import numpy as np
from plan_feline_four_power_feeders import construct


class Feeders(unittest.TestCase):
    def test_two_tiers_keep_end_tangent_and_selected_radius(self):
        cases=[([-108.75,15,45.26],[1,0,0],[-25.125,44.25,45.26],False,4.5),
               ([-133.95,10.2,45.26],[0,1,0],[-25.125,45.25,98],True,4.5),
               ([150,15,45.26],[-1,0,0],[68.625,44.25,45.26],False,16.5),
               ([150,-15,45.26],[-1,0,0],[6.125,57.25,98],True,4.5)]
        for p,d,q,upper,landing in cases:
            rows=construct(p,d,q,upper,landing=landing)
            np.testing.assert_allclose(rows[0]['start'],p,atol=1e-5)
            np.testing.assert_allclose(rows[-1]['end'],q,atol=1e-5)
            for a,b in zip(rows,rows[1:]):np.testing.assert_allclose(a['end'],b['start'],atol=1e-5)
            self.assertTrue(all(r['length_mm']>0 for r in rows))
            self.assertTrue(all(r.get('radius_mm',25.2)>=25.2 for r in rows))
            self.assertAlmostEqual(rows[-1]['length_mm'],landing)


if __name__=='__main__':unittest.main()
