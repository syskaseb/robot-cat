"""Support material gate: exact overlap for solids; exact wire clearance.

The caller in build_remaining_loom_supports consumes ONLY volume for zero
radii. Do not invent a distance: that field is None for Boolean-only results.
Legacy numeric distances remain valid. Not a general distance-check API.
"""
import hashlib,json
from pathlib import Path
from component_pair_receipts import ComponentPairReceipts

class MaterialPairReceipts(ComponentPairReceipts):
    def __init__(self,path,near):
        super().__init__(path,near)
        self.path=path.with_name(path.stem+'-material.json')
        self.revision=hashlib.sha256((self.revision+Path(__file__).read_text()).encode()).hexdigest()
        old=json.loads(self.path.read_text()) if self.path.exists() else {}
        if old.get('checker_sha256')==self.revision:self.records.update(old.get('records',{}))

    def check(self,s,t,rs=0,rt=0):
        if rs or rt or not s.Solids or not t.Solids:return super().check(s,t,rs,rt)
        key=json.dumps(sorted(((self.fingerprint(s),rs),(self.fingerprint(t),rt))),separators=(',',':'))
        if key in self.records:self.reused+=1;return self.records[key]
        # OCC may add internal flags to Boolean operands; keep cached inputs
        # immutable so their serialized identities survive save/reload.
        common=s.copy().common(t.copy())
        assert common.isNull() or common.isValid(),'Invalid material Boolean'
        result=[None,0 if common.isNull() else common.Volume]
        self.records[key]=result;self.computed+=1
        return result
