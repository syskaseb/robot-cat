import hashlib,json,unittest,zipfile
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from plan_feline_rr_two_tier_ground_bay import construct,clone


def load(packet):
    assert sha(ROOT/packet['bundle'])==packet['bundle_sha256'];shapes={}
    with zipfile.ZipFile(ROOT/packet['bundle']) as z:
        for r in packet['geometry']:
            raw=z.read(r['entry']);assert hashlib.sha256(raw).hexdigest()==r['sha256']
            s=Part.Shape();s.importBrepFromString(raw.decode());shapes[r['name']]=s
    return shapes


class RRTwoTier(unittest.TestCase):
    def test_all33_rebuild_from_original_receiver_not_rejected_S_builder(self):
        p=json.loads((OUT/'n01-RR33-two-tier-ground-space.json').read_text());shapes=load(p)
        flat=json.loads((ROOT/p['input_flat_receipt']).read_text());base=load(flat)
        source={n:base[n] for n in (*flat['plan']['recipes'],'RRFlatGuide','RRFlatBand','RRFlatHead')}
        resources={r['resource']:base[r['resource']] for r in flat['plan']['recipes'].values()}
        old={n:shapes['OriginalReceiver:'+n] for n in p['plan']['original_receiver_names']}
        inputs={**source,**resources,**old};before={n:s.exportBrepToString() for n,s in inputs.items()}
        a,plan=construct(source,resources,flat['plan'],old,p['plan']['receiver'])
        self.assertEqual(len(a),33);self.assertEqual(before,{n:s.exportBrepToString() for n,s in inputs.items()})
        for n,s in a.items():
            self.assertTrue(s.isValid());self.assertGreater(len(s.Solids),0)
            self.assertEqual(len(s.Solids),len(shapes[n].Solids))
            self.assertAlmostEqual(s.Volume,shapes[n].Volume,places=5)
            self.assertAlmostEqual(clone(s).common(clone(shapes[n])).Volume,shapes[n].Volume,places=5)
        for row in plan['source_recipes'].values():self.assertEqual(row['parts'][0]['length_mm'],9)
        self.assertEqual(set(p['complete_body_portions']),{'W072/body','W073/body','W074/body'})
        for r in p['complete_body_portions'].values():self.assertAlmostEqual(r['length_mm'],42.375)
        for r in p['positive_print_graph']:self.assertGreater(r['common_mm3'],0)
        printed=clone(a['RRGJointRoot']).multiFuse([clone(a['Station:RR_G:split_common_comb']),clone(shapes['InputParent:PowerMount:Trunk:PETG'])])
        self.assertTrue(printed.isValid());self.assertEqual(len(printed.Solids),1)
        for values in p['print_envelopes_mm'].values():self.assertLess(max(values),250)
        self.assertAlmostEqual(p['case_adhesive_contact_area_mm2'],390)
        self.assertTrue(all(r['ok'] for r in p['checks'].values()));self.assertTrue(all(r['ok'] for r in p['outer'].values()))
        self.assertFalse(p['N01_complete']);self.assertFalse(p['physical_pass']);self.assertFalse(p['native_changed'])
        self.assertTrue(p['full_moving900_and_head_tail_motion_NOT_received'])


if __name__=='__main__':unittest.main()
