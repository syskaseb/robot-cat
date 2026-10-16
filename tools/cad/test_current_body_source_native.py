import unittest
from package_current_body_source_native import compose


class CompositionTests(unittest.TestCase):
    def fixtures(self):
        names = ['FrontLeftFixedCarrier', 'FrontRightFixedCarrier', 'RearLeftFixedCarrier',
                 'RearRightFixedCarrier', 'UpperCarrier'] + ['Cap'+str(i) for i in range(7)]
        prior = dict(status='CURRENT_BODY_RECEIVER_COMPONENT_NATIVE_SET_NOT_W5_SELECTION',
            prints=[dict(identity='CP2:'+n, part=n, path='old/'+n, quantity=1,
                         replaces=None if n.startswith('Cap') else n) for n in names])
        sources = names[:3]+['UpperCarrier001', 'LeftRiser']
        source = dict(status='THIRTEEN_SOURCE_LANDS_FIVE_NATIVE_PARENT_REPLACEMENTS_COMPLETE',
            parts=[dict(part=n, native='new.fcstd', object=n+'Current',
                        original_material_preserved=True, relocated_reopen=True,
                        beam_Z_allowance_restore_mm=[0,.2,0]) for n in sources],
            exports=[dict(part=n, path='new/'+n, quantity=1) for n in sources])
        return prior, source

    def test_replacements_not_extra_frames(self):
        prior, source = self.fixtures()
        rows, replaced = compose(prior, source)
        self.assertEqual((len(rows), len(replaced)), (13, 4))
        self.assertEqual(next(r for r in rows if r['part']=='RearRightFixedCarrier')['path'],
                         'old/RearRightFixedCarrier')
        self.assertEqual(len(prior['prints']), 12)

    def test_unknown_owner_rejected(self):
        prior, source = self.fixtures()
        source['parts'][-1]['part'] = 'Phantom'
        with self.assertRaises(AssertionError): compose(prior, source)

    def test_missing_parameter_trial_rejected(self):
        prior, source = self.fixtures()
        source['parts'][0]['beam_Z_allowance_restore_mm'] = [0,0,0]
        with self.assertRaises(AssertionError): compose(prior, source)


if __name__ == '__main__': unittest.main()
