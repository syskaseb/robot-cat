"""Receive complete station units from ALL qualified functional zones.

One shared domain catalogue, no requirement that20 unequal interfaces use
one orientation. Every pass here includes actual case/all wires/full9grip/
band/head against current owners, true contour and36 leg poses. Roots,
tools, mutual allocation and the other source interfaces remain open N01.
Resumable by exact geometry signatures, not logical wire labels.
"""
import hashlib
import itertools
import json
import os
import sys
import time
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_flat_station_templates import build
from feline_zone_station_templates import zone_build,vertical_build
from feline_underplate_station_templates import build_underplate
from feline_case_zone_allocation import current_world
from feline_fore_power_pair import SolidQueries,pair_spacing
from feline_solid_distance import bbox_lower_bound
from receive_feline_flat_station_proposal import wire_shape
from receive_feline_global_case_candidates import placement


def catalogue(station,zones):
    profile='fixed_P_SYS' if station['fixed_identity_pose'] else 'large' if station['flat_dimensions_pitch_departure_thickness_mm'][2]>10 else 'standard'
    result=[]
    for slot in zones['candidates']:
        if slot['profile']!=profile or zones['received'][str(slot['id'])]['failure']:continue
        family=slot.get('pose_family','FLAT')
        if profile=='fixed_P_SYS':variants=[{}]
        elif family=='UNDER_PLATFORM_SHARED_REMOVABLE_COMBS':variants=[dict(bend_side=b,head_side=h) for b,h in itertools.product((-1,1),(-1,1))]
        elif family=='VERTICAL_DEPARTURE_TWO_SIDE_TIERS':variants=[dict(departure_z=d,lever_sign=l,head_side=h) for d,l,h in itertools.product((-1,1),repeat=3)]
        else:
            modes=('OUTWARD_CONCENTRIC',) if abs(slot['centre_mm'][1])>45 else ('OUTWARD_CONCENTRIC','UP_PARALLEL','INWARD_UP_PARALLEL')
            variants=[dict(departure=d,bend_mode=b) for d,b in itertools.product((-1,1),modes)]
        for v in variants:result.append(dict(slot_id=slot['id'],family=family,**v))
    return result


def signature(st,recipe):
    physical=dict(dimensions=st['flat_dimensions_pitch_departure_thickness_mm'],pitch=st['source_pitch_axis'],departure=st['source_departure_axis'],
        ports=[{k:p[k] for k in ('local_pitch_departure_thickness_mm','radius_mm','minimum_project_R_mm','protected_whole_route_reuse')} for p in st['ports']],
        fixed=st['fixed_identity_pose'],R=st['shared_fan_R_mm'],recipe=recipe)
    return hashlib.sha256(json.dumps(physical,sort_keys=True).encode()).hexdigest()


def materialise(st,slot,r):
    if r['family']=='UNDER_PLATFORM_SHARED_REMOVABLE_COMBS':
        model=build_underplate(st,slot,r['bend_side'],r['head_side']);parts=model['parts']
        kinds={n:'wire' if n.startswith('wire:') else 'project_stock_reservation' if n in ('band_budget','head_budget') else 'proposal_material' for n in parts}
        return parts,kinds
    if st['fixed_identity_pose']:m=build(st,'inner',1,-1)
    elif r['family']=='VERTICAL_DEPARTURE_TWO_SIDE_TIERS':m=vertical_build(st,slot,r['departure_z'],r['lever_sign'],r['head_side'])
    else:m=zone_build(st,slot,r['departure'],r['bend_mode'])
    parts={};kinds={}
    for w in m['wires']:
        n='wire:'+w['endpoint'];parts[n]=wire_shape(w);kinds[n]='wire'
    for b in m['boxes']:
        if b['kind']==3:continue # Explicitly NOT accepted as translated roots.
        lo,hi=b['bounds'];s=Part.makeBox(*(hi-lo),A.Vector(*lo));n='case' if b['kind']==0 else b['name']
        if b['kind']==4:
            for w in m['wires']+m['reused_jacket_lands']:
                q=A.Vector(*w['point_mm']);d=A.Vector(*w['departure_axis'])
                s=s.cut(Part.makeCylinder(w['radius']+.15,11,q-d,d))
        parts[n]=s;kinds[n]='project_stock_reservation' if b['kind']==2 else 'proposal_material'
    assert all(s.isValid() and s.Solids for s in parts.values())
    return parts,kinds


