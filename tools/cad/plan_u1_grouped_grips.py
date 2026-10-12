"""Coupled removable GPIO/PCA insulation grips on actual board bolt axes.

No routing is regenerated. Flat group seats avoid sub-nozzle individual grooves.
Pads/slots and both complete ties are allocated before native feature creation.
"""
import json,time,sys
from pathlib import Path
import FreeCAD as A
import Part
from plan_current_main_sources import ROOT,OUT,SHA
from current_prototype_harness_scene import wire
from u1_socket_current_context import context
from plan_current_tail_complete import tie_z,tie_x


def thin_tie_z(z,x0,x1,y0,y1):
    band=box([x0,y0,z-1.25,x1,y1,z+1.25]).cut(
        box([x0+1,y0+1,z-1.4,x1-1,y1-1,z+1.4]))
    head=box([(x0+x1)/2-2.4,y1,z-1.75,(x0+x1)/2+2.4,y1+4.5,z+1.75])
    return band,head


def box(b):
    return Part.makeBox(*(b[i+3]-b[i] for i in range(3)),A.Vector(*b[:3]))


def material(row):
    if row.get('kind')=='disc':
        return Part.makeCylinder(row['radius_mm'],row['height_mm'],A.Vector(*row['centre_mm']))
    return box(row['bounds_mm'])


