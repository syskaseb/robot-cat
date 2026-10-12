"""Reuse exact valid BRep pair results; no sampled/mesh clearance shortcut.

Keys include both serialized geometries, radii and this checker revision.
Per-edge bounding boxes only discard provably distant curve components.
"""
import hashlib,json
from pathlib import Path


class PairReceipts:
    def __init__(self,path,near):
        self.path=path;self.near=near;self.revision=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        old=json.loads(path.read_text()) if path.exists() else {}
        self.records=old.get('records',{}) if old.get('checker_sha256')==self.revision else {}
        self.fingerprints={};self.components={};self.shapes={};self.reused=0;self.computed=0

    def fingerprint(self,s):
        key=id(s)
        if key not in self.fingerprints:
            assert s.isValid(),'Invalid pair input'
            self.shapes[key]=s  # Prevent Python id reuse during a long gate.
            self.fingerprints[key]=hashlib.sha256(s.exportBrepToString().encode()).hexdigest()
            self.components[key]=[s] if s.Solids else list(s.Edges) or [s]
        return self.fingerprints[key]

    def check(self,s,t,rs=0,rt=0):
        first=(self.fingerprint(s),rs);second=(self.fingerprint(t),rt)
        key=json.dumps(sorted((first,second)),separators=(',',':'))
        if key in self.records:self.reused+=1;return self.records[key]
        pairs=[(a,b) for a in self.components[id(s)] for b in self.components[id(t)] if self.near(a,b,rs+rt+.001)]
        gap=min((a.distToShape(b)[0] for a,b in pairs),default=rs+rt+1)
        volume=0
        if not rs+rt and gap<=1e-5:
            c=s.common(t)
            assert c.isNull() or c.isValid(),'Invalid pair Boolean'
            if not c.isNull():volume=c.Volume
        result=[gap,volume];self.records[key]=result;self.computed+=1
        return result

    def save(self):
        self.path.write_text(json.dumps(dict(checker_sha256=self.revision,records=self.records),separators=(',',':'))+'\n',encoding='utf-8')
