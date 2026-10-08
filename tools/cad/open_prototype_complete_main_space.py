"""One complete eight-feed macro layout, before native support reconstruction.

Separates receiving galleries from five source cases. All paths include both
MTA exits, factory sections, real connector roles and HELU receiving ends.
This is a hypothesis; no stock or native selection follows from a saved plan.
"""
from datetime import datetime, timezone
from pathlib import Path
import copy, json, math, time
from open_prototype_wiring_endpoints import ROOT, BASE, read, sha, bounds
from open_prototype_bundle_spines import add, sub, mul, unit
from open_prototype_distribution_allocation import input_recipe

OUT = BASE/'wiring-checkpoint'
PLAN = OUT/'complete-main-space-plan.json'
PROOF = OUT/'complete-main-space-checks.json'


def line(a, b):
    assert math.dist(a, b) > 1e-7
    return dict(kind='line', start=list(a), end=list(b))


def half_turn(start, tangent, displacement):
    """A tangent 180 degree circular bend in an arbitrary transverse plane."""
    assert abs(sum(x*y for x,y in zip(tangent,displacement))) < 1e-7
    radius = math.dist([0,0,0], displacement)/2
    centre = add(start, mul(displacement,.5))
    return dict(kind='arc', start=start, mid=add(centre,mul(tangent,radius)),
                end=add(start,displacement), radius_mm=radius)


def quarter(start, tangent, final, radius):
    assert abs(sum(x*y for x,y in zip(tangent,final))) < 1e-7
    centre = add(start,mul(final,radius))
    return dict(kind='arc',start=start,
        mid=add(centre,mul(sub(tangent,final),radius/math.sqrt(2))),
        end=add(start,mul(add(tangent,final),radius)),radius_mm=radius)


def factory_reverse(start, tangent, displacement, radius=6):
    """Two small factory bends and a straight transverse leg, not a broad coil.

    HELU never uses this radius. The factory radius is explicitly provisional.
    """
    span=math.dist([0,0,0],displacement)
    assert span>=2*radius, 'No room for the retained factory radius'
    transverse=unit(displacement)
    first=quarter(start,tangent,transverse,radius)
    result=[first];second_start=add(first['end'],mul(transverse,span-2*radius))
    if span>2*radius+1e-7:result.append(line(first['end'],second_start))
    result.append(quarter(second_start,transverse,mul(tangent,-1),radius))
    assert math.dist(result[-1]['end'],add(start,displacement))<1e-7
    return result


def length(parts):
    return sum(math.dist(q['start'],q['end']) if q['kind']=='line' else
        (math.pi if math.dist(q['start'],q['end']) > 1.99*q['radius_mm'] else math.pi/2)*q['radius_mm']
        for q in parts)


