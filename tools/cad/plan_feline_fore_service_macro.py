"""One coupled service allocation: S1/DFL/FLG/all source lands/three cases.

Actual planning BReps only. Full HELU R25.2 domains, remaining factory tails,
roots/tools/ATO/whole harness are OPEN; this is not N01 or native selection.
"""
import itertools
import json
import time
import zipfile
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_candidate_collision_scene import Scene
from feline_solid_distance import distance
from check_feline_all_current_lands import near
from receive_feline_global_case_candidates import matrix_rotation,placement
from plan_feline_fore_vertical_packet import packet,grip


def fore_service_datum(outer_min_x,tab_min_x,tab_max_z,s0_max_y):
    interval=[outer_min_x+10.125+3.25,tab_min_x-1.7-1.25]
    assert interval[0]<=interval[1],'No whole case/thin factory wire interval; no arbitrary offset'
    centre=[sum(interval)/2,s0_max_y+11+1.25,tab_max_z+5.75+1.25+.5+25.5]
    return centre,interval


def rigid_tf(centre,delta,angle):
    r=A.Rotation(A.Vector(0,1,0),angle)
    return A.Placement(centre+A.Vector(*delta)-r.multVec(centre),r)


def main():
    tick=time.monotonic();dest=OUT/'n01-fore-service-macro.json';assert not dest.exists()
    scene=Scene();fixed_original=set(scene.parts);proposal={};rows={};retired={}
    files=dict(s1=OUT/'n01-s1-current-source-datums.json',profiles=OUT/'n01-rev3-whole-profiles.json',
        overrides=OUT/'n01-dedicated-fuse-bays.json',ports=OUT/'n01-twenty-wago-port-contract.json',
        extra=OUT/'n01-all-extra-interface-contract.json',caseproof=OUT/'n01-global-case-candidates-received.json',
        sourcewire=ROOT/'hardware/reference/parent-fuse-extensions-2026-10-03/facts.json')
    data={k:json.loads(p.read_text()) for k,p in files.items()}
    assert data['s1']['nominal_source_matches']==4
    assert data['sourcewire']['HELU23802']['routing_OD_mm']==4.2 and data['sourcewire']['HELU23802']['routing_radius_mm']==25.2
    for key in ('s1','caseproof'):
        for n,h in data[key]['source_sha256'].items():assert sha(ROOT/n)==h,n
    profiles={**data['profiles']['recipes'],**data['overrides']['station_profile_recipes']}
    def put(name,shape,group,wire=False,**meta):
        assert shape.isValid() and shape.Solids,name
        proposal[name]=shape;rows[name]=dict(group=group,wire=wire,**meta)
    def move(name,tf,group,wire=False):
        source=scene.parts.pop(name);retired[name]=scene.meta.pop(name)
        shape=source.copy();shape.Placement=tf*shape.Placement;put(name,shape,group,wire)
    source_s1={r['name'] for r in data['s1']['source_parts']}
    body=scene.parts['Ref_Material_current_S1_body_CP2_0_0'];s1tf=rigid_tf(body.BoundBox.Center,[15,0,0],180)
    assert s1tf.Rotation.multVec(A.Vector(0,1,0)).isEqual(A.Vector(0,1,0),1e-8)
    for n in source_s1:move(n,s1tf,'S1Rigid')
    transformed_ports=[]
    for receipt in data['s1']['receipts']:
        q=s1tf.multVec(A.Vector(*receipt['source_point_mm']));d=s1tf.Rotation.multVec(A.Vector(*receipt['source_departure']))
        name='ServiceS1:'+receipt['endpoint']
        put(name,Part.makeCylinder(2.1,9,q,d),'S1Wire',True,
            mating_ring=receipt['matching_nominal_source_planes'][0]['part'],point_mm=list(q),departure_axis=list(d))
        transformed_ports.append(dict(endpoint=receipt['endpoint'],point_mm=list(q),departure_axis=list(d),
            radius_mm=2.1,full_source_R_mm=25.2,full_bend_or_grip_NOT_qualified=True))
    station_moves={'D_FL':dict(delta=[0,0,0],angle=180),'FL_G':dict(delta=[16,0,0],angle=0)}
    moved_profiles={}
    for ref,spec in station_moves.items():
        n='Ref_Material_'+ref+'_0_0';tf=rigid_tf(scene.parts[n].BoundBox.Center,spec['delta'],spec['angle'])
        move(n,tf,ref)
        for name,r in profiles.items():
            if not name.startswith('REV3Station:'+ref+'.'):continue
            move(name,tf,ref,True);move(name+':after9',tf,ref,True)
            moved_profiles[name]=dict(r,point_mm=list(tf.multVec(A.Vector(*r['point_mm']))),
                departure_axis=list(tf.Rotation.multVec(A.Vector(*r['departure_axis']))),
                bend_unit=list(tf.Rotation.multVec(A.Vector(*r['bend_unit']))),
                after_grip_mm=[list(tf.multVec(A.Vector(*p))) for p in r['after_grip_mm']])
    local={e['endpoint']:e for section in data['extra']['sections'] for e in section['ends'] if e.get('local_point_mm') is not None}
    tab=scene.parts['Ref_Material_P0_Part__Feature_0_0'].BoundBox
    s0max=max(s.BoundBox.YMax for n,s in scene.parts.items() if n.startswith('Ref_Material_S0_'))
    centre,interval=fore_service_datum(scene.outer.BoundBox.XMin,tab.XMin,tab.ZMax,s0max)
    fore,fore_recipes,owncase=packet(scene.templates['F_HY'][1],local,centre,scene.outer.BoundBox.ZMax)
    # Lower custom head sits FORE(-X), away from the actual upright; the
    # band/whole9mm seat remain unchanged, no omitted head volume.
    lower=next(r for r in fore_recipes if r['side']=='out')
    q=A.Vector(*lower['custom_grip_line_mm'][0]);d=A.Vector(*lower['custom_grip_line_mm'][1])-q;d.normalize()
    fore['out:custom_full_grip_head']=(grip(q-d*3.25,d,1.55,False)[2],False)
    for name,(s,wire) in fore.items():put('ForeFHAC:'+name,s,'ForeFHAC',wire)
    prior_cases={r['id']:r for r in data['caseproof']['completed_candidates']}
    for cid,role in ((2,'F_HP'),(3,'F_TY')):
        r=prior_cases[cid];assert r['status']=='SOURCE_CASE_STATIC_AND36SAMPLED_MOTION_CLEAR_TAILS_OPEN'
        source=scene.templates[role][1];rot=placement(matrix_rotation(r['source_axis_to_world_axis']),[0,0,0]).Rotation
        s=source.copy();s.Placement=A.Placement(A.Vector(*r['centre_mm'])-rot.multVec(source.BoundBox.Center),rot)*s.Placement
        put('RearFHAC:'+role,s,role,prior_fixed_static_outer_motion_reused=True)
    scene.bounds={n:s.BoundBox for n,s in scene.parts.items()}
    pins=dict(scene.pins)
    for p in (*files.values(),Path(__file__),Path(__file__).with_name('plan_feline_fore_vertical_packet.py'),Path(__file__).with_name('feline_solid_distance.py')):pins[p.relative_to(ROOT).as_posix()]=sha(p)
    result=dict(status='RUNNING_COUPLED_FORE_SERVICE_MACRO',selected=False,N01_complete=False,physical_pass=False,
        source_sha256=pins,station_moves=station_moves,S1_relative_rotation_Y_degrees=180,S1_relative_translation_mm=[15,0,0],
        S1_whole_owned_hardware_count=len(source_s1),S1_operator_axis_Y_preserved=True,S1_current_source_ends=transformed_ports,
        fore_centre_mm=centre,continuous_fore_X_interval_mm=interval,fore_recipes=fore_recipes,
        transformed_station_recipes=moved_profiles,retired_source_parts=sorted(retired),
        full_HELU25_2_source_domains_and_opposite_WAGO_power_ports_OPEN=True,
        all_rear_factory_tails_roots_tools_80nets123portions246ends_stock_OPEN=True,
        fore_intrinsic_grip_joint_qualification_OPEN=True,
        receipts=[],new_pairs=[],failures=[],errors=[],bundle=None)
    def save():
        result['worker_seconds']=round(time.monotonic()-tick,3)
        dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    def gate():
        if time.monotonic()-tick>240:raise TimeoutError('240s whole service macro; preserve received sources and pairs')
    def operator_receive(shape):
        # The named operator occupies its planned panel aperture. It still
        # stays INSIDE the true200mm outline and clears all actual neighbours.
        # This does not waive wall clearance for other hardware or wires.
        outside=shape.cut(scene.outer);assert outside.isNull() or outside.isValid()
        if outside.Volume>1e-5:return dict(kind='operator_outside_true_outline',volume_mm3=outside.Volume),[]
        q=[dict(scope='true_outline_operator_aperture',actual_outer_gap_mm=shape.distToShape(scene.outer.Shells[0])[0],
            ordinary_interior_wall_gap_not_applicable=True,native_panel_aperture_OPEN=True)]
        for n,s in scene.parts.items():
            gate()
            if not near(shape.BoundBox,s.BoundBox,1.25):continue
            a=shape
            if n==scene.bus['name']:
                a=shape.copy();a.Placement=scene.bus['inverse']*a.Placement;s=scene.bus['original']
            if not s.isValid() or not s.Solids:return dict(kind='operator_invalid_or_curve_source_hold',source=n),q
            g=distance(a,s);q.append(dict(scope='operator_static',source=n,gap_mm=g,minimum_mm=1.25))
            if g<1.25-1e-5:return dict(kind='operator_static_gap',source=n,gap_mm=g),q
        bb=shape.BoundBox;bounds=[np.array([bb.XMin,bb.YMin,bb.ZMin]),np.array([bb.XMax,bb.YMax,bb.ZMax])]
        from receive_feline_global_case_candidates import bounds_near
        for p in scene.motion:
            gate()
            if not bounds_near(bounds,p['bounds']):continue
            original=scene.rest[p['name']];assert original.isValid() and original.Solids
            s=original.copy();s.Placement=placement(p['r'],p['t'])*s.Placement
            assert s.isValid()
            g=distance(shape,s);q.append(dict(scope='operator_sampled_motion',source=p['name'],pose=p['pose'],gap_mm=g,minimum_mm=1.25))
            if g<1.25-1e-5:return dict(kind='operator_motion_gap',source=p['name'],pose=p['pose'],gap_mm=g),q
        return None,q
    save()
    try:
        for n,s in proposal.items():
            gate();r=rows[n]
            if r.get('prior_fixed_static_outer_motion_reused'):
                result['receipts'].append(dict(part=n,unchanged_fixed_static_outer_motion_reused=True));continue
            if n=='Ref_Material_current_S1_control_CP2_0_0':
                bb=s.BoundBox
                result['S1_operator_panel_aperture_plan']=dict(source_control_bounds_mm=[[bb.XMin,bb.YMin,bb.ZMin],[bb.XMax,bb.YMax,bb.ZMax]],
                    nominal_opening_XZ_mm=[[bb.XMin-1.25,bb.ZMin-1.25],[bb.XMax+1.25,bb.ZMax+1.25]],
                    axis=[0,1,0],native_panel_and_actual_delivery_fit_OPEN=True)
                failure,queries=operator_receive(s)
            else:failure,queries=scene.receive(s,wire=r['wire'])
            result['receipts'].append(dict(part=n,failure=failure,completed_queries=queries))
            if failure:result['failures'].append(dict(part=n,**failure))
            save();print(n,'CLEAR' if not failure else failure,flush=True)
        for a,b in itertools.combinations(proposal,2):
            gate();ra,rb=rows[a],rows[b]
            # Each rigid moved source module retains its intrinsic mates;
            # fore packet own-contact qualification is explicitly separate.
            if ra['group']==rb['group']:continue
            minimum=.2 if ra['wire'] and rb['wire'] else 1.25
            sa,sb=proposal[a],proposal[b]
            if not near(sa.BoundBox,sb.BoundBox,minimum):continue
            for name,meta in ((a,ra),(b,rb)):
                if meta.get('mating_ring') in (a,b):
                    q=A.Vector(*meta['point_mm']);d=A.Vector(*meta['departure_axis']);trim=Part.makeCylinder(2.1,6.5,q+d*2.5,d)
                    if name==a:sa=trim
                    else:sb=trim
            gap=distance(sa,sb);row=dict(a=a,b=b,gap_mm=gap,minimum_mm=minimum)
            result['new_pairs'].append(row)
            if gap<minimum-1e-5:result['failures'].append(dict(kind='changed_shared_pair_gap',**row))
        result['status']='COUPLED_FORE_SERVICE_MACRO_REJECTED' if result['failures'] else 'COUPLED_FORE_SERVICE_SOURCE_SPACE_CLEAR_FULL_POWER_DOMAINS_OPEN'
    except Exception as e:result['errors'].append(repr(e));result['status']='PARTIAL_COUPLED_FORE_SERVICE_MACRO'
    bundle=OUT/'n01-fore-service-macro.breps.zip'
    with zipfile.ZipFile(bundle,'w',compression=zipfile.ZIP_DEFLATED) as z:
        result['parts']=[]
        for i,(n,s) in enumerate(proposal.items()):
            entry=f'{i:04}.brep';raw=s.exportBrepToString().encode('utf-8');z.writestr(entry,raw)
            result['parts'].append(dict(name=n,entry=entry,sha256=__import__('hashlib').sha256(raw).hexdigest(),**rows[n]))
    result['bundle']=bundle.relative_to(ROOT).as_posix();result['bundle_sha256']=sha(bundle)
    save();print(json.dumps({k:result[k] for k in ('status','worker_seconds','fore_centre_mm','failures','errors')}),flush=True)


if __name__=='__main__':main()
