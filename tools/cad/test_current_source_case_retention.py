import json,unittest,zipfile
import FreeCAD as A
import Part
from current_source_case_retention import material
from plan_current_harness_interfaces import OUT


class SourceCaseTests(unittest.TestCase):
    def test_actual_twelve_placed_cases_and_independent_wire_end_bindings(self):
        targets={}
        with zipfile.ZipFile(OUT/'remaining25-space-context.zip') as z:
            for r in json.loads(z.read('index.json'))['entries']:
                if r['kind']!='target':continue
                if not (r['name'].startswith('MTA/') or r['name'].split('/')[0] in {w+'_Joint' for w in ('W026','W037','W041','W042','W044','W045','W052','W053')}):continue
                s=Part.Shape();s.importBrepFromString(z.read(r['file']).decode());targets[r['name']]=s
        allocation=json.loads((OUT/'remaining25-interface-allocation.json').read_text())
        legs=json.loads((OUT/'leg-stations-plan.json').read_text());q=material(targets,allocation,legs)
        self.assertEqual(len(q['parts']),12);self.assertEqual(len(q['bands']),4);self.assertEqual(len(q['adhesive']),8)
        self.assertEqual(q['new_case_lacing_candidate_mm'],600)
        owners={r['id']:r['owner'] for r in q['rows']}
        self.assertEqual(owners['SourceJoint_W037'],'FrontRightFixedCarrier')
        self.assertEqual(owners['SourceJoint_W045'],'RearLeftFixedCarrier')
        self.assertEqual(owners['SourceJoint_W053'],'RearRightFixedCarrier')
        self.assertEqual(sum(v=='UpperCarrier001' for v in owners.values()),9)
        for name,r in q['recipes'].items():
            self.assertLess(q['parts'][name].common(targets[r['own_case']]).Volume,1e-5,name)
            self.assertTrue(q['parts'][name].isValid())


if __name__=='__main__':unittest.main()
