"""Whole protected0242.100UAT1 pigtail, not a FHAC replacement.

Source sleeve and all five wire/reference shapes move rigidly together.
Both independent9mm restraints use the existing straight BEFORE each arc;
old after-turn9 remains wire geometry, not an extra mandatory grip.
"""
import hashlib
import itertools
import json
import math
import zipfile
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from plan_feline_joint_fore_domains import cloud
from feline_flat_station_templates import box_points


def candidates():
    path=OUT/'n01-coupled-clocked-joints.json';doc=json.loads(path.read_text())
    bundle=ROOT/doc['bundle'];assert sha(bundle)==doc['bundle_sha256']
    shapes={}
    with zipfile.ZipFile(bundle) as z:
        for row in doc['parts']:
            if row['group']!='F_PWM':continue
            blob=z.read(row['entry']);assert hashlib.sha256(blob).hexdigest()==row['sha256']
            s=Part.Shape();s.importBrepFromString(blob.decode());assert s.isValid() and s.Solids
            shapes[row['name']]=s
    assert len(shapes)==5
    body=shapes['F_PWM:case'];bb=body.BoundBox;c=np.array(list(bb.Center))
    assert np.allclose([bb.XLength,bb.YLength,bb.ZLength],[42,6.4,6.4])
    sourcechunks=[cloud(s) for s in shapes.values()]
    source=np.vstack(sourcechunks)
    sourcetypes=np.concatenate([np.full(len(p),5 if n=='F_PWM:case' else 1) for n,p in zip(shapes,sourcechunks)])
    heads=[];grips=[]
    for sign in (-1,1):
        q=c+np.array([21*sign,0,0]);d=np.array([sign,0.,0.]);rr=1.55
        wire=shapes['F_PWM:'+('in' if sign<0 else 'out')+'_first_bend']
        assert any(type(f.Surface).__name__=='Cylinder' and abs(f.Surface.Radius-rr)<1e-5
            and abs(f.Surface.Axis.x)>.999 for f in wire.Faces)
        cap=[];band=[]
        for angle in np.linspace(0,2*math.pi,17)[:-1]:
            u=np.array([0,math.cos(angle),math.sin(angle)])
            cap.extend([q+k*d+(rr+2)*u for k in np.linspace(0,9,6)])
            band.extend([q+k*d+(rr+3.2)*u for k in (3.25,4.5,5.75)])
        grips.extend(cap);grips.extend(band)
        heads.append([box_points(q+4.5*d+np.array([0,0,h*(rr+6.2)])-3,
                                q+4.5*d+np.array([0,0,h*(rr+6.2)])+3) for h in (-1,1)])
    grips=np.array(grips);rows=[]
    for x,side,z,head0,head1 in itertools.product(range(-100,117,24),(-1,1),(40,48,56),(0,1),(0,1)):
        rot=np.array([[0,0,-side],[0,side,0],[1,0,0.]])
        assert abs(np.linalg.det(rot)-1)<1e-7
        target=np.array([x,side*75,z]);points=(np.vstack((source,grips,heads[0][head0],heads[1][head1]))-c)@rot.T+target
        types=np.r_[sourcetypes,np.full(len(grips)+len(heads[0][head0])+len(heads[1][head1]),2)]
        rows.append(dict(ref='F_PWM_whole',f_pwm_source=True,source_selected_fuse='0242.100UAT1',
            source_sleeve_design_envelope_mm=[42,6.4,6.4],source_case_is_sleeve_not_FHAC=True,
            source_body_and_all5_wire_shapes_rigid_preserved=True,
            source_centre_mm=c.tolist(),centre_mm=target.tolist(),rotation_rows=rot.tolist(),
            two_complete_grips_mm=9,grip_site='Existing first9 BEFORE arc; both old after-turn9 wires remain',
            cap_wall_mm=2,full_band_wall_budget_mm=1.2,full_head_budget_mm=[6,6,6],head_choices=[head0,head1],
            cap_roots_and_service_on_bench_STILL_OPEN=True,
            points=points,radii=np.zeros(len(points)),types=types,boxes=[],wires=[],
            bounds=np.array([points.min(0),points.max(0)])))
    pins={p.relative_to(ROOT).as_posix():sha(p) for p in
        (path,bundle,Path(__file__),ROOT/'tools/electronics/pwm_fused_pigtail_r1.py')}
    return {'F_PWM_whole':rows},pins