def main():
    tick=time.monotonic();dest=OUT/'n01-station-zone-domains.json';zonefile=OUT/'n01-case-zone-allocation.json';zones=json.loads(zonefile.read_text())
    planfile=OUT/'n01-flat-station-architecture.json';plan=json.loads(planfile.read_text());slots={r['id']:r for r in zones['candidates']}
    files=[zonefile,planfile,OUT/'n01-six-source-current-core.json',OUT/'n01-six-source-shared-lanes.outer.brep',Path(__file__),
        Path(__file__).with_name('feline_zone_station_templates.py'),Path(__file__).with_name('feline_underplate_station_templates.py'),Path(__file__).with_name('feline_case_zone_allocation.py')]
    pins={p.relative_to(ROOT).as_posix():sha(p) for p in files}
    result=dict(status='RUNNING_CURRENT_COMPLETE_STATION_DOMAINS',source_sha256=pins,domains={},geometry_cache={},errors=[],N01_complete=False,physical_pass=False,
        roots_tools_all123portions246ends_other27_and_sixsource_mutual_still_required=True)
    if dest.exists():
        old=json.loads(dest.read_text());assert old['source_sha256']==pins,'Receive pinned work only; no old world inheritance after change'
        result=old;result.setdefault('prior_worker_seconds',[]).append(result['worker_seconds'])
    def save():
        result['worker_seconds']=round(time.monotonic()-tick,3)
        dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    def budget():
        if time.monotonic()-tick>240:raise TimeoutError('Atomic4min receiver slice; resume saved actual pairs, window staysON')
    save();world,fixed=current_world();qcache=SolidQueries()
    if result.get('world_source_sha256'):assert result['world_source_sha256']==world.pins,'Changed fixed world invalidates affected receipts'
    result['world_source_sha256']=world.pins;save()
    outer=Part.Shape();outer.read(str(OUT/'n01-six-source-shared-lanes.outer.brep'));surface=Part.makeCompound(outer.Shells)
    def receive(st,parts,kinds,record):
        done=record.setdefault('pairs',{});stats=record.setdefault('stats',{'actual_pairs':0})
        def pair(key,s,t,minimum,own=False):
            budget()
            if key in done:return done[key]['ok']
            gap=qcache.distance(s,t);ok=gap>=minimum-1e-6;volume=None
            if own:
                common=s.copy().common(t.copy());assert common.isValid();volume=common.Volume;ok=volume<1e-5
            done[key]=dict(ok=ok,gap_mm=gap,minimum_mm=minimum,positive_common_mm3=volume);stats['actual_pairs']+=1
            save();return ok
        for n,s in parts.items():
            budget()
            if n=='case':continue # Exact current case/36pose/outer receipt.
            insidekey=n+'|outer'
            if insidekey not in done:
                outside=s.copy().cut(outer);assert outside.isNull() or outside.isValid()
                gap=s.distToShape(surface)[0];done[insidekey]=dict(ok=outside.Volume<1e-5 and gap>=3.25-1e-6,outside_mm3=outside.Volume,gap_mm=gap);save()
            if not done[insidekey]['ok']:return insidekey
            for other,t in fixed.items():
                own=st['fixed_identity_pose'] and other=='W043' and not n.startswith('wire:')
                minimum=.15 if own else pair_spacing(n,{'kind':kinds[n]},other,world.meta.get(other,{}))
                if bbox_lower_bound(s.BoundBox,t.BoundBox)>=minimum:continue
                q=s
                if other==world.bus['name']:q=s.copy();q.Placement=world.bus['inverse']*q.Placement;t=world.bus['original']
                if not t.Solids:return n+'|curve_owner_hold:'+other
                key=n+'|fixed:'+other
                if not pair(key,q,t,minimum,own):return key
            for p in world.motion:
                if bbox_lower_bound(s.BoundBox,A.BoundBox(*p['bounds'][0],*p['bounds'][1]))>=1.25:continue
                q=s.copy();q.Placement=placement(p['r'],p['t']).inverse()*q.Placement
                key=n+'|motion:'+p['name']+':'+str(p['pose'])
                if not pair(key,q,world.rest[p['name']],1.25):return key
        for n,s in parts.items():
            for o,t in parts.items():
                if o<=n or not (kinds[n]=='wire' or kinds[o]=='wire'):continue
                wirewire=kinds[n]==kinds[o]=='wire';minimum=.2 if wirewire else 0.
                if bbox_lower_bound(s.BoundBox,t.BoundBox)>=max(minimum,1e-7):continue
                key=n+'|own:'+o
                if not pair(key,s,t,minimum,not wirewire):return key
        return None
    try:
        for st in plan['stations']:
            name=st['ref'];domain=result['domains'].setdefault(name,[]);options=catalogue(st,zones)
            for r in options:
                key=signature(st,r);record=result['geometry_cache'].setdefault(key,{})
                if 'failure' not in record:
                    budget();parts,kinds=materialise(st,slots[r['slot_id']],r)
                    record['failure']=receive(st,parts,kinds,record);record['recipe_example']=dict(ref=name,**r)
                    save();print('Full unit',name,r,'clear' if record['failure'] is None else 'blocked:'+record['failure'],flush=True)
                if record['failure'] is None and not any(x['geometry_signature']==key for x in domain):domain.append(dict(r,geometry_signature=key))
            result.setdefault('completed_stations',[])
            if name not in result['completed_stations']:result['completed_stations'].append(name)
            save();print('Station complete',name,len(domain),'whole-unit alternatives',flush=True)
        result['status']='CURRENT_COMPLETE_STATION_DOMAINS_RECEIVED_JOINT_REQUIRED'
    except TimeoutError as exc:result['status']='PARTIAL_CURRENT_COMPLETE_STATION_DOMAINS';result['slice_note']=str(exc)
    except Exception as exc:result['status']='STATION_DOMAIN_ERROR_NOT_ACCEPTANCE';result['errors'].append(repr(exc))
    save();print(json.dumps(dict(status=result['status'],worker_seconds=result['worker_seconds'],domains={n:len(v) for n,v in result['domains'].items()},errors=result['errors'])),flush=True)


if __name__=='__main__':
    print('WORKER_PID',os.getpid(),flush=True);main()
