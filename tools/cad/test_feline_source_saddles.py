import unittest
import FreeCAD
from feline_source_saddles import build
from plan_feline_battery_f0_joint import path


class SourceSaddles(unittest.TestCase):
    def test_working_register_has_current_source_and_MTA_not_old_mouths(self):
        import json
        from compose_feline_source_mta_boundaries import current
        from receive_feline_existing_lower_caps import current as old
        from plan_feline_layout import OUT
        base,rows,_=current();_,prior,_=old();index={r['id']:r for r in rows}
        self.assertEqual(len(base['portions']),123)
        self.assertEqual([r['id'] for r in rows],[r['id'] for r in prior])
        self.assertEqual(len(rows),246)
        src=json.loads((OUT/'n01-F0-access-stack.json').read_text())
        self.assertEqual(index['W075/retained0/start']['point_mm'],src['recipes']['W075_factory']['parts'][0]['start'])
        self.assertEqual(index['W041/custom/start']['routing_exit_mm'],[109.49999971389771,83.64999999999999,45.26])
        self.assertTrue(index['W076/retained1/start']['source_restraint_shared_shelf_NOT_accepted'])
        for before,after in zip(prior,rows):
            for k in ('id','wire','portion_id','endpoint','group'):self.assertEqual(before[k],after[k])
            if before['point_mm'] is None:self.assertIsNone(after['point_mm'])

    def test_tie_pad_contact_is_mating_not_foreign_clearance(self):
        from receive_feline_source_restraints import local_limit
        p='SourceGrip:POSTIN:'
        meta={p+'pad':dict(kind='PETG',print_group='upper'),p+'band':dict(kind='T18I',print_group='upper'),p+'head':dict(kind='T18I',print_group='upper')}
        self.assertEqual(local_limit(p+'band',p+'pad',meta,{}, {'POSTIN':{'wire':'factory'}},{}),0.)
        self.assertEqual(local_limit(p+'head',p+'pad',meta,{}, {'POSTIN':{'wire':'factory'}},{}),.2)
        self.assertEqual(local_limit(p+'band','foreign_wire',meta,{}, {'POSTIN':{'wire':'factory'}},{}),1.25)

    def test_full_nine_on_first_R12_arc_no_extra_length(self):
        r=path([0,0,0],[2**-.5,2**-.5,0],[('turn',[-2**-.5,2**-.5,0])],12.4)
        kit,rec=build(r['parts'][0],.3,[0,0,-1],7.)
        self.assertEqual(rec['full_jacket_grip_arclength_mm'],[.3,9.3])
        self.assertEqual(rec['extra_wire_length_mm'],0)
        self.assertAlmostEqual(kit['head'].Volume,5*4.3*5.3,places=5)

    def test_early_vertical_R25_grip_and_whole_head(self):
        r=path([0,0,0],[0,0,-1],[('turn',[-3**.5/2,-.5,0])],25.2)
        kit,rec=build(r['parts'][0],3,[-.5,3**.5/2,0],9)
        self.assertEqual(rec['full_jacket_grip_arclength_mm'],[3,12])
        self.assertEqual(len(kit['pad'].Solids),1)

    def test_reject_invented_grip_beyond_existing_segment(self):
        r=path([0,0,0],[1,0,0],[('line',8)],12.4)
        with self.assertRaises(AssertionError):build(r['parts'][0],0,[0,0,-1],4.5)


if __name__=='__main__':unittest.main()
