"""Correct F_PI entry direction in the received joint six-lead candidate.

R3's W043 bent down through the fuse-holder casing. Approach its end face
outward along -X instead; keep the same short factory wire and P_SYS.2.
Reuse the received clear W066 and P_SYS body, not rejected S1 readiness.
"""
from datetime import datetime,timezone
from pathlib import Path
import json,math,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/electronics')]
from w5_s1_source_layout_r2 import CentreLine
from w5_s1_source_layout_r1 import add,mul,X,Y,Z
from servo_fuse_inputs_r1 import save,sha
OUT=ROOT/'hardware/electronics/full-cat/w5-source-inlet-joint-r1'
PARENT=ROOT/'hardware/electronics/full-cat/w5-s1-source-check-r3'

def factory_path():
    c=CentreLine([-73,-21,115],mul(X,-1));c.line([-75.5,-21,115]);c.arc(Z,radius=6)
    c.line([-81.5,-21,129.5]);c.arc(Y,radius=6)
    angle=math.acos(1-5/12);c.arc(X,angle,radius=6)
    c.arc(add(mul(Y,math.sin(angle)),mul(X,-math.cos(angle))),angle,radius=6)
    c.line([-76.5,7,135.5]);length=sum(e['length_mm'] for e in c.edges)
    assert length+14+10<=80<=84.5
    return dict(wire='W043',a='F_PI.in',b='P_SYS.2',edges=c.edges,start=[-73,-21,115],end=list(c.p),
        OD_mm=3.4,minimum_static_radius_mm=6,exposed_path_mm=length,nominal_trial_blank_mm=80,
        factory_minimum_mm=84.5,strip_allowance_mm=14,trial_reserve_mm=10,actual_cut_mm=None,
        prototype_assumptions=['FHAC0001ZXJ end-face lead direction -X; compare the exact delivered holder before cutting.',
            'OD3.4/R6 inherited project allowances, not measured supplier tolerances.'],selected=False,physical_pass=False)

def main():
    import FreeCAD as A
    import Part
    from w5_r53_owners import installed
    start=datetime.now(timezone.utc);assert not (OUT/'checks.json').exists()
    OUT.mkdir(parents=True,exist_ok=True);parentfile=PARENT/'checks.json'
    received=json.loads(parentfile.read_text(encoding='utf-8'))
    assert received['status']=='SIX_LEAD_SOURCE_REJECTED' and not received['errors']
    assert not any(h['part'] in ('P_SYS_candidate','W066') for h in received['hits'])
    assert all(sha(ROOT/k)==v for k,v in {**received['source_sha256'],**received['files']}.items())
    row=factory_path();parts=[];edges=[]
    for e in row['edges']:
        edge=Part.makeLine(A.Vector(*e['start']),A.Vector(*e['end'])) if e['kind']=='line' else Part.Arc(A.Vector(*e['start']),A.Vector(*e['mid']),A.Vector(*e['end'])).toShape()
        profile=Part.Wire([Part.makeCircle(1.7,edge.valueAt(edge.FirstParameter),edge.tangentAt(edge.FirstParameter))])
        q=Part.Wire([edge]).makePipeShell([profile],True,False);assert q.isValid();parts.append(q);edges.append(edge)
    shape=Part.makeCompound(parts);path=Part.Wire(edges);assert abs(path.Length-row['exposed_path_mm'])<1e-6
    files=[]
    for name,q in [('W043_WORLD.brep',shape),('W043_CENTERLINE.brep',path)]:
        f=OUT/name;q.exportBrep(str(f));files.append(f)
    owners,pins,_=installed(A,Part)
    for key in list(owners):
        if key=='P_SYS_design' or key.startswith(('source-switch-layout-r6/W066_','R49/W043_')):owners.pop(key)
    sourceparts=Part.read(str(PARENT/'CHANGED_BODIES_WORLD.brep')).childShapes()
    owners['P_SYS_candidate']=sourceparts[0]
    siblings=Part.read(str(PARENT/'SOURCE_ROUTES_WORLD.brep')).childShapes();assert len(siblings)==6
    for r,s in zip(received['routes'],siblings):
        if r['wire']!='W043':owners['jointSource/'+r['wire']]=s
    hits=[];errors=[];pairs=0
    for i,a in enumerate(parts):
        for key,t in owners.items():
            if not a.BoundBox.intersect(t.BoundBox):continue
            for b in t.Solids:
                if not a.BoundBox.intersect(b.BoundBox):continue
                pairs+=1
                try:
                    c=a.common(b)
                    if c.Volume>1e-5:
                        bb=c.BoundBox;hits.append(dict(edge=i,owner=key,mm3=c.Volume,bounds_mm=[getattr(bb,n) for n in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]))
                except Exception as exc:errors.append(dict(edge=i,owner=key,error=str(exc)))
    finish=datetime.now(timezone.utc);pins += [Path(__file__),parentfile,Path(__file__).with_name('w5_s1_source_layout_r2.py'),Path(__file__).with_name('w5_s1_source_layout_r1.py')]
    save(OUT/'checks.json',dict(status='SOURCE_INLET_PAIR_REJECTED' if hits or errors else 'SOURCE_INLET_PAIR_STATIC_CLEAR_SUPPORTS_OPEN',
        W043=row,W066_reused_from=parentfile.relative_to(ROOT).as_posix(),hits=hits,errors=errors,pairs=pairs,
        reused_scope='Only received W066/P_SYS body clear pairs; four S1 routes and their rings remain rejected, not selected.',
        native_supports_ready=False,selected=False,W5_complete=False,physical_pass=False,
        source_sha256={q.relative_to(ROOT).as_posix():sha(q) for q in pins},files={q.relative_to(ROOT).as_posix():sha(q) for q in files},
        started_utc=start.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-start).total_seconds()))
    print('SOURCE_INLET_PAIR',pairs,len(hits),len(errors),flush=True)

if __name__=='__main__':main()
