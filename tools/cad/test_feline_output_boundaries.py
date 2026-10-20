import unittest
from compose_feline_output_boundaries import current,parents


class OutputBoundaries(unittest.TestCase):
    def test_all_physical_identities_and_internal_none_are_preserved(self):
        base,rows,_=current();_,before,_=parents()
        self.assertEqual(len(rows),246);self.assertEqual(len(base['portions']),123)
        for a,b in zip(before,rows):
            for key in ('id','wire','portion_id','endpoint','group'):self.assertEqual(a[key],b[key])
            if a['point_mm'] is None:self.assertIsNone(b['point_mm'])

    def test_selected_power_leaves_actual_end_bay_cap_not_old_first9(self):
        _,rows,_=current();ends={r['id']:r for r in rows}
        for w in ('W026','W037','W045','W053'):
            e=ends[w+'/custom/start']
            self.assertEqual(e['prefix_geometry_owner'],'EndCustom:'+w)
            self.assertEqual(e['minimum_R_mm'],25.2)
            self.assertAlmostEqual(e['routing_exit_mm'][2],45.26)
            self.assertEqual(e['grip_length_mm'],9)
            self.assertEqual(e['initial_jacket_land_mm'],.25)
            self.assertFalse(e['full_middle_route_accepted'])

    def test_other_four_mta_factory_circuits_do_not_move(self):
        _,rows,_=current();_,before,_=parents();index={r['id']:r for r in rows}
        for r in before:
            if r['portion_id'] in ('W041/factory','W042/factory','W044/factory','W052/factory'):
                self.assertEqual(index[r['id']],r)


if __name__=='__main__':unittest.main()
