"""AUX3 real screw axes +3 open nut approaches from assembled stand pose.

Driver shafts reach above the planned removable rear roof panel. Tool/own
fastener contacts are mating interfaces; all wires/other modules keep1.25.
The wrench U-envelope includes its entire24mm insertion stroke. Service is
stationary and unpowered, not all36 operating poses at the same time.
"""
import gzip,json,time,math
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT,BASE
from receive_feline_rrp_shared_height import load
from feline_source_restraint_plan import box,joined
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound
from plan_feline_pi_root_access import profile_gap
from receive_feline_global_case_candidates import placement
from feline_atomic_save import save_json


def run(world,fixed,meta,pins,selected_hex_keys=False,exact_selected_radius=False,tool_configuration_search=False):
    tick=time.monotonic();sf=OUT/'n01-AUX-upper-escape-joint-plan.json';p=json.loads(sf.read_text());new=load(p)
    received=OUT/'n01-AUX-upper-escape-joint-received.json';rr=json.loads(received.read_text())
    assert rr['status']=='WHOLE_AUX_BOARD_THREE_SOURCE_GRIPS_ROOT_STATIC36_RECEIVED_N01_OPEN' and not rr['failures']
    assert len(rr['completed_motion'])==len(rr['completed_static'])==37
    targets={n:s for n,s in fixed.items() if n not in p['retired']};targets.update(new)
    rows={**meta,**{r['name']:r for r in p['geometry']}};tools={};own_cluster={};q=SolidQueries();checks={}
    for i in (1,2,3):
        prefix='Ref_Material_AUX40922'+str(i);screw=prefix+'Screw_0_0';nut=prefix+'Nut_0_0'
        sb=new[screw].BoundBox;nb=new[nut].BoundBox;centre=nb.Center
        kr=1.5/math.sqrt(3) if exact_selected_radius else 1.
        shaft=Part.makeCylinder(kr if selected_hex_keys else 1.25,50,A.Vector(sb.Center.x,sb.Center.y,sb.ZMax))
        if selected_hex_keys:
            # Selected baseline tool is DIN912M2 AF1.5, not a generic bulky
            # screwdriver. R1 encloses its0.866 circumradius. Include a60deg
            # re-indexable short-arm sweep, rather than a fictitious tall grip.
            origin=A.Vector(sb.Center.x,sb.Center.y,sb.ZMax+50)
            sector=Part.makeCylinder(18+kr,2*kr,origin-A.Vector(0,0,kr),A.Vector(0,0,1),60)
            clock=180 if i==3 else 0;sector.rotate(origin,A.Vector(0,0,1),clock-30)
            edges=[Part.makeCylinder(kr,18,origin,A.Rotation(A.Vector(0,0,1),clock+a).multVec(A.Vector(1,0,0))) for a in (-30,30)]
            handle=joined([sector,*edges])
        else:handle=Part.makeCylinder(4,20,A.Vector(sb.Center.x,sb.Center.y,sb.ZMax+50))
        tools['M2Driver'+str(i)]=joined([shaft,handle]);own_cluster['M2Driver'+str(i)]=dict(screw=screw,prefix=prefix,mode='driver')
        if tool_configuration_search:
            assert selected_hex_keys and exact_selected_radius
            tools.pop('M2Driver'+str(i));own_cluster.pop('M2Driver'+str(i))
            for clock in range(0,360,30):
                origin=A.Vector(sb.Center.x,sb.Center.y,sb.ZMax+18)
                shaft=Part.makeCylinder(kr,18,A.Vector(sb.Center.x,sb.Center.y,sb.ZMax))
                sector=Part.makeCylinder(50+kr,2*kr,origin-A.Vector(0,0,kr),A.Vector(0,0,1),60)
                sector.rotate(origin,A.Vector(0,0,1),clock-30)
                edges=[Part.makeCylinder(kr,50,origin,A.Rotation(A.Vector(0,0,1),clock+a).multVec(A.Vector(1,0,0))) for a in (-30,30)]
                name='M2Driver'+str(i)+'@'+str(clock)
                tools[name]=joined([shaft,sector,*edges]);own_cluster[name]=dict(screw=screw,prefix=prefix,mode='driver',clock_degrees=clock)
        wrench=joined([box([-24,-3.75,-.6],[-3,3.75,.6]),box([-18,-3.75,-.6],[1.8,-2.1,.6]),box([-18,2.1,-.6],[1.8,3.75,.6])])
        wrench.Placement=A.Placement(centre,A.Rotation(A.Vector(0,0,1),180 if i in (1,2) else 0))*wrench.Placement
        tools['M2NutStroke'+str(i)]=wrench;own_cluster['M2NutStroke'+str(i)]=dict(nut=nut,prefix=prefix,mode='wrench')
    dest=OUT/('n01-AUX-upper-key-configurations-received.json' if tool_configuration_search else 'n01-AUX-upper-AF1p5-tools-received.json' if exact_selected_radius else 'n01-AUX-upper-selected-key-tools-received.json' if selected_hex_keys else 'n01-AUX-upper-tools-received.json');assert not dest.exists();pf=dest.with_suffix('.pairs.json.gz')
    result=dict(status='RUNNING_AUX_UPPER_TOOLS',completed=[],failures=[],
        source_sha256={**pins,**{str(f.relative_to(ROOT)):sha(f) for f in (sf,received,ROOT/p['bundle'],BASE/'phase1-material-selection-r4.json',__import__('pathlib').Path(__file__))}},
        planned_rear_roof_panel_removed_for_access=True,tools_may_extend_above_outer_skin=True,
        operating_legs_and_tools_not_simultaneous=True,standing_pose_only=True,
        native_detail_and_full_N08_assembly_OPEN=True,N01_complete=False,physical_pass=False)
    if selected_hex_keys:result.update(selected_AF1p5_key_from_baseline_not_new_purchase=True,
        enclosing_shaft_radius_mm=kr,exact_AF1p5_circumradius_not_a_tuned_fit=exact_selected_radius,required_straight_leg_reach_project_mm=50.,
        short_arm_project_length_mm=18.,short_arm_stroke_degrees=60.,
        owned_tool_reach_confirmation_is_phase2_gate=True)
    selected={}
    if tool_configuration_search:result.update(short_end_axial_mm=18.,long_arm_mm=50.,
        independent_tools_not_used_simultaneously=True,configured_driver_clocks_degrees=list(range(0,360,30)),
        rejected_configurations=[],selected_tool_configurations=selected)
    def save():
        pf.write_bytes(gzip.compress(json.dumps(checks,separators=(',',':')).encode(),mtime=0))
        result.update(checks=len(checks),failures=[k for k,v in checks.items() if not v['ok']],
            pair_rows=pf.relative_to(ROOT).as_posix(),pair_rows_sha256=sha(pf),worker_seconds=round(time.monotonic()-tick,3));save_json(dest,result)
    for n,s in tools.items():
        family=n.split('@')[0]
        if tool_configuration_search and family in selected:continue
        failed=False
        own=own_cluster[n]
        for b,t in targets.items():
            if rows.get(b,{}).get('kind')=='service_reservation':continue # two maintenance tools aren't installed simultaneous parts
            mate=b==own.get('screw') if own['mode']=='driver' else b==own.get('nut')
            functional=own['mode']=='wrench' and (b in p['print_group'] or b.startswith(own['prefix']))
            limit=0. if mate else .2 if functional else 1.25
            if bbox_lower_bound(s.BoundBox,t.BoundBox)>limit+1e-6:continue
            first=s;other=t
            if b==world.bus['name']:first=s.copy();first.Placement=world.bus['inverse']*first.Placement;other=world.bus['original']
            if not other.Solids:
                radius=rows.get(b,{}).get('nominal_profile_radius_mm') or rows.get(b,{}).get('radius_mm')
                row=profile_gap(first,other,radius,limit) if radius else dict(ok=False,unreceived_profile=True)
            else:
                gap=q.distance(first,other);row=dict(ok=gap>=limit-1e-6,gap_mm=gap,minimum_mm=limit)
                if mate:
                    common=first.copy().common(other.copy()).Volume;row.update(common_mm3=common,ok=common<1e-5,intended_own_tool_engagement=True)
            checks[n+'|'+b]=row
            if not row['ok']:
                if tool_configuration_search:failed=True;break
                result['status']='AUX_UPPER_ACTUAL_TOOL_HOLD';save();print(result['status'],n,b,row,flush=True);return result
        if failed:
            result['rejected_configurations'].append(n);save();continue
        for actor in world.motion:
            if actor['pose']!=0 or bbox_lower_bound(s.BoundBox,A.BoundBox(*actor['bounds'][0],*actor['bounds'][1]))>=1.25:continue
            first=s.copy();first.Placement=placement(actor['r'],actor['t']).inverse()*first.Placement
            gap=q.distance(first,world.rest[actor['name']]);row=dict(ok=gap>=1.25-1e-6,gap_mm=gap,minimum_mm=1.25)
            checks[n+'|stand:'+actor['name']]=row
            if not row['ok']:
                if tool_configuration_search:failed=True;break
                result['status']='AUX_UPPER_STANDING_TOOL_HOLD';save();print(result['status'],n,actor['name'],row,flush=True);return result
        if failed:
            result['rejected_configurations'].append(n);save();continue
        if tool_configuration_search:selected[family]=n
        result['completed'].append(n);save()
    if tool_configuration_search:
        allfile=dest.with_suffix('.all-configurations.json.gz')
        allfile.write_bytes(gzip.compress(json.dumps(checks,separators=(',',':')).encode(),mtime=0))
        result.update(all_configuration_pair_rows=allfile.relative_to(ROOT).as_posix(),all_configuration_pair_rows_sha256=sha(allfile),
            rejected_configuration_witnesses={k:v for k,v in checks.items() if not v['ok']})
        chosen=set(selected.values());checks={k:v for k,v in checks.items() if k.split('|')[0] in chosen}
        required=['M2Driver'+str(i) for i in (1,2,3)]+['M2NutStroke'+str(i) for i in (1,2,3)]
        for family in required:
            if family not in selected:checks['NO_SELECTED_TOOL:'+family+'|configuration']=dict(ok=False,reason='No received access configuration')
        result['status']='AUX_UPPER_SELECTED_3_KEYS_3_NUT_STROKES_RECEIVED' if all(k in selected for k in required) else 'AUX_UPPER_NO_COMPLETE_TOOL_CONFIGURATION'
        save();print(result['status'],selected,result['worker_seconds'],flush=True);return result
    result['status']='AUX_UPPER_ALL3_DRIVERS_AND3_NUT_STROKES_RECEIVED';save()
    print(result['status'],result['checks'],result['worker_seconds'],flush=True);return result
