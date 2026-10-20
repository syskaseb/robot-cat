"""Four inward custom exits: a shared layout cause change, not portal offsets.

Retain all four MTA source bodies, both tails, selected wire and100mm
provisional factory length. Four output inline joints turn180deg as complete
rigid bodies; four input joints/routes remain unchanged. Length and true
envelope preflight only: full mounts/ties/foreign clearance remain OPEN.
"""
import hashlib,json,math,os,time,zipfile
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,SavedShapes,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from rigid_tangent_channel import turn
from plan_current_mta_interfaces import line
from plan_feline_n01_shared import pipe
from receive_feline_global_case_candidates import placement
from plan_feline_usb_service_bight import outer_margin
from feline_selected_material_contract import load as profiles


def return_loop(start,d,end,R=12.4,last=9.25):
    p=np.asarray(start,float);d=np.asarray(d,float);q=np.asarray(end,float)
    lateral=q-p-d*float((q-p)@d);H=float(np.linalg.norm(lateral));v=lateral/H
    assert H>=2*R and abs(v@d)<1e-6
    a=q-lateral+last*d;first=float((a-p)@d);assert first>=9.25
    rows=[line(p.tolist(),a.tolist())]
    arc,heading=turn(a.tolist(),d.tolist(),v.tolist(),math.pi/2,R);rows+=arc;b=np.asarray(arc[-1]['end'])
    if H>2*R:rows.append(line(b.tolist(),(b+(H-2*R)*v).tolist()));b+=(H-2*R)*v
    arc,heading=turn(b.tolist(),v.tolist(),(-d).tolist(),math.pi/2,R);rows+=arc;b=np.asarray(arc[-1]['end'])
    assert np.linalg.norm(q-b+last*d)<1e-5
    rows.append(line(b.tolist(),q.tolist()))
    assert np.linalg.norm(np.asarray(heading)+d)<1e-6
    return rows


