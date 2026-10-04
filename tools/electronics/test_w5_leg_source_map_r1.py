import copy
import json
import unittest
from w5_leg_source_map_r1 import GRAPH, OUT, electrical_roles, PHYSICAL


class LegSourceMap(unittest.TestCase):
    def test_twelve_looms_keep_all_individual_fuses_and_no_parallel_daisy_chain(self):
        graph = json.loads(GRAPH.read_text(encoding='utf-8'))
        rows = [electrical_roles(graph, leg + str(n)) for leg in PHYSICAL for n in (1, 2, 3)]
        self.assertEqual(len({r[k]['wire'] for r in rows for k in ('D', 'V', 'G')}), 36)
        self.assertEqual(len({r['V']['body_end'] for r in rows}), 12)


    def test_bypassing_one_fuse_is_rejected(self):
        graph = copy.deepcopy(json.loads(GRAPH.read_text(encoding='utf-8')))
        wire = next(w for w in graph['wires'] if 'FL1.V' in (w['a'], w['b']))
        wire['a' if wire['a'] != 'FL1.V' else 'b'] = 'FL_P.2'
        with self.assertRaisesRegex(AssertionError, 'individual fuse'):
            electrical_roles(graph, 'FL1')


    def test_saved_map_preserves_physical_names_but_does_not_claim_routes(self):
        result = json.loads((OUT / 'interface.json').read_text(encoding='utf-8'))
        rows = result['looms']
        self.assertEqual(len(rows), 12)
        self.assertEqual(len({r['pcb'] for r in rows}), 12)
        self.assertTrue(all(r['cad_code'] != r['loom'][:2] for r in rows))
        self.assertTrue(all(r['physical_leg'] == PHYSICAL[r['loom'][:2]] for r in rows))
        self.assertTrue(all(r['connector_datums_provisional'] and not r['route_prepared'] for r in rows))
        self.assertFalse(result['physical_pass'] or result['W5_complete'] or result['motion_qualified'])


if __name__ == '__main__':
    unittest.main()
