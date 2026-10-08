"""Shared eight-main-feed receiving space before another route/mount rebuild.

Hypothesis: lower ALL five FHAC bodies/floor by19.5mm, preserve WAGO/MTA
datums, move all five output drops beyond the receiving plate perimeter.
Check exact entry sectors and five full factory inputs together. This is NOT
eight full feeds, finished supports, or proof of manufacturer bend limits.
"""
from datetime import datetime,timezone
from pathlib import Path
import copy,json,math,time
import FreeCAD as A
import Part
from open_prototype_distribution_allocation import input_recipe
from open_prototype_shared_distribution_carriers import planned_shapes
from open_prototype_common_mta_mounts import MODEL
from open_prototype_entry_chambers import MOUNTS,CONTEXT
from open_prototype_wiring_endpoints import ROOT,BASE,read,sha,bounds

OUT=BASE/'wiring-checkpoint'
PLAN=OUT/'main-entry-space-plan.json'
PROOF=OUT/'main-entry-space-checks.json'


def main():
    assert not PLAN.exists() and not PROOF.exists(),'Receive existing common-space result'
    tick=time.monotonic()
    allocation=copy.deepcopy(read(OUT/'shared-allocation-plan.json'))
    ports={p['role']:p for p in read(OUT/'shared-allocation-checks.json')['ports']}
    pins={p.relative_to(ROOT).as_posix():sha(p) for p in (
        MODEL,MOUNTS,CONTEXT,OUT/'shared-allocation-plan.json',
        OUT/'shared-allocation-checks.json',ROOT/'hardware/reference/parent-fuse-extensions-2026-10-03/facts.json',Path(__file__))}
    rows=[]
    for h in allocation['holders']:
        h['input_mm'][2]-=19.5;h['output_mm'][2]-=19.5
        inlet=input_recipe(h['input_mm'],ports[h['target']]['point_mm'],[-v for v in h['axis']])
        strip=14 if h['holder'] in ('F_PI','F_AUX') else 11
        limit=50 if strip==14 else 84.5
        rows.append(dict(holder=h['holder'],target=h['target'],recipe=inlet,
                         required_blank_mm=inlet['centreline_mm']+strip,
                         provisional_limit_mm=limit,
                         impossible=inlet['centreline_mm']+strip>limit,
                         supplier_OD_R6_and_usable_length_are_delivery_gates=True))
    allocation['input_recipes']=rows
    # Opposing quarter sectors diverge before neighbouring ports, not parallel
    # copies of a curve whose true normal spacing is less than conductor OD.
    specs=[('W041','P_FRONT.2',1),('W042','P_FRONT.3',-1),
           ('W044','P_REAR.5',1),('W052','P_REAR.2',-1),
           ('W026','FL_P.1',1),('W037','FR_P.1',1),
           ('W045','RL_P.1',-1),('W053','RR_P.1',-1)]
    r=dict(status='PENDING',selected=False,stage_completed=False,physical_pass=False,
           source_sha256=pins,contacts=[],errors=[],outside_torso=[],tested_pairs=0,
           factory_input_rows=rows,entry_rows=[],receiving_plane_only_not_full8feeds=True,
           nominal_HELU_OD_mm=4.2,retained_project_HELU_radius_mm=25.2,
           proposed_common_floor_z_mm=[93.5,95.5],proposed_FHAC_top_z_mm=117.5,
           preserved=['20WAGO poses/100ports','4MTA bodies and both9mm exits','BankR47','Torso325x200x160','P0/E6/15drives/MG92B'],
           invalidated_if_chosen=['57afce2/4903198 source floor/columns/ribs/body ties and front MTA posts',
               'Five source input curves/body slots/output arms/posts/backers/joints',
               'Previous source current STL selection remains false'],
           assembly=['Keep all tested native historical files unchanged during preflight',
               'If common-space gate clear, plan full8factory/joint/extension paths and all load paths before new native rebuild',
               'Then implement one integrated current module, not another isolated lower-floor CAD'],
           open=['Full8mainfeed routes/factory length and connectors','Native supports/ties/access/full assembly',
                 'All other outputs/stations/S1/PWM/body/legs/stock and delivered U1/S0 datums'])
    PLAN.write_text(json.dumps(dict(r,proposed_allocation=allocation),indent=2)+'\n',encoding='utf-8')
    docs=[A.openDocument(str(p)) for p in (MODEL,MOUNTS,CONTEXT)]
    doc,mount,ctx=docs
    try:
        targets=planned_shapes(allocation,mount,ctx)
        # Replace ALL output first stages coherently; straight20mm before R6
        # takes sleeves/grips to Y+-51.5 outside UpperCarrierY+-40.5.
        def pipe(parts,od):
            edges=[Part.makeLine(A.Vector(*q['start']),A.Vector(*q['end'])) if q['kind']=='line' else
                   Part.Arc(A.Vector(*q['start']),A.Vector(*q['mid']),A.Vector(*q['end'])).toShape() for q in parts]
            for a,b in zip(edges,edges[1:]):
                assert a.tangentAt(a.LastParameter).dot(b.tangentAt(b.FirstParameter))>1-1e-7
            first=edges[0];path=Part.Wire(edges)
            shape=path.makePipeShell([Part.Wire([Part.makeCircle(od/2,first.valueAt(first.FirstParameter),first.tangentAt(first.FirstParameter))])],True,False)
            assert shape.isValid() and len(shape.Solids)==1 and not shape.check(True)
            return shape,path.Length
        changed={}
        for h in allocation['holders']:
            n=h['holder'];axis=A.Vector(*h['axis']);p=A.Vector(*h['output_mm'])
            a=p+axis*20;c=a+A.Vector(0,0,-6);b=c+axis*6;cut=b+A.Vector(0,0,-15)
            mid=c+(axis+A.Vector(0,0,1))*(6/math.sqrt(2))
            parts=[dict(kind='line',start=list(p),end=list(a)),
                   dict(kind='arc',start=list(a),mid=list(mid),end=list(b)),
                   dict(kind='line',start=list(b),end=list(cut))]
            targets[n+'/output'],_=pipe(parts,4)
            targets[n+'/sleeve']=Part.makeCylinder(3,26.5,cut+A.Vector(0,0,14),A.Vector(0,0,-1))
            targets[n+'/new_grip']=Part.makeCylinder(1.05,21.5,cut,A.Vector(0,0,-1))
            for role in ('case','input','output','sleeve','new_grip'):
                changed[n+'/'+role]=targets[n+'/'+role]
        changed['SourceFloorReservation']=Part.makeBox(144,55,2,A.Vector(-62,-27.5,93.5))
        for ident,role,xsign in specs:
            end=A.Vector(*ports[role]['point_mm']);d=A.Vector(*ports[role]['departure']);incoming=-d
            q=end+d*9;t=A.Vector(xsign,0,0);radius=25.2
            start=q-t*radius-incoming*radius;centre=start+incoming*radius
            mid=centre+(t-incoming)*(radius/math.sqrt(2))
            parts=[dict(kind='arc',start=list(start),mid=list(mid),end=list(q)),
                   dict(kind='line',start=list(q),end=list(end))]
            shape,length=pipe(parts,4.2);changed[ident+'/entry_sector']=shape
            r['entry_rows'].append(dict(id=ident,target=role,centreline_mm=length,parts=parts,
               first_tangent=list(t),final_tangent=list(incoming),port9mm_grip=True,
               full_MTA_factory_join_extension_NOT_included=True))
        fixed={}
        # Old source module is explicitly invalidated by the hypothesis; it is
        # NOT quietly claimed to remain qualified at another height.
        for b in (doc.UpperCarrier,doc.LeftDistributionCarrier,doc.RightDistributionCarrier):fixed[b.Name]=b.Shape
        for o in doc.Objects:
            if o.Name.startswith('SourceMount') and 'Shape' in o.PropertiesList:fixed[o.Name]=o.Shape
        for o in mount.Objects:
            if 'Shape' not in o.PropertiesList or o.Shape.isNull() or o.Name in ('UpperCarrier','BUS_CP2'):continue
            if o.Name.startswith(('SourceLeftCarrier','SourceRightCarrier','SideRail','SideColumn','SideDistributionRail','F_PI_','F_AUX_','F_HY_','F_HP_','F_TY_')) or o.Name.endswith('_CurrentReference'):continue
            if o.TypeId in ('PartDesign::Body','App::Link') or o.Name.endswith('NominalPCB') or o.Name.startswith('BUSsupplier'):fixed[o.Name]=o.Shape
        for group in mount.Objects:
            if 'Group' in group.PropertiesList and 'Hardware' in group.Name and group.Name!='SideMountHardware':
                for o in group.Group:
                    if 'Shape' in o.PropertiesList and not o.Shape.isNull():fixed['hardware/'+o.Name]=o.Shape
        for o in ctx.Objects:
            if 'Shape' in o.PropertiesList and not o.Shape.isNull() and o.Name.startswith(('P0_','Head_','TailBridge','S0_','S1_')) and o.Name!='P0_MG92BMount29':fixed[o.Name]=o.Shape
        def check(n,s,m,t):
            if not s.BoundBox.intersect(t.BoundBox):return
            r['tested_pairs']+=1
            try:
                assert s.isValid() and t.isValid();hit=s.common(t);assert hit.isValid()
                if hit.Volume>1e-5:r['contacts'].append(dict(a=n,b=m,volume_mm3=hit.Volume,witness_bounds_mm=bounds(hit)))
            except Exception as e:r['errors'].append(dict(a=n,b=m,error=str(e)))
        items=list(changed.items())
        for i,(n,s) in enumerate(items):
            outside=s.cut(ctx.TorsoEnvelope.Shape);assert outside.isValid()
            if outside.Volume>1e-5:r['outside_torso'].append(dict(part=n,volume_mm3=outside.Volume))
            for m,t in {**targets,**fixed}.items():
                if n==m:continue
                # Same conductor's last9mm reservation, not a physical collision.
                if '/entry_sector' in n:
                    role=next(q['target'] for q in r['entry_rows'] if q['id']==n.split('/')[0])
                    if m=='entry/'+role:continue
                if n.endswith('/new_grip') and m==n.split('/')[0]+'/sleeve':continue
                check(n,s,m,t)
            for m,t in items[i+1:]:
                if n.split('/')[0]==m.split('/')[0] and {n.rsplit('/',1)[-1],m.rsplit('/',1)[-1]}=={'sleeve','new_grip'}:continue
                check(n,s,m,t)
        failed=any(r[k] for k in ('contacts','errors','outside_torso')) or any(q['impossible'] for q in rows)
        r['status']='SHARED_ENTRY_SPACE_CAUSE_CHANGE_REQUIRED' if failed else 'SHARED_ENTRY_SPACE_PREFLIGHT_CLEAR_FULL8FEEDS_AND_NATIVE_OPEN'
    finally:
        for d in docs:A.closeDocument(d.Name)
        r.update(worker_seconds=time.monotonic()-tick,finished_utc=datetime.now(timezone.utc).isoformat())
        PROOF.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
    assert all(sha(ROOT/n)==v for n,v in pins.items())
    print(json.dumps({k:r[k] for k in ('status','tested_pairs','contacts','errors','outside_torso','worker_seconds')}),flush=True)


if __name__=='__main__':main()