def main():
    tick=time.monotonic();lf=OUT/'n01-full-lower-bay-plan-r3.json';lower=json.loads(lf.read_text())
    contract,cf,df=profiles();envelope_file=OUT/'central-cassette-envelope/manifest.json';envelope=json.loads(envelope_file.read_text())
    ef=OUT/'n01-shared-routing-boundaries.json';reg=json.loads(ef.read_text());ends={e['id']:e for e in reg['endpoints']}
    custom={r['wire']:r for r in lower['custom_ends']};factory={r['wire']:r for r in lower['factory_routes']}
    # A necessary bound, not a bbox-intersection claim. To reach a destination
    # behind its departure tangent, a curvature-limited cable must turn at
    # least90deg. Its maximum forward excursion is >=R before that turn.
    necessary=[]
    for w in ('W026','W037'):
        c=custom[w];p=np.asarray(c['point_mm'])+c['prefix_mm']*np.asarray(c['departure_axis']);r=contract['portions'][w+'/custom']
        endpoint=ends[w+'/custom/end']['routing_exit_mm'];assert endpoint[0]>p[0] and c['departure_axis']==[-1,0,0]
        assert r['minimum_project_R_mm']>=25.2,'HELU in composite factory+extension label is still selected HELU'
        minimum_x=float(p[0]-r['minimum_project_R_mm']);limit=envelope['actual_bounds_mm'][0][0]+r['project_radius_mm']+3.25
        necessary.append(dict(wire=w,existing_prefix_tip_mm=p.tolist(),required_R_mm=r['minimum_project_R_mm'],
            unavoidable_centre_X_at_or_before_first90_mm=minimum_x,allowed_centre_X_lower_mm=limit,
            required_fore_bound_violation_mm=limit-minimum_x,existing_orientation_cannot_reach_interior_within_envelope=minimum_x<limit))
    assert all(r['existing_orientation_cannot_reach_interior_within_envelope'] for r in necessary)
    # Only frozen source BReps, not a new whole-world recompute.
    parts={}
    source=ROOT/lower['bundle'] if 'bundle' in lower else None
    # Full lower-bay source is archived by its immutable full-material child.
    sf=OUT/'n01-full-material-scene.json';scene=json.loads(sf.read_text());archive=ROOT/scene['bundle'];assert sha(archive)==scene['bundle_sha256']
    names={'Ref_Material_'+w+'_Joint_0_0' for w in ('W026','W037','W045','W053')}
    with zipfile.ZipFile(archive) as z:
        for r in scene['parts']:
            if r['name'] not in names:continue
            raw=z.read(r['entry']);assert hashlib.sha256(raw).hexdigest()==r['sha256'];s=Part.Shape();s.importBrepFromString(raw.decode());assert s.isValid() and s.Solids;parts[r['name']]=s
    # Source scene joints may precede R3. Recover their current position by
    # centring the unchanged actual shape at the received R3 joint centre.
    reader=SavedShapes();outer=reader.shape(ROOT/envelope['native'],'TorsoEnvelope');assert outer.isValid()
    output={};geometry={};matrix=np.diag([-1.,-1.,1.]);planes=[]
    for w in ('W026','W037','W045','W053'):
        f=factory[w];c=custom[w];start=np.asarray(f['parts'][0]['start'],float)
        d=np.asarray(f['parts'][0]['end'])-start;d/=np.linalg.norm(d)
        assert abs(abs(d[0])-1)<1e-6
        side=1 if start[1]>0 else -1;oldcentre=np.asarray(lower['joint_centres_mm'][w+'_Joint'],float)
        centre=np.array([start[0]+17.5*d[0],side*45.,start[2]])
        tf=placement(matrix,centre-matrix@oldcentre)
        end=np.asarray(list(tf.multVec(A.Vector(*f['parts'][-1]['end']))));end[2]=start[2]
        rows=return_loop(start,d,end);L=sum(r['length_mm'] for r in rows);assert L<=100
        q=np.asarray(list(tf.multVec(A.Vector(*c['point_mm']))));q[2]=start[2];departure=matrix@np.asarray(c['departure_axis'])
        R=contract['portions'][w+'/custom']['minimum_project_R_mm'];radius=contract['portions'][w+'/custom']['project_radius_mm']
        assert R>=25.2 and radius>=2.1-1e-6,'Do not keep an obsolete generic extension bend'
        normal=np.array([0.,-side/math.sqrt(2),1/math.sqrt(2)]);land=q+9.25*departure
        bend,heading=turn(land.tolist(),departure.tolist(),normal.tolist(),math.pi/2,R)
        full=[line(q.tolist(),land.tolist())]+bend
        tube=pipe(rows,f['radius_mm']);prefix=pipe(full,radius)
        n='Ref_Material_'+w+'_Joint_0_0';case=parts[n].copy()
        oldcentre_actual=np.array(list(case.BoundBox.Center));case.translate(A.Vector(*(oldcentre-oldcentre_actual)))
        case.Placement=tf*case.Placement;assert np.linalg.norm(np.array(list(case.BoundBox.Center))-centre)<1e-4
        geometry['InwardJoint:'+w]=case;geometry['InwardFactory:'+w]=tube;geometry['InwardCustom:'+w]=prefix
        margins={k:outer_margin(s,outer) for k,s in ((n,case),('factory',tube),('custom',prefix))}
        output[w]=dict(joint_centre_mm=centre.tolist(),joint_rotation_delta_deg=180,axis=[0,0,1],factory_parts=rows,
            factory_guide_mm=L,provisional100mm_factory_margin_mm=100-L,factory_length_not_catalogue_or_delivered_guarantee=True,
            retained_strip_allowance_mm=11,retained_rework_assumption_mm=10,
            factory_need_with_strip_and_rework_mm=L+21,
            full_factory_budget_gate=L+21<=100,
            factory_first_last_lands_mm=[rows[0]['length_mm'],rows[-1]['length_mm']],
            custom_parts=full,custom_exit_mm=full[-1]['end'],custom_exit_axis=heading,
            selected_project_radius_mm=radius,minimum_custom_bend_mm=R,outer=margins,
            full_seats_ties_heads_root_access_and_changed_neighbors_OPEN=True)
    dest=OUT/'n01-inward-four-output-joints-plan.json';bundle=dest.with_suffix('.breps.zip');records=[]
    with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
        for i,(n,s) in enumerate(geometry.items()):
            assert s.isValid() and s.Solids;raw=s.exportBrepToString().encode();entry=str(i)+'.brep';z.writestr(entry,raw)
            records.append(dict(name=n,entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
    result=dict(status='FOUR_INWARD_OUTPUT_JOINTS_LENGTH_AND_OUTER_PREFLIGHT_ONLY',existing_fore_orientation_necessary_rejection=necessary,
        chosen_common_cause_change='Turn the four complete output inline joints inward; full factory return loops instead of custom power bends through the fore wall',
        outputs=output,geometry=records,bundle=bundle.relative_to(ROOT).as_posix(),bundle_sha256=sha(bundle),
        unchanged_input_joints_and_factory_routes=['W041','W042','W044','W052'],MTA_source_bodies_not_moved=True,
        selected_parts_wire_lengths_and_body_envelope_not_changed=True,N01_complete=False,selected=False,physical_pass=False,
        all_factory_strip_rework_budgets_fit=all(r['full_factory_budget_gate'] for r in output.values()),
        source_sha256={**reader.hashes,**{p.relative_to(ROOT).as_posix():sha(p) for p in (lf,cf,df,ef,envelope_file,sf,archive,Path(__file__),ROOT/'tools/cad/feline_selected_material_contract.py',ROOT/'hardware/electronics/full-cat/servo-fuse-main-feeds-materials-r1/materials.json')}},
        worker_seconds=round(time.monotonic()-tick,3))
    save_json(dest,result);print(json.dumps(dict(status=result['status'],fore_witness=necessary,
        factory_margins_mm={w:r['provisional100mm_factory_margin_mm'] for w,r in output.items()},outer={w:r['outer'] for w,r in output.items()},seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':print('WORKER_PID',os.getpid(),flush=True);main()
