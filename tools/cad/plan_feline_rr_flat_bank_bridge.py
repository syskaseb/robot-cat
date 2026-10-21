"""A whole nine-core section fits the actual bank/upper-case layer as a ribbon.

The bookkeeping seam is not a purchased9-pin connector: its old3x3 grid is
not a supplier constraint. Preserve all wire identities/profiles, actual
motor contacts and independent electrical end grips. Moving900 stays open.
"""
import math
import numpy as np
import FreeCAD as A
import Part
from plan_feline_n01_shared import pipe


def construct(ends,profiles,parent):
    rows=[r for r in ends if r['group']=='NineWireCuffRR'];assert len(rows)==9
    targets={r['wire']:r for r in ends if r['wire'] in {q['wire'] for q in rows} and r['group']!='NineWireCuffRR'}
    rows.sort(key=lambda r:targets[r['wire']]['routing_exit_mm'][0])
    radii=[profiles[r['portion_id']]['project_radius_mm'] for r in rows]
    width=2*sum(radii)+.2*8;assert abs(width-26.2)<1e-7
    # Whole source between the actual XA02 side and the retained skin.
    # No guide edge atY-58.7 through the accepted XA02 approach atY-57.73.
    centre_y=-80.
    z=83+1.25+max(radii);y=centre_y-width/2;points=[]
    for radius in radii:
        y+=radius;points.append(np.array([121.,y,z]));y+=radius+.2
    # Cross inboard on the FORE side of the retained XA02 uprightX59.575,
    # not through that whole cable atZ87.85 or the POWER printed trunkX70.
    # Full wire material endsX<=58.075, .25 to XA02's X58.325 surface.
    offsets=np.array(points)[:,1]-centre_y
    Rc=max(profiles[r['portion_id']]['minimum_project_R_mm']+v for r,v in zip(rows,offsets))
    bend_radii=Rc-offsets
    turn_x=59.575-1.25-.2-.05+min(R-r for R,r in zip(bend_radii,radii))
    actors={};resources={};recipes={};d=np.array([-1.,0,0]);n=np.array([0.,1,0])
    for r,p,radius,R in zip(rows,points,radii,bend_radii):
        q=p+[-9,0,0];a=q.copy();a[0]=turn_x
        at=lambda t:a+R*(math.sin(t)*d+(1-math.cos(t))*n)
        b=at(math.pi/2);tip=b.copy();tip[1]=-28;assert tip[1]>b[1]
        first=[dict(kind='line',start=p.tolist(),end=q.tolist(),length_mm=9.)]
        parts=[dict(kind='line',start=q.tolist(),end=a.tolist(),length_mm=float(q[0]-a[0])),
               dict(kind='arc',start=a.tolist(),mid=at(math.pi/4).tolist(),end=b.tolist(),radius_mm=float(R),length_mm=float(R*math.pi/2)),
               dict(kind='line',start=b.tolist(),end=tip.tolist(),length_mm=float(tip[1]-b[1]))]
        key='RRFlat:'+r['id'];resource='RRFlatResource:'+r['id']
        actors[key]=pipe(first,radius);resources[resource]=pipe(parts,radius)
        recipes[key]=dict(end_id=r['id'],wire=r['wire'],radius_mm=radius,parts=first,
            original_seam_mm=r['point_mm'],proposed_seam_mm=p.tolist(),departure_axis=d.tolist(),
            resource=resource,resource_parts=parts,resource_end_mm=tip.tolist(),resource_end_axis=n.tolist(),
            target_end_id=targets[r['wire']]['id'],target_exit_mm=targets[r['wire']]['routing_exit_mm'],
            target_departure_axis=targets[r['wire']]['routing_exit_axis'],
            full_terminal_forks_NOT_received=True,moving900_NOT_received=True)
    def box(lo,hi):return Part.makeBox(*(b-a for a,b in zip(lo,hi)),A.Vector(*lo))
    left=centre_y-width/2-.2-2;right=centre_y+width/2+.2+2
    floor_bottom=z-max(radii)-.2-2;top=z+max(radii)+.2+2
    guide=box([112,left,floor_bottom],[121,right,floor_bottom+2]).multiFuse([
        box([112,left,floor_bottom],[121,left+2,top]),box([112,right-2,floor_bottom],[121,right,top]),
        box([119,-71.25,floor_bottom],[136,-68.25,floor_bottom+2])]).removeSplitter()
    band=box([115.25,left-1.2,floor_bottom-1.2],[117.75,right+1.2,top+1.2]).cut(
        box([115,left,floor_bottom],[118,right,top]))
    head=box([114,-76.65,top+1.2],[119,-71.35,top+5.5])
    def clone(s):
        c=Part.Shape();c.importBrepFromString(s.exportBrepToString());return c
    joint=clone(guide).common(clone(parent)).Volume;whole=clone(guide).fuse(clone(parent))
    assert joint>0 and whole.isValid() and len(whole.Solids)==1
    actors.update(RRFlatGuide=guide,RRFlatBand=band,RRFlatHead=head)
    assert all(s.isValid() and len(s.Solids)==1 for s in (*actors.values(),*resources.values()))
    return actors,resources,dict(recipes=recipes,parent='AuxGrip:CommonRoot',parent_joint_mm3=joint,
        full_section_width_mm=width,section_centre_Z_mm=z,bank_actual_top_Z_mm=83.,
        upper_case_actual_bottom_Z_mm=93.5,original3x3_is_not_a_supplier_connector=True,
        all9_first9_supported=True,actual_motor_contacts_unchanged=True,
        resource_capacity_not_finished_individual_cut=True,N01_complete=False,physical_pass=False)


