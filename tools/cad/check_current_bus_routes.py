"""Scoped actual BUS material gate, shared carrier passage and one cable jaw.

No old proof is rerun. The movable leg harness remains a nominal reference;
this result does not qualify its motion or the complete W5 release.
"""
import json,time,sys,hashlib
from pathlib import Path
from plan_current_main_sources import ROOT,BASE,OUT,SHA

def run():
    tick=time.monotonic();f=OUT/'BUS-routes-plan.json';p=json.loads(f.read_text())
    assert p['status']=='BUS_SHARED_NOMINAL_CHANNELS_ONLY' and not p['rejected']
    for n,h in p['source_sha256'].items():assert SHA(ROOT/n)==h,n
    from current_complete_harness_context import context,W,Part
    from current_body_harness_context import clipped
    from plan_current_tail_complete import tie_z
    A=W.A;reader,pins,targets,old=context();pins.update((f,Path(__file__)))
    def wire(parts):
        edges=[]
        for q in parts:
            if q['kind']=='bezier':
                c=Part.BezierCurve();c.setPoles([A.Vector(*v) for v in q['poles_mm']]);edges.append(c.toShape())
            else:edges.extend(W.makewire([q]).Edges)
        s=Part.Wire(edges);assert s.isValid();return s
    original=targets['UpperCarrier001'];cols=[];tools=[]
    for n,prefix in p['source_prefixes'].items():
        c=wire(prefix[:2]);e=c.Edges[0]
        pipe=c.makePipeShell([Part.Wire([Part.makeCircle(1.6,e.valueAt(e.FirstParameter),e.tangentAt(e.FirstParameter))])],True,False)
        slab=Part.makeBox(30,40,3.4,A.Vector(45,-40,74.52))
        tool=pipe.common(slab);assert tool.isValid();tools.append(tool)
        cols.append(prefix[2]['start'])
    # Shared jaw rooted on the actual carrier, not on PCB pads or levers.
    x=sum(c[0] for c in cols)/2;y=sum(c[1] for c in cols)/2;z=cols[0][2]+4.5
    pads=[dict(name='BUSRoot',bounds_mm=[x-5,-24,77.71,x-3,-18,z+3.5]),
          dict(name='BUSBacker',bounds_mm=[x-5,min(c[1] for c in cols)-3,z-3.5,x-1.05,max(c[1] for c in cols)+3,z+3.5])]
    band,head=tie_z(z,x-5.8,x+2.3,min(c[1] for c in cols)-2.2,max(c[1] for c in cols)+2.2)
    # Ring return passes through the jaw; preserve the central vertical web.
    slot=band.makeOffsetShape(.15,.01)
    assert slot.isValid()
    altered=original.fuse(W.box(pads[0]['bounds_mm'])).fuse(W.box(pads[1]['bounds_mm']))
    for tool in tools+[slot]:altered=altered.cut(tool)
    altered=altered.removeSplitter();assert altered.isValid() and len(altered.Solids)==1
    targets['UpperCarrier001']=altered
    grip={'BUSBand':band,'BUSHead':head}
    new={n:wire(r['parts']) for n,r in p['routes'].items()}
    cf=OUT/'leg-fanout-channels-plan.json';lf=OUT/'joined-leg-looms-plan.json'
    cp=json.loads(cf.read_text());looms=json.loads(lf.read_text());pins.update((cf,lf))
    nominal={}
    for row in looms['looms']:
        v=next(v for v in row['poses'] if not any(v['angles']));parts=[]
        if row['initial_land_mm']:parts.append(dict(kind='line',start=v['start'],end=v['flex_start']))
        parts.extend(v['departure_parts_mm']);parts.extend(v.get('transition_parts_mm',[]))
        parts.extend(dict(kind='bezier',poles_mm=q) for q in v['spans_mm']);parts.extend(v.get('return_parts_mm',[]))
        nominal['Loom/'+row['loom']]=(wire(parts),3)
    nominal.update({n:(wire(r['parts']),1) for n,r in cp['routes'].items()})
    result=dict(status='PENDING',contacts=[],errors=[],pairs=0,selected=False,W5_complete=False,
        physical_pass=False,actual_nominal_leg_paths=48,sampled_leg_motion_checked=False,
        passage_tools=[dict(bounds_mm=[getattr(t.BoundBox,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')],volume_mm3=t.Volume) for t in tools],
        shared_grip_pads=pads,shared_grip_T18I=1,service_spare_T18I=1,
        provisional_plug_fit_open=True,native_changed=False,bearing_checks=[])
    if '--space-only' in sys.argv:
        # Surface boxes are CONSERVATIVE ROUTING reservations, not collision
        # evidence. Unlike whole-part boxes they do not fill every empty room
        # of an open carrier just because it has a tall post elsewhere.
        boxes=[]
        for name,s in {**targets,**grip}.items():
            if not s.Solids:continue
            assert s.isValid(),name
            for face in s.Faces:
                b=face.BoundBox
                boxes.append(dict(owner=name,bounds_mm=[getattr(b,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]))
        recipe=dict(source_prefix_first_three={n:q[:3] for n,q in p['source_prefixes'].items()},
            jaw_pads=pads,band_centre_mm=[x,y,z])
        spatial=dict(status='CURRENT_MATERIAL_SURFACE_ROUTING_RESERVATIONS_ONLY',boxes=boxes,
            conservative_boxes_not_material_collision_proof=True,geometry_recipe=recipe,
            geometry_recipe_sha256=hashlib.sha256(json.dumps(recipe,sort_keys=True).encode()).hexdigest(),
            selected=False,W5_complete=False,physical_pass=False,worker_seconds=time.monotonic()-tick,
            source_sha256={**reader.hashes,**{q.relative_to(ROOT).as_posix():SHA(q) for q in pins if q!=f}})
        (OUT/'BUS-material-routing-space.json').write_text(json.dumps(spatial,separators=(',',':'))+'\n',encoding='utf-8',newline='\n')
        print(json.dumps(dict(status=spatial['status'],faces=len(boxes),seconds=spatial['worker_seconds'])),flush=True)
        return spatial
    def pair(n,c,rr,m,t,rad=0):
        if not W.near(c,t,rr+rad):return
        assert c.isValid() and t.isValid(),(n,m);result['pairs']+=1
        d,pts,_=c.distToShape(t)
        if d<rr+rad-1e-4:result['contacts'].append(dict(a=n,b=m,distance_mm=d,required_mm=rr+rad,
            witness_mm=[list(v) for v in pts[0]] if pts else None))
    for n,c in new.items():
        role=p['routes'][n]['endpoints'][-1];receiver=role.split('.')[0]
        for m,t in targets.items():
            if t.Solids:pair(n,clipped(c,False,3) if m in (receiver,receiver+'_CP2','W1Ref_'+receiver+'_CP2') else c,1,m,t)
        for m,(t,rad) in {**old,**nominal}.items():pair(n,c,1,m,t,rad)
        for m,t in grip.items():pair(n,c,1,m,t)
        print('BUS complete',n,'contacts',len(result['contacts']),flush=True)
    extra=altered.cut(original);assert extra.isValid()
    for n,s in {'BUSNewMaterial':extra,**grip}.items():
        for m,t in targets.items():
            if m=='UpperCarrier001' or not t.Solids:continue
            pair(n,s,0,m,t)
        for m,(c,rr) in {**old,**nominal}.items():pair(m,c,rr,n,s)
    # Material-to-material dist0 does not distinguish touching from overlap.
    # Exact common volumes are the relevant test for newly added jaw/bands.
    for n,s in {'BUSNewMaterial':extra,**grip}.items():
        for m,t in targets.items():
            if m=='UpperCarrier001' or not t.Solids or not s.BoundBox.intersect(t.BoundBox):continue
            hit=s.common(t);assert hit.isValid()
            if hit.Volume>1e-5:result['contacts'].append(dict(a=n,b=m,volume_mm3=hit.Volume))
    mp=BASE/'mounting-checkpoint/board-mount-plan.json';mounts=json.loads(mp.read_text());pins.add(mp)
    for board,axes in mounts['board_hole_axes_world_xy_mm'].items():
        if board in ('Pi4','BUS'):continue
        zz=mounts['pcb_bottom_planes_mm'][board]
        for xx,yy in axes:
            ring=Part.makeCylinder(2.15,.2,A.Vector(xx,yy,zz-.2)).cut(Part.makeCylinder(1.2,.2,A.Vector(xx,yy,zz-.2)))
            before=original.common(ring).Volume;after=altered.common(ring).Volume
            assert before>1e-5 and abs(before-after)<1e-5,(board,xx,yy)
            result['bearing_checks'].append(dict(board=board,axis=[xx,yy],volume_mm3=after))
    result.update(status='REJECTED_BUS_ACTUAL_MATERIAL' if result['contacts'] else 'BUS_NOMINAL_MATERIAL_AND_JAW_CLEAR_NATIVE_OPEN',
        worker_seconds=time.monotonic()-tick,
        source_sha256={**reader.hashes,**{q.relative_to(ROOT).as_posix():SHA(q) for q in pins}})
    (OUT/'BUS-routes-checks.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(status=result['status'],pairs=result['pairs'],contacts=result['contacts'],seconds=result['worker_seconds'])),flush=True)
    return result

if __name__=='__main__':run()
