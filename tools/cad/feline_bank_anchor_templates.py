"""Complete24 bank source kits and actual paired clamp kits for shared planning.

All q/d/r/first9 and purchased TE/cases retained. Only subsequent bends and
complete band-head direction vary. No native exports or physical fit approval.
"""
import itertools
import json
import math
import zipfile
import numpy as np
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,SavedShapes,sha
from plan_feline_layout import OUT,MODEL
from plan_feline_joint_fore_domains import cloud
from feline_flat_station_templates import box_points


def bank_candidates(proof):
    result={}
    for r in proof['bank_joint_full_source_ports']:
        q=np.array(r['start_mm']);d=np.array(r['departure_axis']);R=r['bend_R_mm'];radius=r['radius_mm']
        assert abs(abs(d[1])-1)<1e-6 and abs(d[0])+abs(d[2])<1e-6
        choices=[];u=np.array([1.,0,0]);v=np.array([0.,0,1.]);a=q+9*d
        for angle,headangle in itertools.product(range(0,360,45),(0,90,180,270)):
            b=u*math.cos(math.radians(angle))+v*math.sin(math.radians(angle))
            aa=np.linspace(0,math.pi/2,32)
            arc=a+R*np.sin(aa)[:,None]*d+R*(1-np.cos(aa))[:,None]*b
            wire=np.vstack((np.linspace(q,a,10),arc,np.linspace(arc[-1],arc[-1]+9*b,10)))
            cap=[];band=[]
            for t in np.linspace(0,2*math.pi,17)[:-1]:
                transverse=u*math.cos(t)+v*math.sin(t)
                cap.extend([p+(radius+2)*transverse for p in np.linspace(q,a,6)])
                band.extend([q+k*d+(radius+3.2)*transverse for k in (3.25,4.5,5.75)])
            cap=np.array(cap);band=np.array(band)
            h=q+4.5*d+(radius+6.2)*(u*math.cos(math.radians(headangle))+v*math.sin(math.radians(headangle)))
            head=box_points(h-3,h+3)
            points=np.vstack((wire,cap,band,head));radii=np.r_[np.full(len(wire),radius),np.zeros(len(cap)+len(band)+len(head))]
            types=np.r_[np.ones(len(wire),int),np.full(len(cap)+len(band)+len(head),2)]
            choices.append(dict(ref='Bank:'+r['id'],bank_source=True,source_endpoint=r['id'],holder=r['holder'],
                terminal_name=r['terminal_name'],terminal_context_key=r['terminal_context_key'],
                point_mm=q.tolist(),departure_axis=d.tolist(),bend_unit=b.tolist(),first_mm=9,R_mm=R,
                radius_mm=radius,after_arc_exit_mm=(arc[-1]+9*b).tolist(),bend_clock_degrees=angle,
                complete_band_head_degrees=headangle,cap_wall_mm=2,band_wall_budget_mm=1.2,
                complete_head_budget_mm=[6,6,6],source_first9_unchanged=True,
                factory_length_not_changed=True,cap_base_to_retained_bank_frame_root_OPEN=True,
                own_terminal_entry3_35mm_mate_requires_exact_no_overlap_check=True,
                points=points,radii=radii,types=types,boxes=[],wires=[],
                bounds=np.array([(points-radii[:,None]).min(0),(points+radii[:,None]).max(0)])))
        result['Bank:'+r['id']]=choices
    assert len(result)==24
    return result


def anchor_candidates(received_parent_mates=None):
    proofpath=OUT/'n01-flat20-actual-clamp-kits.json';proof=json.loads(proofpath.read_text())
    bundle=ROOT/proof['bundle'];assert sha(bundle)==proof['bundle_sha256']
    reader=SavedShapes();parents={side:reader.shape(MODEL,'Ref_Material_P0_Side'+side+'22_0_0') for side in ('Left','Right')}
    shapes={};records={r['name']:r for r in proof['parts']}
    with zipfile.ZipFile(bundle) as z:
        for r in proof['parts']:
            blob=z.read(r['entry']);assert __import__('hashlib').sha256(blob).hexdigest()==r['sha256']
            s=Part.Shape();s.importBrepFromString(blob.decode());assert s.isValid() and s.Solids
            shapes[r['name']]=s
    def faces(s,z):
        return [f for f in s.Faces if abs(f.optimalBoundingBox().ZMin-z)<1e-5 and abs(f.optimalBoundingBox().ZMax-z)<1e-5]
    result={};receipts=[]
    received={(r['ref'],r['axis_X_mm']):r for r in (received_parent_mates or [])}
    for ref,indices,originalx in (('Anchor:Fore',(1,2),0),('Anchor:Rear',(3,4),90)):
        choices=[]
        for x in (-48,-24,0,24,48,72,90,96):
            posed={};bearings=[];errors=[]
            previous=received.get((ref,x))
            for i in indices:
                parent=parents['Right' if i in (1,3) else 'Left']
                for n,r in records.items():
                    if r['clamp']!=i:continue
                    s=shapes[n].copy()
                    if x!=originalx:s.translate(A.Vector(x-originalx,0,0))
                    if not s.isValid():errors.append(n+'invalid');continue
                    posed[n]=s
                    # Positive overlap with actual parent is never a clamp mate.
                    bb=s.BoundBox;pb=parent.BoundBox
                    if previous is None and bb.XMin<pb.XMax and bb.XMax>pb.XMin and bb.YMin<pb.YMax and bb.YMax>pb.YMin and bb.ZMin<pb.ZMax and bb.ZMax>pb.ZMin:
                        volume=s.common(parent).Volume
                        if volume>1e-5:errors.append(dict(part=n,parent_overlap_mm3=volume))
                pad=posed[f'TopClampPad{i}']
                area=next(r['actual_top_contact_mm2'] for r in previous['bearings'] if r['clamp']==i) if previous else sum(a.common(b).Area for a in faces(pad,38.52) for b in faces(parent,38.52))
                bearings.append(dict(clamp=i,actual_top_contact_mm2=area))
                if area<60:errors.append(dict(clamp=i,insufficient_actual_bearing=area))
            if previous:errors=previous['errors']
            receipts.append(dict(ref=ref,axis_X_mm=x,bearings=bearings,errors=errors))
            if errors:continue
            points=np.vstack([cloud(s) for s in posed.values()]);rows=[dict(name=n,clamp=records[n]['clamp']) for n in posed]
            choices.append(dict(ref=ref,anchor_source=True,axis_X_mm=x,source_axis_X_mm=originalx,
                clamp_indices=list(indices),actual_parts=rows,bearing_receipts=bearings,
                actual_parent_no_positive_overlap_verified=True,
                driver_stage='Tighten lower carrier before bank/WAGO/boards; not in-situ quick service',
                carrier_bore_and_washer_seat_subtractions_required=True,
                parent_P0_not_deleted_or_drilled=True,new_bought_parts=0,
                points=points,radii=np.zeros(len(points)),types=np.full(len(points),7),
                boxes=[],wires=[],bounds=np.array([points.min(0),points.max(0)])))
        result[ref]=choices
    pins={**reader.hashes,**{p.relative_to(ROOT).as_posix():sha(p) for p in (proofpath,bundle,__import__('pathlib').Path(__file__))}}
    return result,receipts,pins
