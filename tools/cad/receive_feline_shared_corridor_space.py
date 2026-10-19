"""Shared harness SPACE before carrier branches, not final123 wire curves.

Whole functional galleries and a USB service-loop bay are tested against
actual rigid parts/stock/motion. Existing insulated harness prefixes are
occupancy inside this same proposed routing resource, never deleted parts
or a claim that their final individual separation has been qualified.
"""
import hashlib,json,math,os,time,zipfile
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from feline_common_retention_roots import archived
from feline_two_lane_receive import world_context
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound
from receive_feline_global_case_candidates import placement


def candidates():
    rows=[]
    # Two complete levels, not one later tower per cable. Planning capacity
    # is calculated with55% fill; no ampacity/thermal claim follows from it.
    for side in (-1,1):
        for label,x0,x1,y,z in (('fore',-115,-24,30,72),('central',-24,105,24,70),
                              ('upper',-24,105,12,88),('lower',-90,105,28,-10)):
            start=[x0,side*y,z];end=[x1,side*y,z];r=5.
            rows.append(dict(name=label+str(side),kind='shared_harness_corridor',start_mm=start,end_mm=end,radius_mm=r,
                shape=Part.makeCylinder(r,x1-x0,A.Vector(*start),A.Vector(1,0,0)),
                project_wire_area_capacity_mm2=.55*math.pi*r*r,fill_is_space_budget_not_thermal_rating=True,
                complete_individual_wire_routes_accepted=False))
    # Full continuous helical space: extra length can be secured here instead
    # of arbitrarily shortening the selected0.5m cable in a picture.
    R=34.;pitch=7.;turns=1.5;origin=A.Vector(140,0,70)
    path=Part.makeHelix(pitch,pitch*turns,R);path.translate(origin)
    start=origin+A.Vector(R,0,0);tangent=A.Vector(0,R,pitch/(2*math.pi));tangent.normalize()
    profile=Part.Wire([Part.makeCircle(2.5,start,tangent)])
    loop=path.makePipeShell([profile],True,False);assert loop.isValid() and loop.Solids
    rows.append(dict(name='USB_service_loop',kind='selected_USB500_service_capacity',shape=loop,
        project_OD_mm=5,project_minimum_R_mm=30,coil_R_mm=R,pitch_mm=pitch,maximum_turns_reserved=turns,
        centre_mm=list(origin),curve_capacity_mm=path.Length,selected_total_mm=500,
        external452_mm_is_project_mould_allowance_not_supplier_guarantee=True,
        final_joined_USB_curve_and_exact_needed_slack_open=True))
    return rows


