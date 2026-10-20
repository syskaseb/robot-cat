"""Coupled four fans and TWO full selected tie-head orientations.

Keep P0/all four original feet and all original4mm frame webs. Retain the
received first XY-S; upper directions differ by source side and avoid AUX,
rear frame and S1 together. This is not a grip/root/whole-N01 receipt.
"""
import copy,gzip,hashlib,json,math,time,zipfile
from pathlib import Path
import FreeCAD as A
import Part
import numpy as np
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_main_hung_context import compose
from receive_feline_rrp_shared_height import load
from receive_feline_factory_saddle_revision import owner
from plan_feline_remaining_factory_inputs import offset,forward
from receive_feline_underplate_return_gallery import bend,minimum_for
from plan_feline_n01_shared import pipe
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound
from plan_feline_pi_root_access import profile_gap
from plan_feline_usb_service_bight import outer_margin
from receive_feline_global_case_candidates import placement
from feline_atomic_save import save_json


def head_above_existing_band(band,old,y):
    b=band.BoundBox;x=b.Center.x
    head=Part.makeBox(5,5.3,4.3,A.Vector(x-2.5,y-2.65,b.ZMax))
    assert head.isValid() and len(head.Solids)==1 and abs(head.Volume-old.Volume)<1e-5
    joint=head.common(band);union=head.fuse(band);gap=head.distToShape(band)[0]
    assert joint.isValid() and joint.Volume<1e-5 and union.isValid() and len(union.Solids)==1 and gap<1e-10
    # Read the ACTUAL rectangular top face, not an arbitrary bounding box.
    top=[f for f in band.Faces if isinstance(f.Surface,Part.Plane) and abs(f.CenterOfMass.z-b.ZMax)<1e-8 and abs(f.normalAt(0,0).z)>1-1e-8]
    assert len(top)==1 and len(top[0].Edges)==4 and len(top[0].Wires)==1
    fb=top[0].BoundBox;assert abs(top[0].Area-fb.XLength*fb.YLength)<1e-6
    area=max(0,min(x+2.5,fb.XMax)-max(x-2.5,fb.XMin))*max(0,min(y+2.65,fb.YMax)-max(y-2.65,fb.YMin))
    assert area>1
    return head,dict(unchanged_selected_T18I_head_dims_mm=[5,5.3,4.3],old_volume_mm3=old.Volume,
        new_volume_mm3=head.Volume,actual_existing_band_contact_area_mm2=area,
        contact_area_method='Actual coplanar rectangular face intersection; valid1Solid union, not common.Area',
        kernel_common_area_mm2=joint.Area,actual_nominal_face_gap_mm=gap,head_band_union_solids=1,
        existing_band_pad_root_and_wire_NOT_changed=True,delivered_tie_orientation_fit_gate=True)


