import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import FreeCAD as A
import Part
import resume_remaining_support_gate as R
from immutable_bounds import ImmutableBounds

class CheckpointTest(unittest.TestCase):
    def test_cli_change_does_not_invalidate_geometry_but_geometry_change_does(self):
        source=Path(R.G.__file__).read_text()
        self.assertEqual(R.allocation_identity(source),R.LEGACY_GENERATOR)
        self.assertEqual(R.allocation_identity(source+'\n# CLI note\n'),R.LEGACY_GENERATOR)
        changed=source.replace('def allocation(', '# geometry change\ndef allocation(',1)
        self.assertNotEqual(R.allocation_identity(changed),R.LEGACY_GENERATOR)

    def test_pair_results_and_resume_preserve_negative(self):
        with tempfile.TemporaryDirectory() as td,patch.object(R,'CACHE',Path(td)):
            file=Path(td)/'pairs.json';near=ImmutableBounds().near
            a=Part.makeBox(4,4,4);b=Part.makeBox(4,4,4,A.Vector(2,0,0))
            old=R.PAIRS(Path(td)/'old.json',near);expected=old.check(a,b)
            current=R.StreamingPairs(file,near)
            self.assertEqual(expected,current.check(a,b));self.assertGreater(expected[1],0)
            current.save();again=R.StreamingPairs(file,near)
            self.assertEqual(expected,again.check(a,b));self.assertEqual(again.reused,1)
            c=Part.makeBox(4,4,4,A.Vector(3,0,0));again.check(a,c)
            self.assertEqual(again.computed,1)

    def test_cached_allocation_hash_and_parent_invalidation(self):
        calls=[]
        def allocate(paths,retention,roots,parents):
            calls.append(1);return ({'Unit':parents['Parent'].copy()},{'Unit':{'pads':[]}}, {},{},[])
        paths={'groups':[{'id':'Unit','paths':[]}]};ret={'groups':[{'id':'Unit','ports':[]}]}
        roots={'groups':[{'id':'Unit','preserved_owner':'Parent'}]}
        parent={'Parent':Part.makeBox(2,3,4,A.Vector(12,13,14))}
        with tempfile.TemporaryDirectory() as td,patch.object(R,'CACHE',Path(td)),patch.object(R,'ALLOCATE',allocate):
            first=R.cached_allocation(paths,ret,roots,parent)
            second=R.cached_allocation(paths,ret,roots,parent)
            self.assertEqual(len(calls),1)
            self.assertAlmostEqual(first[0]['Unit'].Volume,second[0]['Unit'].Volume)
            self.assertEqual(list(first[0]['Unit'].Solids[0].CenterOfMass),list(second[0]['Unit'].Solids[0].CenterOfMass))
            parent={'Parent':Part.makeBox(2,3,5,A.Vector(12,13,14))}
            R.cached_allocation(paths,ret,roots,parent);self.assertEqual(len(calls),2)
            receipt=next(Path(td).glob('*/manifest.json'));data=json.loads(receipt.read_text())
            shape=receipt.parent/next(iter(data['shapes'].values()))['file']
            shape.write_text('corrupt test fixture')
            # Return to the first parent corresponding to the first receipt.
            original={'Parent':Part.makeBox(2,3,4,A.Vector(12,13,14))}
            matching=original if data['contract']['parent_sha256']==R.fingerprint(original['Parent']) else parent
            with self.assertRaises(AssertionError):R.cached_allocation(paths,ret,roots,matching)

if __name__=='__main__':unittest.main()
