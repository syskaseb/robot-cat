"""Check the whole rotated IN lug, its local channel, and the retained S0 stack."""
from pathlib import Path
from runpy import run_path
from zipfile import ZipFile
from xml.etree import ElementTree
import hashlib
import json
import math
import FreeCAD as App
import Part

p=Path(__file__).resolve().parent
V=App.Vector; Z=V(0,0,1)
source_path=p.parent/'20D/whole-cat20D.FCStd'
assert hashlib.sha256(source_path.read_bytes()).hexdigest()=='b1549964028b289ccc9b27adb023ed804f331b8f4fa23159c00a072975a750e9'
def box(q):
    return Part.makeBox(*(b-a for a,b in zip(q[:3],q[3:])),V(*q[:3]))
def common(a,b):
    if not a.BoundBox.intersect(b.BoundBox):return None
    q=a.common(b)
    assert q.isNull() or q.isValid()
    return q if q.Volume>1e-4 else None
def bounds(s):
    b=s.BoundBox
    return [round(q,4) for q in (b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax)]
def unit(v):
    return v/v.Length
def circle(start,u,v,r):
    angle=math.acos(u.dot(v))
    n=unit(v-u*math.cos(angle))
    def at(theta):
        return start+r*(math.sin(theta)*u+(1-math.cos(theta))*n)
    e=Part.Arc(at(0),at(angle/2),at(angle)).toShape()
    return e,at(angle)
def sweep(e,r):
    po=e.valueAt(e.FirstParameter)
    sec=Part.Wire([Part.makeCircle(r,po,e.tangentAt(e.FirstParameter))])
    s=Part.Wire([e]).makePipeShell([sec],True,True)
    assert s.isValid() and len(s.Solids)==1
    return s
def read_source(n):
    with ZipFile(source_path) as f:
        tree=ElementTree.fromstring(f.read('Document.xml'))
        out={}
        for k in n:
            q=tree.find(f"./ObjectData/Object[@name='{k}']/Properties/Property[@name='Shape']/Part")
            if q is not None:
                s=Part.Shape()
                s.importBrepFromString(f.read(q.get('file')).decode('ascii'))
                out[k]=s
        return out
point=V(166.5,74,104.5)
outward=V(-math.sqrt(3)/2,0,.5)
t=-outward
mouth=point+26.9*outward
start_collar=mouth-t*5.9
bend_floor=V(105,40,151.65)
def build_ending_at(a,b,t):
    d=unit(b-a)
    u=d*(2*t.dot(d))-t
    r=(b-a).Length/(2*math.sin(math.acos(u.dot(t))/2))
    edge,tip=circle(a,u,t,r)
    assert tip.distanceToPoint(b)<1e-7
    return edge,r,u
lower,r_lo,v=build_ending_at(bend_floor,start_collar,t)
handoff=V(74,-5,149)
upper,r_up,u=build_ending_at(handoff,bend_floor,v)
gateway=V(4,12.823529,145.558824)
forward=unit(V(51,-5,4.5))
def biarc(a,b,t0,t1):
    d=b-a
    w=d.dot(t0+t1)
    k=2*(1-t0.dot(t1))
    arm=(-w+math.sqrt(w*w+k*d.dot(d)))/k
    mid=(a+arm*t0+b-arm*t1)*.5
    h=unit(mid-a);j=unit(b-mid)
    tan_mid=2*t0.dot(h)*h-t0
    assert (tan_mid-(2*t1.dot(j)*j-t1)).Length<1e-7
    rr1=(mid-a).Length/(2*math.sin(math.acos(t0.dot(tan_mid))/2))
    rr2=(b-mid).Length/(2*math.sin(math.acos(t1.dot(tan_mid))/2))
    e1,end1=circle(a,t0,tan_mid,rr1)
    e2,end2=circle(mid,tan_mid,t1,rr2)
    assert end1.distanceToPoint(mid)<1e-7 and end2.distanceToPoint(b)<1e-7
    return e1,e2,rr1,rr2
e1,e2,r1,r2=biarc(gateway,handoff,forward,u)
edges={'inboard_transfer_start':e1,'inboard_transfer_return':e2,
       'upper_regional_handoff':upper,'fixed_R_lower_fan':lower,'straight_at_barrel':Part.makeLine(start_collar,mouth)}

names=[
 'C20_MTA_RR','NIGHT_MTA0100335_UNKNOWN_3','E19_RearBase','E19_RearLid','F19_RearCap',
 'PCA9685_Adafruit815_PCB','E1_populated_prototype_board','G19_E1_population_limits',
 'S0_body','S0_neck','S0_key','S0_ring_IN_0_0','S0_nut_IN_0_0','S0_washer_IN_0_0',
 'S0_stud_IN_0_0','S0_ring_OUT_0_0','S0_stud_OUT_0_0','S0_washer_OUT_0_0','S0_nut_OUT_0_0',
 'D19_SIDE_BUNDLE_POS','E19_WagoRearPos','Speaker','E19_BUS_PCB','E19_BUS_population',
 'H19_Wires_speaker','PBAY_P_SYS','PBAY_F_PI','G19_Group_JRP','G19_Group_JRY','G19_Group_JRT',
 'G19_Group_POWER','E19_KeyedTail','TAIL_FIXED_OUTER_RACE_CAP','NIGHT_INLINE_RR_W052',
 'NIGHT_INLINE_RR_W053','E19_BatteryDoor','C20_BatteryUpperBridge','E19_ForeLid','H19_FrontFrame',
 'Motor_ATO4A_1_2','Motor_ATO4A_1_5','BNO085','C20_Pack_XT60_F','XT60H_mated_with_boots',
 'H19_MainTrunk','H19_PowerBranch','G19_Group_I2S','F0_FHAC0002_30A','G19_PiAudioBoot','PBAY_POST_F0'
]

