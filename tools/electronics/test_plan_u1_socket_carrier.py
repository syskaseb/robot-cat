import copy
import unittest
import plan_u1_socket_carrier as U


class SocketCarrierTests(unittest.TestCase):
    def setUp(self):self.p=U.plan()

    def test_whole_circuit_and_24_real_holes(self):
        r=U.check(self.p)
        self.assertEqual((r['chip_pins'],r['signal_resistors'],r['decouplers']),(24,16,2))
        self.assertEqual(r['adapter_long_jumpers'],0)
        self.assertFalse(self.p['selected'])
        self.assertFalse(self.p['E1_complete'])

    def test_all_three_omitted_cuts_would_short_the_series_resistor(self):
        for i in range(3):
            p=copy.deepcopy(self.p);p['copper_cuts'].pop(i)
            with self.assertRaisesRegex(AssertionError,'Source copper short'):U.check(p)

    def test_disconnected_ground_comb_is_rejected(self):
        self.p['links']=[r for r in self.p['links'] if r['ref']!='JG_COMB']
        with self.assertRaisesRegex(AssertionError,'Disconnected'):U.check(self.p)

    def test_chip_orientation_or_supply_swap_rejected(self):
        for t in self.p['terminals']:
            if t['ref']=='U1.1':t['net']='PWM5_SW'
        with self.assertRaises(AssertionError):U.check(self.p)

    def test_one_hole_is_never_two_conductors(self):
        t=copy.deepcopy(self.p['terminals'][0]);t['ref']='DUPLICATE'
        self.p['terminals'].append(t)
        with self.assertRaisesRegex(AssertionError,'Two ends one hole'):U.check(self.p)

    def test_current_values_not_dropped_for_packing(self):
        self.p['parts']=[r for r in self.p['parts'] if r['ref']!='R14']
        with self.assertRaises(AssertionError):U.check(self.p)

    def test_relabeling_series_components_does_not_hide_swapped_channels(self):
        a=next(c for c in self.p['parts'] if c['ref']=='R1')
        b=next(c for c in self.p['parts'] if c['ref']=='R2')
        a['ends'],b['ends']=b['ends'],a['ends']
        with self.assertRaises(AssertionError):U.check(self.p)

    def test_cut_does_not_enter_neighboring_pad_annuli(self):
        self.p['copper_cuts'][0]['along_trace_y_mm']=.8
        with self.assertRaises(AssertionError):U.check(self.p)

    def test_output_ports_preserve_actual_head_and_tail_wire_holes(self):
        terms={t['ref']:t for t in self.p['terminals']}
        for i in range(1,4):
            output=terms[f'B{i}.out'];resistor=terms[f'R{i}.2']
            self.assertEqual(output['y'],13.97)
            self.assertEqual(resistor['y'],11.43)
            self.assertEqual(output['x'],resistor['x'])
            self.assertEqual(output['net'],resistor['net'])
        U.check(self.p)


if __name__=='__main__':unittest.main()
