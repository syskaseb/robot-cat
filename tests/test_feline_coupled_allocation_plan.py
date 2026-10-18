"""Cheap contract checks; explicitly not a CAD/motion/route acceptance."""
import json
import math
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure'


class CoupledPlan(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=json.loads((OUT/'n01-coupled-allocation-plan.json').read_text())
        cls.ports=json.loads((OUT/'n01-twenty-wago-port-contract.json').read_text())

    def test_all20_and86_cavities_no_duplicates(self):
        refs=[ref for row in self.p['WAGO_station_rows'] for ref in row['refs']]+['P_SYS']
        self.assertEqual(len(refs),20)
        self.assertEqual(len(set(refs)),20)
        self.assertEqual(set(refs),{s['ref'] for s in self.ports['stations']})
        self.assertEqual(sum(len(s['occupied_ports']) for s in self.ports['stations']),86)

    def test_whole_rows_have_unit_bends_and_named_centres(self):
        for row in self.p['WAGO_station_rows']:
            self.assertEqual(len(row['refs']),len(row['centres_X_mm']))
            self.assertEqual(len(row['refs']),len(row['departure_X_signs']))
            self.assertAlmostEqual(sum(x*x for x in row['bend_unit_mm']),1)
            self.assertEqual(row['bend_unit_mm'][0],0)
            self.assertTrue(all(s in (-1,1) for s in row['departure_X_signs']))

    def test_factory_straight_covers_sleeve_before_tip(self):
        j=self.p['FHAC_full_joint']
        self.assertGreaterEqual(j['factory_after_arc_straight_mm'],j['sleeve_before_factory_tip_mm'])
        self.assertEqual(j['sleeve_before_factory_tip_mm']+j['sleeve_after_factory_tip_mm'],j['sleeve_mm'])
        self.assertGreater(j['custom_grip_relative_factory_tip_mm'][0],j['sleeve_after_factory_tip_mm'])
        self.assertEqual(j['custom_grip_relative_factory_tip_mm'][1]-j['custom_grip_relative_factory_tip_mm'][0],9)

    def test_six_factory_nominal_budgets_below_assumed100(self):
        lengths=[]
        for fuse in self.p['FHAC']:
            first=[fuse['both_factory_first_mm']]*2 if 'both_factory_first_mm' in fuse else [
                fuse['upper_factory_first_mm'],fuse['lower_factory_first_mm']]
            for a in first:
                length=a+math.pi*12.4/2+14+3
                self.assertLess(length,100)
                lengths.append(length)
        self.assertEqual(len(lengths),6)
        self.assertTrue(self.p['FHAC_full_joint']['factory100mm_is_unconfirmed_delivery_assumption'])

    def test_not_misrepresented_as_selected_or_full_n01(self):
        self.assertFalse(self.p['selected'])
        self.assertFalse(self.p['N01_complete'])
        self.assertFalse(self.p['physical_pass'])
        self.assertEqual(self.p['routing_capacity_candidate']['status'],'RESERVATIONS_ONLY_NOT_CHECKED')


if __name__=='__main__':unittest.main()
