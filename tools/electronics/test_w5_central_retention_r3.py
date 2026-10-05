"""Bounded construction regression; not a world-fit or strength approval."""
import json
import unittest
import w5_central_retention_layout_r3 as R


class RetentionRecipe(unittest.TestCase):
    def test_bearing_and_body_roles(self):
        spec = R.layout()
        self.assertEqual(spec['bearing_plane_mm'], 109)
        self.assertEqual(spec['body_bands'][1]['x'], 98)
        self.assertEqual(spec['new_screws'], 0)
        names = [n for n, _ in spec['stops']]
        self.assertEqual(len(names), len(set(names)))
        self.assertTrue(all(n.endswith('Stop') for n in names))

    def test_received_straight_roots_and_band_tunnels(self):
        import FreeCAD as A, Part
        family = json.loads((R.N.BASE/'w5-central-bridge-low-arc-r1/received-family.json').read_text(encoding='utf-8'))
        bands, seats, slots, recipes = R.endpoint_geometry(A, Part, family)
        self.assertEqual((len(bands), len(seats), len(slots)), (50, 10, 25))
        tool = Part.makeCompound([Part.makeBox(v[3]-v[0], v[4]-v[1], v[5]-v[2], A.Vector(*v[:3])) for v in slots.values()])
        for row in recipes:
            key = row['key']
            seat = seats[key+'InsulationSeat'].cut(tool)
            self.assertTrue(seat.isValid(), key)
            self.assertGreater(seat.Volume, 0, key)
            self.assertEqual(len(seat.Solids), 1, key)
            if row['angle_deg'] == -90:
                self.assertEqual(row['band_bottom_mm'], 108.2)
                self.assertTrue(row['head_on_top'])
                self.assertEqual(row['raw_seat_local_mm'][1], .2)
                self.assertEqual(row['raw_seat_local_mm'][4], 5.8)
                self.assertIn(key+'UnderBand', slots)
            self.assertEqual(row['straight_mm'], 6)


if __name__ == '__main__':
    unittest.main()
