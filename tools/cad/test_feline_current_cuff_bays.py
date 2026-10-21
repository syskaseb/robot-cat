import unittest
from compose_feline_current_cuff_bays import compose,parent,current
from compose_feline_integrated_boundaries import apply_updates


class CurrentCuffBays(unittest.TestCase):
    def test_current36_and_all246_identities(self):
        p=compose();_,old,_=parent();rows=apply_updates(old,p['updates'])
        self.assertEqual(len(rows),246);self.assertEqual(len(p['updates']),36)
        self.assertEqual(len({r['portion_id'] for r in rows}),123)
        self.assertEqual(p['changed_kinematic_seams'],27)
        for a,b in zip(old,rows):
            for k in ('id','wire','portion_id','endpoint','group'):self.assertEqual(a[k],b[k])
            if a['point_mm'] is None:self.assertIsNone(b['point_mm'])
            if a['id'] not in p['updates']:self.assertEqual(a,b)
        self.assertFalse(p['N01_complete']);self.assertFalse(p['physical_pass'])
        _,received,_=current();self.assertEqual(rows,received)


if __name__=='__main__':unittest.main()
