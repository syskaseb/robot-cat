"""One rear source-pair layout, away from the crowded inner ground/aux feeds.

Keep all four MTA bodies and accepted front exactly unchanged. Both rear
factory leads turn outward/up to straight supported joints above the bank.
New HELU extensions approach the joints along the outside shoulder. Factory
100mm usable lengths and joint dimensions are explicit project assumptions.
Only changed interfaces are checked; previous unrelated failures are retained.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, math, sys
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/electronics'),str(ROOT/'tools/cad')]
from servo_fuse_inputs_r1 import sha,save
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-rear-source-pair-r1'

def main():
    import FreeCAD as A
    import Part
    from servo_fuse_rolled_cradles_native_r1 import retained_owners
    start=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists(),'Do not overwrite prior result'
    pins={};V=A.Vector;X=V(1,0,0);Z=V(0,0,1)
    def pin(p):pins[p.relative_to(ROOT).as_posix()]=sha(p)
    def load(p):pin(p);return Part.read(str(p))
    def bounds(s):return [getattr(s.BoundBox,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]
    src=ROOT/'tools/electronics/servo_fuse_parent_complete_layout_r5.py';pin(src)
    text=src.read_text(encoding='utf-8');defs=text[text.index('    class Route:'):text.index('    X=V')]
    ctx=dict(V=V,Part=Part,math=math)
    exec(compile('def define():\n'+defs+'\n    return Route\n','route_definitions','exec'),ctx)
    Route=ctx['define']()
    prior=ROOT/'hardware/electronics/full-cat/servo-fuse-front-source-ports-r2'
    p=prior/'checks.json';pin(p);base=json.loads(p.read_text(encoding='utf-8'))
    assert not base['errors'] and not base['factory_failures']
    owners=retained_owners(pin,load,Part)
    owners['CandidateDeck']=load(ROOT/'hardware/cad/studies/servo-fuse-rolled-cradles-native-r7/Deck_WORLD.brep')
    owners['RetainedCover']=load(ROOT/'hardware/cad/studies/servo-fuse-fr-joint-station-native-r1/Cover_WORLD.brep')
    owners['Bank/RightClipAccessFinished_WORLD']=load(ROOT/'hardware/cad/studies/servo-fuse-fr-return-guard-native-r3/BankRight_WORLD.brep')
    owners['FRReturnGuard']=load(ROOT/'hardware/cad/studies/servo-fuse-fr-return-guard-native-r3/Guard_WORLD.brep')
    for folder,pattern,prefix in [
        ('servo-fuse-main-joint-layout-r3','*_MTA_BODY.brep','MTA'),
        ('servo-fuse-rolled-cradles-native-r7','*Tie*_DESIGN.brep','BodyTie'),
        ('servo-fuse-fr-joint-station-native-r1','*Tie*_DESIGN.brep','FRTie'),
        ('servo-fuse-fr-return-guard-native-r3','*DESIGN.brep','FRHardware')]:
        for p in (ROOT/'hardware/electronics/full-cat'/folder).glob(pattern):owners[prefix+'/'+p.stem]=load(p)
    affected=('W044','W052')
    for p in prior.glob('*_DESIGN.brep'):
        if not p.stem.startswith(affected):owners['OtherFeed/'+p.stem]=load(p)
    fixed={n:bounds(s) for n,s in owners.items() if any(t in n for t in ('XA02','XA06','W060','P_AUX','G_TAIL','G1_design','RR_G','Carrier','Bank/'))}
    save(OUT/'fixed-interface-bounds.json',fixed)
    changed={};rows=[];joints=[];intended=set();factory_failures=[]
    def wire(name,r,od,kind,strip,leg):
        path,s=r.shape(od,r.edges[0].tangentAt(r.edges[0].FirstParameter));changed[name]=s
        path.exportBrep(str(OUT/(name+'_CENTERLINE.brep')))
        total=path.Length+strip+10
        row=dict(id=name,leg=leg,kind=kind,path_mm=path.Length,OD_mm=od,radii_mm=r.radii,
            endpoints_mm=[list(path.Vertexes[0].Point),list(r.p)],strip_allowance_mm=strip,
            trim_reserve_mm=10,minimum_blank_mm=total,stock_blank_mm=math.ceil(total/10)*10,
            actual_cut_mm=None,physical_pass=False)
        if kind=='MTA_factory':
            row.update(factory_usable_assumption_mm=100,within_factory_assumption=total<=100)
            if total>100:factory_failures.append(row)
        rows.append(row)
    for leg,w,right,cy,cz,sy in [('RL','W044',51.5,72,130,-6.8),('RR','W052',63.5,-86,121.5,6.8)]:
        side=1 if leg=='RL' else -1;Y=V(0,side,0)
        normal=Y*.5+Z*math.sqrt(.75)
        f=Route([right,cy,cz]);f.arc(X,normal,20,math.pi)
        jy=f.p.y;jz=f.p.z;fx=right-16
        f.line([fx,jy,jz])
        # Leave17.5mm of straight intact insulation before each lap end:
        #9mm sleeve overlap,4mm grip and4.5mm free assembly allowance.
        e=Route([32,sy,129]);e.shift(X,Z*(jz-129),25.2)
        ex=e.p.x+4
        e.line([ex,sy,jz]);e.arc(X,Y,25.2)
        assert side*(jy-e.p.y)>25.2,(leg,list(e.p),jy)
        e.line([e.p.x,jy-side*25.2,jz]);e.arc(Y,-X,25.2)
        assert e.p.x>fx-8+17.5,(leg,list(e.p),fx)
        e.line([fx-8,jy,jz])
        a=f.p;b=e.p;assert abs((a-b).Length-8)<1e-6
        centre=(a+b)*.5;axis=-X;barestart=centre-axis*4
        changed[w+'_Sleeve']=Part.makeCylinder(4.5,26,centre-axis*13,axis).cut(Part.makeCylinder(2.5,26.2,centre-axis*13.1,axis))
        changed[w+'_Solder']=Part.makeCylinder(2.4,8,barestart,axis)
        for role,dy in [('Factory',1.15),('Extension',-1.15)]:
            n=w+'_Bare'+role;changed[n]=Part.makeCylinder(math.sqrt(4/math.pi),8,barestart+V(0,dy,0),axis)
            intended.add(frozenset((n,w+'_Solder')))
        wire(w+'_factory',f,5,'MTA_factory',8,leg);wire(w+'_extension',e,4.2,'HELU23802',22,leg)
        joints.append(dict(id=w,leg=leg,centre_mm=list(centre),axis=list(axis),factory_insulation_end_mm=list(a),extension_insulation_end_mm=list(b),
            factory_grip_centre_mm=[fx+12,jy,jz],extension_grip_centre_mm=[fx-20,jy,jz],grip_length_mm=4,
            bare_each_mm=8,sleeve_blank_mm=26,intact_insulation_overlap_each_mm=9,
            sleeve_SKU='RNF-100-3/8-0-STK',solder_SKU='T0051402499',native_grips='PENDING_SHARED_ROUTE_FIT'))
    for n,s in changed.items():s.exportBrep(str(OUT/(n+'_DESIGN.brep')))
    save(OUT/'intent.json',dict(selected=False,physical_pass=False,routes=rows,joints=joints,
        assumptions='MTA35x22x16,OD5,R20,usable100mm per side; HELU4.2/R25.2;8mm solder lap/26mm sleeve OD9. Not delivered measurements.',
        unchanged_front='front-source-ports-r2 + FRJointStation + FRGuardR3; no new front routing'))
    hits=[];errors=[];pairs=0
    def check(n,s,m,t):
        nonlocal pairs
        if not s.BoundBox.intersect(t.BoundBox):return
        pairs+=1
        try:
            h=s.common(t)
            if h.Volume>1e-5:
                hits.append(dict(part=n,owner=m,volume_mm3=h.Volume,bounds_mm=bounds(h)))
                h.exportBrep(str(OUT/f'HIT_{len(hits)}.brep'))
        except Exception as exc:errors.append(dict(part=n,owner=m,error=str(exc)))
    for n,s in changed.items():
        for m,t in owners.items():check(n,s,m,t)
        print('REAR_PAIR_SHARED',n,len(hits),flush=True)
    items=list(changed.items())
    for i,(n,s) in enumerate(items):
        for m,t in items[i+1:]:
            if frozenset((n,m)) not in intended:check(n,s,m,t)
    end=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='REAR_SOURCE_PAIR_CONTACTS' if hits or errors or factory_failures else 'REAR_SOURCE_PAIR_CLEAR_NATIVE_GRIPS_PENDING',
        selected=False,physical_pass=False,W5_complete=False,routes=rows,joints=joints,hits=hits,errors=errors,pairs=pairs,factory_failures=factory_failures,
        inherited_unrelated_contacts=[r for r in base['hits'] if not r['part'].startswith(affected) and not r['owner'].startswith(affected) and not r['part'].startswith(('W041','W042'))],
        source_sha256=pins,script_sha256=sha(Path(__file__)),started_utc=start.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-start).total_seconds(),
        open=['Native joint supports/ties and cover passages after real shared fit; WAGO grips, RR clips, combined removal, stock/E3 and selection.']))
    print(json.dumps(dict(pairs=pairs,hits=len(hits),errors=len(errors),factory_failures=len(factory_failures))),flush=True)
if __name__=='__main__':main()
