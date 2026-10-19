"""Focused geometry/ownership guards, not a whole-layout acceptance."""
import json, math, unittest
from receive_feline_positive_service_deck import usb_edges, pipe, open_grip, reused_internal_pair, intentional_mate
from plan_feline_layout import OUT


class ServiceDeckGeometry(unittest.TestCase):
    def test_intentional_connector_mates_are_symmetric_not_blanket_Pi_exclusion(self):
        self.assertTrue(intentional_mate('PiGPIO:PI.H1','PiBudget:GPIO1992OccupiedHousing'))
        self.assertTrue(intentional_mate('PiBudget:GPIO1992OccupiedHousing','PiGPIO:PI.H1'))
        self.assertFalse(intentional_mate('USB500:whole','PiBudget:Ethernet'))
        self.assertFalse(intentional_mate('PiGPIO:PI.H1','CurrentBUS:BUS_UpperPositiveRoot'))

    def test_new_cables_are_not_omitted_by_common_group_label(self):
        roles={'a':'PiFlexible','b':'PiFlexible','c':'PiRigid','d':'PiRigid'}
        self.assertFalse(reused_internal_pair('a','b',roles))
        self.assertTrue(reused_internal_pair('c','d',roles))
        self.assertFalse(reused_internal_pair('a','c',roles))

    def test_whole_USB_nominal_length_positive_volume_curvature(self):
        c=json.loads((OUT/'n01-common-upper-deck-underpass-usb-plan.json').read_text())['candidate']
        u=json.loads((OUT/'n01-physical-cable-contract.json').read_text())['usb']
        es,k,bus=usb_edges(c,u);s,path=pipe(es,2.5)
        self.assertAlmostEqual(path.Length,452,places=5)
        self.assertAlmostEqual(s.Volume,math.pi*2.5**2*path.Length,delta=.01)
        self.assertTrue(s.isValid());self.assertEqual(len(s.Solids),1)
        self.assertGreaterEqual(k['minimum_radius_mm'],30)
        self.assertAlmostEqual((bus[1]-bus[0]).dot(bus[1]-bus[0]),81,places=7)

    def test_open_pad_and_full_tie_are_real_solids(self):
        g=open_grip([0,0,0],[1,0,0],[0,1,0],4.5)
        self.assertEqual(set(g),{'pad','band','head'})
        for s in g.values():
            self.assertTrue(s.isValid());self.assertEqual(len(s.Solids),1)
            self.assertGreater(s.Volume,0)
        self.assertAlmostEqual(g['pad'].Volume,9*2*5.2)
        self.assertAlmostEqual(g['head'].Volume,5*4.3*5.3)


if __name__=='__main__':unittest.main()
