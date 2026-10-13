"""Exact distance over pure solid compounds, with component broad phase.

For a compound containing ONLY solids, distance to another shape is the
minimum over its solids. Component bounds reject only distant candidates.
Boolean volume stays the original whole-shape operation. Mixed compounds
are not decomposed. Legacy exact results remain valid for identical inputs.
"""
import hashlib,json
from pathlib import Path
from exact_pair_receipts import PairReceipts

class ComponentPairReceipts(PairReceipts):
    def __init__(self,path,near):
        legacy=path
        current=path.with_name(path.stem+'-components.json')
        super().__init__(current,near)
        base_revision=self.revision
        self.revision=hashlib.sha256((base_revision+Path(__file__).read_text()).encode()).hexdigest()
        old=json.loads(legacy.read_text()) if legacy.exists() else {}
        new=json.loads(current.read_text()) if current.exists() else {}
        self.records=old.get('records',{}) if old.get('checker_sha256')==base_revision else {}
        if new.get('checker_sha256')==self.revision:self.records.update(new.get('records',{}))
        self.decomposed=0

    def fingerprint(self,s):
        fresh=id(s) not in self.fingerprints
        result=super().fingerprint(s)
        if fresh and s.ShapeType=='Compound':
            children=s.childShapes()
            if len(children)>1 and all(child.ShapeType=='Solid' for child in children):
                self.components[id(s)]=children;self.decomposed+=1
        return result
