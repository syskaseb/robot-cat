"""Resolve only conservative component hits with the pinned provisional flat profile."""
import json
from pathlib import Path
import head_factory_lead_storage_r1 as B
from head_factory_lead_storage_r2 import centerline_edges
A,Part=B.A,B.Part
P=B.ROOT/'hardware/electronics/full-cat/head-factory-lead-storage-r3'
OUT=B.ROOT/'hardware/electronics/full-cat/head-factory-lead-local-profiles-r1'
def main():
    OUT.mkdir(exist_ok=True);assert not (OUT/'checks.json').exists()
    old=json.loads((P/'checks.json').read_text());edges=centerline_edges();tubes={};rows=[]
    for i in sorted({r['segment'] for r in old['hits']}):
        e=edges[i];start=e.valueAt(e.FirstParameter);t=e.tangentAt(e.FirstParameter)
        if i in (0,1,2):width=A.Vector(-t.y,t.x,0)
        else:width=A.Vector(1,0,0)
        width.normalize();thin=t.cross(width);thin.normalize()
        verts=[start+width*u*1.75+thin*v*.9 for u,v in [(-1,-1),(1,-1),(1,1),(-1,1),(-1,-1)]]
        print(f'Flat component {i}',flush=True)
        s=Part.Wire([e]).makePipeShell([Part.makePolygon(verts)],True,True)
        assert s.isValid() and len(s.Solids)==1 and not s.check(True)
        s.exportBrep(str(OUT/f'FlatLead{i}.brep'));tubes[i]=s
    owners={'Fork':B.J/'ForkJRHolder.brep','Carrier':B.J/'PitchCarrierThroughLeadExit.brep','FrontRight':B.P/'FrontRightWirePassage.brep'}
    for r in old['hits']:
        p=owners[r['owner']];shape=B.load(p)
        if isinstance(r['pose'],dict):shape=B.mv(shape,0,r['pose']['pitch'])
        s=shape.Solids[r['solid']];hit=s.common(tubes[r['segment']]);v=B.R.volume(hit)
        rows.append(dict(**{k:r[k] for k in ('owner','segment','solid','pose')},hit_mm3=v,witness_centers=[list(x.CenterOfMass) for x in hit.Solids] if v>1e-5 else []))
    hits=[r for r in rows if r['hit_mm3']>1e-5]
    result=dict(status='LOCAL_FLAT_PROFILE_COLLISIONS' if hits else 'LOCAL_PROFILE_CLEAR_ONLY',rows=rows,hits=hits,
      parent_checks_sha256=B.R.sha(P/'checks.json'),script_sha256=B.R.sha(Path(__file__)),profile_provisional=True,new_stls=0,physical_pass=False,phase1_complete=False)
    (OUT/'checks.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result),flush=True)
if __name__=='__main__':main()
