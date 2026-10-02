"""A service-slack construction, with fixed upper fans and R12.4 bends.

R2 moved the upper85.5mm turns and hit all12 Deck portals. Do not repeat it.
The old lower crossbar is only0.3mm long: narrowing it5.5mm is impossible
atR12.4, so that unrun source proposal is replaced, not executed as a trial.
Add50mm per input below the Deck. A descending S shifts the lower U inward
while its small vertical rise compensates the S arc excess exactly. Installed
configuration plus four release samples; no continuous or physical claim.
"""
from pathlib import Path
from datetime import datetime, timezone
import math,json,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/electronics')]
from servo_fuse_inputs_r1 import save,sha
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-bank-connected-release-r3'


def main():
    import FreeCAD as A
    import Part
    import servo_fuse_side_bank_r10 as layout
    begin=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists();hashes={}
    def pin(p):hashes[p.relative_to(ROOT).as_posix()]=sha(p)
    def load(p):pin(p);return Part.read(str(p))
    source=ROOT/'tools/electronics/servo_fuse_side_bank_r8.py';pin(source)
    code=source.read_text(encoding='utf-8');code=code[code.index('def input_path('):code.index('\ndef current_owners(')]
    code=code.replace('R=12.4):','R=12.4, release=0):')
    code=code.replace('assert p.z>end[2]', '''assert p.z>80
    line(A.Vector(p.x,p.y,80))
    rise=0
    if release>0:
        angle=math.acos(1-5.5*release/(2*R))
        arc(dz,-u,angle)
        tangent=dz*math.cos(angle)-u*math.sin(angle)
        inward=dz*math.sin(angle)+u*math.cos(angle)
        arc(tangent,inward,angle)
        rise=(2*R*angle-2*R*math.sin(angle))/2
    assert p.z>end[2]-35+rise''')
    code=code.replace('line(A.Vector(p.x,p.y,end[2]));arc(dz,u,math.pi/2)',
        'line(A.Vector(p.x,p.y,end[2]-35+rise));arc(dz,u,math.pi/2)')
    code=code.replace('line(A.Vector(p.x,side*stop,p.z));arc(u,up,math.pi/2)',
        'line(A.Vector(p.x,side*stop,p.z));arc(u,up,math.pi/2);line(A.Vector(*end))')
    ns={'math':math};exec(code,ns);route=ns['input_path']
    p=ROOT/'hardware/electronics/full-cat/servo-fuse-side-bank-r11/checks.json';pin(p)
    spec=json.loads(p.read_text(encoding='utf-8'));assert not spec['hits'] and not spec['errors']
    p=ROOT/'hardware/electronics/full-cat/servo-fuse-parent-feed-grips-native-r2/checks.json';pin(p)
    native=json.loads(p.read_text(encoding='utf-8'));assert not native['hits'] and not native['errors']
    save(OUT/'intent.json',dict(selected=False,physical_pass=False,started_utc=begin.isoformat(),
        upper_turn_y_mm=85.5,upper_fan_lift_mm=-5,unchanged_WAGO_ends=True,
        lower_U_inward_mm=5.5,service_S_start_z_mm=80,added_insulated_path_mm_per_wire=50,
        new_installed_U_grip_mm=35,old_U_grip_mm=10,constant_length_identity_mm='S_arc_excess-2*U_rise=0',
        nominal_bank_input_stock_mm=spec['planned_required_blank_mm']+12*50,
        nominal_bank_input_and_W001_mm=spec['planned_required_blank_mm']+12*50+140,
        stock_candidate_only=True,samples=[0,.25,.5,.75,1],nominal_radius_mm=12.4,
        sequence='Power absent. Use inputs50mm longer, prewire loose WAGO and close levers before mounting. Thread bare wires through Deck before TE crimps; form deeper installedU. Remove ATO/unclip holders and raise10mm; cut24bank ties. Keep upper fans fixed; release inputTE5.5mm inward using only lower serviceS/U. OutputTE stay fixed. Barebank/cover lift inherited from service-r3 only if wires clear. New lower spans need actual current Deck/P0 fit; do not assume old portals suffice.',
        continuous_deformation_qualified=False))
    print('FIXED_PORTAL_LOWER_U_RELEASE',flush=True)
    owners,more,_=layout.current_owners();hashes.update(more)
    for n in list(owners):
        if any(f in n for f in ('/servo-fuse-bank-restraints-r2/','/servo-fuse-bank-restraints-fit-r2/')):del owners[n]
    owners['R49Deck']=load(ROOT/'hardware/cad/studies/servo-fuse-parent-feed-grips-native-r2/Deck_WORLD.brep')
    for p in (ROOT/'hardware/cad/studies/servo-fuse-bank-clip-access-r1').glob('*_WORLD.brep'):owners[p.stem]=load(p)
    for p in (ROOT/'hardware/electronics/full-cat/servo-fuse-side-bank-r11').glob('F_*_OUT_DESIGN.brep'):owners[p.stem]=load(p)
    p=ROOT/'hardware/electronics/full-cat/servo-fuse-bank-service-r3/checks.json';pin(p)
    service=json.loads(p.read_text(encoding='utf-8'));assert not service['hits'] and not service['errors']
    hits=[];errors=[];records=[];pairs=0
    def check(phase,n,s,m,t):
        nonlocal pairs
        if not s.BoundBox.intersect(t.BoundBox):return
        pairs+=1
        try:
            c=s.common(t)
            if c.Volume>1e-5:
                hits.append(dict(phase=phase,part=n,owner=m,hit_mm3=c.Volume,
                    bounds_mm=[getattr(c.BoundBox,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]))
                c.exportBrep(str(OUT/(phase+'_'+n+'_HIT_'+str(len(hits))+'.brep')))
        except Exception as exc:errors.append(dict(phase=phase,part=n,owner=m,error=str(exc)))
    for fraction in (0.,.25,.5,.75,1.):
        phase='release_'+str(fraction);tubes={};print(phase,flush=True)
        for row in spec['lengths']:
            n=row['id'];pose=spec['placements'][n];start=pose['start'];end=list(pose['end']);side=1 if end[1]>0 else -1
            end[1]-=side*5.5*fraction
            if n=='W046':end[2]+=2
            delay=13-4*int(next(e for e in (row['a'],row['b']) if e.startswith('F_')).split('.')[0][-1])
            path=route(A,Part,start,end,side,lift=-5,delay=delay,release=fraction)
            if n=='W046':
                path=Part.Wire(path.Edges[:-1]+[Part.makeLine(path.Edges[-1].valueAt(path.Edges[-1].FirstParameter),A.Vector(end[0],end[1],end[2]-2))])
            target=row['path_mm']+50
            assert abs(path.Length-target)<1e-6,(n,path.Length,target)
            assert all(abs(e.Curve.Radius-12.4)<1e-6 for e in path.Edges if hasattr(e.Curve,'Radius'))
            s=path.makePipeShell([Part.Wire([Part.makeCircle(1.55,A.Vector(*start),A.Vector(0,side,0))])],True,False)
            assert s.isValid() and len(s.Solids)==1
            path.exportBrep(str(OUT/(phase+'_'+n+'_CENTERLINE.brep')));s.exportBrep(str(OUT/(phase+'_'+n+'_DESIGN.brep')));tubes[n]=s
            records.append(dict(phase=phase,wire=n,path_length_mm=path.Length,target_length_mm=target,
                fixed_upper_turn_y_mm=85.5,fixed_upper_fan_lift_mm=-5,service_S_start_z_mm=80,
                TE_end_mm=[end[0],end[1],end[2]-(2 if n=='W046' else 0)]))
        for n,s in tubes.items():
            for m,t in owners.items():check(phase,n,s,m,t)
        for i,(n,s) in enumerate(tubes.items()):
            for m,t in list(tubes.items())[i+1:]:check(phase,n,s,m,t)
        save(OUT/(phase+'_partial.json'),dict(paths=records,hits=hits,errors=errors,pairs=pairs,complete=False))
    end=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='FIXED_PORTAL_LOWER_U_RELEASE_CONFLICTS' if hits or errors else 'SAMPLED_FIXED_PORTAL_LOWER_U_RELEASE_CLEAR',
        selected=False,physical_pass=False,W5_complete=False,hits=hits,errors=errors,pairs=pairs,paths=records,
        sampled_fractions=[0,.25,.5,.75,1],continuous_deformation_qualified=False,
        added_insulated_path_mm_per_wire=50,
        new_nominal_input_blanks=[dict(wire=r['id'],blank_mm=r['nominal_unselected_blank_mm']+50,actual_cut_mm=None) for r in spec['lengths']],
        bank_over_stationary_released_ends_inherited_from='servo-fuse-bank-service-r3/checks.json',
        source_sha256=hashes,script_sha256=sha(Path(__file__)),started_utc=begin.isoformat(),finished_utc=end.isoformat(),
        worker_wall_seconds=(end-begin).total_seconds()))
    print(json.dumps(dict(hits=hits,errors=errors,pairs=pairs)),flush=True)


if __name__=='__main__':main()
