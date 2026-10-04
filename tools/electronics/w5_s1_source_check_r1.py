"""Check all four new source routes together, against installed R53.

Leg R4 is a separately-labelled, unselected neighbour, never an installed
replacement. No whole body audit, repeated bank checks, hardware I/O or
fabricated switch seating. Keep grouped BReps rather than a file per edge.
"""
from datetime import datetime,timezone
from pathlib import Path
import json,sys

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/electronics'),str(ROOT/'tools/cad')]
from servo_fuse_inputs_r1 import save,sha
OUT=ROOT/'hardware/electronics/full-cat/w5-s1-source-check-r1'


def main():
    import FreeCAD as A
    import Part
    from w5_r53_owners import installed
    start=datetime.now(timezone.utc)
    assert not (OUT/'checks.json').exists(),'Preserve completed evidence'
    OUT.mkdir(parents=True,exist_ok=True)
    source=ROOT/'hardware/electronics/full-cat/w5-s1-source-layout-r1/intent.json'
    intent=json.loads(source.read_text(encoding='utf-8'))
    assert len(intent['routes'])==4 and not intent['selected']
    assert all(sha(ROOT/k)==v for k,v in intent['source_sha256'].items())
    selected_file=ROOT/'hardware/manufacturing/one-batch-prototype-r53/selection.json'
    selected=json.loads(selected_file.read_text(encoding='utf-8'))
    owners,owner_pins,omitted=installed(A,Part)
    deck=ROOT/selected['current_deck_world'];owners['CandidateDeck']=Part.read(str(deck))
    bus_file=ROOT/'hardware/electronics/full-cat/w5-bus-pair-r52-r4/intent.json'
    def box(b):return Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
    # Retain the original provisional S1 reserved family; no certified pocket,
    # tightening torque, screw bearing or delivered datum is claimed.
    owners['S1_body_provisional']=box([111,49,66,135,91,103])
    for row in intent['routes']:
        end=row['end'];left=end[0] if row['wire'] in ('W064','W067') else end[0]-27.686
        owners[row['b']+'_ring_provisional']=box([left,end[1]-9.525/2,56,left+27.686,end[1]+9.525/2,68])
    geometries=[];paths=[];hits=[];errors=[];pairs=0
    def check(wire,s,key,t,scope='selected_R53'):
        nonlocal pairs
        if not s.BoundBox.intersect(t.BoundBox):return
        pairs+=1
        try:
            common=s.common(t)
            if common.Volume>1e-5:
                b=common.BoundBox
                hits.append(dict(wire=wire,owner=key,scope=scope,mm3=common.Volume,
                    bounds_mm=[getattr(b,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]))
        except Exception as exc:errors.append(dict(wire=wire,owner=key,scope=scope,error=str(exc)))
    for row in intent['routes']:
        edges=[];pieces=[]
        for e in row['edges']:
            edge=Part.makeLine(A.Vector(*e['start']),A.Vector(*e['end'])) if e['kind']=='line' else Part.Arc(A.Vector(*e['start']),A.Vector(*e['mid']),A.Vector(*e['end'])).toShape()
            profile=Part.Wire([Part.makeCircle(2.1,edge.valueAt(edge.FirstParameter),edge.tangentAt(edge.FirstParameter))])
            shape=Part.Wire([edge]).makePipeShell([profile],True,False)
            assert shape.isValid() and len(shape.Solids)==1
            edges.append(edge);pieces.append(shape)
            for key,other in owners.items():
                if key==row['b']+'_ring_provisional':continue # own reserved termination family
                check(row['wire'],shape,key,other)
        path=Part.Wire(edges);assert abs(path.Length-row['exposed_path_mm'])<1e-6
        paths.append(path);geometries.append(Part.makeCompound(pieces))
        print('S1_ROUTE',row['wire'],'fixed_hits',len(hits),flush=True)
    for i,s in enumerate(geometries):
        for j,t in enumerate(geometries[i+1:],i+1):check(intent['routes'][i]['wire'],s,intent['routes'][j]['wire'],t,'new_S1_mutual')
    # Receive the whole leg candidate first. It can inform interference, but
    # a rejected candidate never supersedes selected R53 objects in this proof.
    leg_folder=ROOT/'hardware/electronics/full-cat/w5-leg-fanouts-r4'
    leg_file=leg_folder/'checks.json';leg=json.loads(leg_file.read_text(encoding='utf-8'))
    assert len(leg['routes'])==36
    assert all(sha(ROOT/k)==v for k,v in {**leg['source_sha256'],**leg['files']}.items())
    neighbours={}
    leg_shapes=Part.read(str(leg_folder/'FANOUTS_WORLD.brep')).childShapes()
    assert len(leg_shapes)==36 and all(s.isValid() for s in leg_shapes)
    for r,s in zip(leg['routes'],leg_shapes):neighbours[r['wire']]=s
    for name,s in zip(leg['changed_mounts'],Part.read(str(leg_folder/'RELOCATED_OWNERS_WORLD.brep')).childShapes()):neighbours[name]=s
    for row,s in zip(intent['routes'],geometries):
        for key,t in neighbours.items():check(row['wire'],s,'legR4/'+key,t,'UNSELECTED_leg_R4')
    files=[]
    for name,shapes in (('S1_ROUTES_WORLD.brep',geometries),('CENTERLINES_WORLD.brep',paths)):
        file=OUT/name;Part.makeCompound(shapes).exportBrep(str(file));files.append(file)
    fixed=[h for h in hits if h['scope']!='UNSELECTED_leg_R4']
    finished=datetime.now(timezone.utc)
    pins=owner_pins+[source,selected_file,deck,bus_file,leg_file,leg_folder/'FANOUTS_WORLD.brep',leg_folder/'RELOCATED_OWNERS_WORLD.brep',Path(__file__),
          ROOT/'hardware/electronics/full-cat/w5-installed-r52/owners.json',ROOT/'hardware/electronics/full-cat/w5-installed-r52/installed.brep']
    save(OUT/'checks.json',dict(status='SOURCE_ROUTES_REJECTED' if fixed or errors else 'SOURCE_STATIC_ROUTES_ONLY_RESTRAINTS_OPEN',
        hits=hits,errors=errors,pairs=pairs,leg_candidate_status=leg['status'],leg_candidate_errors=leg['errors'],
        omitted_retired_carrier_aliases=omitted,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in pins},files={p.relative_to(ROOT).as_posix():sha(p) for p in files},
        nominal_trial_total_mm=intent['new_nominal_trial_total_mm'],native_supports_ready=False,
        selected=False,W5_complete=False,physical_pass=False,
        started_utc=start.isoformat(),finished_utc=finished.isoformat(),worker_wall_seconds=(finished-start).total_seconds()))
    print('S1_RESULT',len(fixed),len(hits)-len(fixed),len(errors),flush=True)


if __name__=='__main__':main()
