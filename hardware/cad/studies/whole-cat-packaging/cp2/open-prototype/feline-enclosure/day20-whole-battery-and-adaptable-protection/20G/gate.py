"""Assemble the scoped 20G evidence without mutating the native source."""
from pathlib import Path
from runpy import run_path
from zipfile import ZipFile
import hashlib
import json
import math
import os
import FreeCAD as App
import Part

p=Path(__file__).resolve().parent
hw=next(x for x in p.parents if x.name=='hardware')
g=run_path(str(p/'candidate.py'))
a=run_path(str(p/'assembly.py'))
h=run_path(str(p/'hardware.py'))
f=run_path(str(p.parent/'20F/clocked.py'))
source=g['source_shapes']()
rings=g['chosen_rings'](source)
parts={**source,**rings}
V=App.Vector
R=g['r']
box=g['box']; common=g['common']; sweep=g['sweep']; xyz=g['xyz']
rec=a['record']
baseline=p.parent/'20F/20F-S0-stack-gate.json'
sha=lambda q:hashlib.sha256(q.read_bytes()).hexdigest()
assert sha(baseline)=='97ec4d0a24505cc9766fc13dd225d5690638c2dcfc78562518f5a14c77ea23f1'
frozen=json.loads(baseline.read_bytes())

def positives(shape,targets):
    return {k:h for k,s in targets.items() if (h:=rec(shape,s))}

bounds=g['bounds']
out_edges=g['out_edges']
out_gauge={n:sweep(e,3.35) for n,e in out_edges.items()}
in_gauge={n:sweep(e,3.35) for n,e in f['edges'].items()}
layout=run_path(str(p.parent/'20D/layout.py'))
service_boxes={k:box(layout[k]) for k in ('BOX_SWEEP','HAND_M','HAND_F','HAND_F_UPPER')}
out_hits={n:positives(s,{**parts,**service_boxes}) for n,s in out_gauge.items()}
assert all(not row for row in out_hits.values()),out_hits
in_new_hits={n:positives(s,{g['ring_out']:rings[g['ring_out']],**out_gauge}) for n,s in in_gauge.items()}
assert all(not q for q in in_new_hits.values()),in_new_hits
ring_fit={n:positives(s,{k:x for k,x in parts.items() if k!=n}) for n,s in rings.items()}
assert all(set(t)=={'S0_body'} for t in ring_fit.values()),ring_fit
washer_bearing={}
for suffix in ('IN','OUT'):
    n='S0_ring_'+suffix+'_0_0'
    bearing=rings[n].copy()
    bearing.translate(V(0,-.025,0))
    washer_bearing[suffix]=round(bearing.common(source['S0_washer_'+suffix+'_0_0']).Volume/.025,6)

phase_parts={k:parts[k] for k in a['holds'] if k in parts and k!='S0_key'}
rigid={k:parts[k] for k in g['stack_names']}
phase={}
for n,fn in (('top_drop_after_m10_bench_prewiring',a['drop_shape']),('six_mm_axial_seating',a['axial_shape'])):
    phase[n]={k:positives(fn(k,s),phase_parts) for k,s in rigid.items()}
    assert all(not q for q in phase[n].values()),(n,phase[n])

def line(x,y):return Part.makeLine(x,y)
def park(start,lead_dir,first_length,end_dir,last_length):
    a=start+lead_dir*first_length
    bend,b=g['circle'](a,lead_dir,end_dir,R)
    return [line(start,a),bend,line(b,b+end_dir*last_length)]
Z=V(0,0,1)
parks={'IN':park(f['mouth'],g['unit'](V(-math.sqrt(3)/2,0,.5)),16,Z,30),
       'OUT':park(g['mouth_out'],g['out_axis'],2.5,V(-.5,0,math.sqrt(3)/2),30)}
def tight_bb(shape):
    # Section bounds from analytic edges and known gauge radius use a solid
    # mesh only to tighten the conservative envelope at the empty upper exit.
    verts,faces=shape.tessellate(.08)
    return [*[min(v[i] for v in verts)-.12 for i in range(3)],
            *[max(v[i] for v in verts)+.12 for i in range(3)]]
parks_results={}
for side,edges in parks.items():
    ss=[sweep(e,3.35) for e in edges]
    records=[]
    for s in ss:
        b=tight_bb(s)
        top=box([b[0],b[1]+a['inboard'],b[2],b[3],b[4],b[5]+a['stack_growth']])
        # Check the actual moving gauge at seated/open pose separately from
        # the box above, whose conservative width is used to flag the rim.
        records.append({'occupied_sweep_box_mm':bounds(top),
                        'open_frame_broad_contacts':positives(top,phase_parts),
                        'open_seated_occupied_section_contacts':positives(s,phase_parts),
                        'versus_populated_E1':rec(top,parts['E1_populated_prototype_board'])})
    parks_results[side]={'staged_length_mm':round(sum(e.Length for e in edges),4),'checks':records}

