from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/cad'))
from feline_component_conflict_alias import extra_case_cuts


class ComponentAlias(unittest.TestCase):
    def test_only_identical_cases_and_named_wire_owner(self):
        choices=[('A',dict(key='A',slot=0)),('B',dict(key='B',slot=0)),
                 ('C',dict(key='C',slot=1)),('P_SYS',dict(key='P',slot=2))]
        idx={r['key']:i for i,(_,r) in enumerate(choices)}
        geometry={k:k for k in idx};bygeometry={k:[i] for k,i in idx.items()}
        cache={'A|P':dict(ok=False,pairs=[dict(part='case',other='wire:P_SYS.1',gap_mm=0,minimum_mm=1.25)])}
        result,proof=extra_case_cuts([['A','P']],cache,choices,idx,bygeometry,geometry,lambda r:[r['slot'],[30,19,9]])
        self.assertEqual(result,{(0,3),(1,3)})
        self.assertEqual(len(proof),1)
        cache['A|P']['pairs'][0]['other']='wire:SomeoneElse.1'
        result,proof=extra_case_cuts([['A','P']],cache,choices,idx,bygeometry,geometry,lambda r:[r['slot'],[30,19,9]])
        self.assertFalse(result)


if __name__=='__main__':unittest.main()
