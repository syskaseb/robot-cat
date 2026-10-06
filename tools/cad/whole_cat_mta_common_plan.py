"""One bounded shared MTA route plan against CP2 geometry, not selected wiring.

Search centreline primitives before creating supports/full pipe CAD. Planning
samples are conservative rejections, NEVER a proof of exact swept clearance.
No unchanged retry: one recorded recipe; each of eight routes has a time cap.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import heapq
import itertools
import json
import math
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/cad'))
from whole_cat_source_bay_plan import Route, add, dot, scale
BASE=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2'
NATIVE=BASE/'ATOStackCandidate.FCStd'
OUT=BASE/'mta-common-plan.json'
SIDE_LANES='--side-lanes' in sys.argv
if SIDE_LANES:OUT=BASE/'mta-side-lanes-plan.json'
UPPER_LEVEL='--upper-level' in sys.argv
if UPPER_LEVEL:OUT=BASE/'mta-upper-level-plan.json'
ALLOCATED_LEVELS='--allocated-levels' in sys.argv
if ALLOCATED_LEVELS:UPPER_LEVEL=True;OUT=BASE/'mta-allocated-levels-plan.json'
JOINT_SOURCE='--joint-source-layout' in sys.argv
if JOINT_SOURCE:ALLOCATED_LEVELS=True;UPPER_LEVEL=True;OUT=BASE/'mta-source-shared-plan.json'
PAIRED_AUX='--paired-aux' in sys.argv
if PAIRED_AUX:JOINT_SOURCE=True;ALLOCATED_LEVELS=True;UPPER_LEVEL=True;OUT=BASE/'mta-source-aux-plan.json'
HORIZONTAL='--horizontal-receivers' in sys.argv
if HORIZONTAL:PAIRED_AUX=True;JOINT_SOURCE=True;ALLOCATED_LEVELS=True;UPPER_LEVEL=True;OUT=BASE/'mta-horizontal-receivers-plan.json'
HORIZONTAL_CORRECTED='--horizontal-corrected' in sys.argv
if HORIZONTAL_CORRECTED:HORIZONTAL=True;PAIRED_AUX=True;JOINT_SOURCE=True;ALLOCATED_LEVELS=True;UPPER_LEVEL=True;OUT=BASE/'mta-horizontal-corrected-plan.json'
R=25.2
AXES=[[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]]


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def length(a):return math.sqrt(dot(a,a))
def minus(a,b):return add(a,scale(b,-1))


def line(p,u,L):
    return dict(kind='line',start_mm=p,end_mm=add(p,scale(u,L)),tangent=u,length_mm=L)


def arc(p,u,v):
    r=Route('primitive',p,u,4.2,R,0,[]);r.turn(v,R)
    return r.row['segments'][0]


def points(segment):
    L=segment['length_mm'];n=max(2,math.ceil(L/3))
    p=segment['start_mm']
    if segment['kind']=='line':
        return [add(p,scale(segment['tangent'],L*i/n)) for i in range(n+1)]
    u=segment['start_tangent'];v=segment['end_tangent'];theta=segment['angle_rad']
    normal=scale(add(v,scale(u,-math.cos(theta))),1/math.sin(theta))
    return [add(p,add(scale(u,R*math.sin(theta*i/n)),
        scale(normal,R*(1-math.cos(theta*i/n))))) for i in range(n+1)]


def suffix(p,u,goal,goal_u):
    """Exact tangent S-shift; may include a folded (>90degree) pair of arcs."""
    tail=[]
    if dot(u,goal_u)<1-1e-7:
        if dot(u,goal_u)<-1+1e-7:return None
        s=arc(p,u,goal_u);tail.append(s);p=s['end_mm'];u=goal_u
    delta=minus(goal,p);v=dot(delta,u);hvec=minus(delta,scale(u,v));h=length(hvec)
    if h<1e-7:
        return tail+[line(p,u,v)] if v>=9 else None
    if h<4*R-1e-7:
        theta=math.acos(1-h/(2*R));advance=2*R*math.sin(theta);middle=0
    else:
        theta=math.pi/2;advance=2*R;middle=h-2*R
    if v<advance+9-1e-7:return None
    lead=v-advance-9
    if lead>1e-7:
        s=line(p,u,lead);tail.append(s);p=s['end_mm']
    oblique=add(scale(u,math.cos(theta)),scale(hvec,math.sin(theta)/h))
    s=arc(p,u,oblique);tail.append(s);p=s['end_mm']
    if middle>1e-7:
        s=line(p,oblique,middle);tail.append(s);p=s['end_mm']
    s=arc(p,oblique,u);tail.append(s);p=s['end_mm']
    tail.append(line(p,u,9))
    assert length(minus(tail[-1]['end_mm'],goal))<1e-6
    return tail


def main():
    import FreeCAD as A
    import Part
    started=datetime.now(timezone.utc);tick=time.monotonic()
    assert started<datetime.fromisoformat('2026-10-06T07:00:00+00:00')
    assert not OUT.exists(),'No unchanged repeat; inspect recorded result first'
    pins={p.relative_to(ROOT).as_posix():sha(p) for p in [NATIVE,
        BASE/'ato-stack-checks.json',ROOT/'hardware/reference/wago-inline-2212411/source.json',
        ROOT/'hardware/electronics/full-cat/source-switch-selected-r1/body-harness.json',Path(__file__)]}
    d=A.openDocument(str(NATIVE));d.recompute()
    # One COUPLED packaging assumption: twelve stacks/ten side cages permit
    # four inclined bidirectional main holders with straight factory joints.
    # No narrowing or widening of the torso; source/S0/S1 pipes stay fixed.
    d.getObject('ATOStackDatums').FlangeTop=126 if UPPER_LEVEL else 122
    for side,sign in [('L',1),('R',-1)]:
        for i in range(1,7):
            prefix=f'F_{side}{i}_CP2'
            for role in ['Housing','ATO']:
                ob=d.getObject(prefix+'_'+role);ob.Placement.Base.y+=sign*4
            for role in ['IN','OUT']:
                ob=d.getObject(prefix+'_'+role)
                expressions=dict(ob.ExpressionEngine)
                key=next(k for k in expressions if k.endswith('Placement.Base.y'))
                expr=expressions[key]
                ob.setExpression('Placement.Base.y',f'({expr})+{sign*4} mm')
            d.getObject('Access_'+prefix).Placement.Base.y+=sign*4
    for bus in ['FL_P','FL_G','D_FL','RL_P','RL_G','FR_P','FR_G','D_FR','RR_P','RR_G']:
        ob=d.getObject(bus+'_CP2');ob.Placement.Base.y+=2*(1 if ob.Placement.Base.y>0 else -1)
    monitor=d.getObject('Monitor_CP2');monitor.Placement.Base=A.Vector(108,0,42)
    for old in ['Splice_L2_CP2','Splice_L3_CP2','Splice_R1_CP2','Splice_R2_CP2']:
        d.removeObject(old) # FOUR replacement output joints, not eight extras.
    angle=A.Rotation(A.Vector(0,1,0),-45)
    u=[math.sqrt(.5),0,math.sqrt(.5)]
    factory=[];endpoints=[];roles=[]
    wires={w['id']:w for w in json.loads((ROOT/'hardware/electronics/full-cat/source-switch-selected-r1/body-harness.json').read_text(encoding='utf-8'))['conductors']}
    ig=d.getObject('InteriorReservations')
    invalidated=[]
    placements={'FL':(15,38,96.5),'FR':(15,-38,96.5),
                'RL':(50,38,96.5),'RR':(50,-38,96.5)}
    placement_search=None
    if UPPER_LEVEL:
        placements={'FL':(-25,40,138),'FR':(-25,-40,138),
                    'RL':(105,40,138),'RR':(105,-40,138)}
        angle=A.Rotation();u=[1,0,0]
        # Whole layer reassignment, not another centreline offset. Existing
        # source/S0/S1 geometry stays fixed; branch fuse routes are invalidated.
        for name,x,y in [('F_PI',-43,84),('F_AUX',10,84),('F_HY',63,84),
                         ('F_HP',-15,-84),('F_TY',40,-84)]:
            ob=d.getObject(name+'_CP2');delta=A.Vector(x,y,91)-ob.Shape.BoundBox.Center
            ob.Placement.Base+=delta
            access=d.getObject('Access_'+name)
            if access:access.Placement.Base+=delta
            invalidated.append(name+'_CP2')
        # W043 belonged to old F_PI datum; do not preserve it as a second wire.
        for name in ['W043_CP2','W043_strip_CP2']:
            if d.getObject(name):d.removeObject(name);invalidated.append(name)
        placement_search=dict(method='Reassign main and branch fuses to two separate levels',
            invalidated_branch_routes_and_mounts=True,source_S0_S1_retained=True)
        if ALLOCATED_LEVELS:
            # Dimensioned layer allocation uses FULL26mm ATO access, not15mm
            # housing width. Separate rear from front end joints in Z to leave
            # room for R25.2 turns within the tapered rear torso.
            placements={'FL':(-25,36.6,140.6),'FR':(-25,-36.6,140.6),
                        'RL':(90,36.6,115),'RR':(90,-36.6,115)}
            for name,x,y in [('F_PI',-30,87),('F_AUX',23,87),
                             ('F_HP',-30,-87),('F_TY',23,-87)]:
                ob=d.getObject(name+'_CP2');delta=A.Vector(x,y,91)-ob.Shape.BoundBox.Center
                ob.Placement.Base+=delta
                access=d.getObject('Access_'+name)
                if access:access.Placement.Base+=delta
            ob=d.getObject('F_HY_CP2');oldcentre=ob.Shape.BoundBox.Center
            rotation=A.Rotation(A.Vector(0,1,0),-90)
            centre=A.Vector(-95,-42,90)
            access=d.getObject('Access_F_HY')
            if access:
                access.Placement=A.Placement(centre,rotation).multiply(
                    A.Placement(-oldcentre,A.Rotation())).multiply(access.Placement)
            ob.Placement=A.Placement(centre+rotation.multVec(A.Vector(-25.5,-10.125,-11)),rotation)
            for name,centre in [('G_AUX',A.Vector(-74,-22,120)),
                                ('G_TAIL',A.Vector(138,-53,114.5))]:
                ob=d.getObject(name+'_CP2');delta=centre-ob.Shape.BoundBox.Center
                ob.Placement.Base+=delta
                access=d.getObject('Access_'+name+'_CP2')
                if access:access.Placement.Base+=delta
                invalidated.append(name+'_CP2')
            placement_search['method']='Dimensioned front-upper/rear-middle main bank; four side branches plus one vertical front branch'
            placement_search['constraints_mm']=dict(ATO_access_y_inner=49,main_front_y_outer=47.6,
                main_front_bottom=132.6,P_FRONT_top=130.2,TE_IN_y_outer=74.1181,
                four_side_branch_y_inner=76.875,main_rear_joint_tip_x=152)
            if JOINT_SOURCE:
                ob=d.getObject('P_REAR_CP2');delta=A.Vector(0,-20,0);ob.Placement.Base+=delta
                access=d.getObject('Access_P_REAR')
                if access:access.Placement.Base+=delta
                invalidated.append(ob.Name)
                for wid in ['W064','W065','W067','W068']:
                    for name in [wid+'_CP2',wid+'_strip_CP2']:
                        if d.getObject(name):d.removeObject(name);invalidated.append(name)
                s1=json.loads((BASE/'interfaces.json').read_text(encoding='utf-8'))['S1_joint_plan']
                for key,turn in [('2',-90),('5',90)]:
                    ob=d.getObject('S1_ring_'+key)
                    s=ob.Shape.copy();s.rotate(A.Vector(*s1['terminal_centres_mm'][key]),A.Vector(0,1,0),turn)
                    ob.Shape=s;invalidated.append(ob.Name)
                placement_search['S1_ring_rotation_degrees']={'2':-90,'5':90}
                placement_search['S1_terminal_bearings_still_provisional']=True
                if PAIRED_AUX:
                    ob=d.getObject('P_AUX_CP2');delta=A.Vector(-74,-22,135)-ob.Shape.BoundBox.Center
                    ob.Placement.Base+=delta
                    access=d.getObject('Access_P_AUX')
                    if access:access.Placement.Base+=delta
                    invalidated.append(ob.Name)
                    placement_search['AUX_power_ground_paired_front_levels_mm']=[135,120]
                    if HORIZONTAL:
                        # Change approach topology, not another guess at an
                        # old pipe: horizontal receivers remove forced U-turns.
                        placements['FL']=(-15,36.6,140.6)
                        placements['FR']=(-15,-36.6,140.6)
                        for bus in ['FL_P','FL_G','D_FL','RL_P','RL_G','FR_P','FR_G','D_FR','RR_P','RR_G']:
                            ob=d.getObject(bus+'_CP2');c=ob.Shape.BoundBox.Center
                            rot=A.Rotation(A.Vector(0,0,1),180) if c.y>0 else A.Rotation()
                            ob.Placement=A.Placement(c+rot.multVec(A.Vector(-15,-9.5,-4.5)),rot)
                            invalidated.append(ob.Name)
                        ob=d.getObject('P_SYS_CP2');oldcentre=ob.Shape.BoundBox.Center
                        newplacement=A.Placement(A.Vector(-37,1.5,113.5),A.Rotation())
                        ob.Placement=newplacement;invalidated.append(ob.Name)
                        # Old access and W066 depend on the former UP receiver.
                        if d.getObject('Access_P_SYS'):d.removeObject('Access_P_SYS')
                        for name in ['W066_CP2','W066_strip_CP2']:
                            if d.getObject(name):d.removeObject(name);invalidated.append(name)
                        placement_search['receiver_entry_change']='10 side blocks inward horizontal; P_SYS from+Y, old lever/service and all affected harness routes invalidated'
                        if HORIZONTAL_CORRECTED:
                            for ob in list(d.Objects):
                                if ob.Name.startswith('W043'):
                                    invalidated.append(ob.Name);d.removeObject(ob.Name)
                            placement_search['stale_FPI_wire_corrected']='Remove actual W043_FPI native name as well as W043 aliases; old F_PI moved, no old route acceptance'
    if SIDE_LANES:
        # Architectural alternative: complete longitudinal packages below the
        # ATO terminals, not further offsets of the rejected central layout.
        # Search a finite shared allocation; retained routes remain obstacles.
        torso=d.getObject('TorsoEnvelope').Shape
        fixed=[(o.Name,o.Shape) for o in d.Objects if 'Shape' in o.PropertiesList
            and not o.Name.startswith('MTA_') and o.Name not in ['TorsoEnvelope','BatteryNominal']
            and (any(p.Name in ['InteriorReservations','HarnessCandidate','S0TerminalCandidates',
                'S1TerminalCandidates','ServiceReservations','ATOStackCandidates'] for p in o.InList)
                or 'Category' in o.PropertiesList and o.Category!='electronics')]
        found={1:[],-1:[]};tested=0;rejects={}
        for sign in [1,-1]:
            for x,y,z in itertools.product(range(-70,161,10),[63,66,69,72],[45,52,59,66]):
                tested+=1;centre=[x,sign*y,z]
                shapes=[Part.makeBox(35,22,16,A.Vector(x-17.5,sign*y-11,z-8)),
                    Part.makeBox(35.5,8.1,8.9,A.Vector(x-62,sign*y-4.05,z-4.45)),
                    Part.makeBox(35.5,8.1,8.9,A.Vector(x+26.5,sign*y-4.05,z-4.45)),
                    Part.makeCylinder(2.1,9,A.Vector(x-17.5,sign*y,z),A.Vector(-1,0,0)),
                    Part.makeCylinder(2.1,9,A.Vector(x+17.5,sign*y,z),A.Vector(1,0,0))]
                bad=None
                for s in shapes:
                    if not all(torso.isInside(v.Point,1e-7,True) for v in s.Vertexes):
                        bad='TorsoEnvelope';break
                    for name,t in fixed:
                        if not s.BoundBox.intersect(t.BoundBox):continue
                        if not t.isValid():bad=name+':invalid';break
                        c=s.common(t)
                        if not c.isValid() or c.Volume>1e-5:bad=name;break
                    if bad:break
                if bad:rejects[bad]=rejects.get(bad,0)+1
                else:found[sign].append((centre,shapes))
                if datetime.now(timezone.utc)>=datetime.fromisoformat('2026-10-06T07:00:00+00:00'):
                    raise RuntimeError('Deadline during bounded layout allocation')
        chosen={}
        for sign,front,rear in [(1,'FL','RL'),(-1,'FR','RR')]:
            pairs=[]
            for a,b in itertools.combinations(found[sign],2):
                if a[0][0]>b[0][0]:a,b=b,a
                # Full packages span124mm. Keep an additional4mm axial gap;
                # no interleaving support or crossed opposite factory leads.
                if b[0][0]-a[0][0]<128:continue
                score=abs(a[0][0]+40)+abs(b[0][0]-100)+abs(a[0][1]-sign*66)+abs(b[0][1]-sign*66)
                pairs.append((score,a[0],b[0]))
            if pairs:
                _,chosen[front],chosen[rear]=min(pairs)
        placement_search=dict(tested=tested,free_packages_per_side={str(k):len(v) for k,v in found.items()},
            rejects=rejects,chosen=chosen,scope='Nominal package allocation only; no support/service acceptance')
        print('Side-lane allocation:',placement_search,flush=True)
        if len(chosen)!=4:
            A.closeDocument(d.Name)
            OUT.write_text(json.dumps(dict(status='SIDE_LANES_NO_FOUR_PACKAGE_ALLOCATION',
                selected=False,physical_pass=False,W1_complete=False,W5_complete=False,
                placement_search=placement_search,source_sha256=pins,
                started_utc=started.isoformat(),finished_utc=datetime.now(timezone.utc).isoformat(),
                worker_wall_seconds=round(time.monotonic()-tick,3)),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            assert sha(NATIVE)==pins[NATIVE.relative_to(ROOT).as_posix()]
            return
        placements=chosen;angle=A.Rotation();u=[1,0,0]
    for leg,x,y,source_id,out_id,src_target,out_target in [
        ('FL',15,38,'W041','W026','P_FRONT.2','FL_P.1'),
        ('FR',15,-38,'W042','W037','P_FRONT.3','FR_P.1'),
        ('RL',50,38,'W044','W045','P_REAR.2','RL_P.1'),
        ('RR',50,-38,'W052','W053','P_REAR.3','RR_P.1')]:
        x,y,z=placements[leg]
        centre=A.Vector(x,y,z);ob=d.getObject('MTA_'+leg+'_CP2')
        ob.Placement=A.Placement(centre+angle.multVec(A.Vector(-17.5,-11,-8)),angle)
        for role,sign,wid,target in [('SOURCE',-1,source_id,src_target),('OUTPUT',1,out_id,out_target)]:
            tangent=scale(u,sign);exit_point=add([x,y,z],scale(u,sign*17.5))
            near=add(exit_point,scale(tangent,9));far=add(near,scale(tangent,35.5))
            rot=A.Rotation(A.Vector(1,0,0),A.Vector(*tangent))
            joint=d.addObject('Part::Box',f'Joint_{leg}_{role}')
            joint.Length=35.5;joint.Width=8.1;joint.Height=8.9
            joint.Placement=A.Placement(A.Vector(*near)+rot.multVec(A.Vector(0,-4.05,-4.45)),rot)
            ig.addObject(joint)
            own=f'Factory_{leg}_{role}'
            s=Part.makeCylinder(2.1,9,A.Vector(*exit_point),A.Vector(*tangent))
            f=d.addObject('PartDesign::Feature',own);f.Shape=s;ig.addObject(f)
            factory.append(dict(id=wid,holder=leg,role=role,wire_exit_mm=exit_point,
                joint_factory_port_mm=near,joint_extension_port_mm=far,factory_cut_nominal_mm=20,
                factory_insulated_straight_mm=9,strip_mm=11,
                existing_factory_available_length_confirmed=False,OD4_2_and_port_datum_provisional=True))
            bus,port=target.split('.');bo=d.getObject(bus+'_CP2')
            local_x=5.5+(int(port)-1)*(7.5 if bus in ['P_FRONT','P_REAR'] else 6.75)
            goal=bo.Placement.multVec(A.Vector(local_x,22 if bus in ['P_FRONT','P_REAR'] else 19,5.5 if bus in ['P_FRONT','P_REAR'] else 4.5))
            direction=bo.Placement.Rotation.multVec(A.Vector(0,1,0))*(-1)
            endpoints.append(dict(id=wid,holder=leg,role=role,start=far,tangent=tangent,
                goal=list(goal),goal_u=list(direction),joint=joint.Name,target=bo.Name,
                electrical_a=wires[wid]['a'],electrical_b=wires[wid]['b']))
            roles.append(joint.Name)
    d.recompute()
    if JOINT_SOURCE:
        s1=json.loads((BASE/'interfaces.json').read_text(encoding='utf-8'))['S1_joint_plan']
        for wid,key,bus,port,heading in [('W064','3','P_FRONT',1,[-1,0,0]),
                ('W065','6','P_REAR',1,[1,0,0]),('W067','2','P_SYS',3,[-1,0,0]),
                ('W068','5','P_SYS',4,[1,0,0])]:
            start=add(s1['terminal_centres_mm'][key],scale(heading,22.123))
            bo=d.getObject(bus+'_CP2')
            goal=bo.Placement.multVec(A.Vector(5.5+(port-1)*7.5,22,5.5))
            heading_in=bo.Placement.Rotation.multVec(A.Vector(0,1,0))*(-1)
            endpoints.append(dict(id=wid,holder='S1',role='SOURCE_SWITCH',start=start,tangent=heading,
                goal=list(goal),goal_u=list(heading_in),joint='S1_ring_'+key,target=bo.Name,
                electrical_a=wires[wid]['a'],electrical_b=wires[wid]['b']))
        if HORIZONTAL:
            sp=json.loads((BASE/'interfaces.json').read_text(encoding='utf-8'))['S0_joint_plan']
            heading=sp['ring_barrel_directions'][1]
            start=add(sp['stud_centres_mm'][1],scale(heading,26.9))
            bo=d.getObject('P_SYS_CP2');goal=bo.Placement.multVec(A.Vector(5.5,22,5.5))
            direction=bo.Placement.Rotation.multVec(A.Vector(0,1,0))*(-1)
            endpoints.append(dict(id='W066',holder='S0',role='SOURCE_SWITCH',start=start,tangent=heading,
                goal=list(goal),goal_u=list(direction),joint='S0_ring_OUT',target=bo.Name,
                electrical_a=wires['W066']['a'],electrical_b=wires['W066']['b']))
    torso=d.getObject('TorsoEnvelope').Shape.copy()
    owners={o.Name:o.Shape.copy() for o in d.Objects if 'Shape' in o.PropertiesList
        and o.Name not in ['TorsoEnvelope','BatteryNominal']
        and (any(p.Name in ['InteriorReservations','HarnessCandidate','S0TerminalCandidates',
            'S1TerminalCandidates','ServiceReservations','ATOStackCandidates'] for p in o.InList)
             or 'Category' in o.PropertiesList and o.Category!='electronics')}
    # Initial package contradiction is retained; a route search must not hide it.
    package_hits=[]
    parts=[d.getObject('MTA_'+leg+'_CP2').Name for leg in ['FL','FR','RL','RR']]+roles
    if UPPER_LEVEL:parts += [n for n in invalidated if d.getObject(n)]
    for name in parts:
        s=d.getObject(name).Shape
        outside=s.cut(torso)
        if not outside.isValid() or outside.Volume>1e-5:
            package_hits.append(dict(pair=[name,'TorsoEnvelope'],outside_mm3=outside.Volume,
                basis='Outside nominal interior, not printable shell clearance'))
        for other,t in owners.items():
            if other==name or other.startswith('Joint_'+name[4:6]+'_'):continue
            if name.startswith('S1_') and other.startswith('S1_'):continue
            if s.BoundBox.intersect(t.BoundBox):
                if not s.isValid() or not t.isValid():
                    package_hits.append(dict(pair=[name,other],error='Invalid input; not clearance'));continue
                c=s.common(t)
                if not c.isValid():package_hits.append(dict(pair=[name,other],error='Invalid common'))
                elif c.Volume>1e-5:package_hits.append(dict(pair=[name,other],volume_mm3=c.Volume,
                    basis='nominal reservation intersection; not supplier-material proof'))
    print('Coupled package preflight:',len(package_hits),'contradictions',flush=True)
    routes=[];failed=[]
    existing_routes=[]
    def plan(ep):
        begin=time.monotonic();cache={};rejects={};expanded=0
        def safe(p):
            k=tuple(round(c/2) for c in p)
            if k in cache:return cache[k]
            q=A.Vector(*(2*c for c in k));padding=4.1
            # Occupancy cell covers wire radius plus cell quantisation, not a
            # physical swept check. Final candidate requires exact pipe gate.
            for name,s in owners.items():
                if name==ep['joint'] and length(minus(list(q),ep['start']))<12:continue
                if name==ep['target'] and length(minus(list(q),ep['goal']))<18:continue
                bb=s.BoundBox
                if not (bb.XMin-padding<=q.x<=bb.XMax+padding and bb.YMin-padding<=q.y<=bb.YMax+padding and bb.ZMin-padding<=q.z<=bb.ZMax+padding):continue
                try:
                    if not s.isValid():blocked=True
                    else:blocked=s.isInside(q,1e-7,True) or s.distToShape(Part.Vertex(q))[0]<padding
                except Exception:blocked=True
                if blocked:
                    rejects[name]=rejects.get(name,0)+1;cache[k]=False;return False
            for axis in AXES:
                if not torso.isInside(q+A.Vector(*scale(axis,4.5)),1e-7,True):
                    rejects['TorsoEnvelope']=rejects.get('TorsoEnvelope',0)+1;cache[k]=False;return False
            for curve in existing_routes:
                if any(length(minus(list(q),v))<5.8 for v in curve):
                    rejects['Earlier_MTA_route']=rejects.get('Earlier_MTA_route',0)+1;cache[k]=False;return False
            cache[k]=True;return True
        def clear(ss):return all(safe(p) for s in ss for p in points(s))
        initial=line(ep['start'],ep['tangent'],3)
        if not clear([initial]):
            return None,dict(reason='connector_runout_blocked',expanded=0,rejects=rejects)
        start=initial['end_mm'];serial=itertools.count();heap=[];seen={}
        heapq.heappush(heap,(length(minus(ep['goal'],start)),next(serial),start,ep['tangent'],[initial],3))
        while heap and expanded<1400 and time.monotonic()-begin<45:
            if datetime.now(timezone.utc)>=datetime.fromisoformat('2026-10-06T07:00:00+00:00'):break
            _,_,p,heading,path,cost=heapq.heappop(heap)
            k=tuple(round(c/6) for c in p)+tuple(round(c,3) for c in heading)
            if seen.get(k,float('inf'))<=cost:continue
            seen[k]=cost;expanded+=1
            ending=suffix(p,heading,ep['goal'],ep['goal_u'])
            if ending and clear(ending):
                ss=path+ending;return ss,dict(expanded=expanded,planning_wall_seconds=round(time.monotonic()-begin,3),rejects=rejects)
            options=[line(p,heading,L) for L in [9,25.2,50.4]]
            for v in AXES:
                c=dot(heading,v)
                if abs(c)<1-1e-7:options.append(arc(p,heading,v))
            for s in options:
                if not clear([s]):continue
                point=s['end_mm'];h=s['tangent'] if s['kind']=='line' else s['end_tangent'];nc=cost+s['length_mm']
                priority=nc+1.12*length(minus(ep['goal'],point))
                heapq.heappush(heap,(priority,next(serial),point,h,path+[s],nc))
        return None,dict(reason='bounded_search_no_complete_path',expanded=expanded,
            planning_wall_seconds=round(time.monotonic()-begin,3),rejects=rejects)

    if not package_hits:
        if JOINT_SOURCE:
            d.saveAs(str(BASE/('MTAHorizontalCandidate.FCStd' if HORIZONTAL else 'MTASourceLayoutCandidate.FCStd')))
        for ep in ([] if HORIZONTAL else endpoints):
            try:
                ss,info=plan(ep)
            except Exception as exc:
                ss=None;info=dict(reason='planning_error_not_clearance',error=repr(exc))
            print(ep['id'],ep['role'],'PLANNED' if ss else 'OPEN',info.get('expanded'),flush=True)
            if ss:
                L=sum(s['length_mm'] for s in ss)
                allowance=14.452+14 if ep['holder']=='S1' else 11+(14 if ep['target'] in ['P_FRONT_CP2','P_REAR_CP2'] else 11)
                routes.append(dict(**ep,segments=ss,extension_nominal_mm=L+allowance,
                    endpoint_straight_mm=9,connector_runout_mm=3,
                    runout_is_NOT_an_insulation_grip=True,info=info))
                existing_routes.append([p for s in ss for p in points(s)])
            else:failed.append(dict(**ep,info=info))
        if HORIZONTAL:failed=[dict(**ep,info=dict(reason='Package_gate_saved_full_route_search_pending')) for ep in endpoints]
    else:
        failed=[dict(**ep,info=dict(reason='shared_package_requires_change_before_route_search')) for ep in endpoints]
    A.closeDocument(d.Name)
    assert sha(NATIVE)==pins[NATIVE.relative_to(ROOT).as_posix()]
    report=dict(status='ALL_SHARED_ROUTES_PLANNED_EXACT_PIPE_GATE_REQUIRED' if len(routes)==len(endpoints) else 'SHARED_PLAN_OPEN_NO_CAD_ACCEPTANCE',
        selected=False,physical_pass=False,W1_complete=False,W5_complete=False,
        complete_routes=len(routes),required_routes=len(endpoints),factory_segments=factory,routes=routes,open_routes=failed,
        shared_package_contradictions=package_hits,
        placement_search=placement_search,
        invalidated_interfaces=invalidated,
        changed_layout=dict(MTA_centres_mm=placements,
            MTA_axis=u,MTA_body_size_assumed_mm=[35,22,16],ATO_flange_mm=126 if UPPER_LEVEL else 122,ATO_bank_y_mm=62,
            side_WAGO_centres_y_mm=81.5,Monitor_origin_mm=[108,0,42]),
        inventory_candidate=dict(inline2212411_installed=8,source_additions=4,output_replacements=4,
            removed_four_existing_output_roles=True,retained_XB11_and_post_F0=True,purchase_or_selection=False),
        assumptions=['MTA body35x22x16 and exact opposing exit datums unknown',
            'Factory20mm/side is a required prototype cut length NOT availability from L140',
            'MTA OD4.2/R25.2 planning assumptions; factory strand class unconfirmed',
            'WAGO inline port datum/lever envelope not dimensioned',
            '3mm connector runout is NOT grip; actual strain supports remain OPEN',
            'Changed12ATO/10WAGO/Monitor previous mounts and routes not qualified'],
        proof_scope='Bounded centreline planning against nominal envelopes and retained shapes; samples NOT exact swept BRep proof or complete harness',
        source_sha256=pins,started_utc=started.isoformat(),finished_utc=datetime.now(timezone.utc).isoformat(),
        worker_wall_seconds=round(time.monotonic()-tick,3))
    OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(report['status'],len(routes),'/',len(endpoints),'; no selection',flush=True)


if __name__=='__main__':main()
