"""Exercise resume verification against the actual saved interrupted document."""
import copy
import json
import unittest
import FreeCAD as A
import build_remaining_supports_native as N


class NativeResumeTest(unittest.TestCase):
    def test_saved_features_and_mismatched_recipe(self):
        path=N.P.OUT/'remaining-supports/StationFramesSupported.partial.FCStd'
        gate=json.loads((N.P.OUT/'remaining-support-shared-material.json').read_text())
        d=A.openDocument(str(path))
        count=0
        try:
            for name,recipe in gate['recipes'].items():
                if not name.endswith('FixedCarrier'):continue
                body=d.getObject(recipe['preserved_owner'])
                for cut,rows in ((False,recipe['pads']),(True,recipe['cuts'])):
                    for i,row in enumerate(rows):
                        feature=name+'Loom'+('Cut' if cut else 'Pad')+str(i)
                        if not d.getObject(feature):continue
                        assert N.add_feature(d,body,row,feature,cut) is False
                        changed=copy.deepcopy(row);changed['bounds_mm'][3]+=.1
                        with self.assertRaises(AssertionError):N.add_feature(d,body,changed,feature,cut)
                        count+=1
            self.assertGreater(count,0)
            print('Verified saved feature reuse and mismatch rejection:',count,flush=True)
        finally:A.closeDocument(d.Name)


if __name__=='__main__':unittest.main()