# E1 stays soldered. Its installation is the whole E1 envelope without the
# temporary loose leads in the vertical working space beside the frame.
e1={}
for k in ('E1_populated_prototype_board','G19_E1_population_limits'):
    b=a['bbvals'](parts[k]);b[5]+=a['stack_growth']
    e1[k]=positives(box(b),rigid)
assert all(not q for q in e1.values()),e1
end_access={}
for name,(lo,hi) in {
    'P_SYS.1_handle_lever':([156,48.3,67.5],[166.5,56.8,89]),
    'P_SYS.1_insert_far_end':([165,47.5,57.5],[184,57,79.5])
}.items():
    q=box([*lo,*hi])
    end_access[name]=positives(q,{k:parts[k] for k in ('E19_RearBase','E1_populated_prototype_board',
      'S0_body','PBAY_F_PI','C20_MTA_RR','S0_ring_IN_0_0','S0_ring_OUT_0_0','D19_SIDE_BUNDLE_POS')})
assert all(not q for q in end_access.values()),end_access

bench={}
for k,x in (('IN',166.5),('OUT',190.5)):
    other='IN' if k=='OUT' else 'OUT'
    # Same 24 mm OD nominal socket, stopping 0.25 mm before the washer-side
    # nut face. 7.75 of the nominal 8 mm nut flank remains engaged.
    tool=Part.makeCylinder(12,34,V(x,70.70,104.5),V(0,-1,0))
    relevant={n:s for n,s in rigid.items()
              if n.startswith((f'S0_stud_{other}',f'S0_ring_{other}',f'S0_nut_{other}',
                               f'S0_washer_{other}',f'S0_ring_{k}'))}
    bench[k]={'external_tool_checks':positives(tool,relevant),
              'retained_case_proxy_overlap_conditional':rec(tool,parts['S0_body'])}
assert all(not q['external_tool_checks'] for q in bench.values()),bench

steel=h['load']()
plate=source['E19_RearBase']
points=[(178.5,85.5,3.25),(178.5,104.5,12.0),(178.5,123.5,3.25)]
pattern_tools=[Part.makeCylinder(r,4.3,V(x,98.9,z),V(0,1,0)) for x,z,r in points]
pattern_read=[{'point_mm':[x,99,z],'diameter_mm':2*r,'retained_material_in_bore':rec(q,plate)}
              for (x,z,r),q in zip(points,pattern_tools)]
# Frozen stock transported as whole source geometry. A through-bore control
# answers the limited question "would restoring only the specified pattern
# make the full fixed stack clear?". It is never exported or credited.
panel_control=plate.cut(Part.makeCompound(pattern_tools),1e-6).removeSplitter()
assert panel_control.isValid() and len(panel_control.Solids)==1
moved=parts['S0_body'].copy();moved.translate(V(0,.02,0))
seat_before=moved.common(plate).Volume/.02
seat_control=moved.common(panel_control).Volume/.02
material_key={}
for n,s in steel.items():
    material_key[n]={'bounds_mm':bounds(s),
                     'key_full_work_envelope':rec(s,parts['S0_key']),
                     'body_family_proxy':rec(s,parts['S0_body']),
                     'retained_frame':rec(s,plate),
                     'pattern_restored_frame_control':rec(s,panel_control)}
assert any(q['key_full_work_envelope'] for q in material_key.values())
history=Path(h['source'])
steel_archive=Path(h['archive'])
map_path=p.parent.parent/'day19-complete-first-fit/whole-termination-plan.json'
parent=json.loads(map_path.read_bytes())
mapping={x['wire']:x for x in parent['wires']}
assert mapping['W066']['ends']==['S0.out','P_SYS.1']
assert mapping['W076/factory']['ends']==['F0.out','POST_F0.1']
assert mapping['W076/custom']['ends']==['POST_F0.2','S0.in']
assert mapping['W077']['ends']==['F_PI.out','SPLICE_PI.16']
term=mapping['W066']['material'][0]['termination_project_allowance_mm']
laying=20
length=sum(e.Length for e in out_edges.values())
def pin(q):
    return {'path':q.relative_to(hw).as_posix(),'sha256':sha(q)}
