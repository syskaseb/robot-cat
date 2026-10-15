import unittest
from compose_fixed_body_cut_contribution import blank,material_draw


class FixedBodyCuts(unittest.TestCase):
    def test_project_trim_is_not_hidden_in_strip(self):
        q=blank(100,22)
        self.assertEqual(q['minimum_project_blank_mm'],122)
        self.assertEqual(q['nominal_fit_blank_mm'],145)
        self.assertIsNone(q['actual_cut_mm'])

    def test_factory_limit_cannot_be_relaxed(self):
        self.assertEqual(blank(25,5,0,50)['nominal_fit_blank_mm'],30)
        with self.assertRaises(AssertionError):blank(45,11,0,50)

    def test_shared_factory_cable_is_one_maximum_not_two_lengths(self):
        rows=[dict(wire=n,sku='BUS900 factory',physical_unit='BUS',nominal_fit_blank_mm=l)
              for n,l in [('D',395),('G',390)]]
        units,draw=material_draw(rows)
        self.assertEqual(draw,{'BUS900':395})
        self.assertEqual(len(units),1)


if __name__=='__main__':unittest.main()