def rec(a,b):
    c=common(a,b)
    if c is None:
        return None
    actual_vertices=[[round(q,5) for q in v.Point] for v in c.Vertexes]
    vertex_bounds=[*[min(v[i] for v in actual_vertices) for i in range(3)],
                   *[max(v[i] for v in actual_vertices) for i in range(3)]]
    return {'mm3':round(c.Volume,6),'vertex_bounds_mm':vertex_bounds}

def pose_checks():
    src=read_source(names)
    old=src['S0_ring_IN_0_0']
    clocked=old.copy()
    clocked.rotate(point,V(0,1,0),-30)
    assert abs(old.Volume-clocked.Volume)<1e-5
    ring_hole=[f for f in clocked.Faces if isinstance(f.Surface,Part.Cylinder)
               and abs(f.Surface.Radius-5.02)<1e-6]
    assert len(ring_hole)==1
    hole_axis=unit(ring_hole[0].Surface.Axis)
    pin=ring_hole[0].Surface.Center
    assert abs(hole_axis.y)>.99999 and math.hypot(pin.x-point.x,pin.z-point.z)<1e-4

    lid_reference=run_path(str(p.parent/'20D/layout.py'))
    rr_left=box([129.5,61.5,139.5,142.5,79.5,158])
    rr_right=box([174.5,61.5,139.5,187.5,79.5,158])
    rr_lid=box([142.5,61.5,158,174.5,79.5,174])
    related=dict(src)
    related['S0_ring_IN_0_0']=clocked
    related.update({n:box(lid_reference[n]) for n in ('BOX_SWEEP','HAND_M','HAND_F','HAND_F_UPPER')})
    related.update(RR_installed_project_left_full_end=rr_left,RR_installed_project_right_full_end=rr_right,
                   RR_project_open_lid=rr_lid)
    section_results={}
    for label,e in edges.items():
        outer=sweep(e,3.35)
        hits={n:r for n,s in related.items() if (r:=rec(outer,s))}
        section_results[label]={'length_mm':round(e.Length,6),'outer_project_clearance_OD_mm':6.7,
                                'bounds_mm':bounds(outer),'hits':hits}
    ring_hits={n:r for n,s in src.items() if n!='S0_ring_IN_0_0' and (r:=rec(clocked,s))}
    assert set(ring_hits)=={'S0_body'},ring_hits
    old_proxy=rec(old,src['S0_body'])
    assert old_proxy['mm3']>ring_hits['S0_body']['mm3']

    shifted=clocked.copy()
    shifted.translate(V(0,-.025,0))
    washer_bearing=shifted.common(src['S0_washer_IN_0_0']).Volume/.025
    assert washer_bearing>100
    assert not rec(clocked,src['S0_nut_IN_0_0']) and not rec(clocked,src['S0_washer_IN_0_0'])

    out=rec(src['S0_ring_OUT_0_0'],src['E19_RearBase'])
    out_of_case=src['S0_ring_OUT_0_0'].cut(src['S0_body'])
    assert abs(rec(out_of_case,src['E19_RearBase'])['mm3']-out['mm3'])<1e-3
    tool=Part.makeCylinder(12,26,V(166.5,62.95,104.5),V(0,-1,0))
    tool_check={n:rec(tool,src[n]) for n in ('E19_RearBase','E1_populated_prototype_board','S0_body',
                                           'S0_stud_OUT_0_0','S0_ring_OUT_0_0','S0_nut_OUT_0_0','S0_washer_OUT_0_0')}
    # One candidate for keeping the prior IN angle after moving all of RR.
    rr_candidate=box([169,47,139,187,79,157])
    rr_in=box([168,33,140,188,47,155])
    root=box([163,76,129,192,89,139])
    fallback={'body_bounds_mm':bounds(rr_candidate),'inboard_factory_end_bounds_mm':bounds(rr_in),
              'inboard_end_vs_E1':rec(rr_in,src['E1_populated_prototype_board']),
              'support_region_bounds_mm':bounds(root),'support_region_common':rec(root,src['E19_RearBase'])}
    min_r=min(r1,r2,r_up,r_lo)
    assert min_r-2.1>=25.2 and out['mm3']>73 and fallback['inboard_end_vs_E1']['mm3']>500
    assert all(not x['hits'] for x in section_results.values()),section_results
    return {
       'full_IN_lug_bounds_mm':bounds(clocked),'IN_washer_bearing_mm2':round(washer_bearing,6),
       'stud_centre_mm':[point.x,point.y,point.z],'rotation_about_world_Y_degrees':-30,
       'wire_entry_mm':[round(x,6) for x in mouth],
       'IN_vs_conservative_undimensioned_case_proxy':{'prior':old_proxy,'clocked':ring_hits['S0_body']},
       'new_regional_section':section_results,
       'minimum_centre_R_mm':round(min_r,6),'minimum_inner_R_mm':round(min_r-2.1,6),
       'retained_OUT_ring_vs_actual_rear_wall':out,
       'OUT_overlap_outside_case_proxy':True,
       'open_bay_socket_24mm_OD_project_reserve':tool_check,
       'RR_alternate_zone_first_falsifier':fallback,
    }

