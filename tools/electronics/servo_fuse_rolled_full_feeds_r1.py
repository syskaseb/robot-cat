"""All eight actual feeds for the SAME rolled main-holder layout.

One FL factory source lead can reach its front mouth in the project100mm
assumption. Seven other feeds have explicit4mm2 extensions and two-sided
insulated solder-lap joints, not fictional long factory wire. Candidate only;
native joint grips, modified cover and assembly fit remain necessary.
"""
from pathlib import Path
from datetime import datetime,timezone
import sys,json,math
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/electronics'),str(ROOT/'tools/cad')]
from servo_fuse_inputs_r1 import sha,save
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-full-feeds-r1'


def main():
    import FreeCAD as A
    import Part
    from servo_fuse_rolled_cradles_native_r1 import retained_owners
    started=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists(),'Preserve previous evidence'
    pins={}
    def pin(p):pins[p.relative_to(ROOT).as_posix()]=sha(p)
    def load(p):pin(p);return Part.read(str(p))
    base=ROOT/'tools/electronics/servo_fuse_parent_complete_layout_r5.py';pin(base)
    text=base.read_text(encoding='utf-8');defs=text[text.index('    class Route:'):text.index('    X=V')]
    ctx=dict(V=A.Vector,math=math,Part=Part)
    exec(compile('def define():\n'+defs+'\n    return Route\n','route_builder','exec'),ctx)
    Route=ctx['define']();V=A.Vector;X=V(1,0,0);Z=V(0,0,1)
    points=dict(FL=(-62,64,126),FR=(-62,-72,126),RL=(34,72,130),RR=(46,-86,121.5))
    joint_path=ROOT/'hardware/electronics/full-cat/servo-fuse-main-joint-layout-r3/checks.json';pin(joint_path)
    r3=json.loads(joint_path.read_text(encoding='utf-8'));assert not r3['hits'] and not r3['errors']
    assert {r['leg']:tuple(r['centre_mm']) for r in r3['holders']}==points
    facts=ROOT/'hardware/reference/parent-fuse-extensions-2026-10-03/facts.json';pin(facts)
    ledger=ROOT/'hardware/electronics/full-cat/source-switch-selected-r1/body-harness.json';pin(ledger)
    catalogue=ROOT/'hardware/manufacturing/one-batch-prototype-r51/nonfastener-catalog.json';pin(catalogue)
    cad=ROOT/'hardware/cad/studies/servo-fuse-rolled-cradles-native-r1/Deck_WORLD.brep'
    cradle=ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-cradles-native-r1/checks.json'
    assert cradle.exists(),'Receive the existing cradle worker first, no duplicate'
    pin(cradle)
    changed={};paths={};rows=[];joints=[];intended=set();factory_failures=[]
    def wire(name,r,od,tangent,kind,strip,leg):
        path,s=r.shape(od,tangent);changed[name]=s;paths[name]=path
        path.exportBrep(str(OUT/(name+'_CENTERLINE.brep')));s.exportBrep(str(OUT/(name+'_DESIGN.brep')))
        total=path.Length+strip+10
        row=dict(id=name,leg=leg,kind=kind,path_mm=path.Length,OD_mm=od,radii_mm=r.radii,
            endpoints_mm=[list(path.Vertexes[0].Point),list(r.p)],strip_allowance_mm=strip,
            rework_assumption_mm=10,minimum_blank_with_allowance_mm=total,
            stock_blank_mm=math.ceil(total/10)*10,actual_cut_mm=None,physical_pass=False)
        if kind=='MTA_factory':
            row.update(factory_usable_assumption_mm=100,within_factory_assumption=total<=100)
            if total>100:factory_failures.append(dict(id=name,total_mm=total))
        rows.append(row)
        print('FULL_FEED_SAVED',name,round(path.Length,3),flush=True)
        return row
    def lap(leg,ident,factory,ext,ftangent,etangent,axis):
        # End faces are separated by8mm, each bare end overlaps that interval.
        a=factory.p;b=ext.p;assert abs((a-b).Length-8)<1e-6
        assert abs(ftangent.dot(etangent)+1)<1e-7
        centre=(a+b)*.5;start=centre-axis*4
        sleeve=Part.makeCylinder(4.5,26,centre-axis*13,axis).cut(Part.makeCylinder(2.5,26.2,centre-axis*13.1,axis))
        core=Part.makeCylinder(2.4,8,start,axis)
        changed[ident+'_Sleeve']=sleeve;changed[ident+'_Solder']=core
        for role,dx in [('Factory',1.15),('Extension',-1.15)]:
            n=ident+'_Bare'+role;changed[n]=Part.makeCylinder(math.sqrt(4/math.pi),8,start+X*dx,axis)
            intended.add(frozenset((n,ident+'_Solder')))
        joints.append(dict(id=ident,leg=leg,centre_mm=list(centre),axis=list(axis),
            factory_insulation_end_mm=list(a),extension_insulation_end_mm=list(b),
            bare_each_mm=8,sleeve_blank_mm=26,intact_insulation_overlap_each_mm=9,
            sleeve_envelope_OD_assumed_mm=9,selected_sleeve_SKU='RNF-100-3/8-0-STK',TE='5053142077',
            wire_SKU='SIF4.00-R',solder_SKU='T0051402499',
            recipe='Removed unpowered Deck: slide exact sleeve first;8mm opposing stripped fine-strand copper lap, solder, inspect, shrink9mm intact overlap each side; independent grips on insulation both sides. No solder/tin at WAGO cage ends.',
            model='Equivalent4mm2 bare copper cylinders and solder envelope, not strand-level or supplier-approved joint; nominal insertion/crimp/pull/current/thermal tests phase2.',
            native_grips='OPEN: two-sided insulation grips and strap insertion not constructed yet.'))
        wire(ident+'_factory',factory,5,ftangent if not factory.edges else factory.edges[0].tangentAt(factory.edges[0].FirstParameter),'MTA_factory',8,leg)
        wire(ident+'_extension',ext,4.2,ext.edges[0].tangentAt(ext.edges[0].FirstParameter),'HELU23802',14+8,leg)
    for leg,(cx,cy,cz) in points.items():
        side=1 if leg.endswith('L') else -1;Y=V(0,side,0);left=cx-17.5;right=cx+17.5
        out_id=dict(FL='W026',FR='W037',RL='W045',RR='W053')[leg]
        in_id=dict(FL='W041',FR='W042',RL='W044',RR='W052')[leg]
        mx=-82.5 if leg.startswith('F') else 25.5
        # Output: outside-facing quarter bend, then a straight supported joint.
        f=Route([left,cy,cz])
        extra=22.5 if leg=='RL' else 0
        f.line([left-extra,cy,cz]);f.arc(-X,Y,20)
        end_y=dict(FL=105,FR=-111,RL=120,RR=-117)[leg]
        f.line([left-extra-20,end_y,cz])
        e=Route([mx,side*49.5,113.5]);e.line([mx,side*55.5,113.5])
        radius=30 if leg=='RL' else 25.2
        target_x=left-extra-20
        e.shift(Y,V(target_x-mx,0,cz-113.5),radius)
        end=V(target_x,end_y+side*8,cz)
        assert (end-e.p).dot(Y)>=0,(leg,list(e.p),list(end))
        e.line(end);lap(leg,out_id,f,e,Y,-Y,Y)
        # Source FL has a complete direct factory route into the +Y mouth.
        if leg=='FL':
            f=Route([right,cy,cz]);f.arc(X,-Y,20)
            f.shift(-Y,V(-7,0,-12.5),20);assert f.p.y>=11
            f.line([-31.5,11,113.5]);wire(in_id+'_factory_direct',f,5,X,'MTA_factory',14,leg)
        elif leg=='FR':
            f=Route([right,cy,cz]);f.arc(X,-Y,20);f.line([right+20,-41,cz])
            e=Route([-24,11,113.5]);e.line([-24,17,113.5]);e.shift(V(0,1,0),Z*12.5,25.2)
            e.arc(V(0,1,0),X,25.2)
            # One upper hairpin, not the rejected long R8 perimeter loop.
            e.arc(X,Z,25.2,math.pi)
            e.line([.7,e.p.y,e.p.z]);e.arc(-X,V(0,-1,0),25.2)
            e.shift(V(0,-1,0),-Z*50.4,30);assert e.p.y>=-33
            e.line([-24.5,-33,cz]);lap(leg,in_id,f,e,V(0,1,0),V(0,-1,0),V(0,1,0))
        else:
            # Rear source +X mouth to a joint on the inner straight factory lead.
            f=Route([right,cy,cz]);f.arc(X,-Y,25.2)
            factory_y=cy-side*(25.2+11);f.line([right+25.2,factory_y,cz])
            sy=-6.8 if leg=='RL' else 6.8
            e=Route([32,sy,129]);delta=Z*(cz-129)
            travel=2*25.2*math.sin(math.acos(1-delta.Length/(2*25.2)))
            assert right-32>=travel
            e.line([right-travel,sy,129]);e.shift(X,delta,25.2);e.arc(X,Y,25.2)
            end=V(right+25.2,factory_y-side*8,cz)
            assert (end-e.p).dot(Y)>=0,(leg,list(e.p),list(end))
            e.line(end);lap(leg,in_id,f,e,-Y,Y,Y)
    save(OUT/'intent.json',dict(selected=False,physical_pass=False,W5_complete=False,routes=rows,joints=joints,
        factory_failures=factory_failures,strip_rule='Retained221-615:12..14mm,14mm stock allowance;8mm solder lap. Final stripping from delivered housing marking. No221-412 assumed here.',stock_contribution=dict(HELU_extension_blanks_mm=sum(r['stock_blank_mm'] for r in rows if r['kind']=='HELU23802'),
            solder_joints=len(joints),TE3_8_installed_blank_mm=26*len(joints),additional_WAGO221412=0),
        scope='All eight full feeds at one body layout; joints/stock explicit, no native grip or service qualification from routing alone.'))
    owners=retained_owners(pin,load,Part);owners['CandidateDeck']=load(cad)
    for r in r3['holders']:owners[r['leg']+'_MTA_BODY']=load(ROOT/f"hardware/electronics/full-cat/servo-fuse-main-joint-layout-r3/{r['leg']}_MTA_BODY.brep")
    for q in (ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-cradles-native-r1').glob('*Tie*_DESIGN.brep'):owners['BodyStrap/'+q.stem]=load(q)
    hits=[];errors=[];pairs=0
    def check(n,s,m,t):
        nonlocal pairs
        if not s.BoundBox.intersect(t.BoundBox):return
        pairs+=1
        try:
            h=s.common(t)
            if h.Volume>1e-5:
                hits.append(dict(part=n,owner=m,volume_mm3=h.Volume))
                h.exportBrep(str(OUT/f'HIT_{len(hits)}.brep'))
        except Exception as ex:errors.append(dict(part=n,owner=m,error=str(ex)))
    for n,s in changed.items():
        s.exportBrep(str(OUT/(n+'_DESIGN.brep')))
        for m,t in owners.items():check(n,s,m,t)
        print('FULL_FEED_SHARED_FIT',n,len(hits),len(errors),flush=True)
    items=list(changed.items())
    for i,(n,s) in enumerate(items):
        for m,t in items[i+1:]:
            if frozenset((n,m)) not in intended:check(n,s,m,t)
    end=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='FULL_FEEDS_CONTACTS' if hits or errors or factory_failures else 'FULL_FEEDS_STATIC_CLEAR_GRIPS_SERVICE_OPEN',
        selected=False,physical_pass=False,W5_complete=False,routes=rows,joints=joints,factory_failures=factory_failures,
        hits=hits,errors=errors,pairs=pairs,source_sha256=pins,script_sha256=sha(Path(__file__)),
        started_utc=started.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-started).total_seconds(),
        open=['Native two-sided joint grips and all strap insertion, casing changes and shared bank removal.',
              'One coherent export/stock/E3 contribution, not a new selected W5.']))
    print(json.dumps(dict(hits=len(hits),errors=len(errors),factory_failures=len(factory_failures),pairs=pairs)),flush=True)


if __name__=='__main__':main()
