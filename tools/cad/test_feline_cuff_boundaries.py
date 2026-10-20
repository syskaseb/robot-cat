import unittest
from compose_feline_cuff_boundaries import current
from compose_feline_rooted_rrp_boundaries import current as parent


class CuffBoundaries(unittest.TestCase):
    def test_27_new_outlets_do_not_move_seams_or_create_wires(self):
        base,rows,_=current();_,old,_=parent();changed=[]
        self.assertEqual(len(base['portions']),123);self.assertEqual(len(rows),246)
        for a,b in zip(old,rows):
            for k in ('id','wire','portion_id','endpoint','group','point_mm','departure_axis'):
                self.assertEqual(a.get(k),b.get(k))
            if a!=b:
                changed.append(b);self.assertTrue(b['capacity_cap_is_NOT_physical_wire_termination'])
                self.assertTrue(b['independent_individual_termination_relief_NOT_inferred'])
                self.assertTrue(b['full_flexible_kinematics_NOT_qualified'])
                self.assertGreaterEqual(b['source_capacity_radius_mm'],b['selected_project_radius_mm'])
        self.assertEqual(len(changed),27)
        self.assertEqual({e['group'] for e in changed},{'NineWireCuffFL','NineWireCuffRL','NineWireCuffRR'})


if __name__=='__main__':unittest.main()
