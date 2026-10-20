import hashlib,json,unittest,zipfile
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from receive_feline_rrp_shared_height import load
from receive_feline_rrp_root import construct


def take(filename,field,names,prefix=''):
    doc=json.loads((OUT/filename).read_text());arc=ROOT/doc['bundle']
    assert sha(arc)==doc['bundle_sha256'];result={}
    with zipfile.ZipFile(arc) as z:
        for r in doc[field]:
            if r['name'] not in names:continue
            raw=z.read(r['entry']);assert hashlib.sha256(raw).hexdigest()==r['sha256']
            s=Part.Shape();s.importBrepFromString(raw.decode());result[prefix+r['name']]=s
    assert len(result)==len(names)
    return result


class RRRoot(unittest.TestCase):
    def test_root_and_case_backer_reach_actual_bed_without_changing_holders(self):
        r=json.loads((OUT/'n01-RRP-shared-height.json').read_text());parts=load(r)
        parts.update(take('n01-full-material-scene.json','parts',{'Ref_Material_F_L3_CP2_Housing_0_0','Ref_Material_F_L4_CP2_Housing_0_0'}))
        parts.update(take('n01-shared54-current.json','parts',{'Station:RR_P:case'}))
        parts.update(take('n01-channelled-foundation-static.json','geometry',{'BankBedCurrent:1'},'CurrentFoundation:'))
        root,recipe=construct(parts,r)
        self.assertEqual(len(root.Solids),1);self.assertTrue(root.isValid())
        self.assertGreater(recipe['grip_positive_union_mm3'],1)
        self.assertGreater(recipe['bank_bed_positive_union_mm3'],10)
        self.assertAlmostEqual(recipe['column_axis_mm'][0],13.)
        self.assertAlmostEqual(recipe['column_axis_mm'][1],60.5)
        self.assertLess(max(recipe['combined_envelope_mm']),250)

    def test_current_boundaries_have_received_root_not_physical_strength_claim(self):
        from compose_feline_rooted_rrp_boundaries import current
        _,rows,_=current()
        rr=[e for e in rows if e.get('prefix_geometry_owner','').startswith('EarlyRR:')]
        self.assertEqual(len(rr),4)
        for e in rr:
            self.assertFalse(e['support_load_path_OPEN'])
            self.assertTrue(e['constructive_RRP_assembly_received'])
            self.assertTrue(e['native_manufacture_and_force_NOT_physically_qualified'])
            self.assertTrue(e['own_mating_continuous_access_gate_OPEN'])


if __name__=='__main__':unittest.main()
