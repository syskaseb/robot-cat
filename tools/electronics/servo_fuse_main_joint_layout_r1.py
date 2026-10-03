"""One rolled four-holder construction layout with both real exit datums.

R8 failed as an installed layout. Use three conservative free cavities and
one rear-right cavity previously hidden by broad curved-wire owner boxes.
Check real solids together before rebuilding native supports or long routes.
Both exits are retained; proximity alone is not a wire-length/routing PASS.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/electronics'),str(ROOT/'tools/cad')]
from servo_fuse_inputs_r1 import save,sha
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-main-joint-layout-r1'


def main():
    import FreeCAD as A
    import Part
    started=datetime.now(timezone.utc)
    OUT.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists()
    pins={}
    def pin(p):pins[p.relative_to(ROOT).as_posix()]=sha(p)
    def load(p):
        pin(p);return Part.read(str(p))
    def bounds(s):return [getattr(s.BoundBox,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]
    report=ROOT/'hardware/electronics/full-cat/servo-fuse-main-space-plan-r2/checks.json'
    pin(report);space=json.loads(report.read_text(encoding='utf-8'))
    assert space['status']=='STATIC_BODY_ROOM_FOUND'
    script=ROOT/'tools/electronics/servo_fuse_parent_complete_layout_r8.py'
    ns={'__file__':str(script),'__name__':'joint_layout_definition_only'}
    exec(compile(script.read_text(encoding='utf-8'),str(script),'exec'),ns)
    for rev in (5,6,7,8):pin(ROOT/f'tools/electronics/servo_fuse_parent_complete_layout_r{rev}.py')
    code=ns['code'];owner_code=code[code.index('    # Reuse exact retained source recipe'):code.index('    basepath=')]
    ctx=dict(ROOT=ROOT,Part=Part,pin=pin,load=load,pins=pins,sha=sha,Path=Path)
    exec(compile('def receive_owners():\n'+owner_code+'\n    return owners\n','retained_R8_recipe','exec'),ctx)
    owners=ctx['receive_owners']()
    owners['RetainedDeck']=load(ROOT/'hardware/cad/studies/servo-fuse-parent-feed-grips-native-r2/Deck_WORLD.brep')
    owners['ModifiableCoverR4']=load(ROOT/'hardware/cad/studies/servo-fuse-cover-native-r4/Cover_WORLD.brep')
    points=dict(FL=[-62,64,126],FR=[-62,-72,126],RL=[34,72,130],RR=[74,-66,126])
    bodies={};rows=[];hits=[];errors=[];pairs=0
    ids=dict(FL=('W026','W041'),FR=('W037','W042'),RL=('W045','W044'),RR=('W053','W052'))
    for leg,centre in points.items():
        x,y,z=centre;b=[x-17.5,y-11,z-8,x+17.5,y+11,z+8]
        body=Part.makeBox(35,22,16,A.Vector(*b[:3]));bodies[leg]=body
        body.exportBrep(str(OUT/(leg+'_MTA_BODY.brep')))
        rows.append(dict(leg=leg,centre_mm=centre,bounds_mm=b,
            orientation='catalogue envelope rolled90deg about its lead axis X',
            dimensions_source='Recorded prototype35x16x22mm assumption, rotated35x22x16; not supplier tolerance',
            exits=[dict(face='minusX',centre_mm=[x-17.5,y,z],outward_normal=[-1,0,0]),
                   dict(face='plusX',centre_mm=[x+17.5,y,z],outward_normal=[1,0,0])],
            output_wire_id=ids[leg][0],source_wire_id=ids[leg][1],
            assignment_and_full_routes='Both exits present; choose source/output face only with tangent full routes. Factory100mm usable/side still provisional. Extend using real selected wire/joint stock if needed, not invented long factory wire.',
            native_support='Must connect to retained Deck without new faulty channelCut, maintain existing mouths/grips and removable bank. Not yet constructed.'))
        for name,shape in owners.items():
            if not body.BoundBox.intersect(shape.BoundBox):continue
            pairs+=1
            try:
                hit=body.common(shape)
                if hit.Volume>1e-5:
                    hits.append(dict(part=leg,owner=name,volume_mm3=hit.Volume,bounds_mm=bounds(hit),
                        modifiable_cover=name=='ModifiableCoverR4'))
                    hit.exportBrep(str(OUT/('HIT_'+str(len(hits))+'.brep')))
            except Exception as exc:errors.append(dict(part=leg,owner=name,error=str(exc)))
        save(OUT/'progress.json',dict(last_body=leg,rows=rows,hits=hits,errors=errors,pairs=pairs,
            selected=False,physical_pass=False))
        print('JOINT_BODY_CHECKED',leg,len(hits),len(errors),flush=True)
    for i,(leg,body) in enumerate(bodies.items()):
        for other,shape in list(bodies.items())[i+1:]:
            pairs+=1
            hit=body.common(shape)
            if hit.Volume>1e-5:hits.append(dict(part=leg,owner=other,volume_mm3=hit.Volume,bounds_mm=bounds(hit),modifiable_cover=False))
    ended=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='FOUR_BODY_STATIC_CLEAR_FULL_CONSTRUCTION_OPEN' if not hits and not errors else 'JOINT_LAYOUT_CONTACTS',
        selected=False,physical_pass=False,W5_complete=False,holders=rows,hits=hits,errors=errors,pairs=pairs,
        open=['Full8feeds with actual stock joints and insulation restraints, not just exit datums.',
            'Native support/straps/cover, bank removal and selected export.',
            'No partial W5 completion or physical fit acceptance.'],
        started_utc=started.isoformat(),finished_utc=ended.isoformat(),worker_wall_seconds=(ended-started).total_seconds(),
        source_sha256=pins,script_sha256=sha(Path(__file__))))
    print(json.dumps(dict(hits=len(hits),errors=len(errors),pairs=pairs)),flush=True)


if __name__=='__main__':main()