proof={
    'actual_input':'01a1f9cb-6621-7862-a714-44ba442ff708',
    'status':'PAIRED_ELECTRICAL_LAYOUT_AND_OPEN_INSERTION_SUPPORTED_FASTENING_HOLD',
    'turn_scope':'One upward OUT direction, positive-Y outward body retained. Order uses bench M10 access followed by open-frame insertion and later E1.',
    'source_pins':{
       '20D_native':pin(g['src_path']),'20F_scoped_IN':pin(baseline),
       '19I_graph':pin(map_path),'source_M6_steel_geometry':pin(steel_archive),'source_M6_role_and_datum':pin(history),
       'HELLA_mount_pattern':pin(hw/'reference/power-hardware-2026-09-23/HELLA-46020100.pdf'),
       'TE130207':pin(hw/'reference/manual-stop-p0-2026-09-24/130207-TE.pdf'),
       'HELU_23802':pin(hw/'electronics/power-platform/POWER-WIRE-P0.md')},
    'terminal_map':{n:mapping[n]['ends'] for n in ('W066','W076/factory','W076/custom','W077')},
    'full_terminal_stacks':{'IN_clock_about_Y_deg':g['in_clock'],'OUT_clock_about_Y_deg':g['out_clock'],
                           'IN_stud':xyz(g['pin_in']),'OUT_stud':xyz(g['pin_out']),
                           'IN_mouth':xyz(f['mouth']),'OUT_mouth':xyz(g['mouth_out']),
                           'nominal_washer_contact_mm2':washer_bearing,'only_case_proxy_overlap':ring_fit},
    'W066_YZ_and_XZ_regional_fan':{'min_inner_R_mm':round(R-2.1,5),'minimum_intrusion_proof_gauge_OD_mm':6.7,
                                  'tangent_near_P_SYS.1':[-1,0,0],
                                  'straight_length_before_P_SYS_face_mm':round(float(g['straight'][-1]),4),
                                  'affected_neighbor_checks':out_hits,'20F_IN_changed_neighbor_checks':in_new_hits},
    'assembly':{
        'bench_M10_tool_project_OD_mm':24,'flank_engagement_nominal_mm':7.75,'M10_bench':bench,
        'first_case_drop_mm':64,'first_case_drop_at_world_delta_Y_mm':-6,'rigid_insertion':phase,
        'loose_wire_staging':parks_results,'installed_soldered_E1_clear_of_S0':e1,
        'far_P_SYS_connection_access':end_access,
        'qualified_scope':'Rigid prewired body stack insertion and final wire occupancy in CAD. Loose handling views represent open stages. Actual HELLA rear seat, M10 insulation and physical socket fit have to be compared to the source assembly.'},
    'mounting':{
        'nominal_stock':{'DIN912_M6x20':2,'washers_6p4x12x1p6':4,'AF10_M6_nut_5mm':2,'ownership':None,'purchase_authorized':False},
        'nominal_source_axes':'38 mm vertical pattern perpendicular to the fixed lateral pole pair. Manufacturer mounting drawing supplies pitch and holes. Relative clock uses the earlier selected project datum and remains a physical comparison.',
        'actual_pattern_frozen_base':pattern_read,
        'outer_source_seat_Y_mm':102.0,
        'retained_case_axial_seat_mm2':round(seat_before,4),'bore_only_control_case_seat_mm2':round(seat_control,4),
        'fixing_stack_controls':material_key,
        'whole_stack_result':'HOLD. Existing key handling/actuation envelope extends 15 mm from the operator axis beginning at Y102. Outer washers at radius 19 with radius 6 reach to 13 mm in that envelope. To satisfy 1.25 mm, the real rotating near-panel radius must be at most 11.75 mm in the washer band Y102 to 103.6, and at most 12.75 mm in the cap-head band to Y109.6. Actual axial key/shaft and through-mount seat are not dimensioned by the selected sources. The bore-only print cannot resolve that interaction.',
        'native_control_exported':False},
    'planning_unit_budgets':{
        'W066':{'free_fan_mm':round(length,4),'terminal_project_allowance_once':term,'laying_reserve_once':laying,
                'conditional_planning_blank_mm':math.ceil(length+term+laying),'actual_cut_mm':None},
        'W076/custom':{'conditional_planning_blank_mm':frozen['unit_budget_mm']['conditional_unreleased_W076_blank'],'actual_cut_mm':None},
        'W076/factory':'Original uncut 12 AWG FHAC0002 output retained with POST.1. No seams or stock credit.',
        'W077':'Preserved the independent F_PI factory output. Its physical length and planning allocation remain outside 20G.',
        'nominal_LAPP0107001_mm':3000,'nominal_HELU23802_mm':9000,'project_ordered_mm':0,'actual_owned_stock':None},
    'decision':'Keep the paired inlet/outlet in the new 20G reference native, with the received base and all printed assets. Do not export the incompatible bore-only control or release a mounted S0 until the source key and flange pass the defined sample checks.',
    'new_prints_released':0,'physicalPASS':False,'actualfit':None,'cut':None,'slack':None
}
out=p/'20G-assembly-gate.json'
prev=out.read_bytes() if out.exists() else None
t=out.with_suffix('.tmp')
with t.open('x',encoding='utf-8',newline='\n') as stream:
    json.dump(proof,stream,ensure_ascii=False,indent=2);stream.write('\n')
assert (out.read_bytes() if out.exists() else None)==prev
os.replace(t,out)
print(proof['status'],proof['planning_unit_budgets'],flush=True)
