"""Actual source datums and provenance guards, not whole N01 acceptance."""
import json
import math
import unittest
from pathlib import Path

OUT=Path(__file__).resolve().parents[2]/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure'


class ActiveDatums(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=json.loads((OUT/'n01-active-Pi-BUS-datums.json').read_text())

    def test_board_thickness_uses_parallel_source_faces_not_group_centre(self):
        for b in self.p['boards']:
            a,c=b['large_plane_faces']
            n=a['normal']
            delta=[y-x for x,y in zip(a['centre_mm'],c['centre_mm'])]
            self.assertAlmostEqual(abs(sum(x*y for x,y in zip(n,delta))),1.6,places=5)
            self.assertAlmostEqual(sum(x*y for x,y in zip(n,c['normal'])),-1,places=6)
        bus=self.p['boards'][1]
        x=sum(face['centre_mm'][0] for face in bus['large_plane_faces'])/2
        self.assertAlmostEqual(x,130.5,places=5)
        self.assertGreater(abs(x-126),4)

    def test_pi_mounting_axes_are_four_actual_cylinders(self):
        holes=self.p['boards'][0]['cylindrical_surfaces']
        self.assertEqual(len(holes),4)
        n=self.p['boards'][0]['large_plane_faces'][0]['normal']
        for h in holes:
            self.assertAlmostEqual(h['radius_mm'],1.375)
            self.assertAlmostEqual(abs(sum(a*b for a,b in zip(n,h['axis']))),1)

    def test_eleven_unique_jacket_mouths_have_unit_departure_axes(self):
        mouths=self.p['occupied_jacket_mouths']
        self.assertEqual(len(mouths),11)
        self.assertEqual(len({tuple(m['point_mm']) for m in mouths}),11)
        for m in mouths:self.assertAlmostEqual(math.dist(m['departure_axis'],[0,0,0]),1)

    def test_pi_budgets_remain_reservations_and_USB_assumptions_unchanged(self):
        rows=[r for r in self.p['Pi_BUS_parts'] if r['name'].startswith('PiBudget:')]
        contract=json.loads((OUT/'n01-pi-full-port-contract.json').read_text())
        self.assertEqual(len(rows),len(contract['parts'])+len(contract['additional_reservations'])+1)
        self.assertTrue(all(r['kind']=='reservation' for r in rows))
        cable=self.p['USB_project_contract']
        self.assertEqual((cable['catalogue_total_mm'],cable['project_external_target_mm'],cable['project_OD_mm'],cable['minimum_fixed_project_R_mm']),(500,452,5,30))
        self.assertTrue(cable['external452_mm_is_project_mould_allowance_not_supplier_guarantee'])
        self.assertFalse(self.p['selected']);self.assertFalse(self.p['N01_complete'])
        self.assertEqual((self.p['shared_portions'],self.p['shared_ends']),(123,246))

    def test_local_USB_layer_has_two_mm_window_not_whole_volume_approval(self):
        c=self.p['necessary_local_layer_constraints']
        self.assertEqual(c['USB_axis_Z_interval_mm'],[86.75,88.75])
        for a,b in zip(c['necessary_inverted_Pi_PCB_Z_interval_mm'],[92.05,94.05]):self.assertAlmostEqual(a,b)
        self.assertTrue(c['NOT_globally_free_volume']);self.assertTrue(c['no_new_pose_chosen'])
        self.assertIn('MAIN whole stack',c['unresolved_exclusions'])


if __name__=='__main__':unittest.main()