def main():
    tick=time.monotonic();rows=candidates();world,fixed=world_context();query=SolidQueries()
    files={k:OUT/n for k,n in dict(shared='n01-shared54-current.json',inline='n01-remaining-inline-body-closure.json',
        frame='n01-channelled-foundation-static.json',ends='n01-shared-routing-boundaries.json').items()}
    docs={k:json.loads(p.read_text()) for k,p in files.items()};assert docs['inline']['status']=='TWO_WHOLE_INLINE_KITS_RECEIVED_ROOTS_CORRIDORS_OPEN'
    shared=archived(docs['shared'],'parts');inline=archived(docs['inline'],'geometry');frame=archived(docs['frame'],'geometry')
    obstacles={**fixed,**shared,**{'CurrentInline:'+n:s for n,s in inline.items()},**{'CurrentFoundation:'+n:s for n,s in frame.items()}}
    for n in ('StructureReserve:BankBed-1','StructureReserve:BankBed1'):obstacles.pop(n,None)
    proposalmeta={r['name']:r for r in docs['shared']['parts']};inlinemeta={r['name']:r for r in docs['inline']['geometry']}
    def kind(n):
        if n in proposalmeta:return proposalmeta[n]['kind']
        if n.startswith('CurrentInline:'):return inlinemeta[n.removeprefix('CurrentInline:')]['kind']
        return world.meta.get(n,{}).get('kind','')
    def jacket(n):
        if ':bare' in n.lower() or kind(n)=='bare':return False
        return kind(n) in ('wire','proposal_wire','actual_wire','insulation_reservation') or bool(world.meta.get(n,{}).get('wire_owner')) or n.startswith(('End:','Factory:','CustomPrefix:','BankFullPrefix:','ShelfPWM:jacket:','PiGPIO:','PiPower:','PiUSBData')) or n in ('W043','W077','W078')
    outer=Part.Shape();outer.read(str(OUT/'n01-six-source-shared-lanes.outer.brep'))
    dest=OUT/'n01-shared-corridor-space.json';pins={p.relative_to(ROOT).as_posix():sha(p) for p in (*files.values(),Path(__file__))}
    result=dict(status='RUNNING_SHARED_CORRIDOR_RESOURCE_SPACE',source_sha256=pins,world_source_sha256=world.pins,
        galleries={},errors=[],N01_complete=False,physical_pass=False,selected=False,
        all123_individual_middle_curves_and_all_access_fans_still_open=True)
    if dest.exists():
        result=json.loads(dest.read_text());assert result['source_sha256']==pins and result['world_source_sha256']==world.pins
        result.setdefault('previous_worker_seconds',[]).append(result['worker_seconds'])
    def save():result['worker_seconds']=round(time.monotonic()-tick,3);save_json(dest,result)
    def receive(s,row,rec):
        pairs=rec.setdefault('pairs',{})
        def record(k,op):
            if time.monotonic()-tick>235:raise TimeoutError('Whole-gallery completed pairs saved')
            if k not in pairs:pairs[k]=op();save()
            return pairs[k]['ok']
        def skin():
            common=s.copy().cut(outer);assert common.isNull() or common.isValid();gap=s.distToShape(outer.Shells[0])[0]
            return dict(ok=common.Volume<1e-5 and gap>=3.25-1e-6,gap_mm=gap,outside_mm3=common.Volume,required_mm=3.25)
        if not record('outer',skin):return 'outer'
        rec['existing_harness_prefix_occupancy']=[]
        for n,t in obstacles.items():
            if bbox_lower_bound(s.BoundBox,t.BoundBox)>=1.25:continue
            if jacket(n):
                rec['existing_harness_prefix_occupancy'].append(n);continue
            def exact():
                q,target=s,t
                if n==world.bus['name']:q=s.copy();q.Placement=world.bus['inverse']*q.Placement;target=world.bus['original']
                gap=query.distance(q,target);return dict(ok=gap>=1.25-1e-6,gap_mm=gap,required_mm=1.25)
            if not record('fixed:'+n,exact):return 'fixed:'+n
        for p in world.motion:
            if bbox_lower_bound(s.BoundBox,A.BoundBox(*p['bounds'][0],*p['bounds'][1]))>=1.25:continue
            def moving():
                q=s.copy();q.Placement=placement(p['r'],p['t']).inverse()*q.Placement;gap=query.distance(q,world.rest[p['name']])
                return dict(ok=gap>=1.25-1e-6,gap_mm=gap,required_mm=1.25)
            if not record('motion:'+p['name']+':'+str(p['pose']),moving):return 'motion:'+p['name']+':'+str(p['pose'])
        return None
    try:
        for row in rows:
            rec=result['galleries'].setdefault(row['name'],{k:v for k,v in row.items() if k!='shape'})
            if 'failure' not in rec:rec['failure']=receive(row['shape'],row,rec);save();print('Whole corridor',row['name'],rec['failure'],flush=True)
        result['status']='SHARED_GALLERY_RESOURCES_RECEIVED_ACCESS_ALLOCATION_OPEN' if all(r['failure'] is None for r in result['galleries'].values()) else 'SHARED_GALLERY_ARCHITECTURE_REQUIRES_ALLOCATION_CHANGE_NOT_N01'
    except TimeoutError as exc:result.update(status='PARTIAL_SHARED_CORRIDOR_RESOURCE_SPACE',slice_note=str(exc))
    except Exception as exc:result['errors'].append(repr(exc));result['status']='SHARED_CORRIDOR_RESOURCE_ERROR'
    save();print(json.dumps(dict(status=result['status'],seconds=result['worker_seconds'],errors=result['errors'])),flush=True)


if __name__=='__main__':print('WORKER_PID',os.getpid(),flush=True);main()
