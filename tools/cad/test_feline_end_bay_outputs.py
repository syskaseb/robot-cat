import unittest
import numpy as np
from receive_feline_end_bay_outputs import build_paths


class EndBayBudgetTests(unittest.TestCase):
    def route(self,x,y,d,centre):
        f=dict(parts=[dict(start=[x,y,-33.99999389648437],end=[x+d*9,y,-34.])])
        return build_paths(f,centre,25.2)

    def test_fore_both_sides_keep_factory_allowances(self):
        for y in (-15,15):
            r=self.route(-57.5,y,-1,-90.75)
            self.assertAlmostEqual(r['factory_required_mm'],36.5)
            np.testing.assert_allclose(r['custom_grip'],[-133.95,y,-8.8],atol=1e-6)
            np.testing.assert_allclose(r['custom_exit'],[-108.75,y,45.26],atol=1e-6)

    def test_rear_both_sides_keep_factory_allowances(self):
        for y in (-15,15):
            r=self.route(82.5,y,1,132)
            self.assertAlmostEqual(r['factory_required_mm'],52.75)
            np.testing.assert_allclose(r['custom_grip'],[175.2,y,-8.8],atol=1e-6)
            np.testing.assert_allclose(r['custom_exit'],[150,y,45.26],atol=1e-6)

    def test_rejects_budget_overrun_before_geometry(self):
        with self.assertRaises(AssertionError):self.route(82.5,15,1,220)


if __name__=='__main__':unittest.main()
