"""One common allocation for remaining PCB1-side wire restraint.

Replacement anchors retain their exact bearing/eye/bolt stack. No old routes
are moved to rescue a blocked grip; added load paths and installed tie budgets
are checked together before editable details. Candidate, not selected.
"""
import json,time,sys
from pathlib import Path
import FreeCAD as A
import Part
from plan_current_main_sources import ROOT,OUT,SHA
from current_prototype_harness_scene import wire
from u1_socket_current_context import context
import plan_u1_grouped_grips as G


def allocation():
    pads=[];bands={};groups=[]
    def add(owner,name,b):pads.append(dict(owner=owner,name=name,bounds_mm=b))
    def vertical(owner,name,ids,x0,x1,y,z=89.82):
        # Backing north of each vertical row; rectangular installed budgets.
        add(owner,name+'Seat',[x0,y+.7,85.32,x1,y+3.2,94.32])
        band,head=G.thin_tie_z(z,x0-1,x1+1,y-1.7,y+4.2)
        # Lock lies beyond the row on the east, not through the solder pins.
        head=G.box([x1+1,y-1.6,z-1.75,x1+5.5,y+3.2,z+1.75])
        bands[name+'Band']=band;bands[name+'Lock']=head
        groups.append(dict(name=name,ends=ids,T18R=1,land_mm=9))
    owner='AnchorLeft'
    add(owner,'WestRoot',[59,0,84.3202,67,2.3,85.3202])
    add(owner,'WestColumn',[58,0,84.3202,61,3,94.32])
    add(owner,'WestTopRail',[58,-17.17,91.82,61,22.25,94.32])
    add(owner,'RearBeam',[58,19.75,91.82,77.75,22.25,94.32])
    vertical(owner,'RearLeft',['XL09/a','XL08/b'],72.41,77.75,19.05)
    add(owner,'OEBeam',[58,7.05,91.82,80.29,9.55,94.32])
    vertical(owner,'OE',['XL07/b'],77.49,80.29,6.35)
    # Front LOGIC3V3 seat uses the opposite side of the isolated vertical end.
    add(owner,'FrontBeam',[58,-17.17,91.82,75.21,-14.67,94.32])
    add(owner,'FrontSeat',[72.41,-17.17,85.32,75.21,-14.67,94.32])
    band,head=G.thin_tie_z(89.82,71.41,76.21,-18.17,-12.27)
    bands['FrontBand']=band
    bands['FrontLock']=G.box([76.21,-17.17,88.07,80.71,-12.37,91.57])
    groups.append(dict(name='Front',ends=['XL01/b'],T18R=1,land_mm=9))
    # Three fine fixed X-running wires share a flat seat, no1.27mm grooves.
    add(owner,'FineColumn',[70,0,85.3202,72,2.3,89.9])
    add(owner,'FineRoot',[70,-4.95,88.9,72,2.3,89.9])
    add(owner,'FineSeat',[62,-10.29,88.9,71,-4.95,89.9])
    bands['FineBand']=G.box([64.25,-11.29,87.9,66.75,-3.95,91.7]).cut(
        G.box([64.1,-10.29,88.9,66.9,-4.95,90.7]))
    bands['FineLock']=G.box([63.1,-15.79,88.05,67.9,-11.29,91.55])
    groups.append(dict(name='Fine',ends=['XS11/b','XS21/b','XS31/b'],T18R=1,land_mm=9))
    # Horizontal XL02 escape south; flat seat below it, separate from pads.
    add(owner,'SouthBridge',[58,-27,88.62,77.05,-24.5,91.12])
    add(owner,'SouthRoot',[58,-27,88.62,61,-15,94.32])
    add(owner,'XL02Seat',[75.65,-28.97,88.62,78.15,-19.97,90.62])
    bands['XL02Band']=G.box([74.65,-26.25,87.62,79.15,-23.75,93.02]).cut(
        G.box([75.65,-26.4,88.62,78.15,-23.6,92.02]))
    bands['XL02Lock']=G.box([79.15,-27.4,88.07,83.65,-22.6,91.57])
    groups.append(dict(name='XL02',ends=['XL02/a'],T18R=1,land_mm=9))
    owner='AnchorRight'
    add(owner,'RightColumn',[114.5,.5,84.3202,117,3,94.32])
    add(owner,'RightTopRail',[114.5,.5,91.82,117,22.25,94.32])
    add(owner,'RightRearBeam',[107.97,19.75,91.82,117,22.25,94.32])
    vertical(owner,'RearRight',['XL10/b'],107.97,110.77,19.05)
    # The original high common rails and1mm tie family is REJECTED. Allocate
    # the complete load path below BUS and use thin source-backed lacing at
    # the1.215mm centre-to-female gaps; no route or pin location is changed.
    p={v['name']:v for v in pads}
    p['WestRoot']['bounds_mm']=[59,0,84.3202,67,2.3,85.3202]
    p['WestColumn']['bounds_mm']=[58,0,84.3202,61,3,87.32]
    p['WestTopRail']['bounds_mm']=[58,-27,85.3202,61,22.25,87.32]
    for name in ('RearBeam','FrontBeam','RightTopRail','RightRearBeam','OEBeam'):
        p[name]['bounds_mm'][2:6:3]=[85.3202,87.32]
    p['RightColumn']['bounds_mm'][5]=87.32
    p['OESeat']['bounds_mm']=[75.69,5.65,85.32,78.19,7.05,94.32]
    p['OEBeam']['bounds_mm']=[58,5.65,85.3202,78.19,7.05,87.32]
    p['FineColumn']['bounds_mm']=[59,-9.79,86.32,62,-5.45,89.9]
    p['FineRoot']['bounds_mm']=[58,-9.79,85.3202,62,-5.45,87.32]
    p['FineSeat']['bounds_mm']=[62,-9.79,88.9,71,-5.45,89.9]
    p['SouthRoot']['bounds_mm']=[58,-27,85.3202,61,-15,91.12]
    p['SouthBridge']['bounds_mm']=[58,-27,88.62,75.65,-24.5,90.62]
    t=.381;w=1.6764;z=89.82
    def lace(name,inner,knot,axis='z',centre=z):
        x,y,Z,X,Y,ZZ=inner
        if axis=='z':
            outer=G.box([x-t,y-t,centre-w/2,X+t,Y+t,centre+w/2])
            hole=G.box([x,y,centre-w,X,Y,centre+w])
        else:
            outer=G.box([centre-w/2,y-t,Z-t,centre+w/2,Y+t,ZZ+t])
            hole=G.box([centre-w,y,Z,centre+w,Y,ZZ])
        bands[name+'Band']=outer.cut(hole);bands[name+'Lock']=G.box(knot)
    lace('OE',[75.69,5.65,0,79.59,7.05,1],[72.69,5.4,88.82,75.309,7.4,90.82])
    lace('Front',[72.41,-17.17,0,75.21,-13.27,1],[69.41,-15.3,88.82,72.029,-13.3,90.82])
    lace('Fine',[0,-9.79,88.9,1,-5.45,90.7],[64,-13.171,88.8,67,-10.171,90.8],axis='x',centre=65.5)
    # Exact solder-plane datum is84.3202; remove the old rounded .0002mm
    # interference rather than relaxing the distance gate tolerance.
    p['XL02Seat']['bounds_mm'][2]=88.6202;p['XL02Seat']['bounds_mm'][5]=90.6202
    bands['XL02Band']=G.box([74.65,-26.25,87.6202,79.15,-23.75,93.0202]).cut(
        G.box([75.65,-26.4,88.6202,78.15,-23.6,92.0202]))
    for group in groups:
        if group['name'] in ('OE','Front','Fine'):group.pop('T18R');group['lacing_802534B_blank_mm']=150
    # Two complete families exposed an actual BUS alley on the outboard west
    # side. Root the whole left comb INSIDE that alley, beside the known PCB
    # edge (female XMin72.165), not at another height through the same BUS.
    p['WestRoot']['bounds_mm']=[70,0,84.3202,72,2.3,85.3202]
    p['WestColumn']['bounds_mm']=[70,0,84.3202,72,3,87.32]
    p['WestTopRail']['bounds_mm']=[70,-27,85.3202,72,22.25,87.32]
    for name in ('RearBeam','FrontBeam','OEBeam'):p[name]['bounds_mm'][0]=70
    p['FineRoot']['bounds_mm']=[70,-9.79,85.3202,72,-5.45,87.32]
    p['FineColumn']['bounds_mm']=[70,-9.79,86.32,71,-5.45,89.9]
    # The XL02 backing is attached at its NORTH end, outside its strap
    # plane. The previous under-seat bridge physically crossed that strap.
    p['SouthRoot']['bounds_mm']=[70,-22.75,85.3202,72,-19.97,95.0202]
    p['SouthBridge']['bounds_mm']=[70,-22.75,93.0202,78.15,-19.97,95.0202]
    add('AnchorLeft','XL02SeatLink',[77.65,-22.75,90.6202,78.15,-19.97,95.0202])
    # Use the exact saved bearing datum, not a rounded plane0.0002mm below
    # it. That sliver is healed inconsistently by native Refine.
    for row in pads:
        if row['bounds_mm'][2]==85.32:row['bounds_mm'][2]=85.3202
    # Preserve the EXISTING module band passage and screw-head clearance.
    # Added comb material must not close an already qualified interface.
    cuts=[dict(owner='AnchorLeft',name='ExistingBandPassage',
               bounds_mm=[70,-4.6,86.3202,72.01,-1.8,87.32]),
          dict(owner='AnchorLeft',name='ExistingHeadClearance',kind='cylinder',
               centre_mm=[73.81,0,85.3202],radius_mm=2.1,height_mm=12)]
    return dict(pads=pads,cuts=cuts,bands=bands,groups=groups,ties_quantity=3,lacing_blanks_mm=[150]*3,
        replaces=['U1_AnchorLeft','U1_AnchorRight'],new_screws=0,
        original_foot_eye_and_bolt_stack_unchanged=True,selected=False,physical_pass=False)