def build():
    allocation=read(OUT/'shared-allocation-plan.json')
    ports={p['role']:copy.deepcopy(p) for p in read(OUT/'shared-allocation-checks.json')['ports']}
    distribution=copy.deepcopy(allocation['distribution'])
    for row in distribution:
        if row['role'] in ('P_SYS','P_REAR','P_FRONT','P_AUX'):
            row['centre_mm'][0]+=60;row['centre_mm'][2]=145
        if row['role'] in ('G2','D_RR'):
            row['centre_mm'][1]=43 if row['side']=='L' else -43
    for p in ports.values():
        role=p['role'].split('.')[0]
        if role in ('P_SYS','P_REAR','P_FRONT','P_AUX'):
            p['point_mm'][0]+=60;p['point_mm'][2]=145
        if role in ('G2','D_RR'):
            p['point_mm'][1]+=23 if p['point_mm'][1]>0 else -23
    # Only same-net port permutation. Keep every other port explicitly mapped.
    remap={'P_REAR.5':'P_REAR.1','P_REAR.1':'P_REAR.2','P_REAR.2':'P_REAR.5',
           'P_FRONT.3':'P_FRONT.5','P_FRONT.5':'P_FRONT.3'}
    mapping=[dict(original=p['role'],current=remap.get(p['role'],p['role']),
                  point_mm=ports[remap.get(p['role'],p['role'])]['point_mm'])
             for p in read(OUT/'shared-allocation-checks.json')['ports']]
    holders=[]
    for name,x,y,z,target in [('F_PI',6.5,36.25,136,'P_SYS.2'),
            ('F_AUX',53,36.25,136,'P_REAR.3'),
            ('F_HY',70,-36.25,115,'P_AUX.2'),
            ('F_HP',95,-36.25,115,'P_AUX.3'),
            ('F_TY',120,-36.25,115,'P_AUX.4')]:
        start=[x,y,z];end=ports[target]['point_mm']
        if y>0:
            a=add(start,[0,0,3]);arc=quarter(a,[0,0,1],[0,1,0],6)
            parts=[line(start,a),arc,line(arc['end'],end)]
            centreline=3+math.pi*3+9
        else:
            arcstart=[end[0],-37.75,139]
            inlet=input_recipe(start,arcstart,[0,0,1],6)
            arc=quarter(arcstart,[0,0,1],[0,-1,0],6)
            parts=inlet['segments']+[arc,line(arc['end'],end)]
            centreline=inlet['centreline_mm']+math.pi*3+9
        strip=14 if y>0 else 11;limit=50 if y>0 else 84.5
        holders.append(dict(holder=name,axis=[0,0,-1],input_mm=start,
            output_mm=add(start,[0,0,-51]),target=target,input_parts=parts,
            input_centreline_mm=centreline,strip_mm=strip,blank_mm=centreline+strip,
            project_blank_limit_mm=limit,exceeds_project_limit=centreline+strip>limit))
    mts=[]
    for n,c in [('MTA_FL_CP2',[-30,12,115]),('MTA_FR_CP2',[-30,-12,115]),
                ('MTA_RL_CP2',[135,18,125]),('MTA_RR_CP2',[135,-18,125])]:
        original=next(q for q in allocation['mts'] if q['native']==n)
        mts.append(dict(original,centre_mm=c))
    feeds=[]
    # Nested, concentric upper receiving arcs: no coincident approach straights.
    specs=[('W041','FL','P_FRONT.2',-29.45),('W042','FR','P_FRONT.5',-48.95),
           ('W044','RL','P_REAR.1',17.05),('W052','RR','P_REAR.5',-8.95)]
    for ident,leg,role,lane in specs:
        m=next(q for q in mts if q['native']=='MTA_'+leg+'_CP2')['centre_mm']
        start=add(m,[-17.5,0,0]);direction=[-1,0,0]
        if leg in ('FL','FR'):
            a=add(start,[-9,0,0]);reverse=factory_reverse(a,direction,[0,lane-m[1],145-m[2]])
            cut=add(reverse[-1]['end'],[17,0,0])
            factory=[line(start,a)]+reverse+[line(reverse[-1]['end'],cut)]
            upperstart=[14.8,lane,145]
            extension=[line(cut,upperstart)]
        else:
            # Input uses RIGHT factory side in the rear; output uses LEFT.
            start=add(m,[17.5,0,0]);a=add(start,[9,0,0])
            reverse=factory_reverse(a,[1,0,0],[0,0,89-m[2]])
            cut=add(reverse[-1]['end'],[-17,0,0])
            factory=[line(start,a)]+reverse+[line(reverse[-1]['end'],cut)]
            low=[14.8,m[1],89];lift=half_turn(low,direction,[0,lane-m[1],56])
            upperstart=lift['end'];extension=[line(cut,low),lift]
        end=ports[role]['point_mm'];radius=end[0]-14.8
        arc=quarter(upperstart,[1,0,0],[0,1,0],radius)
        extension += [arc,line(arc['end'],end)]
        factory_mm=length(factory)
        feeds.append(dict(id=ident,leg=leg,side='source',target=role,
            factory_parts=factory,extension_parts=extension,factory_centreline_mm=factory_mm,
            factory_blank_mm=factory_mm+8,assumed_factory_budget_mm=100,
            exceeds_ASSUMED_not_catalog_factory_budget=factory_mm+8>100,
            factory_radius_assumption_mm=6,extension_min_radius_mm=25.2,
            joint=dict(kind='solder_lap',sku='TE5053142077',lap_mm=8,sleeve_mm=26,
                       centreline_cut_mm=cut,axis=[1,0,0] if leg in ('FL','FR') else [-1,0,0]),
            extra_FL_extension_and_lap_is_candidate_not_stock_selection=leg=='FL'))
    for ident,leg,role in [('W026','FL','FL_P.1'),('W037','FR','FR_P.1'),
                           ('W045','RL','RL_P.1'),('W053','RR','RR_P.1')]:
        m=next(q for q in mts if q['native']=='MTA_'+leg+'_CP2')['centre_mm']
        sign=1 if leg in ('FL','RL') else -1
        front=leg in ('FL','FR');direction=[1 if front else -1,0,0]
        start=add(m,mul(direction,17.5));a=add(start,mul(direction,9))
        z=128.4 if front else 138.4;wire_y=sign*10;factory_y=sign*16.5
        reverse=factory_reverse(a,direction,[0,factory_y-m[1],z-m[2]])
        jointx=-55.3 if front else 125
        factory_end=[jointx,factory_y,z]
        factory=[line(start,a)]+reverse+[line(reverse[-1]['end'],factory_end)]
        joint=[jointx,wire_y,z];end=ports[role]['point_mm']
        tangent=[1 if front else -1,0,0]
        receive=[end[0]+(25.2 if front else -25.2),sign*31.3,67.99]
        top=[receive[0],wire_y,z]
        turn=half_turn(top,tangent,[0,receive[1]-wire_y,receive[2]-z])
        quarter_arc=quarter(turn['end'],mul(tangent,-1),[0,sign,0],25.2)
        extension=[line(joint,top),turn,quarter_arc,line(quarter_arc['end'],end)]
        factory_mm=length(factory)
        feeds.append(dict(id=ident,leg=leg,side='output',target=role,
            factory_parts=factory,extension_parts=extension,factory_centreline_mm=factory_mm,
            factory_blank_mm=factory_mm+11,assumed_factory_budget_mm=100,
            exceeds_ASSUMED_not_catalog_factory_budget=factory_mm+11>100,
            factory_radius_assumption_mm=6,extension_min_radius_mm=25.2,
            joint=dict(kind='WAGO221-412',installed_existing_role=leg+'_OUTPUT',
                factory_port_mm=factory_end,extension_port_mm=joint,
                case_x_mm=[jointx-13,jointx] if front else [jointx,jointx+13],
                case_y_mm=[sign*13.25-9.15,sign*13.25+9.15],case_z_mm=[z-4.075,z+4.075],
                port_frame_is_project_reservation_not_delivered_datum=True)))
    return dict(status='COMPLETE8FEED_MACRO_HYPOTHESIS_NOT_SELECTED',selected=False,
        stage_completed=False,physical_pass=False,distribution=distribution,
        ports=list(ports.values()),port_mapping=mapping,holders=holders,mts=mts,feeds=feeds,
        assumptions=['All factory lead lengths100mm/OD4/radius6 remain delivery gates',
            'HELU4mm2 project OD4.2/radius25.2 retained, not supplier radius certification',
            '221-412 real SKU/case18.3x13x8.15; connector entry frame is provisional',
            'Solder laps use actual RNF-100-3/8,26mm sleeve/8mm lap process gates'],
        invalidated=['All relocated WAGO mounts and their existing fanouts',
            'CommonSourcePlatform/4MTA mounts and source inputs/output drops',
            'Old WAGO port positions for changed roles; topology and untouched sources retained'],
        assembly=['Prewire connected groups on bench; bolt platform/rails before board installation',
            'Allocate independent lead restraints around straight factory/HELU joint sections, never WAGO levers',
            'Vertical FHAC requires supported bottom and two case bands; use open roof for ATO service',
            'No routine74-WAGO disconnection; retain local ATO access with wiring in place'],
        remaining=['New common support load paths and reliefs/native CAD',
            'Whole auxiliary output continuation/head/tail/S1/PWM/body/legs/stock',
            'Actual U1/S0 pinout; provisional holder/joint/grip/ATO motion'],
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in
            (OUT/'shared-allocation-plan.json',OUT/'shared-allocation-checks.json',Path(__file__))})


