import json,math,unittest
from pathlib import Path
from body_receiver_lands import candidates


class ReceiverLandTests(unittest.TestCase):
    def test_only_existing_straights_with_bounded_terminal_run(self):
        root=Path(__file__).resolve().parents[2]
        file=root/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/body-harness-checkpoint/body-fanout-layout.json'
        plan=json.loads(file.read_text());rows={r['wire']:r for r in plan['rows']}
        for name,route in plan['routes'].items():
            options=candidates(rows[name],route)
            self.assertTrue(options[0]['primary_terminal_land'])
            for land in options:
                part=route['parts'][land['route_part_index']]
                self.assertEqual(part['kind'],'line')
                self.assertAlmostEqual(math.dist(land['start_world_mm'],land['end_world_mm']),9)
                self.assertLessEqual(land['terminal_run_to_grip_centre_mm'],80+1e-6)
                for point in (land['start_world_mm'],land['end_world_mm']):
                    self.assertAlmostEqual(math.dist(part['start'],point)+math.dist(point,part['end']),part['length_mm'])
        self.assertGreater(len(candidates(rows['W024'],plan['routes']['W024'])),1)


if __name__=='__main__':unittest.main()
