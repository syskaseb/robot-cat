"""One coupled four-output plan: underplate joints and over-bank gallery.

Both MTA source sides stay present. Keep factory strip/rework allowances.
Every physical wire has a full independent9mm open pad/selected tie kit;
an extra grip before every bend is NOT silently a manufacturer dimension.
No native manufacture, final custom cuts, joint-case roots or N01 award.
"""
import gzip,hashlib,json,math,os,time,zipfile
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from feline_profile_corrected_context import compose
from feline_selected_material_contract import load as profiles
from rigid_tangent_channel import turn
from plan_current_mta_interfaces import line
from plan_feline_n01_shared import pipe
from receive_feline_positive_service_deck import open_grip
from receive_feline_global_case_candidates import placement
from feline_fore_power_pair import SolidQueries,pair_spacing
from feline_common_space_context import is_jacket
from feline_solid_distance import bbox_lower_bound
from plan_feline_pi_root_access import profile_gap
from plan_feline_usb_service_bight import outer_margin
from receive_feline_psys_frame_load_paths import load

WIRES=('W026','W037','W045','W053')


def factory_axis(start,end):
    v=np.asarray(end)-start;v=v/np.linalg.norm(v);d=np.array([np.sign(v[0]),0.,0.])
    # Saved endpoint coordinates contain micrometre-scale roundoff. This is
    # the existing nominal axial MTA datum, not a guessed new wire direction.
    assert np.linalg.norm(v-d)<1e-5,'Wrong MTA source frame, not numerical roundoff'
    return d,float(np.linalg.norm(v-d))


def minimum_for(a,ar,b,br):
    def nylon(n,r):
        return r.get('material_role')=='selected_T18I_nylon_budget' or (r.get('kind') in ('tie_reservation','project_stock_reservation') and ('Tie' in n or n.endswith((':band_budget',':head_budget'))))
    if nylon(a,ar) and (is_jacket(b,br) or nylon(b,br)) or nylon(b,br) and is_jacket(a,ar):return .2
    return pair_spacing(a,ar,b,br)


def forward(rows,q,d,length):
    end=np.asarray(q)+length*np.asarray(d)
    if length>1e-8:rows.append(line(list(q),end.tolist()))
    return end


def bend(rows,q,d,n,R,angle=math.pi/2):
    arc,heading=turn(list(q),list(d),list(n),angle,R);rows+=arc
    return np.asarray(arc[-1]['end']),np.asarray(heading)


