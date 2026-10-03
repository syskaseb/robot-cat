"""One coupled FR/RL/RR output construction above the closed ground/aux cases.

Retain the accepted four MTA bodies and complete sources/native stations.
FR reverses its rolled cage assignment; RL/RR factory approaches rise with
two tangent arcs and their HELU ends use the upper cage. This is one complete
layout, not a search over bolt offsets. Changed Cover/Bank contacts remain
failures requiring native construction, not silently accepted clearances.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,math,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/electronics'),str(ROOT/'tools/cad')]
from servo_fuse_inputs_r1 import sha,save
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-output-returns-complete-r1'

def main():
    import FreeCAD as A
    import Part
    from servo_fuse_rolled_cradles_native_r1 import retained_owners
    start=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists(),'Preserve prior construction result'
    pins={};V=A.Vector;X=V(1,0,0);Z=V(0,0,1)
    def pin(p):pins[p.relative_to(ROOT).as_posix()]=sha(p)
    def load(p):pin(p);return Part.read(str(p))
    def bounds(s):return [getattr(s.BoundBox,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]
    native=ROOT/'hardware/electronics/full-cat/servo-fuse-rl-source-station-native-r5/checks.json';pin(native)
    station=json.loads(native.read_text(encoding='utf-8'))
    assert not station['hits'] and not station['errors'],'Receive accepted RL native result first'
    definition=ROOT/'tools/electronics/servo_fuse_parent_complete_layout_r5.py';pin(definition)
    text=definition.read_text(encoding='utf-8');defs=text[text.index('    class Route:'):text.index('    X=V')]
    ctx=dict(V=V,Part=Part,math=math)
    exec(compile('def define():\n'+defs+'\n    return Route\n','output_route_builder','exec'),ctx)
    Route=ctx['define']()
    prior=ROOT/'hardware/electronics/full-cat/servo-fuse-front-source-ports-r2';pin(prior/'checks.json')
    facts=ROOT/'hardware/reference/parent-fuse-extensions-2026-10-03/facts.json';pin(facts)
    affected=('W037','W045','W053')
    owners=retained_owners(pin,load,Part)
    owners['CandidateDeck']=load(ROOT/'hardware/cad/studies/servo-fuse-rl-source-station-native-r5/Deck_WORLD.brep')
    cover=next(r for r in station['exports'] if r['tag']=='Cover')
    cover_brep=(ROOT/cover['file']).parent/'Cover_WORLD.brep'
    owners['ModifiableCover']=load(cover_brep)
    owners.pop('RetainedCover',None)
    owners['Bank/RightClipAccessFinished_WORLD']=load(ROOT/'hardware/cad/studies/servo-fuse-fr-return-guard-native-r3/BankRight_WORLD.brep')
    owners['FRReturnGuard']=load(ROOT/'hardware/cad/studies/servo-fuse-fr-return-guard-native-r3/Guard_WORLD.brep')
    for folder,pattern,prefix in [
        ('servo-fuse-main-joint-layout-r3','*_MTA_BODY.brep','MTA'),
        ('servo-fuse-rolled-cradles-native-r7','*Tie*_DESIGN.brep','BodyTie'),
        ('servo-fuse-fr-joint-station-native-r1','*Tie*_DESIGN.brep','FRTie'),
        ('servo-fuse-fr-return-guard-native-r3','*DESIGN.brep','FRHardware'),
        ('servo-fuse-rr-source-station-native-r4','RR*Tie*_DESIGN.brep','RRTie'),
        ('servo-fuse-rl-source-station-native-r5','RL*Tie*_DESIGN.brep','RLTie'),
        ('servo-fuse-rr-source-complete-r8','W052*_DESIGN.brep','RRSource'),
        ('servo-fuse-rl-source-complete-r2','W044*_DESIGN.brep','RLSource')]:
        for p in (ROOT/'hardware/electronics/full-cat'/folder).glob(pattern):owners[prefix+'/'+p.stem]=load(p)
    for p in prior.glob('*_DESIGN.brep'):
        if not p.stem.startswith(affected+('W044','W052')):owners['RetainedFeed/'+p.stem]=load(p)
    changed={};routes=[];joints=[];factory_failures=[];hits=[];errors=[];pairs=0
    def wire(name,r,od,kind,strip,leg):
        path,s=r.shape(od,r.edges[0].tangentAt(r.edges[0].FirstParameter));changed[name]=s
        path.exportBrep(str(OUT/(name+'_CENTERLINE.brep')))
        total=path.Length+strip+10
        row=dict(id=name,leg=leg,kind=kind,path_mm=path.Length,OD_mm=od,radii_mm=r.radii,
            endpoints_mm=[list(path.Vertexes[0].Point),list(r.p)],strip_allowance_mm=strip,trim_reserve_mm=10,
            minimum_blank_mm=total,stock_blank_mm=math.ceil(total/10)*10,actual_cut_mm=None,physical_pass=False)
        if kind=='MTA_factory':
            row.update(factory_usable_PROJECT_assumption_mm=100,within_factory_assumption=total<=100)
            if total>100:factory_failures.append(row)
        routes.append(row)
    for leg,ident,left,cy,cz,rise_sine,extra,target_y in [
        ('FR','W037',-79.5,-72,126,0,0,-111),
        ('RL','W045',16.5,72,130,.85,4,120),
        ('RR','W053',28.5,-86,121.5,.4,0,-117)]:
        side=1 if leg=='RL' else -1;Y=V(0,side,0)
        f=Route([left,cy,cz]);f.line([left-extra,cy,cz])
        if rise_sine:
            co=math.sqrt(1-rise_sine**2);normal=Y*co+Z*rise_sine
            f.arc(-X,normal,20)
            f.arc(normal,Y*rise_sine-Z*co,20,math.asin(rise_sine))
        else:f.arc(-X,Y,20)
        tx=f.p.x;factory_z=f.p.z
        assert (V(tx,target_y,factory_z)-f.p).dot(Y)>=0
        f.line([tx,target_y,factory_z])
        mx=-82.5 if leg=='FR' else 25.5
        e=Route([mx,side*49.5,113.5]);e.line([mx,side*(53.5 if leg=='RL' else 55.5),113.5])
        extension_z=factory_z+6.5;radius=31 if leg=='RL' else 25.2
        e.shift(Y,V(tx-mx,0,extension_z-113.5),radius)
        end=V(tx,target_y,extension_z);straight=(end-e.p).dot(Y)
        assert straight>=4,dict(leg=leg,straight=straight)
        e.line(end)
        lowy=min(target_y,target_y+side*18.3);lowz=factory_z-3.25
        changed[ident+'_221412']=Part.makeBox(8.15,18.3,13,V(tx-4,lowy,lowz))
        wire(ident+'_factory',f,5,'MTA_factory',11,leg)
        wire(ident+'_extension',e,4.2,'HELU23802',25,leg)
        joints.append(dict(id=ident,leg=leg,kind='WAGO221-412',SKU='221-412',
            ports_mm=[[tx,target_y,factory_z],[tx,target_y,extension_z]],
            body_bounds_mm=[tx-4,lowy,lowz,tx+4.15,lowy+18.3,lowz+13],
            strip_mm=11,grip_straight_extension_mm=straight,dimensions_source=facts.relative_to(ROOT).as_posix(),
            native_grips='OPEN: two independent insulation seats and housing retention after full shared fit.',
            recipe='Removed unpowered Deck: one UNTINNED4mm2 bare end per separate same-face cage; close levers before fixing. Factory and extension cage assignment is coupled to these routes, not a new electrical net.',
            assumptions='Nominal manufacturer envelope, project cage positions; rolled lower factory/upper extension, not delivered motion or tolerance.'))
    for n,s in changed.items():s.exportBrep(str(OUT/(n+'_DESIGN.brep')))
    save(OUT/'intent.json',dict(selected=False,physical_pass=False,routes=routes,joints=joints,factory_failures=factory_failures,
        unchanged='Four MTA bodies/front sources/rear sources/nativeRL_R5/nativeRR_R4/FRGuard; unchanged FL output retained by hashes.',
        assumptions='Factory100mm/OD5/R20 and HELUOD4.2/radius>=25.2 remain project assumptions. Native mounts and casing must follow shared contacts, not bbox-only decisions.'))
    def check(n,s,m,t):
        nonlocal pairs
        if not s.BoundBox.intersect(t.BoundBox):return
        pairs+=1
        try:
            h=s.common(t)
            if h.Volume>1e-5:
                hits.append(dict(part=n,owner=m,volume_mm3=h.Volume,bounds_mm=bounds(h),modifiable_casing=m in ('ModifiableCover','Bank/RightClipAccessFinished_WORLD','Bank/LeftClipAccessFinished_WORLD')))
                h.exportBrep(str(OUT/f'HIT_{len(hits)}.brep'))
        except Exception as exc:errors.append(dict(part=n,owner=m,error=str(exc)))
    for n,s in changed.items():
        for m,t in owners.items():check(n,s,m,t)
        print('OUTPUT_RETURN_SHARED',n,len(hits),len(errors),flush=True)
    items=list(changed.items())
    for i,(n,s) in enumerate(items):
        for m,t in items[i+1:]:check(n,s,m,t)
    end=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='OUTPUT_RETURN_CONTACTS' if hits or errors or factory_failures else 'OUTPUT_RETURNS_STATIC_CLEAR_NATIVE_GRIPS_OPEN',
        selected=False,physical_pass=False,W5_complete=False,routes=routes,joints=joints,pairs=pairs,hits=hits,errors=errors,factory_failures=factory_failures,
        source_sha256=pins,script_sha256=sha(Path(__file__)),started_utc=start.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-start).total_seconds(),
        open=['Native housing/insulation restraints and genuine lever/assembly release access.',
            'Any reported casing contact requires a matched native casing, not a waived collision.',
            'Whole bank removal, selected export/stock/E3 remain OPEN.']))
    print(json.dumps(dict(pairs=pairs,hits=len(hits),errors=len(errors),factory_failures=len(factory_failures))),flush=True)
if __name__=='__main__':main()
