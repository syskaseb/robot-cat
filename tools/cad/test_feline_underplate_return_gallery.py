import unittest
import numpy as np
from receive_feline_underplate_return_gallery import factory_axis,minimum_for,bend


class UnderplateReturn(unittest.TestCase):
    def test_legacy_endpoint_roundoff_not_new_tilted_MTA_axis(self):
        d,error=factory_axis(np.array([-57.5,15,-33.99999389648437]),[-79.24999389648437,14.99999923706055,-34])
        np.testing.assert_array_equal(d,[-1,0,0]);self.assertLess(error,1e-5)
        rows=[];q,t=bend(rows,[0,0,0],d,[0,0,1],12.4)
        np.testing.assert_allclose(t,[0,0,1],atol=1e-8)

    def test_real_wrong_source_axis_is_not_normalized_away(self):
        with self.assertRaises(AssertionError):factory_axis(np.zeros(3),[1,.2,0])

    def test_nylon_classification_does_not_depend_on_alias_name(self):
        stock=dict(kind='project_stock_reservation',material_role='selected_T18I_nylon_budget')
        self.assertEqual(minimum_for('ReturnGrip:Factory:W026:head',stock,'End:test',dict(kind='wire')),.2)
        self.assertEqual(minimum_for('ReturnGrip:Factory:W026:head',stock,'PCB',dict(kind='actual_case')),1.25)


if __name__=='__main__':unittest.main()
