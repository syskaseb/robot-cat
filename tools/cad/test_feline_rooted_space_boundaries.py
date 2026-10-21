import copy
import json
import unittest
from unittest.mock import patch
import numpy as np
import FreeCAD
from compose_feline_rooted_space_boundaries import compose, current, DEST, parent
from compose_feline_integrated_boundaries import apply_updates


class RootedBoundaries(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = compose()
        cls.base, cls.old, _ = parent()
        cls.rows = apply_updates(cls.old, cls.packet['updates'])
        cls.byid = {r['id']: r for r in cls.rows}

    def test_all_identities_and_internal_contacts_are_preserved(self):
        self.assertEqual(len(self.rows), 246)
        self.assertEqual(len({r['portion_id'] for r in self.rows}), 123)
        for a, b in zip(self.old, self.rows):
            for key in ('id','wire','portion_id','endpoint','group'):
                self.assertEqual(a[key],b[key])
            if a['point_mm'] is None: self.assertIsNone(b['point_mm'])
            if a['id'] not in self.packet['updates']: self.assertEqual(a,b)

    def test_actual_late_world_datums_and_curved_lands(self):
        for eid, q in [
            ('XS11/extra/end',[76.35,77.5201,-23.59]),
            ('XP02.module/extra/end',[88.75,86.25483506235435,41.18]),
            ('XP03.module/extra/end',[88.75,88.89536493764564,41.18]),
            ('XP02.source/extra/start',[96.05057991231608,-94.1168607114588,54.075]),
            ('XA02/extra/end',[151.43,-57.73,73.21]),
        ]:
            self.assertTrue(np.allclose(self.byid[eid]['routing_exit_mm'],q,atol=1e-6),eid)
        for wire in ('XP02.module','XP03.module'):
            self.assertIsNone(self.byid[wire+'/extra/end']['jacket_grip9_mm'])
            self.assertIn('curved_grip_receipt',str(self.byid[wire+'/extra/end']))
        # An E2 source mouth is nine millimetres BEFORE its prefix cap.
        e = self.byid['XP02.source/extra/end']
        self.assertAlmostEqual(e['routing_exit_mm'][0]-e['point_mm'][0],9)
        self.assertEqual(e['source_prefix_length_mm'],9)

    def test_closed_portions_not_duplicated_and_no_whole_n01_claim(self):
        self.assertEqual(len(self.packet['complete_late_portions']),7)
        for pid in self.packet['complete_late_portions']:
            for r in self.rows:
                if r['portion_id']==pid: self.assertTrue(r['whole_portion_received'])
        for wire in ('XP02.source','XP03.source','XP02.module','XP03.module'):
            ee=[r for r in self.rows if r['portion_id']==wire+'/extra']
            need=next(e['whole_factory_required_mm'] for e in ee if 'whole_factory_required_mm' in e)
            self.assertLessEqual(need,220)
        self.assertIsNone(self.byid['XP01/extra/end']['point_mm'])
        self.assertIsNone(self.byid['XP02.source/extra/start']['point_mm'])
        self.assertFalse(self.packet['N01_complete'])
        self.assertFalse(self.packet['physical_pass'])
        self.assertTrue(self.packet['shared_corridor_capacity_NOT_received'])

    def test_identity_mutation_and_stale_source_rejected(self):
        with self.assertRaises(AssertionError):
            apply_updates(self.old,{self.old[0]['id']:{'group':'invented'}})
        if DEST.exists():
            with patch('compose_feline_rooted_space_boundaries.sha',return_value='changed'):
                with self.assertRaises(AssertionError): current()


if __name__=='__main__': unittest.main()
