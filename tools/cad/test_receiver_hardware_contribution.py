import unittest
from prepare_receiver_hardware_contribution import quantities,thread_fit


class ReceiverHardwareTest(unittest.TestCase):
    def groups(self):
        groups={f'T{i}':dict(kind='triple',wires=[f'{i}/{j}' for j in range(3)]) for i in range(6)}
        groups['RR_G']=dict(kind='triple',retainer='M2_cap',wires=['RR1','RR2','RR3'])
        groups.update({f'S{i}':dict(kind='single',wires=[f'S{i}']) for i in range(15)})
        return groups
    def test_scope_counts_no_double_prints(self):
        q=quantities(self.groups());self.assertEqual(q['T18I_receiver_quantity'],21)
        self.assertEqual(q['replacement_Frame_prints'],4)
        self.assertEqual(q['separate_cap_prints'],7)
    def test_duplicate_conductor_rejected(self):
        g=self.groups();g['S0']['wires']=['S1']
        with self.assertRaises(AssertionError):quantities(g)
    def test_partial_thread_accounts_for_cap_take_up(self):
        for t in (0,.7):self.assertTrue(thread_fit(t)['nominal_engagement_inside_thread'])
        with self.assertRaises(AssertionError):thread_fit(.8)


if __name__=='__main__':unittest.main()
