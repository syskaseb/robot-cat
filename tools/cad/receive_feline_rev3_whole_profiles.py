"""ONE whole REV3 changed-end/case gate before another local route trial.

Typed nominal source jackets vs actual valid BReps and true outer envelope.
No original CAD writes. Five explicitly reallocatable scaffold beams remain
structural HOLDs, not discarded physical parts or a load-path approval.
"""
import json
import time
from pathlib import Path
import FreeCAD as A
from check_main_p0_placement import ROOT,SavedShapes,sha
from plan_feline_layout import OUT
from feline_rev3_query_scene import build
from feline_current_scene import load
from plan_feline_central_pi_wedge import packed
from check_feline_all_current_lands import near
from check_feline_shared_space import tube_prefix
from plan_feline_front_service_split import line_tube


def main():
    tick=time.monotonic();dest=OUT/'n01-rev3-whole-profiles.json'
    assert not dest.exists(), 'Receive existing partial; do not overwrite evidence'
    old,oldmeta,_,data,oldpins,_=load()
    scene,meta,pins,bus=build();pins.update(oldpins)
    contractfile=OUT/'n01-station-profile-contract.json'
    contract=json.loads(contractfile.read_text());ports={r['endpoint']:r for r in contract['ports']}
    for n,h in contract['source_sha256'].items():assert sha(ROOT/n)==h,n
    planfile=OUT/'n01-coupled-allocation-plan.json';plan=json.loads(planfile.read_text())
    stations={r['ref']:r for r in data['ports']['stations']}
    recipes={};groups={};mouth_mates={};trimmed={};changed=set()
    def record(n,group):changed.add(n);groups[n]=group
    for row in plan['WAGO_station_rows']:
        for ref in row['refs']:
            station=stations[ref]
            casename=next(n for n,r in oldmeta.items() if r.get('role')==station['current_group'])
            record(casename,ref)
            tf=scene[casename].Placement*old[casename].Placement.inverse()
            for port in station['occupied_ports']:
                source=ports[port['endpoint']];radius=source['query_radius_mm'];R=source['bend_radius_mm']
                q=tf.multVec(A.Vector(*port['point_mm']));d=tf.Rotation.multVec(A.Vector(*port['departure_axis']))
                b=A.Vector(*row['bend_unit_mm']);en='REV3Station:'+port['endpoint']
                scene[en]=tube_prefix(list(q),list(d),radius,list(b),R,3)
                tip=q+d*(3+R)+b*R
                scene[en+':after9']=line_tube(list(tip),list(tip+b*9),radius)
                trimmed[en]=tube_prefix(list(q+d*2.5),list(d),radius,list(b),R,.5)
                mouth_mates[en]={casename}
                for n in (en,en+':after9'):
                    record(n,ref);meta[n]=dict(kind='wire',wire_owner=port['wire'])
                recipes[en]=dict(endpoint=port['endpoint'],wire=port['wire'],radius_mm=radius,
                    point_mm=list(q),departure_axis=list(d),bend_unit=list(b),R_mm=R,
                    first_straight_mm=3,after_grip_mm=[list(tip),list(tip+b*9)],
                    source_profile=source)
    # Add the unchanged selected F_PWM and head/tail local owners omitted in
    # early USB-only queries. They are fixed neighbours, not new changed parts.
    for file,group in ((OUT/'n01-coupled-clocked-joints.json','F_PWM'),
                       (OUT/'n01-selected-local-head-tail-sources.json',None)):
        _,shapes,rows=packed(file)
        for n,s in shapes.items():
            if group is None or rows[n]['group']==group:
                scene[n]=s;meta[n]=rows[n]
        pins[file.relative_to(ROOT).as_posix()]=sha(file)
    for n,r in meta.items():
        if n.startswith('REV3:') or r.get('group')=='PiCoupled':
            record(n,r.get('group') or n.split(':')[1].split('.')[0])
    # Explicit source-case mates only. No waiver for adjacent unrelated parts.
    for spec in plan['FHAC']:
        for side in ('in','out'):
            n='REV3:'+spec['role']+'.'+side+':factory'
            mouth_mates[n]={'REV3:'+spec['role']}
            # Its first9 includes the native case face. Trim only the first2.5
            # for this one mate, never the rest of the material/world checks.
            local=next(e for sec in json.loads((OUT/'n01-all-extra-interface-contract.json').read_text())['sections']
                for e in sec['ends'] if e['endpoint']==spec['role']+'.'+side)
            rot=A.Rotation(A.Vector(0,1,0),-90)
            q=A.Vector(*spec['centre_mm'])+rot.multVec(A.Vector(*local['local_point_mm']))
            d=rot.multVec(A.Vector(*local['departure_axis']));b=A.Vector(*spec['bend_unit_mm'])
            first=tube_prefix(list(q+d*2.5),list(d),2,list(b),12.4,6.5)
            end=q+d*(9+12.4)+b*12.4
            trimmed[n]=first.fuse(line_tube(list(end),list(end+b*14),2))
    ownershipfile=OUT/'n01-reservation-ownership-plan.json'
    ownership=json.loads(ownershipfile.read_text())
    reallocated={'StructureReserve:'+x for x in ('BankArm-69_-1','BankArm-69_1','BankArm105_-1','BankArm105_1','UpperStrip1')}
    reader=SavedShapes();outerfile=OUT/'central-cassette-envelope/FelineLayoutEnvelope.FCStd'
    outer=reader.shape(outerfile,'TorsoEnvelope');assert outer.isValid()
    pins.update(reader.hashes)
    for p in (contractfile,planfile,ownershipfile,Path(__file__)):
        pins[p.relative_to(ROOT).as_posix()]=sha(p)
    result=dict(status='RUNNING_WHOLE_REV3_PROFILES',selected=False,N01_complete=False,physical_pass=False,
        source_sha256=pins,profile_contract=contractfile.relative_to(ROOT).as_posix(),
        recipes=recipes,changed_parts=sorted(changed),
        completed_queries=[],material_gap_failures=[],reservation_holds=[],wire_failures=[],
        outer_failures=[],errors=[],pairs=0,whole_middles_mounts_tools_motion_qualified=False,
        nominal_source_mating_trim_mm=2.5,
        intrinsic_stack_and_pad_fits_not_accepted=True,
        reallocatable_beams=sorted(reallocated),reallocated_load_paths_still_required=True)
    def save():
        result['worker_seconds']=round(time.monotonic()-tick,3)
        dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    bounds={n:s.BoundBox for n,s in scene.items()}
    def iswire(n):
        r=meta[n]
        return bool(r.get('wire_owner')) or r.get('kind') in ('wire','proposal_wire','actual_wire') or n.startswith(('End:','BankFullPrefix:','Factory:','CustomPrefix:')) or n in ('W043','W077','W078')
    def reservation(n):
        return 'reservation' in meta[n].get('kind','') or meta[n].get('role')=='ScaffoldPlanning' or n.startswith(('StructureReserve:','PiBudget:'))
    def wire_owner(n):
        if n in recipes:return recipes[n]['wire']
        if n.endswith(':after9') and n[:-7] in recipes:return recipes[n[:-7]]['wire']
        if n.startswith('REV3:PCA:'):return n.split(':')[2]
        if n.startswith('REV3:') and '.' in n:return n.split(':')[1]
        return meta[n].get('wire_owner') or n
    def group(n):return groups.get(n,meta[n].get('group') or meta[n].get('role') or n)
    seen=set();save()
    try:
        for n in sorted(changed):
            s=scene[n]
            if not s.Solids:result['errors'].append(dict(part=n,error='Changed curve is not full jacket'));continue
            if not s.isValid():raise ValueError('Invalid changed source:'+n)
            # Only torso-owned changed material, not the unchanged head itself.
            outside=s.cut(outer);volume=outside.Volume
            wallgap=s.distToShape(outer.Shells[0])[0] if volume<1e-5 else 0
            if volume>1e-5 or wallgap<3.25-1e-5:
                result['outer_failures'].append(dict(part=n,outside_volume_mm3=volume,
                    actual_outer_surface_gap_mm=wallgap,required_wall_plus_air_mm=3.25,
                    reservation_only=reservation(n)))
            for m,t in scene.items():
                if n==m or m in reallocated or meta[m].get('role','').startswith('leg:'):continue
                pair=tuple(sorted((n,m)))
                minimum=.2 if iswire(n) and iswire(m) else 1.25
                if pair in seen or not near(bounds[n],bounds[m],minimum):continue
                if group(n)==group(m) and not iswire(n) and not iswire(m):continue
                if iswire(n) and iswire(m) and wire_owner(n)==wire_owner(m):continue
                if n.startswith('REV3:') and m.startswith('REV3:') and n.rsplit(':',1)[0]==m.rsplit(':',1)[0] and ('sleeve' in n or 'sleeve' in m):continue
                # Intrinsic pad fit remains explicit HOLD; no false blanketPASS.
                if n.startswith('REV3:PCA:') and ':bare' in n and oldmeta.get(m,{}).get('role')=='PWM9685':continue
                seen.add(pair)
                if time.monotonic()-tick>180:raise TimeoutError('180s cap; all completed pairs preserved')
                tested=trimmed.get(n,s) if m in mouth_mates.get(n,set()) else s
                if n in mouth_mates.get(m,set()):continue # reverse iteration owns trimmed check
                if m==bus['name']:
                    inverse=tested.copy();inverse.Placement=bus['inverse']*inverse.Placement
                    gap=inverse.distToShape(bus['original'])[0]
                else:
                    if not t.Solids:
                        result['errors'].append(dict(a=n,b=m,error='Unqualified neighbour curve, not complete jacket'));continue
                    if not t.isValid():raise ValueError('Invalid neighbour:'+m)
                    gap=tested.distToShape(t)[0]
                row=dict(a=n,b=m,gap_mm=gap,minimum_mm=minimum,
                    reservation_only=reservation(n) or reservation(m),
                    nominal_own_mate_trim=m in mouth_mates.get(n,set()),
                    zero_distance_not_claimed_positive_overlap=True)
                result['completed_queries'].append(row);result['pairs']+=1
                if gap<minimum-1e-5:
                    key='reservation_holds' if row['reservation_only'] else 'wire_failures' if iswire(n) and iswire(m) else 'material_gap_failures'
                    result[key].append(row)
                if result['pairs']%20==0:save()
            print('Profile received',n,'pairs',result['pairs'],flush=True);save()
        result['status']='WHOLE_REV3_PROFILE_GATE_RECEIVED_NOT_N01'
    except Exception as e:
        result['status']='PARTIAL_WHOLE_REV3_PROFILE_GATE';result['errors'].append(repr(e))
    save()
    print(json.dumps({k:len(result[k]) for k in ('material_gap_failures','reservation_holds','wire_failures','outer_failures','errors')}),flush=True)


if __name__=='__main__':main()