def allocation():
    pads=[];cuts=[];bands={};lands=[];axes={}
    def add(owner,name,b):pads.append(dict(owner=owner,name=name,bounds_mm=b))
    def cut(owner,name,b):cuts.append(dict(owner=owner,name=name,bounds_mm=b))
    def vertical(owner,name,b,wires,z,x0,x1,y0,y1):
        add(owner,name+'Seat',b)
        band,head=thin_tie_z(z,x0,x1,y0,y1)
        # Lock on SOUTH side, away from adjacent GPIO row. Installed envelope,
        # not a manufacturer-specified bend shape or force qualification.
        head.translate(A.Vector(0,-(y1-y0+4.5),0))
        bands[name+'Band']=band;bands[name+'Lock']=head
        for label,bb in [('West',[x0-.15,y0-.15,z-1.45,x0+1.35,y1+.15,z+1.45]),
                         ('East',[x1-1.35,y0-.15,z-1.45,x1+.15,y1+.15,z+1.45]),
                         ('Back',[x0-.15,y0-.15,z-1.45,x1+.15,y0+1.35,z+1.45])]:
            cut(owner,name+label,bb)
        lands.append(dict(group=name,wires=wires,T18R=1,nominal_land_z_mm=z))
    # Existing north Pi M2 axes, actual PCB top49.32. Replace only the upper
    # .3mm washers with1mm bearing feet; do not disturb the lower washer/post.
    owner='GPIOGrip';axes[owner]=[[-15.5,24.5],[42.5,24.5]]
    for i,x in enumerate((-15.5,42.5)):
        add(owner,'Foot'+str(i),[x-2.4,22.1,49.32,x+2.4,31.5,50.32])
        if i==1:add(owner,'Riser'+str(i),[x-1.5,28.5,50.32,x+1.5,31.5,73.82])
    add(owner,'NorthRail',[-17,28.5,49.32,44,31.5,51.32])
    # One right-rooted cantilever avoids the accepted MAIN W080 on the left.
    # No next local offset of the blocked left riser; stiffness is a phase2 gate.
    add(owner,'TopBridge',[-17,28.5,71.32,44,31.5,73.82])
    add(owner,'FrontSeatRoot',[-17,20.03,71.32,-12.5,31.5,73.82])
    # Separate low rear post, behind the plug casing YMax27.05, rooted on
    # the base rail. It does not depend on a bridge across W080 above it.
    add(owner,'RearSeatRoot',[-6.8,27.55,50.32,-4.3,28.97,68.32])
    vertical(owner,'GPIOFront',[-12.5,20.03,66.32,4,22.53,73.82],
             ['XL01/a','XL05/a','XL06/a','XL07/a'],70,-13.5,5,19.03,24.93)
    # Separate rear H6 row; a strap across both rows would not bear on all five.
    # Opposite-side backing for row2 leaves the row1 approach unobstructed.
    vertical(owner,'GPIORear',[-6.8,26.47,65.82,-4.3,28.97,68.32],
             ['XL10/a'],66.92,-7.8,-3.3,24.07,29.97)
    bands['GPIORearLock']=box([-12.3,25.0,65.17,-7.8,29.8,68.67])
    # This free-standing post is wholly INSIDE the loop; no through-slot is
    # required and none may sever its lower load path.
    cuts[:]=[v for v in cuts if not (v['owner']==owner and v['name'].startswith('GPIORear'))]
    owner='PCAGrip';axes[owner]=[[-35.825,-9.525],[-35.825,9.525]]
    for i,y in enumerate((-9.525,9.525)):
        pads.append(dict(owner=owner,name='Foot'+str(i),kind='disc',centre_mm=[-35.825,y,84.32],radius_mm=2.4,height_mm=1))
        add(owner,'FootBridge'+str(i),[-44,y-1,84.32,-35.825,y+1,85.32])
    add(owner,'WestSpine',[-44,-11.925,84.32,-41,11.925,94.32])
    add(owner,'JP3Bridge',[-44,-5.1,91.82,-37.795,7.9,94.32])
    # Rotate the tie about Z so its band encompasses the Y row, not four
    # separate micro-clamps. Slot tools follow exactly the same rotation.
    b0=[-40.295,-5.1,85.82,-37.795,7.9,94.32]
    add(owner,'JP3Seat',b0)
    band,head=thin_tie_z(89.82,-41.295,-35.395,-6.1,8.9)
    # Move locking head to west; loop still has the same band dimensions.
    head=box([-40.5,-10.6,88.07,-35.7,-6.1,91.57])
    bands['PCAJP3Band']=band;bands['PCAJP3Lock']=head
    for n,b in [('South',[-41.65,-6.75,88.37,-36.24,-5.25,91.27]),
                ('North',[-41.65,8.05,88.37,-36.24,9.55,91.27]),
                ('Back',[-41.65,-6.75,88.37,-40.145,9.55,91.27])]:cut(owner,n,b)
    lands.append(dict(group='PCAJP3',wires=['XL02/b','XL05/b','XL06/b','XL08/a'],T18R=1))
    add(owner,'PWMRoot',[-44,-20,85.42,-31.615,-15,86.42])
    add(owner,'PWMRootReturn',[-44,-20,84.32,-41,-10,86.42])
    add(owner,'PWMSeat',[-33.415,-17.5,85.42,-25.535,-8.5,86.42])
    # Three fixed fine PWM wires sit on a common flat seat. No .17mm walls.
    for i,y in enumerate((-15.5,)):
        # tie_x is reoriented to run across X around the horizontal Y cables.
        # Construct directly in world XY, not a second board transform.
        band=box([-34.415,y-1.25,84.42,-24.535,y+1.25,88.22]).cut(
            box([-33.415,y-1.4,85.42,-25.535,y+1.4,87.22]))
        head=box([-24.535,y-2.4,84.57,-20.035,y+2.4,88.07])
        bands['PCAPWM'+str(i)+'Band']=band;bands['PCAPWM'+str(i)+'Lock']=head
        cut(owner,'PWMReturn'+str(i),[-34.8,y-1.45,84.27,-24.15,y+1.45,85.57])
        for j,(x0,x1) in enumerate(((-34.8,-33.265),(-25.685,-24.15))):
            cut(owner,'PWMSide'+str(i)+str(j),[x0,y-1.45,83.27,x1,y+1.45,87.37])
    lands.append(dict(group='PCAPWM',wires=['XS11/a','XS21/a','XS31/a'],T18R=1))
    return dict(pads=pads,cuts=cuts,bands=bands,mount_axes_mm=axes,lands=lands,
        upper_washers_replaced=4,new_T18R_11100405=4,existing_M2x12_reused=2,existing_M2x14_reused=2,
        tie_supplier=dict(SKU='111-00405',type='T18R',width_mm=2.5,thickness_mm=1.0,
            source='https://www.hellermanntyton.us/products/cable-ties/t18r/111-00405',
            locked_head_budget_mm=[4.8,4.5,3.5],head_is_project_reservation=True),
        nominal_Pi_tip_after_foot_mm=38.32,nominal_Pi_nut_bottom_mm=39.92,
        nominal_thread_beyond_nut_mm=1.5,
        assumptions=['PETG washer-foot1mm in place of upper.3mm washer; bearing/creep dry fit phase2.',
                     'Tie paths are installed rectangular budgets; snug by hand without crushing insulation.',
                     'No tie over connector/socket/PCB pad. Cut dedicated wire ties before removing bracket.',
                     'GPIO bracket must be removed before12mm GPIO plug withdrawal; PCB is supported during service.'],
        selected=False,physical_pass=False)


