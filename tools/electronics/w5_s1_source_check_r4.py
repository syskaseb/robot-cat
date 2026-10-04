"""One shared source test, including actual TE shapes and received inlets.

No casing/Deck/bank waiver. Separate actual P0 and purchase conflicts from
editable PETG. Retain all rejected leg candidates as labelled additional
obstacles, never as selected or qualified wiring.
"""
from datetime import datetime,timezone
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import save,sha
OUT=ROOT/'hardware/electronics/full-cat/w5-s1-source-check-r4'
INTENT=ROOT/'hardware/electronics/full-cat/w5-s1-source-layout-r4/intent.json'

def main():
    import FreeCAD as A
    import Part
    from w5_r53_owners import installed
    begin=datetime.now(timezone.utc);assert not (OUT/'checks.json').exists()
    OUT.mkdir(parents=True,exist_ok=True)
    intent=json.loads(INTENT.read_text(encoding='utf-8'))
    assert all(sha(ROOT/k)==v for k,v in intent['source_sha256'].items())
    owners,pins,omitted=installed(A,Part)
    replaced=[]
    for key in list(owners):
        if key.startswith(('source-switch-layout-r6/W066_','R49/W043_')):
            replaced.append(key);owners.pop(key)
    assert len(replaced)==12
    owners.pop('P_SYS_design');owners.pop('CandidateDeck')
    parent=ROOT/'hardware/electronics/full-cat/w5-source-platform-native-r4'
    receipt=json.loads((parent/'checks.json').read_text(encoding='utf-8'))
    assert receipt['status']=='SOURCE_INLET_PLATFORM_LOCAL_COMPLETE_UNSELECTED'
    assert not receipt['hits'] and not receipt['errors']
    assert all(sha(ROOT/k)==v for k,v in {**receipt['source_sha256'],**receipt['files']}.items())
    for name in ('Platform','Deck'):
        p=ROOT/f'hardware/cad/studies/w5-source-platform-native-r4/{name}_WORLD.brep'
        owners['SourcePlatform/'+name]=Part.read(str(p));pins.append(p)
    for p in parent.glob('*_WORLD.brep'):
        if p.name.startswith(('Platform_','DeckBearingPad_')):continue
        owners['SourcePlatform/'+p.stem]=Part.read(str(p));pins.append(p)
    p=ROOT/'hardware/electronics/full-cat/w5-s1-source-check-r3/CHANGED_BODIES_WORLD.brep'
    owners['P_SYS_candidate']=Part.read(str(p)).childShapes()[0];pins.append(p)
    p=ROOT/'hardware/electronics/full-cat/w5-s1-source-check-r3/SOURCE_ROUTES_WORLD.brep'
    owners['SourcePlatform/W066']=Part.read(str(p)).childShapes()[4];pins.append(p)
    p=ROOT/'hardware/electronics/full-cat/w5-source-inlet-joint-r2/W043_WORLD.brep'
    owners['SourcePlatform/W043']=Part.read(str(p));pins.append(p)
    # Drawing-bounded reserved casing, not a CAD model or a physical pocket.
    owners['S1_casing_provisional']=Part.makeBox(24,42,37,A.Vector(111,49,66))
    reference=ROOT/'hardware/reference/source-terminal-2026-10-04/TE130171_LOCAL.brep'
    ring_base=Part.read(str(reference));pins += [reference,reference.parent/'received.json']
    rings={};routes={};paths=[]
    for row in intent['routes']:
        centre=intent['S1_ring_seat_centres'][row['b']]
        ring=ring_base.copy();ring.rotate(A.Vector(),A.Vector(1,1,1),120)
        if row['wire'] in ('W065','W068'):ring.rotate(A.Vector(),A.Vector(0,0,1),180)
        ring.translate(A.Vector(*centre));assert ring.isValid()
        rings[row['b']]=ring
        # Verify the actual sleeve centre transformed by the same placement.
        entry=A.Vector(0,2.8067,-22.1234)
        entry=A.Rotation(A.Vector(1,1,1),120).multVec(entry)
        if row['wire'] in ('W065','W068'):entry=A.Rotation(A.Vector(0,0,1),180).multVec(entry)
        entry+=A.Vector(*centre);assert (entry-A.Vector(*row['end'])).Length<1e-7
        pieces=[];edges=[]
        for e in row['edges']:
            edge=Part.makeLine(A.Vector(*e['start']),A.Vector(*e['end'])) if e['kind']=='line' else Part.Arc(A.Vector(*e['start']),A.Vector(*e['mid']),A.Vector(*e['end'])).toShape()
            profile=Part.Wire([Part.makeCircle(row['OD_mm']/2,edge.valueAt(edge.FirstParameter),edge.tangentAt(edge.FirstParameter))])
            s=Part.Wire([edge]).makePipeShell([profile],True,False)
            assert s.isValid() and len(s.Solids)==1;pieces.append(s);edges.append(edge)
        routes[row['wire']]=Part.makeCompound(pieces);path=Part.Wire(edges)
        assert abs(path.Length-row['exposed_path_mm'])<1e-6;paths.append(path)
    files=[]
    for name,values in [('SOURCE_ROUTES_WORLD.brep',list(routes.values())),('CENTERLINES_WORLD.brep',paths),('TE_RINGS_WORLD.brep',list(rings.values()))]:
        p=OUT/name;Part.makeCompound(values).exportBrep(str(p));files.append(p)
    print('FOUR_SOURCE_ACTUAL_TE_GEOMETRY_SAVED',flush=True)
    hits=[];errors=[];pairs=0
    def check(label,s,key,t):
        nonlocal pairs
        for a in s.Solids:
            for b in t.Solids:
                if not a.BoundBox.intersect(b.BoundBox):continue
                pairs+=1
                try:
                    common=a.common(b)
                    if common.Volume>1e-5:
                        bb=common.BoundBox;hits.append(dict(part=label,owner=key,mm3=common.Volume,
                            bounds_mm=[getattr(bb,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]))
                except Exception as exc:errors.append(dict(part=label,owner=key,error=str(exc)))
    for label,s in rings.items():
        for key,t in owners.items():check(label,s,key,t)
    for row in intent['routes']:
        s=routes[row['wire']]
        for key,t in owners.items():check(row['wire'],s,key,t)
        for key,t in rings.items():
            if key!=row['b']:check(row['wire'],s,key,t)
        save(OUT/'progress.json',dict(completed_wire=row['wire'],pairs=pairs,hits=hits,errors=errors))
        print('SOURCE_RECEIVED',row['wire'],len(hits),len(errors),flush=True)
    keys=list(routes)
    for i,key in enumerate(keys):
        for other in keys[i+1:]:check(key,routes[key],other,routes[other])
    finish=datetime.now(timezone.utc);pins += [Path(__file__),INTENT,parent/'checks.json']
    save(OUT/'checks.json',dict(status='SOURCE_JOINT_REJECTED' if hits or errors else 'SOURCE_JOINT_STATIC_CLEAR_NATIVE_GUARDS_OPEN',
        hits=hits,errors=errors,pairs=pairs,exact_TE_reference=True,provisional_S1_casing=True,
        checked_received_inlet_family=True,replaced_old_wire_owners=replaced,omitted_retired_carrier_aliases=omitted,
        routes=intent['routes'],selected=False,native_supports_ready=False,
        full_leg_candidate_checked=False,leg_R5_is_rejected_not_qualified=True,
        W5_complete=False,physical_pass=False,
        source_sha256={q.relative_to(ROOT).as_posix():sha(q) for q in list(dict.fromkeys(pins))},
        files={q.relative_to(ROOT).as_posix():sha(q) for q in files},
        started_utc=begin.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-begin).total_seconds()))
    print('SOURCE_JOINT_FINAL',pairs,len(hits),len(errors),flush=True)

if __name__=='__main__':main()