if __name__=='__main__':
    import os
    base=p.parent/'20D'
    hw=next(q for q in p.parents if q.name=='hardware')
    def read(q):
        return json.loads(q.read_bytes())
    def sha(q):
        return hashlib.sha256(q.read_bytes()).hexdigest()
    checks=pose_checks()
    data=read(base/'20D-final-gate.json')['wire_budgets']['W076_custom']
    prefix_pts=[V(*row) for row in data['allocated_waypoints']]
    j=next(i for i in range(len(prefix_pts)-1) if prefix_pts[i].x<4<prefix_pts[i+1].x)
    prefix=sum((b-a).Length for a,b in zip(prefix_pts[:j],prefix_pts[1:j+1]))
    prefix+=(gateway-prefix_pts[j]).Length
    local=sum(e.Length for e in edges.values())
    parts={'TE130207_F':hw/'reference/manual-stop-p0-2026-09-24/130207-TE.pdf',
           'HELLA_mount_sheet':hw/'reference/power-hardware-2026-09-23/HELLA-46020100.pdf',
           'HELLA_catalogue':hw/'reference/power-hardware-2026-09-23/HELLA-switches.pdf',
           'HELU23802_fixed_radius':hw/'electronics/power-platform/POWER-WIRE-P0.md',
           '20D_saved_native':source_path,'20F_current_azimuth_obstruction':p/'20F-interface-gate.json'}
    plan={
      'status':'IN_CHANNEL_PROVEN_DIGITALLY_WHOLE_S0_STACK_HOLD_RETAINED_OUT',
      'actual_input':'01a1f9b0-fcf3-7ef1-b684-2a4247814e1c',
      'source_pins':{k:{'path':v.relative_to(hw).as_posix(),'sha256':sha(v)} for k,v in parts.items()},
      'clocking_source':{
          'TE_drawing':'Round 10.3 +/- 0.13 mm hole for M10, no keyed feature on the tongue in revision F.',
          'HELLA_mount_sheet':'Low-resolution family illustration with two screw contacts, no dimensioned rear contact seat or permitted clocking angle. Exact body-to-insulated-barrel and tool access cannot be inferred from this drawing.',
          'S0_case_native':'Full 57 mm round family enclosure proxy extends through the terminal zone. Existing modeled contact with the ring is inherited. External stack and chassis constraints are kept exact. No space inside the proxy is credited for routing an insulated wire.',
          'polarity':'IN and OUT are project identifiers. Retained on their original studs and unchanged protection.'
      },
      'checks':checks,
      'assembly_disposition':'Lay the wire from the cable bay to the inward clock with access from above. A socket cannot enter on axis through the frame and populated E1. Bench installation before seating the switch is a conditional operation. The full modeled OUT ring crosses the retained rear printed wall at X207.4–209 even with the cover absent. No qualified released assembly with both stacks, no print change.',
      'unit_budget_mm':{
          '20D_retained_upstream_regional_length_to_x4':round(prefix,3),
          '20F_qualified_local_IN_geometry_length':round(local,3),
          'ends_once':data['terminal_debits_mm'],'laying_once':data['one_laying_allowance_mm'],
          'conditional_unreleased_W076_blank':math.ceil(prefix+local+data['terminal_debits_mm']+data['one_laying_allowance_mm']),
          'actual_accepted_cut':None,'nominal_HELU_stock':9000,'physical_HELU_stock':None
      },
      'retained_prints':'All ten 20C/20D prints and all 19I parts, pending whole joint decision.',
      'new_prints':0,'native_changed':False,'physicalPASS':False,'actualfit':None,'cut':None,'slack':None
    }
    out=p/'20F-S0-stack-gate.json'
    prior=out.read_bytes() if out.exists() else None
    tmp=out.with_suffix('.tmp')
    with tmp.open('x',encoding='utf-8',newline='\n') as f:
        json.dump(plan,f,ensure_ascii=False,indent=2);f.write('\n')
    assert (out.read_bytes() if out.exists() else None)==prior
    os.replace(tmp,out)
    print(plan['status'],checks['minimum_inner_R_mm'],checks['retained_OUT_ring_vs_actual_rear_wall'],plan['unit_budget_mm'],flush=True)