def make_parts(g):
    shapes={}
    for owner in g['mount_axes_mm']:
        pieces=[material(v) for v in g['pads'] if v['owner']==owner]
        s=pieces[0].multiFuse(pieces[1:])
        tools=[box(v['bounds_mm']) for v in g['cuts'] if v['owner']==owner]
        if tools:s=s.cut(tools[0].multiFuse(tools[1:]))
        for x,y in g['mount_axes_mm'][owner]:s=s.cut(Part.makeCylinder(1.2,70,A.Vector(x,y,30)))
        shapes[owner]=s.removeSplitter()
    return shapes


def local_preflight(g,p):
    tick=time.monotonic();new={**make_parts(g),**g['bands']};hits=[]
    for n,s in new.items():
        assert s.isValid() and len(s.Solids)==1 and not s.check(True),n
        for m,t in new.items():
            if n<m and s.BoundBox.intersect(t.BoundBox):
                v=s.common(t).Volume
                if v>1e-5:hits.append([n,m,v])
        for wid,r in {**p['complete_routes'],**p['changed_MAIN_pair']}.items():
            c=wire(r['parts']);rr=r.get('radius',r.get('radius_mm'));b=c.BoundBox;b.enlarge(rr)
            if not b.intersect(s.BoundBox):continue
            gap=c.distToShape(s)[0]
            if gap<rr-1e-5:hits.append([n,wid,gap,rr])
    result=dict(scope='New parts/bands mutual and13accepted routes ONLY. Retained217wire/material full gate stillrequired.',
        contacts=hits,worker_seconds=round(time.monotonic()-tick,3),selected=False,physical_pass=False)
    (OUT/'u1-grouped-grips-local.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result),flush=True)


def run():
    tick=time.monotonic();g=allocation();pf=OUT/'u1-common-wiring-plan.json'
    p=json.loads(pf.read_text());receipt=OUT/'u1-common-wiring-checks.json';r0=json.loads(receipt.read_text())
    assert SHA(pf)==r0['plan_sha256']
    assert not any(r0[k] for k in ('material_resolutions','wire_contacts','USB_fit_reservations','errors'))
    if '--local' in sys.argv:return local_preflight(g,p)
    reader,pins,targets,old=context()
    model=OUT/'U1InterfaceCarriersCurrent.FCStd';native=json.loads((OUT/'u1-interface-carriers-native.json').read_text())
    assert SHA(model)==native['native_sha256']
    d=A.openDocument(str(model))
    for n in ('UpperCarrier001','LowerCarrier001'):targets[n]=d.getObject(n).Shape.copy()
    A.closeDocument(d.Name)
    curves={}
    for wid,r in p['complete_routes'].items():curves[wid]=(wire(r['parts']),r['radius']);old.pop(wid,None)
    for wid,r in p['changed_MAIN_pair'].items():curves[wid]=(wire(r['parts']),r['radius_mm']);old.pop(wid,None)
    for n,r in p['bare'].items():curves[n+'/bare']=(wire(r['parts']),r['radius'])
    curves.update(old)
    shapes=make_parts(g)
    result=dict(status='PENDING',pairs=0,contacts=[],errors=[],selected=False,physical_pass=False)
    def near(s,t,r=0):
        b=s.BoundBox;b.enlarge(r);return b.intersect(t.BoundBox)
    def solid(n,s,m,t):
        if not s.Solids or not t.Solids or not near(s,t):return
        result['pairs']+=1
        try:
            assert s.isValid() and t.isValid(),(n,m)
            v=sum(a.common(b).Volume for a in s.Solids for b in t.Solids)
            if v>1e-5:result['contacts'].append(dict(a=n,b=m,volume_mm3=v))
        except Exception as ex:result['errors'].append(dict(a=n,b=m,error=str(ex)))
    # Remove ONLY named upper washers at these four physical axes; replacement
    # feet bear there. Every bolt/head/nut/other washer remains an obstacle.
    removed=[]
    for n,s in list(targets.items()):
        if 'Washer' not in n:continue
        bb=s.BoundBox;c=bb.Center
        if any(abs(c.x-x)<.01 and abs(c.y-y)<.01 and abs(bb.ZMin-z)<.01
               for owner,z in [('GPIOGrip',49.32),('PCAGrip',84.32)] for x,y in g['mount_axes_mm'][owner]):
            removed.append(n);targets.pop(n)
    result['replaced_upper_washer_names']=removed
    assert len(removed)==4,removed
    # Rebind existing shafts/heads together to the replacement1mm feet.
    # Pi12mm retains1.6mm tip beyond its captive nut; no extra screws needed.
    result['changed_screws']=[]
    for n in ('Pi410Screw','Pi412Screw','PWM968517Screw','PWM968518Screw'):
        assert n in targets,n
        targets[n]=targets[n].copy();targets[n].translate(A.Vector(0,0,.7))
        result['changed_screws'].append(dict(name=n,translation_mm=[0,0,.7],same_length_reused=True))
    for n,s in shapes.items():
        if not s.isValid() or len(s.Solids)!=1 or s.check(True):
            result['errors'].append(dict(part=n,error='invalid/disconnected',solids=len(s.Solids)))
    all_new={**shapes,**g['bands'],**{r['name']:targets.pop(r['name']) for r in result['changed_screws']}}
    for n,s in all_new.items():
        for m,t in targets.items():solid(n,s,m,t)
        for m,t in all_new.items():
            if n<m:solid(n,s,m,t)
        for m,(c,rr) in curves.items():
            if not near(c,s,rr):continue
            result['pairs']+=1;gap=c.distToShape(s)[0]
            if gap<rr-1e-5:result['contacts'].append(dict(a=n,b=m,distance_mm=gap,required_mm=rr))
        print('Grouped grip',n,'pairs',result['pairs'],'issues',len(result['contacts']),flush=True)
    result.update(status='GROUPED_GRIP_SPACE_CLEAR_NATIVE_OPEN' if not result['contacts'] and not result['errors'] else 'GROUPED_GRIP_LAYOUT_REQUIRES_RESOLUTION',
        worker_seconds=round(time.monotonic()-tick,3),source_sha256={**reader.hashes,**{f.relative_to(ROOT).as_posix():SHA(f) for f in [*pins,pf,receipt,model,Path(__file__)]}})
    plan={k:v for k,v in g.items() if k!='bands'}
    (OUT/'u1-grouped-grips-plan.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')
    (OUT/'u1-grouped-grips-checks.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='source_sha256'}),flush=True)


if __name__=='__main__':run()