def main():
    tick=time.monotonic();world,parts,meta,pins,docs=compose()
    sf=OUT/'n01-MTA-inboard-fans-preflight.json';source=json.loads(sf.read_text())
    assert len(source['completed_static'])==4 and len(source['failures'])==4
    for p,h in source['source_sha256'].items():assert sha(ROOT/p)==h,p
    bf=OUT/'n01-factory-saddles-received.json';base=json.loads(bf.read_text());kit=load(base)
    fixed={n:s for n,s in parts.items() if n not in base['retired']};fixed.update(kit);fm={**meta,**base['actor_meta']}
    for n in list(fixed):
        w=owner(n)
        if w in ('W044','W052') and not n.startswith('Factory:'):
            fixed[n]=fixed[n].copy();fixed[n].translate(A.Vector(-10,0,0))
        if w and n.startswith(('Seat:'+w+':custom','TieLoop:Seat:'+w+':custom','TieHead:Seat:'+w+':custom')):
            fixed.pop(n);fm.pop(n,None)
    for w in ('W044','W052'):
        rows=copy.deepcopy(base['recipes'][w]['parts']);rows[-1]['end'][0]-=10;rows[-1]['length_mm']+=10;fixed['Factory:'+w]=pipe(rows,2.1)
    actors={};ameta={};recipes={};heads={}
    for n,old in source['recipes'].items():
        w=owner(n);fixed.pop(n);fm.pop(n,None);side=np.sign(old['point_mm'][1]);d=np.asarray(old['axis']);rows=copy.deepcopy(old['parts'][:3]);q=np.array(rows[-1]['end'])
        sine=.25 if d[0]>0 else .5;cosine=math.sqrt(1-sine*sine)
        q,t=bend(rows,q,d,[0,side*sine,cosine],25.2)
        q,t=bend(rows,q,t,[0,-side*cosine,sine],25.2,math.asin(sine))
        assert np.linalg.norm(t-[0,0,1])<1e-6
        if d[0]<0:q=offset(rows,q,t,[0,side*25-q[1],0])
        assert q[2]<45.26;forward(rows,q,t,45.26-q[2])
        actors[n]=pipe(rows,2.1);ameta[n]=dict(kind='actual_wire')
        recipes[n]=dict(old,parts=rows,upper_tilt_sine=sine,routing_exit_mm=rows[-1]['end'],
            first_XY_S_byte_recipe_preserved=True,original_P0_feet_and_frame_webs_unchanged=True,
            full_grip_root_and_whole_moved_kit_motion_still_OPEN=True)
    for w in ('W045','W053'):
        name='EndGrip:Factory:'+w+':head';old=fixed.pop(name);band=fixed['EndGrip:Factory:'+w+':band'];b=band.BoundBox
        y=15. if w=='W045' else -15.
        head,heads[name]=head_above_existing_band(band,old,y)
        actors[name]=head;ameta[name]=dict(kind='project_stock_reservation',material_role='selected_T18I_nylon_budget')
        fm.pop(name,None)
    dest=OUT/'n01-MTA-tilted-fans.json';pf=dest.with_suffix('.pairs.json.gz');archive=dest.with_suffix('.breps.zip')
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (sf,ROOT/source['bundle'],bf,ROOT/base['bundle'],Path(__file__))})
    checks={};result=dict(status='RUNNING_MTA_TILTED_FOUR_FANS',source_sha256=pins,recipes=recipes,head_orientation_proofs=heads,
        completed_static=[],completed_motion=[],N01_complete=False,native_changed=False,physical_pass=False,
        original_P0_feet_webs_and_purchased_parts_unchanged=True,all_grips_roots_moved_kit_access_stock_still_OPEN=True)
    if dest.exists():
        result=json.loads(dest.read_text());assert result['source_sha256']==pins
        assert sha(pf)==result['pair_rows_sha256'];checks=json.loads(gzip.decompress(pf.read_bytes()));actors=load(result)
    else:
        geometry=[]
        with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
            for i,(n,s) in enumerate(actors.items()):
                raw=s.exportBrepToString().encode();entry=str(i)+'.brep';z.writestr(entry,raw);geometry.append(dict(ameta[n],name=n,entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
        result.update(geometry=geometry,bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive))
    def save():
        pf.write_bytes(gzip.compress(json.dumps(checks,separators=(',',':')).encode(),mtime=0))
        result.update(checks=len(checks),failures=[k for k,v in checks.items() if not v['ok']],pair_rows=pf.relative_to(ROOT).as_posix(),pair_rows_sha256=sha(pf),worker_seconds=round(time.monotonic()-tick,3));save_json(dest,result)
    save();query=SolidQueries()
    for n,s in actors.items():
        if n in result['completed_static']:continue
        checks[n+'|outer']=outer_margin(s,docs['outer']);w=owner(n)
        for m,t in {**fixed,**actors}.items():
            if n==m:continue
            key='|'.join(sorted((n,m))) if m in actors else n+'|'+m
            if key in checks:continue
            mr=ameta[m] if m in actors else fm[m];minimum=minimum_for(n,ameta[n],m,mr)
            if bbox_lower_bound(s.BoundBox,t.BoundBox)>=minimum:continue
            a=s;ownmouth=n.startswith('CustomPrefix:') and m=='Ref_Material_'+w+'_Joint_0_0'
            if ownmouth:
                c=s.common(t);assert c.isNull() or c.isValid();assert c.Volume<1e-5
                a=s.cut(Part.makeCylinder(3,2.5,A.Vector(*recipes[n]['point_mm']),A.Vector(*recipes[n]['axis'])))
            if m==world.bus['name']:a=a.copy();a.Placement=docs['inverse']*a.Placement;t=world.bus['original']
            row=dict(ok=(gap:=query.distance(a,t))>=minimum-1e-6,gap_mm=gap,minimum_mm=minimum) if t.Solids else profile_gap(a,t,mr.get('nominal_profile_radius_mm') or mr.get('radius_mm'),minimum)
            if n.startswith('CustomPrefix:') and m=='CaseBase:'+w+'_Joint':
                oldwire=kit.get(n,parts.get(n)).copy()
                if w in ('W044','W052'):oldwire.translate(A.Vector(-10,0,0))
                before=oldwire.common(t);now=s.common(t);baseline=query.distance(oldwire,t)
                assert (before.isNull() or before.isValid()) and (now.isNull() or now.isValid())
                row.update(ok=now.cut(before).Volume<1e-5 and gap>=min(baseline,minimum)-1e-6,old_own_shoe_gap_mm=baseline)
            if n in heads and m==n.removesuffix('head')+'band':row.update(ok=True,actual_head_band_contact_area_mm2=heads[n]['actual_existing_band_contact_area_mm2'])
            if not row['ok'] and t.Solids:
                _,pts,_=a.distToShape(t);row['witness_mm']=[[list(x),list(y)] for x,y in pts[:1]]
            checks[key]=row
        result['completed_static'].append(n);save();print(n,'holds',len(result['failures']),flush=True)
        if time.monotonic()-tick>220:result['status']='PARTIAL_MTA_TILTED_FANS_SAVED';save();return
    if not result['failures']:
        for n,s in actors.items():
            if n in result['completed_motion']:continue
            for pose in world.motion:
                if bbox_lower_bound(s.BoundBox,A.BoundBox(*pose['bounds'][0],*pose['bounds'][1]))>=1.25:continue
                key=n+'|motion:'+pose['name']+':'+str(pose['pose'])
                if key in checks:continue
                a=s.copy();a.Placement=placement(pose['r'],pose['t']).inverse()*a.Placement
                gap=query.distance(a,world.rest[pose['name']]);checks[key]=dict(ok=gap>=1.25-1e-6,gap_mm=gap,minimum_mm=1.25)
            result['completed_motion'].append(n);save()
            if time.monotonic()-tick>220:result['status']='PARTIAL_MTA_TILTED_FANS_SAVED';save();return
    result['status']='MTA_TILTED_FAN_HOLDS' if result['failures'] else 'FOUR_MTA_TILTED_FANS_TWO_T18I_HEADS_STATIC36_RECEIVED_GRIPS_ROOTS_OPEN'
    result['sampled_motion_not_continuous']=True;save();print(result['status'],result['checks'],len(result['failures']),result['worker_seconds'],flush=True)


if __name__=='__main__':main()