def package(actors,resources,plan,parent,ends,profiles,static,outer,motion,prior_root):
    import time,hashlib,json,zipfile
    from pathlib import Path
    from check_main_p0_placement import ROOT,sha
    from plan_feline_layout import OUT
    from feline_atomic_save import save_json
    from plan_feline_usb_service_bight import outer_margin
    tick=time.monotonic();assert not static['failures'];all_shapes={**actors,**resources};checks=dict(static['checks'])
    for n,s in all_shapes.items():
        if n=='RRFlatGuide':continue
        gap=s.distToShape(parent)[0];checks[n+'|'+plan['parent']]=dict(gap_mm=gap,minimum_mm=1.25,ok=gap>=1.25-1e-6)
    outerfile=ROOT/json.loads((OUT/'n01-shared-Pi-carrier-r3-core-received.json').read_text())['recipe']['outer_file']
    current_outer=Part.Shape();current_outer.read(str(outerfile));assert abs(outer.Volume-current_outer.Volume)<1e-5
    outside={n:outer_margin(s,current_outer) for n,s in all_shapes.items()}
    assert all(r['ok'] for r in checks.values()) and all(r['ok'] for r in outside.values())
    zbound=min(s.BoundBox.ZMin for s in all_shapes.values())-max(r['bounds'][1][2] for r in motion)
    assert zbound>1.25 and {r['pose'] for r in motion}==set(range(36))
    # The unchanged AUX->POWER chain is received already. Change its first
    # guide joint only; do not retest every other root in the robot.
    graph=[dict(a='RRFlatGuide',b=plan['parent'],common_mm3=plan['parent_joint_mm3']),*prior_root['positive_shared_print_graph'][1:]]
    path=OUT/'n01-RR9-flat-common-bank-bridge.json';archive=path.with_suffix('.breps.zip');geometry=[]
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for n,s in {**all_shapes,'Input:parent':parent}.items():
            raw=s.exportBrepToString().encode();entry=str(len(geometry))+'.brep';z.writestr(entry,raw)
            geometry.append(dict(name=n,entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
    wires={r['wire'] for r in plan['recipes'].values()};rows=[r for r in ends if r['wire'] in wires]
    specs={r['portion_id']:{k:profiles[r['portion_id']][k] for k in ('project_radius_mm','minimum_project_R_mm')} for r in rows}
    result=dict(status='RR9_FLAT_COMMON_BANK_BRIDGE_STATIC_SAMPLE36_RECEIVED_TERMINAL_FORKS_OPEN',
        plan=plan,checks=checks,outer=outside,constructor_rows=rows,constructor_profiles=specs,
        sampled36_leg_vertical_separation_lower_bound_mm=zbound,positive_shared_print_graph=graph,
        retained_unchanged_root_chain='n01-RR9-service-spine-rooted-space.json',
        geometry=geometry,bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive),
        source_sha256={**static['source_sha256'],outerfile.relative_to(ROOT).as_posix():sha(outerfile),
                       Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
        N01_complete=False,physical_pass=False,native_changed=False,whole123_not_received=True,
        moving900_and_terminal_forks_NOT_received=True,worker_seconds=round(time.monotonic()-tick,3))
    save_json(path,result);return result