def make_parts(p,targets):
    result={}
    for owner in ('AnchorLeft','AnchorRight'):
        pieces=[G.box(r['bounds_mm']) for r in p['pads'] if r['owner']==owner]
        result[owner]=targets['U1_'+owner].multiFuse(pieces).removeSplitter()
        for cut in p['cuts']:
            if cut['owner']==owner:result[owner]=result[owner].cut(cut_shape(cut)).removeSplitter()
    return result


def cut_shape(cut):
    if cut.get('kind')=='cylinder':
        return Part.makeCylinder(cut['radius_mm'],cut['height_mm'],A.Vector(*cut['centre_mm']))
    return G.box(cut['bounds_mm'])


def run():
    tick=time.monotonic();p=allocation();reader,pins,targets,curves=context()
    print('Board grip retained context',round(time.monotonic()-tick,3),flush=True)
    cf=OUT/'u1-common-wiring-plan.json';c=json.loads(cf.read_text())
    gf=OUT/'u1-grouped-grips-native.json';g=json.loads(gf.read_text())
    df=OUT/'u1-interface-carriers-native.json';d=json.loads(df.read_text())
    for receipt in (g,d):assert SHA(ROOT/receipt['native'])==receipt['native_sha256']
    for n,r in {**c['complete_routes'],**c['changed_MAIN_pair']}.items():
        curves[n]=(wire(r['parts']),r.get('radius',r.get('radius_mm')))
    curves.update({n+'/bare':(wire(r['parts']),r['radius']) for n,r in c['bare'].items()})
    for receipt,names in ((d,('UpperCarrier001','LowerCarrier001')),(g,('GPIOGrip','PCAGrip'))):
        doc=A.openDocument(str(ROOT/receipt['native']))
        for n in names:targets[n]=doc.getObject(n).Shape.copy()
        A.closeDocument(doc.Name)
    targets.update(G.allocation()['bands'])
    for n in g['replaced_upper_washers']:assert n in targets;targets.pop(n)
    for r in g['changed_existing_hardware']:
        targets[r['name']]=targets[r['name']].copy();targets[r['name']].translate(A.Vector(*r['translation_mm']))
    parts=make_parts(p,targets)
    for n in p['replaces']:targets.pop(n)
    # Only added material is changed: existing bearing/eye interlocks retain
    # their qualified intended contacts, not an exemption for the new arms.
    ret=A.openDocument(str(OUT/'U1SocketRetainer.FCStd'))
    original={n:ret.getObject(n).Shape.copy() for n in parts}
    additions={n:s.cut(original[n]).removeSplitter() for n,s in parts.items()}
    A.closeDocument(ret.Name)
    r=dict(status='PENDING',pairs=0,contacts=[],errors=[],selected=False,physical_pass=False)
    new={**additions,**p['bands']}
    bounds={n:s.BoundBox for n,s in {**targets,**new}.items()}
    valid={}
    curve_bounds={}
    for n,(s,rr) in curves.items():b=s.BoundBox;b.enlarge(rr);curve_bounds[n]=b
    for n,s in parts.items():
        if not s.isValid() or len(s.Solids)!=1 or s.check(True):r['errors'].append(dict(part=n,solids=len(s.Solids)))
    def check(n,s,m,t):
        if not bounds[n].intersect(bounds[m]):return
        r['pairs']+=1
        try:
            if n not in valid:valid[n]=s.isValid()
            if m not in valid:valid[m]=t.isValid()
            assert valid[n] and valid[m]
            v=sum(a.common(b).Volume for a in s.Solids for b in t.Solids)
            if v>1e-5:r['contacts'].append(dict(a=n,b=m,volume_mm3=v))
        except Exception as e:r['errors'].append(dict(a=n,b=m,error=str(e)))
    for n,s in new.items():
        for m,t in targets.items():check(n,s,m,t)
        if n in p['bands']:
            for m,t in original.items():
                key='Original_'+m;bounds[key]=t.BoundBox;valid[key]=t.isValid();check(n,s,key,t)
        for m,t in new.items():
            if n<m:check(n,s,m,t)
        for m,(w,rr) in curves.items():
            if not curve_bounds[m].intersect(bounds[n]):continue
            r['pairs']+=1;gap=w.distToShape(s)[0]
            if gap<rr-1e-5:r['contacts'].append(dict(a=n,b=m,distance_mm=gap,required_mm=rr))
        print('Board grip',n,r['pairs'],len(r['contacts']),round(time.monotonic()-tick,1),flush=True)
    r.update(status='BOARD_GRIPS_SHARED_CLEAR_NATIVE_OPEN' if not r['contacts'] and not r['errors'] else 'BOARD_GRIPS_REJECTED_SHARED_LAYOUT',
        worker_seconds=round(time.monotonic()-tick,3),source_sha256={**reader.hashes,**{f.relative_to(ROOT).as_posix():SHA(f) for f in [*pins,cf,gf,df,Path(__file__),ROOT/'hardware/reference/alpha-802534b-2026-10-12/dimensions.json']}})
    (OUT/'u1-board-grips-plan.json').write_text(json.dumps({k:v for k,v in p.items() if k!='bands'},indent=2)+'\n')
    (OUT/'u1-board-grips-checks.json').write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps({k:v for k,v in r.items() if k!='source_sha256'}),flush=True)


if __name__=='__main__':run()
