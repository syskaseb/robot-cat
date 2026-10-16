import copy,json,unittest
from compose_current_body_native import compose,OUT


class CompositionTests(unittest.TestCase):
    def test_four_replacements_do_not_increase_print_count_or_change_frozen_sources(self):
        old=json.loads((OUT/'current-body-source-native-set.json').read_text())
        native=json.loads((OUT/'remaining-frame-saddles-native/manifest.json').read_text())
        frozen=copy.deepcopy(old);rows=compose(old,native)
        self.assertEqual(old,frozen);self.assertEqual(len(rows),13)
        self.assertEqual(len({r['part'] for r in rows}),13)
        self.assertEqual(sum(r.get('remaining_saddle_groups',0) for r in rows),30)


if __name__=='__main__':unittest.main()
