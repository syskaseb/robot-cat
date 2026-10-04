"""Receive one complete six-lead candidate against the selected R53 census.

Only the old P_SYS body and its two actually replaced wire geometries leave
the candidate census. Old supports remain obstacles until redesigned; no
Deck/P0 or populated-bank omission. Save geometry before expensive checks.
"""
from datetime import datetime,timezone
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/electronics')]
from servo_fuse_inputs_r1 import save,sha
OUT=ROOT/'hardware/electronics/full-cat/w5-s1-source-check-r3'
INTENT=ROOT/'hardware/electronics/full-cat/w5-s1-source-layout-r3/intent.json'

def main():
    import FreeCAD as A
    import Part
    from w5_r53_owners import installed
    start=datetime.now(timezone.utc);assert not (OUT/'checks.json').exists()
    OUT.mkdir(parents=True,exist_ok=True)
    intent=json.loads(INTENT.read_text(encoding='utf-8'))
    assert len(intent['routes'])==6 and not intent['selected']
    assert all(sha(ROOT/k)==v for k,v in intent['source_sha256'].items())
    owners,pins,omitted=installed(A,Part)
    replaced=[]
    for key in list(owners):
        if key.startswith('source-switch-layout-r6/W066_') or key.startswith('R49/W043_'):
            replaced.append(key);owners.pop(key)
    assert len(replaced)==12
    body=owners.pop('P_SYS_design').copy();body.translate(A.Vector(*intent['P_SYS_displacement_mm']))
    changed={'P_SYS_candidate':body};geometries=[];paths=[]
    def box(b):return Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
    owners['S1_body_provisional']=box([111,49,66,135,91,103])
    for row in intent['routes']:
        if row['wire'] not in ('W064','W065','W067','W068'):continue
        e=row['end'];left=e[0] if row['wire'] in ('W064','W067') else e[0]-27.686
        changed[row['b']+'_ring_provisional']=box([left,e[1]-9.525/2,56,left+27.686,e[1]+9.525/2,68])
    for row in intent['routes']:
        pieces=[];edges=[]
        for e in row['edges']:
            edge=Part.makeLine(A.Vector(*e['start']),A.Vector(*e['end'])) if e['kind']=='line' else Part.Arc(A.Vector(*e['start']),A.Vector(*e['mid']),A.Vector(*e['end'])).toShape()
            profile=Part.Wire([Part.makeCircle(row['OD_mm']/2,edge.valueAt(edge.FirstParameter),edge.tangentAt(edge.FirstParameter))])
            s=Part.Wire([edge]).makePipeShell([profile],True,False)
            assert s.isValid() and len(s.Solids)==1;pieces.append(s);edges.append(edge)
        path=Part.Wire(edges);assert abs(path.Length-row['exposed_path_mm'])<1e-6
        paths.append(path);geometries.append(Part.makeCompound(pieces))
    files=[]
    for name,objects in [('SOURCE_ROUTES_WORLD.brep',geometries),('CENTERLINES_WORLD.brep',paths),('CHANGED_BODIES_WORLD.brep',list(changed.values()))]:
        q=OUT/name;Part.makeCompound(objects).exportBrep(str(q));files.append(q)
    print('SIX_SOURCE_GEOMETRY_SAVED',flush=True)
    hits=[];errors=[];pairs=0
    def check(label,s,key,t):
        nonlocal pairs
        if not s.BoundBox.intersect(t.BoundBox):return
        # Per-solid bbox avoids testing long compound empty space as material.
        for a in s.Solids:
            for b in t.Solids:
                if not a.BoundBox.intersect(b.BoundBox):continue
                pairs+=1
                try:
                    c=a.common(b)
                    if c.Volume>1e-5:
                        bb=c.BoundBox;hits.append(dict(part=label,owner=key,mm3=c.Volume,bounds_mm=[getattr(bb,n) for n in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]))
                except Exception as exc:errors.append(dict(part=label,owner=key,error=str(exc)))
    for label,s in changed.items():
        for key,t in owners.items():check(label,s,key,t)
    for row,s in zip(intent['routes'],geometries):
        for key,t in {**owners,**changed}.items():
            if key==row['b']+'_ring_provisional':continue # own termination only
            check(row['wire'],s,key,t)
        print('SOURCE_ROUTE_RECEIVED',row['wire'],len(hits),len(errors),flush=True)
    for i,(row,s) in enumerate(zip(intent['routes'],geometries)):
        for other,t in zip(intent['routes'][i+1:],geometries[i+1:]):check(row['wire'],s,other['wire'],t)
    finish=datetime.now(timezone.utc);pins += [Path(__file__),INTENT]
    save(OUT/'checks.json',dict(status='SIX_LEAD_SOURCE_REJECTED' if hits or errors else 'SIX_LEAD_STATIC_CANDIDATE_RESTRAINTS_OPEN',
        hits=hits,errors=errors,pairs=pairs,replaced_old_wire_owners=replaced,omitted_retired_carrier_aliases=omitted,
        unchanged_old_restraints_retained_as_obstacles=True,changed_body_order=list(changed),
        routes=intent['routes'],source_qualified_wires_reopened=['W043','W066'],native_supports_ready=False,
        current_selected_batch='one-batch-prototype-r53',selected=False,W5_complete=False,physical_pass=False,
        source_sha256={q.relative_to(ROOT).as_posix():sha(q) for q in pins},files={q.relative_to(ROOT).as_posix():sha(q) for q in files},
        started_utc=start.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-start).total_seconds()))
    print('SIX_SOURCE_RESULT',pairs,len(hits),len(errors),flush=True)

if __name__=='__main__':main()
