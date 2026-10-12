import unittest
import plan_u1_external_interfaces as E


class ExternalInterfaceTests(unittest.TestCase):
    def setUp(self):self.p=E.build();self.rows={q['id']:q for q in self.p['wires']}

    def test_every_real_end_has_unique_ownership(self):
        self.assertEqual(len(self.rows),11)
        ends=[q[e]['ref'] for q in self.rows.values() for e in ('a','b')]
        self.assertEqual(len(set(ends)),22)
        self.assertTrue(all(q[e]['world_mm'] is not None for q in self.rows.values() for e in ('a','b')))
        self.assertFalse(self.p['E1_complete'])

    def test_current_numbered_ground_port_not_regulator_return(self):
        self.assertEqual(self.rows['XL09']['b']['ref'],'G_TAIL.4')
        self.assertEqual(self.rows['XL09']['b']['world_mm'],[37.5,-39.75,141.])
        self.assertEqual(self.rows['XL09']['b']['departure'],[1,0,0])

    def test_fine_wire_only_three_fixed_logic_inputs(self):
        fine={n for n,q in self.rows.items() if q.get('AWG')==30}
        self.assertEqual(fine,{'XS11','XS21','XS31'})
        self.assertTrue(all(self.rows[n]['fixed_low_current_logic_only'] for n in fine))
        self.assertEqual(self.rows['XL09']['nominal_area_mm2'],.25)
        self.assertEqual(self.rows['XL09']['sku_candidate'],'LAPP4126002S')
        self.assertTrue(all(self.rows[n]['AWG']==26 for n in ('XL01','XL05','XL06','XL07','XL10')))

    def test_pca_original_artwork_origin_is_normalized(self):
        self.assertEqual(self.rows['XL02']['b']['world_mm'],[-37.095,-3.683,84.32])
        self.assertEqual(self.rows['XS11']['a']['ref'],'PCA.JP2.10')
        self.assertEqual(self.rows['XS31']['a']['ref'],'PCA.JP2.4')


if __name__=='__main__':unittest.main()
