"""Constructive two-axis MAIN fastener access, not full harness extraction.

One F_R2 ATO is temporarily removed AFTER its received withdrawal path;
the socket enters sideways above the bank bed, then rises3mm. No74WAGO.
Tool dimensions are explicit provisional envelopes, not catalogue guarantees.
"""
import gzip,json,os,time
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_main_hung_context import compose
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound
from plan_feline_pi_root_access import profile_gap
from feline_atomic_save import save_json


def box(lo,hi):return Part.makeBox(*(b-a for a,b in zip(lo,hi)),A.Vector(*lo))


def main():
    tick=time.monotonic();wf=OUT/'n01-MAIN-hung-world.json';receipt=json.loads(wf.read_text())
    assert receipt['status']=='MAIN_WHOLE_STATIC36_RECEIVED_TOOLS_ASSEMBLY_OPEN' and not receipt['failures']
    for p,h in receipt['source_sha256'].items():assert sha(ROOT/p)==h,p
    world,parts,meta,pins,docs=compose();removed='Ref_Material_F_R2_CP2_ATO_0_0';assert removed in parts
    checks={};recipes=[];query=SolidQueries();dest=OUT/'n01-MAIN-fastener-access.json';rows=dest.with_suffix('.pairs.json.gz')
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (wf,ROOT/receipt['pair_rows'],Path(__file__))})
    r=dict(status='RUNNING_MAIN_FASTENER_ACCESS',source_sha256=pins,completed_axes=[],recipes=recipes,
        temporarily_removed_actual_parts=[removed],not_simultaneous_other_service_tool_reservations=True,
        native_changed=False,N01_complete=False,physical_pass=False,full_harness_extraction_NOT_received=True,
        linked_service_dependencies=['F_PI holder and fixed solder splice release','future common middles/service slack','top cosmetic panel removal'],
        tool_dimensions_are_provisional_fit_gate=True)
    def save():
        rows.write_bytes(gzip.compress(json.dumps(checks,separators=(',',':')).encode(),mtime=0))
        r.update(checks=len(checks),failures=[k for k,v in checks.items() if not v['ok']],pair_rows=rows.relative_to(ROOT).as_posix(),pair_rows_sha256=sha(rows),worker_seconds=round(time.monotonic()-tick,3));save_json(dest,r)
    save()
    for i in (0,1):
        prefix=f'Ref_Material_MAIN_{i}_';head=parts[prefix+'head_0_0'];nut=parts[prefix+'nut_0_0'];shaft=parts[prefix+'shaft_0_0']
        x,y=nut.BoundBox.Center.x,nut.BoundBox.Center.y;top=head.BoundBox.ZMax
        bottom=nut.BoundBox.ZMin;cup_top=nut.BoundBox.ZMax-.05;base=shaft.BoundBox.ZMin-.5252
        cup=Part.makeCylinder(3,cup_top-base+.5,A.Vector(x,y,base-.5)).cut(Part.makeCylinder(2.5,cup_top-base+.1,A.Vector(x,y,base)))
        socket=cup.fuse(Part.makeCylinder(1.5,base-(bottom-21),A.Vector(x,y,bottom-21))).removeSplitter()
        assert socket.isValid() and len(socket.Solids)==1
        # The final hollow cup contains both the nut's circumradius and the
        # protruding shaft at every point of the coaxial upward3mm stroke.
        for tag in ('nut','shaft','lower_washer'):
            target=parts[prefix+tag+'_0_0'];v=socket.common(target)
            assert v.isNull() or v.isValid();checks[f'axis{i}|actual_socket|{tag}']=dict(ok=v.Volume<1e-5,positive_common_mm3=v.Volume)
        if meta[prefix+'nut_0_0'].get('source'):pass
        paths={
            'top_tip_and_handle':Part.makeCylinder(1.5,43,A.Vector(x,y,top)).fuse(Part.makeCylinder(5,25,A.Vector(x,y,top+18))),
            'socket_side_approach':box([x-3,y-3,bottom-24],[x+15,y+3,cup_top-3]),
            'socket_upward3':box([x-3,y-3,bottom-24],[x+3,y+3,cup_top])}
        recipes.append(dict(axis=i,axis_world_mm=[x,y],actual_nut_bottom_Z_mm=bottom,actual_shaft_tip_Z_mm=shaft.BoundBox.ZMin,
            top_tip_radius_mm=1.5,top_handle_radius_mm=5,top_handle_start_Z_mm=top+18,
            socket_outer_radius_mm=3,socket_cup_inner_radius_mm=2.5,socket_cup_base_Z_mm=base,
            socket_side_entry_mm=12,socket_upward_stroke_mm=3,entry_above_bankbed_not_through_it=True,
            provisional_4mm_socket_fit_and_actual_driver_bit_phase2_gate=True))
        for tag,s in paths.items():
            for n,t in parts.items():
                if n==removed or n.startswith('Service:'):continue
                # Only the driven stack is a tool mate. Foreign fasteners,
                # copper and neighbouring PCB materials retain1.25mm.
                if n.startswith(prefix):continue
                minimum=.15 if n in ('MainSupported:root','MainSupported:comb') else 1.25
                if bbox_lower_bound(s.BoundBox,t.BoundBox)>=minimum:continue
                a=s
                if n==world.bus['name']:
                    a=s.copy();a.Placement=docs['inverse']*a.Placement;t=world.bus['original']
                key=f'axis{i}|{tag}|{n}'
                checks[key]=dict(ok=(gap:=query.distance(a,t))>=minimum-1e-6,gap_mm=gap,minimum_mm=minimum) if t.Solids else profile_gap(a,t,meta[n].get('nominal_profile_radius_mm') or meta[n].get('radius_mm'),minimum)
        r['completed_axes'].append(i);save();print('MAIN tool axis',i,'holds',len(r['failures']),flush=True)
    r['status']='MAIN_FASTENER_TOOL_HOLDS' if r['failures'] else 'MAIN_TWO_AXIS_FASTENER_ACCESS_RECEIVED_HARNESS_RELEASE_OPEN'
    r['sequence']=['Top service panel absent; unpowered assembly only','Withdraw only F_R2 ATO using unchanged received path',
        'Bring socket sideways above bank bed, rise3mm; mate upper driver','Remove two screw stacks and park loose hardware',
        'Withdraw tools and reinstall ATO after MAIN fixed','Full F_PI/splice/harness release remains common-plan dependency, not PCB-only removal approval']
    save();print(r['status'],r['checks'],len(r['failures']),r['worker_seconds'],flush=True)


if __name__=='__main__':print('WORKER_PID',os.getpid(),flush=True);main()
