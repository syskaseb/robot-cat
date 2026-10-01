"""Offline source/assembly-map regression; no actual board or power tests."""
import copy
import unittest
import connection_map_e4_r1 as e4


class ConnectionMap(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.net=e4.build()
        cls.ports=e4.pinouts()

    def test_selected_nominal_map(self):
        r=e4.validate(self.net,self.ports)
        self.assertGreaterEqual(r['tests_passed'],60)
        self.assertEqual(len(r['fuse_cut_removed_drives']),23)
        self.assertTrue(all(r['negative_injections_detected'].values()))

    def test_source_actual_channels_not_connector_order(self):
        self.assertEqual([(x['header'],x['pad'])for x in e4.pca_outputs()],
                         [('JP2','10'),('JP2','7'),('JP2','4')])

    def test_wrong_GPIO_rejected(self):
        bad=copy.deepcopy(self.net)
        next(x for x in bad['edges']if x['id']=='XL07')['a']='PI.H12'
        with self.assertRaisesRegex(AssertionError,'Pi_GPIO_edges_5_exact'):
            e4.validate(bad,self.ports)

    def test_wrong_OE_pin_rejected(self):
        bad=copy.deepcopy(self.ports)
        next(p for p in bad if p['device']=='U1' and p['physical_pin']=='22')['role']='VCCB5V'
        with self.assertRaisesRegex(AssertionError,'U1_enable_and_dual_supply_pinout'):
            e4.validate(self.net,bad)

    def test_fuse_bypass_rejected(self):
        bad=copy.deepcopy(self.net)
        bad['edges'].append(dict(id='SYNTHETIC_bypass',a='F_TY.in',b='F_TY.out',physical_pass=False))
        with self.assertRaisesRegex(AssertionError,'cut_F_TY'):
            e4.validate(bad,self.ports)

    def test_no_factory_second_socket_alias(self):
        self.assertFalse(any('second_socket'in r['a'] or 'second_socket'in r['b'] for r in self.net['edges']))
        self.assertEqual(sum(d['model']=='Waveshare22414 ST3215 12V'for d in self.net['drive_assignments']),12)
        self.assertEqual(sum(d['model']=='TowerProMG92B positional'for d in self.net['drive_assignments']),3)

    def test_no_GTech_pin_guessed(self):
        self.assertTrue(all(x['physical_GTech_cavity']is None for x in self.net['balance_interface']))
        self.assertEqual([x['to']for x in self.net['balance_interface']],
                         ['P309.minus','P309.1S','P309.2S','P309.3S'])

    def test_pins_are_sources_not_measurements(self):
        self.assertTrue(all(not x['physical_pass']for x in self.ports))
        self.assertTrue(all(e4.sha(e4.ROOT/p)==h for p,h in self.net['source_bindings'].items()))


if __name__=='__main__':
    unittest.main()