def main():
    import FreeCAD as A
    import Part
    from open_prototype_entry_chambers import MOUNTS, CONTEXT
    tick=time.monotonic()
    assert not PLAN.exists() and not PROOF.exists(),'Receive existing whole macro plan, no unchanged rerun'
    plan=build();PLAN.write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')
    docs=[A.openDocument(str(p)) for p in (MOUNTS,CONTEXT)]
    mount,ctx=docs;items={};owners={};actual={};r=dict(status='PENDING',selected=False,
        stage_completed=False,physical_pass=False,contacts=[],errors=[],outside=[],pairs=0,
        paths=[],source_sha256=dict(plan['source_sha256'],**{
            p.relative_to(ROOT).as_posix():sha(p) for p in (MOUNTS,CONTEXT)}))
    def put(name,s,owner):
        assert s.isValid() and len(s.Solids)==1 and not s.check(True),name
        items[name]=s;owners[name]=owner
    def pipe(name,parts,od,owner):
        edges=[Part.makeLine(A.Vector(*q['start']),A.Vector(*q['end'])) if q['kind']=='line'
               else Part.Arc(A.Vector(*q['start']),A.Vector(*q['mid']),A.Vector(*q['end'])).toShape() for q in parts]
        for e,f in zip(edges,edges[1:]):
            assert e.tangentAt(e.LastParameter).dot(f.tangentAt(f.FirstParameter))>1-1e-7,name
        path=Part.Wire(edges);first=edges[0]
        shape=path.makePipeShell([Part.Wire([Part.makeCircle(od/2,
            first.valueAt(first.FirstParameter),first.tangentAt(first.FirstParameter))])],True,False)
        put(name,shape,owner)
        radii=[e.Curve.Radius for e in edges if isinstance(e.Curve,Part.Circle)]
        r['paths'].append(dict(name=name,centreline_mm=path.Length,
                              min_radius_mm=min(radii) if radii else None))
    try:
        for q in plan['distribution']+plan['mts']:
            ob=mount.getObject(q['native']) or ctx.getObject(q['native']);s=ob.Shape.copy();b=s.BoundBox
            s.translate(A.Vector(*q['centre_mm'])-A.Vector((b.XMin+b.XMax)/2,(b.YMin+b.YMax)/2,(b.ZMin+b.ZMax)/2))
            put(q['native'],s,q['native'])
        for q in plan['holders']:
            n=q['holder'];s=mount.getObject(n+'_body_budget_CurrentReference').Shape.copy();b=s.BoundBox
            s.translate(-A.Vector((b.XMin+b.XMax)/2,(b.YMin+b.YMax)/2,(b.ZMin+b.ZMax)/2))
            rot=A.Rotation(A.Vector(1,0,0),A.Vector(*q['axis']))
            s.rotate(A.Vector(),rot.Axis,rot.Angle*180/math.pi)
            s.translate(A.Vector(*q['input_mm'])+A.Vector(*q['axis'])*25.5+rot.multVec(A.Vector(0,0,1)))
            put(n+'/case',s,n+'/case');pipe(n+'/input',q['input_parts'],4,n+'/input')
            # Straight output sleeve/first new-wire grip only; load continuation open.
            p=A.Vector(*q['output_mm']);cut=p+A.Vector(0,0,-22)
            put(n+'/output',Part.makeCylinder(2,22,p,A.Vector(0,0,-1)),n+'/output')
            put(n+'/output_sleeve',Part.makeCylinder(3,26.5,cut+A.Vector(0,0,14),A.Vector(0,0,-1)),n+'/output')
        for q in plan['feeds']:
            n=q['id'];pipe(n+'/factory',q['factory_parts'],4,n)
            pipe(n+'/HELU',q['extension_parts'],4.2,n)
            j=q['joint']
            if j['kind']=='solder_lap':
                p=A.Vector(*j['centreline_cut_mm']);axis=A.Vector(*j['axis'])
                put(n+'/sleeve',Part.makeCylinder(4.5,26,p-axis*14,axis),n)
            else:
                x,y,z=j['case_x_mm'],j['case_y_mm'],j['case_z_mm']
                put(n+'/221412',Part.makeBox(x[1]-x[0],y[1]-y[0],z[1]-z[0],A.Vector(x[0],y[0],z[0])),n+'/connector')
        for ob in mount.Objects:
            if 'Shape' not in ob.PropertiesList or ob.Shape.isNull():continue
            if ob.Name=='BUS_CP2' or ob.Name.endswith('_CurrentReference'):continue
            if ob.Name.startswith(('SourceLeft','SourceRight','F_PI_','F_AUX_','F_HY_','F_HP_','F_TY_','SideRail','SideColumn','SideDistribution','SideMount')):continue
            if ob.TypeId in ('PartDesign::Body','App::Link') or ob.Name.endswith('NominalPCB') or ob.Name.startswith('BUSsupplier'):
                actual[ob.Name]=ob.Shape
        for ob in ctx.Objects:
            if 'Shape' in ob.PropertiesList and not ob.Shape.isNull() and ob.Name.startswith(('P0_','Head_','TailBridge','S0_','S1_')) and ob.Name!='P0_MG92BMount29':actual[ob.Name]=ob.Shape
        def check(n,s,m,t):
            if not s.BoundBox.intersect(t.BoundBox):return
            r['pairs']+=1
            try:
                assert s.isValid() and t.isValid();hit=s.common(t);assert hit.isValid()
                if hit.Volume>1e-5:r['contacts'].append(dict(a=n,b=m,volume_mm3=hit.Volume,bounds_mm=bounds(hit)))
            except Exception as e:r['errors'].append(dict(a=n,b=m,error=str(e)))
        pairs=list(items.items())
        for i,(n,s) in enumerate(pairs):
            outside=s.cut(ctx.TorsoEnvelope.Shape);assert outside.isValid()
            if outside.Volume>1e-5:r['outside'].append(dict(part=n,volume_mm3=outside.Volume))
            for m,t in actual.items():check(n,s,m,t)
            for m,t in pairs[i+1:]:
                if owners[n]==owners[m]:continue # Same conductor's insulation/joint.
                if m.endswith('/221412') or n.endswith('/221412'):
                    if n.split('/')[0]==m.split('/')[0]:continue # Intended entry at own case face.
                check(n,s,m,t)
        r['assumed_factory_budget_exceeded']=[q['id'] for q in plan['feeds'] if q['exceeds_ASSUMED_not_catalog_factory_budget']]
        r['prefuse_limit_exceeded']=[q['holder'] for q in plan['holders'] if q['exceeds_project_limit']]
        r['status']='MACRO_LAYOUT_REQUIRES_CAUSE_CHANGE' if any(r[k] for k in
            ('contacts','errors','outside','assumed_factory_budget_exceeded','prefuse_limit_exceeded')) else 'MACRO8FEED_SPACE_CLEAR_SUPPORTS_AND_REMAINING_WIRING_OPEN'
    finally:
        for d in docs:A.closeDocument(d.Name)
        r.update(worker_seconds=time.monotonic()-tick,finished_utc=datetime.now(timezone.utc).isoformat())
        PROOF.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:r[k] for k in ('status','pairs','contacts','errors','outside','assumed_factory_budget_exceeded','prefuse_limit_exceeded','worker_seconds')}),flush=True)


if __name__=='__main__':main()
