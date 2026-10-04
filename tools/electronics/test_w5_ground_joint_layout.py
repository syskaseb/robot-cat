import json
import unittest
from w5_ground_joint_layout_r1 import ROOT, BLOCKS, ports, attached_ends


class GroundJointLayoutTest(unittest.TestCase):
    def test_balanced_r4_fits_both_received_DATA_strap_limits(self):
        import w5_ground_joint_layout_r4 as new
        self.assertEqual(new.CENTRAL_Y, 5.5)
        self.assertAlmostEqual(new.CENTRAL_Y - 15 - (-11.4), 1.9)
        self.assertAlmostEqual(22.4 - (new.CENTRAL_Y + 15), 1.9)
        self.assertEqual(new.ports()['G2.5']['point_mm'], [120.5, -6.5, 113.5])
        self.assertEqual(new.ports()['G1.5']['point_mm'], [77, 13, 113.5])

    def test_shifted_r3_moves_entire_central_interface_not_just_body(self):
        import w5_ground_joint_layout_r2 as old
        import w5_ground_joint_layout_r3 as new
        for end, row in old.ports().items():
            delta = 8 if end.split('.')[0] in ('G1', 'G2') else 0
            self.assertEqual(new.ports()[end]['point_mm'],
                             [row['point_mm'][0], row['point_mm'][1] + delta, row['point_mm'][2]])
            self.assertEqual(new.ports()[end]['outward_axis'], row['outward_axis'])
        self.assertEqual(new.ports()['G2.5']['point_mm'], [120.5, -4, 113.5])

    def test_side_exit_r2_preserves_height_and_net_inventory(self):
        import w5_ground_joint_layout_r2 as new
        graph = json.loads((ROOT / 'hardware/electronics/power-platform/wiring-p0.json').read_text(encoding='utf-8'))
        old = attached_ends(graph)
        rows = new.attached_ends(graph)
        self.assertEqual([(r['wire'], r['end'], r['other_end']) for r in rows],
                         [(r['wire'], r['end'], r['other_end']) for r in old])
        p = new.ports()
        self.assertEqual(p['G1.3']['point_mm'], [77, 0, 113.5])
        self.assertEqual(p['G2.1']['point_mm'], [120.5, 0, 113.5])
        self.assertEqual(p['G2.4']['point_mm'], [120.5, -6, 113.5])
        self.assertEqual(p['G2.5']['point_mm'], [120.5, -12, 113.5])
        self.assertEqual(p['G1.3']['outward_axis'], [1, 0, 0])
        self.assertEqual(p['G2.1']['outward_axis'], [1, 0, 0])
        for r in rows:
            self.assertEqual(r['point_mm'][2], 113.5)
        for angle in (0, 90, -90, 180):
            v = new.rotate_xy(5, 7, angle)
            self.assertEqual(new.rotate_xy(*v, -angle if abs(angle) == 90 else angle), (5, 7))

    def test_complete_end_inventory(self):
        graph = json.loads((ROOT / 'hardware/electronics/power-platform/wiring-p0.json').read_text(encoding='utf-8'))
        before = json.dumps(graph, sort_keys=True)
        rows = attached_ends(graph)
        self.assertEqual((len(rows), len({r['wire'] for r in rows})), (26, 21))
        self.assertEqual(sum(r['wire'] == 'W061' for r in rows), 2)
        self.assertNotIn('XA06', {r['wire'] for r in rows})
        self.assertEqual(json.dumps(graph, sort_keys=True), before)

    def test_central_grid_received_not_wrong_675(self):
        p = ports()
        self.assertEqual(p['G2.2']['point_mm'], [99, 9.5, 123.5])
        self.assertEqual(p['G2.3']['point_mm'], [105, 9.5, 123.5])
        self.assertEqual(p['G2.4']['point_mm'], [117, 9.5, 123.5])
        self.assertEqual(p['G1.2']['point_mm'], [81, 11, 123.5])

    def test_four_outward_faces_and_no_duplicate_cages(self):
        p = ports()
        for leg in ('FL', 'FR', 'RL', 'RR'):
            key = leg + '_G'
            self.assertEqual(BLOCKS[key]['angle'], 180)
            coords = [p[f'{key}.{i}']['point_mm'] for i in range(1, 6)]
            self.assertEqual(len({tuple(x) for x in coords}), 5)
            self.assertEqual({x[1] for x in coords}, {49.5 if leg.endswith('L') else -49.5})
            self.assertEqual({x[2] for x in coords}, {117.5})
            self.assertTrue(all(p[f'{key}.{i}']['provisional'] for i in range(1, 6)))
            self.assertEqual(p[key + '.1']['outward_axis'], [0, 1 if leg.endswith('L') else -1, 0])


if __name__ == '__main__': unittest.main()
