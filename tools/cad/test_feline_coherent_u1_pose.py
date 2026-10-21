import json
import unittest
from build_u1_socket_retainer import references
from plan_feline_coherent_u1_pose import clock_full_tie,normal_projection_proposal,translated_static_candidates


class WholeStockClock(unittest.TestCase):
    def test_reused_gap_is_a_bound_not_a_new_measurement(self):
        import FreeCAD as A
        import Part
        actor=Part.makeBox(1,1,1)
        fixed=Part.makeCompound([Part.makeBox(1,1,1,A.Vector(-10,0,0)),Part.makeBox(1,1,1,A.Vector(10,0,0))])
        gap=actor.distToShape(fixed)[0]
        actor.translate(A.Vector(.5,0,0))
        r=translated_static_candidates({'a':actor},{'b':fixed},{'a':dict(kind='PETG')},
            {'a|b':dict(ok=True,gap_mm=gap,minimum_mm=1.25)},.5)
        row=r['reused_measured_pairs']['a|b']
        self.assertAlmostEqual(row['certified_new_lower_bound_mm'],actor.distToShape(fixed)[0])
        self.assertFalse(row['new_measurement'])
        self.assertFalse(r['unresolved_pairs'])

    def test_missing_pair_remains_open_not_a_collision_or_a_pass(self):
        import FreeCAD as A
        import Part
        actor=Part.makeBox(1,1,1)
        fixed=Part.makeCompound([Part.makeBox(1,1,1,A.Vector(-10,0,0)),Part.makeBox(1,1,1,A.Vector(10,0,0))])
        r=translated_static_candidates({'a':actor},{'b':fixed},{'a':dict(kind='PETG')},{},.5)
        self.assertEqual(r['unresolved_pairs'],[['a','b']])
        self.assertEqual(r['status'],'TRANSLATED_STATIC_NEW_PAIRS_OPEN')

    def test_one_whole_unit_interval_keeps_all_measured_margins(self):
        rows={'a':dict(ok=True,gap_mm=3.1485722423,minimum_mm=1.25)}
        r=normal_projection_proposal(1.8001,rows)
        self.assertAlmostEqual(r['translation_norm_mm'],1.7)
        self.assertLessEqual(r['interval_mm'][0],1.7)
        self.assertGreaterEqual(r['interval_mm'][1],1.7)

    def test_empty_interval_requires_layout_change(self):
        rows={'a':dict(ok=True,gap_mm=1.4,minimum_mm=1.25)}
        with self.assertRaises(ValueError):normal_projection_proposal(1.8,rows)

    def test_band_and_full_supplier_head_are_not_shrunk(self):
        refs,facts_path=references();old=refs['TieLeft']
        new,head,proof=clock_full_tie(old,json.loads(facts_path.read_text()))
        self.assertAlmostEqual(new.Volume,old.Volume)
        self.assertAlmostEqual(head.Volume,4.8*4.5*3.5)
        self.assertTrue(proof['unchanged_whole_band'])
        self.assertEqual(proof['degrees'],180)
        self.assertFalse(proof['selected_SKU_changed'])
        self.assertFalse(proof['N01_complete'])
        self.assertGreater(new.BoundBox.XMin,old.BoundBox.XMin)

    def test_different_stock_is_not_silently_retyped(self):
        refs,facts_path=references();facts=json.loads(facts_path.read_text())
        facts['head_height_mm']=2.
        with self.assertRaises(AssertionError):clock_full_tie(refs['TieLeft'],facts)


if __name__=='__main__':unittest.main()