def main():
    tick=time.monotonic();world,parts,meta,pins,docs=compose();contract,cf,df=profiles()
    lf=OUT/'n01-full-lower-bay-plan-r3.json';lower=json.loads(lf.read_text());factory={r['wire']:r for r in lower['factory_routes']}
    dest=OUT/'n01-underplate-return-gallery.json';pairfile=dest.with_suffix('.pairs.json.gz')
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (lf,cf,df,Path(__file__),ROOT/'tools/cad/feline_selected_material_contract.py',ROOT/'tools/cad/receive_feline_positive_service_deck.py',ROOT/'hardware/reference/cable-ties/t18i-111-02370/head-envelope.json')})
    old={};retired=[]
    for w in WIRES:
        for row in lower['parts']:
            n=row['name']
            if n in ('Ref_Material_'+w+'_Joint_0_0','Factory:'+w,'CustomPrefix:'+w) or n.startswith(('Seat:'+w+':','TieLoop:Seat:'+w+':','TieHead:Seat:'+w+':')):
                assert n in parts,('Missing current lower source',n);old[n]=parts[n];retired.append(n)
    assert len(retired)==48
    fixed={n:s for n,s in parts.items() if n not in retired};actors={};roles={};ameta={};recipes={}
    plate=parts['Print_P0_BATTERY_PLATE_R4'].BoundBox
    anchor=parts['Ref_Material_U1_AnchorRight_0_0'].BoundBox
    pcb=parts['Ref_Material_U1_Adapter1208PCB_0_0'].BoundBox
    caseheight=old['Ref_Material_W026_Joint_0_0'].BoundBox.ZLength
    lo=max(anchor.ZMax+1.25+caseheight/2,pcb.ZMax+1.25+2.1)
    hi=plate.ZMin-1.25-caseheight/2;assert hi>lo,('No real common slot',lo,hi)
    Z=(lo+hi)/2;Y=max(abs(pcb.YMin),abs(pcb.YMax))+4.05+1.25+.25
    def add(n,s,kind,role):
        assert s.isValid() and s.Solids,n;actors[n]=s;roles[n]=role;ameta[n]=dict(kind=kind)
        if n.startswith('ReturnGrip:') and not n.endswith(':pad'):ameta[n]['material_role']='selected_T18I_nylon_budget'
    result=dict(status='RUNNING_UNDERPLATE_COMMON_RETURN_GALLERY',source_sha256=pins,
        slot=dict(lower_mm=lo,upper_mm=hi,chosen_Z_mm=Z,chosen_absY_mm=Y,
            source_actual_U1_anchor_top_mm=anchor.ZMax,source_actual_U1_PCB_top_mm=pcb.ZMax,battery_plate_bottom_mm=plate.ZMin),
        retired_current_actors=retired,recipes=recipes,completed_static=[],completed_motion=[],
        joint_case_retention_roots_and_full_custom_routes_OPEN=True,physical_pass=False,N01_complete=False,selected=False)
    checks={}
    def save():
        pairfile.write_bytes(gzip.compress(json.dumps(checks,separators=(',',':')).encode(),mtime=0))
        result.update(worker_seconds=round(time.monotonic()-tick,3),pair_rows=pairfile.relative_to(ROOT).as_posix(),pair_rows_sha256=sha(pairfile))
        save_json(dest,result)
    if dest.exists():
        result=json.loads(dest.read_text());assert result['source_sha256']==pins
        assert sha(pairfile)==result['pair_rows_sha256'];checks=json.loads(gzip.decompress(pairfile.read_bytes()))
        actors=load(result,'geometry');roles=result['actor_roles'];ameta=result['actor_meta'];recipes=result['recipes']
    else:
        for w in WIRES:
            f=factory[w];p=np.asarray(f['parts'][0]['start']);d,axis_error=factory_axis(p,f['parts'][0]['end'])
            side=1 if p[1]>0 else -1;fore=d[0]<0
            first,last=(28.7,9.25) if fore else (.25,29.8)
            delta=np.array([0.,side*Y-p[1],Z-p[2]]);H=float(np.linalg.norm(delta));n=delta/H
            assert H>=24.8
            ff=[];q=forward(ff,p,d,first);q,t=bend(ff,q,d,n,12.4)
            q=forward(ff,q,t,H-24.8);q,t=bend(ff,q,t,-d,12.4);q=forward(ff,q,t,last)
            length=sum(e['length_mm'] for e in ff);assert length+11+10<=100,(w,length+21)
            oldcase=old['Ref_Material_'+w+'_Joint_0_0'];b=oldcase.BoundBox
            assert abs(b.XLength-35.5)<1e-4 and abs(b.YLength-8.1)<1e-4 and abs(b.ZLength-8.9)<1e-4
            centre=q-17.75*d;R180=np.diag([-1.,-1.,1.]);tf=placement(R180,centre-R180@np.array(list(b.Center)))
            case=oldcase.copy();case.Placement=tf*case.Placement
            mouth=centre-17.75*d;full=[];tip=forward(full,mouth,-d,.25)
            radius=contract['portions'][w+'/custom']['project_radius_mm'];R=contract['portions'][w+'/custom']['minimum_project_R_mm']
            assert radius>=2.1-1e-6 and R>=25.2
            outward=np.array([0.,float(side),0.]);tip,t=bend(full,tip,-d,outward,R)
            grip=tip+.25*t;tip=forward(full,tip,t,17.75)
            tip,t=bend(full,tip,t,[0,0,1],R)
            assert tip[2]<62.8;tip=forward(full,tip,t,62.8-tip[2])
            tip,t=bend(full,tip,t,-outward,R)
            add('ReturnFactory:'+w,pipe(ff,f['radius_mm']),'wire','Factory:'+w)
            add('ReturnCustom:'+w,pipe(full,radius),'wire','Custom:'+w)
            add('ReturnJoint:'+w,case,'proposal_material','Joint:'+w)
            for typ,start,axis,support in (('Factory',q+9.25*d,-d,outward),('Custom',grip,outward,np.array([0,0,-1]))):
                kit=open_grip(start,axis,support,4.5);kit['pad'].translate(A.Vector(*(-.25*support)))
                for short,s in kit.items():add('ReturnGrip:'+typ+':'+w+':'+short,s,'proposal_material' if short=='pad' else 'project_stock_reservation',typ+':'+w)
            recipes[w]=dict(factory_parts=ff,factory_guide_mm=length,strip_mm=11,rework_mm=10,
                factory_required_mm=length+21,factory_project100_margin_mm=100-length-21,
                custom_parts=full,custom_prefix_length_mm=sum(e['length_mm'] for e in full),custom_exit_mm=tip.tolist(),custom_exit_axis=t.tolist(),
                custom_grip_start_mm=grip.tolist(),custom_grip_axis=outward.tolist(),joint_centre_mm=centre.tolist(),
                legacy_first_line_nominal_axis_roundoff_norm=axis_error,nominal_MTA_source_axis_retained=d.tolist(),
                case_transform=dict(rotation=R180.tolist(),translation_mm=list(tf.Base)),
                one_independent_full9_factory_grip_near_joint=True,one_independent_full9_custom_grip_after_first_arc=True,
                no_manufacturer_mandatory_straight9_before_arc_claimed=True,
                final_custom_wire_cut_and_stock_not_selected=True,joint_case_retention_and_all_new_grip_roots_OPEN=True)
        archive=dest.with_suffix('.breps.zip');geometry=[]
        with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
            for i,(n,s) in enumerate(actors.items()):
                raw=s.exportBrepToString().encode();entry=str(i)+'.brep';z.writestr(entry,raw);geometry.append(dict(name=n,entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
        result.update(geometry=geometry,bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive),recipes=recipes,actor_roles=roles,actor_meta=ameta)
        save();print('Whole construction saved',len(actors),'factory margins',{w:r['factory_project100_margin_mm'] for w,r in recipes.items()},flush=True)
    bounds={n:s.BoundBox for n,s in {**fixed,**actors}.items()};query=SolidQueries()
    def static(n,s):
        key=n+'|outer'
        if key not in checks:checks[key]=outer_margin(s,docs['outer'])
        for m,t in {**fixed,**actors}.items():
            if n==m:continue
            key='|'.join(sorted((n,m))) if m in actors else n+'|'+m
            if key in checks:continue
            minimum=minimum_for(n,ameta[n],m,ameta[m] if m in actors else meta[m])
            if bbox_lower_bound(bounds[n],bounds[m])>=minimum:continue
            if m==world.bus['name']:
                a=s.copy();a.Placement=docs['inverse']*a.Placement;gap=query.distance(world.bus['original'],a)
            elif t.Solids:gap=query.distance(s,t)
            else:
                rr=meta[m].get('nominal_profile_radius_mm');assert rr,('Unknown curve profile',m)
                checks[key]=profile_gap(s,t,rr,minimum);continue
            r=dict(ok=gap>=minimum-1e-6,gap_mm=gap,minimum_mm=minimum)
            if m in actors and roles[n]==roles[m]:
                common=s.common(t);assert common.isNull() or common.isValid()
                r.update(ok=common.Volume<1e-5,nominal_same_independent_grip_kit_common_mm3=common.Volume)
            if n.startswith('Return') and m in actors:
                w=n.split(':')[1] if not n.startswith('ReturnGrip:') else n.split(':')[2]
                if m=='ReturnJoint:'+w and n.startswith(('ReturnFactory:','ReturnCustom:')):
                    common=s.common(t);assert common.isNull() or common.isValid();r.update(ok=common.Volume<1e-5,nominal_joint_mouth_common_mm3=common.Volume)
            if n.startswith('ReturnFactory:') and m in ('Ref_Material_MTA_FL_0_0','Ref_Material_MTA_FR_0_0','Ref_Material_MTA_RL_0_0','Ref_Material_MTA_RR_0_0'):
                w=n.split(':')[1]
                if factory[w]['source_group'] in m:
                    common=s.common(t);prior=old['Factory:'+w].common(t);assert common.isNull() or common.isValid()
                    difference=common.cut(prior).Volume+prior.cut(common).Volume
                    r.update(ok=difference<1e-5,unchanged_actual_source_mouth_ingress_difference_mm3=difference)
            checks[key]=r
        result['completed_static'].append(n);save()
    try:
        for n,s in actors.items():
            if n in result['completed_static']:continue
            static(n,s);print('Static',n,'holds',sum(not r['ok'] for r in checks.values()),flush=True)
            if time.monotonic()-tick>225:raise TimeoutError('Atomic source/whole-pair receipt slice; resume same inputs')
        bad=[k for k,r in checks.items() if not r['ok']]
        if not bad:
            for n,s in actors.items():
                if n in result['completed_motion']:continue
                for pose in world.motion:
                    key=n+'|motion:'+pose['name']+':'+str(pose['pose'])
                    if key in checks or bbox_lower_bound(bounds[n],A.BoundBox(*pose['bounds'][0],*pose['bounds'][1]))>=1.25:continue
                    a=s.copy();a.Placement=placement(pose['r'],pose['t']).inverse()*a.Placement
                    gap=query.distance(a,world.rest[pose['name']]);checks[key]=dict(ok=gap>=1.25-1e-6,gap_mm=gap,minimum_mm=1.25)
                result['completed_motion'].append(n);save()
                if time.monotonic()-tick>225:raise TimeoutError('Motion actor received; resume remaining actors only')
        bad=[k for k,r in checks.items() if not r['ok']]
        result.update(status='UNDERPLATE_RETURN_WHOLE_CHANGED_HOLDS' if bad else 'UNDERPLATE_RETURN_WHOLE_CHANGED_STATIC36_RECEIVED_ROOTS_OPEN',
            failures=bad,checks=len(checks),full_changed_motion_received=not bad and len(result['completed_motion'])==len(actors))
    except TimeoutError as exc:result.update(status='PARTIAL_UNDERPLATE_RETURN_GALLERY',slice_note=str(exc))
    save();print(json.dumps(dict(status=result['status'],checks=len(checks),holds=sum(not r['ok'] for r in checks.values()),seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':print('WORKER_PID',os.getpid(),flush=True);main()
