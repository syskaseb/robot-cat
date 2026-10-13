import json,unittest
import FreeCAD as A
import build_complete_source_carriers as B
from support_entry_port import build

class EntryTest(unittest.TestCase):
    def test_shared_two_entry_templates(self):
        ret=json.loads((B.P.OUT/'remaining-retention-current.json').read_text())
        roots=json.loads((B.P.OUT/'remaining-loom-roots-plan.json').read_text())
        lands={p['id']:p for g in roots['groups'] for p in g['lands']}
        count=0
        for group in ret['groups']:
            for port in group['ports']:
                if not port['recipe'].get('construction'):continue
                count+=1;old=build(lands[port['land_id']],port);new=build(lands[port['land_id']],port,6)
                self.assertLess(old['body'].cut(new['body']).Volume,1e-6)
                self.assertLess(old['band'].cut(new['band']).Volume,1e-6)
                self.assertEqual(new['recipe']['jacket_land_mm'],9)
                x,y,z=new['arrival_world_mm'];seed=B.P.box([x-2,y-3,z-2,x+2,y+3,z+2])
                self.assertGreater(seed.distToShape(new['band'])[0],.3)
                self.assertGreater(seed.common(new['body']).Volume,1)
                self.assertEqual(len(new['body'].Solids),1)
                self.assertAlmostEqual((A.Vector(*old['arrival_world_mm'])-A.Vector(*new['arrival_world_mm'])).Length,6)
        self.assertEqual(count,2)

if __name__=='__main__':unittest.main()
