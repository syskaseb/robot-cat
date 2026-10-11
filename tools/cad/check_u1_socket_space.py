"""One whole socketed-module space preflight, before native changes.

Use exact PCB outline/drills and rectangular supplier maximum housings/body
envelopes. A positive overlap with an envelope remains a required resolution,
NOT a claim of real part intersection. All retained material/wires included.
"""
import sys,json,time,math,hashlib
from pathlib import Path
import FreeCAD as A
import Part
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'electronics'))
import plan_u1_socket_carrier as U
from current_prototype_harness_scene import context
from plan_current_main_sources import ROOT,OUT,SHA
import plan_u1_socket_links as L
from plan_current_pwm_branch import input_recipe
from build_current_pwm_fixture import tube


def box(b):
    x,y,z,X,Y,Z=b;return Part.makeBox(X-x,Y-y,Z-z,A.Vector(x,y,z))


def run(links_only=False, top_only=False, retainer_only=False):
    tick=time.monotonic();f=OUT/'u1-socket-carrier-plan.json';p=json.loads(f.read_text())
    assert U.check(p)['chip_pins']==24
    for n,h in p['source_sha256'].items():assert SHA(ROOT/n)==h,n
    body_receipt=OUT/'u1-socket-space-checks.json'
    if links_only:
        assert SHA(body_receipt)=='f4fa4c858499e6d59aa88a2315e088cc431d51edc6ab5095cdfc14ca0f147e0d'
        previous=json.loads(body_receipt.read_text())
        assert not previous['overlaps'] and not previous['wire_clearance_resolutions'] and not previous['errors']
        signature=hashlib.sha256(json.dumps({k:p[k] for k in ('parts','adapter_local_parts','adapter','connectors')},sort_keys=True).encode()).hexdigest()
        assert signature=='3d369b79173ce0ca9342a84ab25931db591d4c9e82976322326b63f02827e1cd'
    if top_only:
        reused_local=OUT/'u1-socket-links-space.json'
        reused_hash=SHA(reused_local)
        old_local=json.loads(reused_local.read_text())
        assert not old_local['errors'] and not old_local['overlaps'] and not old_local['wire_clearance_resolutions']
        assert len(old_local['local_link_material_resolutions'])==1
        assert old_local['local_link_material_resolutions'][0]['a']=='J4'
    print('Socket preflight: loading retained current material/wires',flush=True)
    r,pins,targets,wires=context()
    print('Socket preflight: context ready',round(time.monotonic()-tick,2),flush=True)
    removed=[n for n in targets if n.startswith(('U1BoardAllowance','U1Spacer','U1Insulator','U1Mount','U1_unknown_height'))]
    for n in removed:targets.pop(n)
    # Exactly the obsolete U1 post/platform functions, not the retained floor.
    cuts=[[77,26,80.22,97,29,87.52],[77,11,87.52,97,45,90.02]]
    upper=targets['UpperCarrier001'];v0=upper.Volume
    for b in cuts:
        upper=upper.cut(box(b));print('Socket preflight: obsolete function subtraction',round(time.monotonic()-tick,2),flush=True)
    assert upper.isValid() and len(upper.Solids)==1
    targets['UpperCarrier001']=upper
    # Shared changes established by the first preflight, not an overlap waiver.
    # The socket bears on the board datum; maximum height grows UP from it.
    # Right custom printed washer loses only0.1mm of outside radius, preserving
    # neck/bore and metal-head support; native owner still must be updated.
    washer=targets['PWM160824TopInsulator'];wb=washer.BoundBox
    wx=(wb.XMin+wb.XMax)/2;wy=(wb.YMin+wb.YMax)/2
    ring=Part.makeCylinder(2.51,1.01,A.Vector(wx,wy,84.3202)).cut(Part.makeCylinder(2.4,1.01,A.Vector(wx,wy,84.3202)))
    targets['PWM160824TopInsulator']=washer.cut(ring)
    old_e2=BASE_E2=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/pwm-branch-checkpoint/selection.json'
    ep=json.loads(old_e2.read_text());changed_e2={}
    for n,x,z,y in [('XP02_module',109.37,81.,-6.35),('XP03_module',106.83,79.,-6.35)]:
        q=ep['routes'][n]['parts'][:4]
        assert abs(q[-1]['end'][2]-z)<1e-5
        q=q+input_recipe(q[-1]['end'],[x+1,y,z],[-1,0,0],11.1)['segments']
        bare=[dict(kind='arc',start=[x+1,y,z],mid=[x+1-1/math.sqrt(2),y,z+1-1/math.sqrt(2)],end=[x,y,z+1]),
              dict(kind='line',start=[x,y,z+1],end=[x,y,85.8202])]
        from current_prototype_harness_scene import wire
        for tag,parts,rad in [(n,q,.925),(n+'_bare',bare,.4060597505826003)]:
            c=wire(parts);wires['pwm-branch-checkpoint/'+tag]=(c,rad)
            changed_e2[tag]=dict(parts=parts,radius=rad,guide_mm=c.Length)
            targets.pop(tag,None)
        targets.pop(n+'_BoardInsulation',None)
    # Drill actual manufacturer pad holes, not a blanket PCB wire exception.
    pcb1=targets['PWM1608NominalPCB'];drills=[]
    for g in p['board']['groups']:
        for v in g['pads']:drills.append(Part.makeCylinder(float(v['drill'])/2,3,A.Vector(91.59+float(v['x']),float(v['y']),82.5)))
    pcb1=pcb1.cut(Part.makeCompound(drills));assert pcb1.isValid()
    targets['PWM1608NominalPCB']=pcb1
    # Validate retained bodies ONCE, not once per new resistor against the same
    # expensive carrier. This is a space check, not repeated full BOP audits.
    invalid=[n for n,t in targets.items() if not t.isValid()]
    assert not invalid,invalid
    zbase=84.3202;parts={};kinds={}
    def body(name,center,size):
        x,y,z=center;dx,dy,dz=size
        parts[name]=box([91.59+x-dx/2,y-dy/2,zbase+z-dz/2,91.59+x+dx/2,y+dy/2,zbase+z+dz/2])
        kinds[name]='supplier_max_body_or_housing_envelope'
    for y in (-11.43,3.81):
        body('Female'+str(y),[-3.81,y,4.325],[31.23,2.65,8.65])
        body('Male'+str(y),[-3.81,y,9.77],[30.48,2.54,2.54])
    #1208 exact eight straight outline segments, transformed once.
    mapping=json.loads(U.MAP.read_text());edges=[]
    def world(x,y):
        xf=17.78-x;return A.Vector(91.59-1.27-(y-17.78),-3.81+(xf-8.89),95.3602)
    for x,y,X,Y in mapping['board_outline_segments_mm']:edges.append(Part.makeLine(world(x,y),world(X,Y)))
    pcb=Part.Face(Part.Wire(edges)).extrude(A.Vector(0,0,1.6))
    for row in mapping['rows']:
        x,y=row['TSSOP_face_up_xy_mm'];xx=91.59-1.27-(y-17.78);yy=-3.81+x-8.89
        pcb=pcb.cut(Part.makeCylinder(.508,1.6,A.Vector(xx,yy,95.3602)))
    # Four unused holes retained physically, never populated or hidden.
    for x in (1.27,16.51):
        for y in (3.81,1.27):
            xx=91.59-1.27-(y-17.78);yy=-3.81+x-8.89
            pcb=pcb.cut(Part.makeCylinder(.508,1.6,A.Vector(xx,yy,95.3602)))
    assert pcb.isValid() and len(pcb.Solids)==1
    parts['Adapter1208PCB']=pcb;kinds['Adapter1208PCB']='actual_source_PCB_outline_drills_project_thickness'
    body('TI_PW_MaxBody',[-1.92,-3.81,13.24],[7.9,4.5,1.2])
    for c in p['parts']+p['adapter_local_parts']:body(c['ref'],c['body_center_local_mm'],c['body_size_mm'])
    retainer_names=[];retainer_pins=[]
    if retainer_only:
        import build_u1_socket_retainer as T
        rf=OUT/'u1-socket-retainer-native.json';rp=json.loads(rf.read_text())
        nf=ROOT/rp['native'];assert SHA(nf)==rp['native_sha256']
        doc=A.openDocument(str(nf))
        for n in ('AnchorLeft','AnchorRight','RetainerBar'):
            parts[n]=doc.getObject(n).Shape.copy();kinds[n]='native_editable_PETG_candidate';retainer_names.append(n)
        A.closeDocument(doc.Name)
        refs,facts=T.references()
        for n,s in refs.items():parts[n]=s;kinds[n]='nominal_installed_retention_reference';retainer_names.append(n)
        for n in rp['replaces']:targets.pop(n)
        retainer_pins=[nf,rf,facts,Path(T.__file__)]
    out=dict(status='PENDING',selected=False,E1_complete=False,E2_requalified=False,physical_pass=False,
             removed_old_objects=removed,obsolete_U1_function_cuts_mm=cuts,
             old_carrier_volume_mm3=v0,new_carrier_volume_mm3=upper.Volume,
             changed_E2_routes=changed_e2,right_printed_insulator_OD_mm=4.8,
             parts=len(parts),pairs=0,overlaps=[],wire_clearance_resolutions=[],errors=[],
             intentionally_mating=['Male against Female row: insertion/housing seating; stack tolerances remainOPEN',
                                  'TI_PW_MaxBody at Adapter1208PCB top face, zero penetration expected'],
             not_covered=['Local C1/C2 formed leads','Chip/header pins and solder joints','Independent external grips',
                          'Actual socket withdrawal/tool path/retention stop','Changed native carrier and complete E2 board ends'],
             scope='Whole changed body/housing envelope preflight, not full actual lead/native/assembly acceptance')
    names=list(parts)
    selected_names=retainer_names if retainer_only else [] if links_only else names
    for a in selected_names:
        i=names.index(a)
        s=parts[a]
        prior_parts=[n for n in names[:i] if n not in retainer_names] if retainer_only else []
        for b,t in list(targets.items())+[(n,parts[n]) for n in prior_parts+names[i+1:]]:
            if a.startswith('Female') and b=='Male'+a.removeprefix('Female'):continue
            if {a,b}=={'Adapter1208PCB','TI_PW_MaxBody'}:continue
            if a.startswith('Female') and b=='PWM1608NominalPCB':
                assert s.BoundBox.ZMin>=t.BoundBox.ZMax-1e-6
                continue  # Defined bottom-face bearing; tails checked separately.
            mating=retainer_only and (
                (a.startswith('Anchor') and (b=='PWM1608NominalPCB' or b in ('PWM160824Screw','PWM160825Screw')))
                or (a.startswith('Foam') and b in ('Adapter1208PCB','RetainerBar'))
                or (a=='RetainerBar' and b.startswith(('Foam','Band','Head')))
                or (a.startswith('Band') and b=='Head'+a.removeprefix('Band')))
            if not s.BoundBox.intersect(t.BoundBox):continue
            out['pairs']+=1
            try:
                dist=s.distToShape(t)[0]
                if dist<.05 and mating:
                    assert s.common(t).Volume<1e-5,('Intended bearing must not penetrate',a,b)
                elif dist<.05:out['overlaps'].append(dict(a=a,b=b,distance_mm=dist,
                    interpretation='Conservative envelope has<0.05mm gap: touching or overlapping, NOT disambiguated as actual part collision. Resolve interface before detailed CAD.'))
            except Exception as e:out['errors'].append(dict(a=a,b=b,error=repr(e)))
        print('Socket preflight body',a,'pairs',out['pairs'],'resolutions',len(out['overlaps'])+len(out['wire_clearance_resolutions']),round(time.monotonic()-tick,2),flush=True)
        if retainer_only:
            print('Retainer issues',json.dumps([v for v in out['overlaps']+out['wire_clearance_resolutions'] if v['a']==a]),flush=True)
        for b,(c,rad) in wires.items():
            bb=s.BoundBox;bb.enlarge(rad)
            if not bb.intersect(c.BoundBox):continue
            out['pairs']+=1
            try:
                dist=c.distToShape(s)[0]
                if dist<rad-1e-5:out['wire_clearance_resolutions'].append(dict(a=a,b=b,distance_mm=dist,required_mm=rad))
            except Exception as e:out['errors'].append(dict(a=a,b=b,error=repr(e)))
    # Whole planned underside links against retained matter, every new body,
    # re-bound E2 tails and every other external conductor.
    lf=OUT/'u1-socket-links-plan.json';lp=json.loads(lf.read_text());assert not lp['conflicts']
    links={q['ref']:(L.path(q['start_mm'],q['end_mm'],q['underside_plane_world_mm'],q['via_xy_mm']),.4) for q in lp['links']}
    bus=lp['ground_bus']['centreline_mm'];links['JG_COMB']=(Part.makeLine(*[A.Vector(*v) for v in bus]),.25)
    out['local_link_material_resolutions']=[]
    for a,(c,rad) in links.items():
        if top_only and a not in ('J2','J4'):continue
        link_targets={n:parts[n] for n in retainer_names} if retainer_only else {**targets,**parts}
        for b,s in link_targets.items():
            bb=s.BoundBox;bb.enlarge(rad)
            if not bb.intersect(c.BoundBox):continue
            out['pairs']+=1;dist=c.distToShape(s)[0]
            if dist<rad-1e-5:out['local_link_material_resolutions'].append(dict(a=a,b=b,distance_mm=dist,required_mm=rad))
        for b,(d,rr) in ([] if retainer_only else wires.items()):
            bb=d.BoundBox;bb.enlarge(rad+rr)
            if not bb.intersect(c.BoundBox):continue
            out['pairs']+=1;dist=c.distToShape(d)[0]
            if dist<rad+rr-1e-5:out['local_link_material_resolutions'].append(dict(a=a,b=b,distance_mm=dist,required_mm=rad+rr))
        print('Socket local link',a,'pairs',out['pairs'],'resolutions',len(out['local_link_material_resolutions']),round(time.monotonic()-tick,2),flush=True)
    out['status']='SOCKET_MODULE_BODY_SPACE_REQUIRES_CHANGE' if any(out[k] for k in ('overlaps','wire_clearance_resolutions','local_link_material_resolutions','errors')) else 'SOCKET_MODULE_BODY_AND_LOCAL_LINK_SPACE_CLEAR_PASSIVE_LEADS_NATIVE_OPEN'
    pins.update((Path(__file__),f,U.POP,U.MAP,U.SIGNAL,Path(U.__file__),Path(L.__file__),lf,old_e2,*retainer_pins))
    if links_only:
        pins.add(body_receipt);out['reused_body_subset']=dict(receipt=body_receipt.relative_to(ROOT).as_posix(),sha256=SHA(body_receipt),
            geometry_signature=signature,scope='Unchanged25bodies, reboundE2 ends and4.8mm right insulator only; rejected old link subset explicitly NOT reused')
    if top_only:
        out['reused_local_subset']=dict(receipt=reused_local.relative_to(ROOT).as_posix(),sha256=reused_hash,
            scope='Nine unchanged underside links: allocation is isolated from top layer by>0.95mm. Both top routes J2/J4 rechecked together after adding both actual screw heads.')
        out['checked_local_geometry']={n:q for n,q in links_plan_geometry(lp).items()}
    if retainer_only:
        top=OUT/'u1-socket-top-links-space.json';tp=json.loads(top.read_text())
        assert not tp['local_link_material_resolutions'] and not tp['errors']
        assert tp['checked_local_geometry']==links_plan_geometry(lp)
        out['reused_local_subset']=dict(receipt=top.relative_to(ROOT).as_posix(),sha256=SHA(top),
            scope='All11local curves vs retained context; changed retainer checked separately against every curve')
        out['retainer_parts']=retainer_names;pins.add(top)
    out['source_sha256']={**r.hashes,**{f.relative_to(ROOT).as_posix():SHA(f) for f in pins}}
    out['worker_seconds']=round(time.monotonic()-tick,3)
    (OUT/('u1-socket-retainer-space.json' if retainer_only else 'u1-socket-top-links-space.json' if top_only else 'u1-socket-links-space.json' if links_only else 'u1-socket-space-checks.json')).write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:out[k] for k in ('status','parts','pairs','overlaps','wire_clearance_resolutions','local_link_material_resolutions','errors','worker_seconds')}),flush=True)


def links_plan_geometry(p):
    return {q['ref']:{k:q[k] for k in ('start_mm','end_mm','underside_plane_world_mm','via_xy_mm')} for q in p['links']}


if __name__=='__main__':run(any(q in sys.argv for q in ('--links-only','--top-only','--retainer-only')),'--top-only' in sys.argv,'--retainer-only' in sys.argv)
