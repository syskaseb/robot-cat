"""Editable common-space reservation and honest current-robot overlays.

The loft is a planning envelope, not a selected printable shell. Existing
supports/wires remain visible in overlays; native parts are not silently cut.
"""
import json
import math
import pickle
import time
from pathlib import Path

import FreeCAD as A
import Part
import Sketcher
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from check_main_p0_placement import ROOT, sha
from plan_feline_layout import BASE, OUT, MODEL, transforms, apply, STAGES

STATIONS = [(-141.5,100,158),(-112,196,158),(-65,196,158),
            (10,180,158),(55,166,158),(112,188,158),(158,132,158),(183.5,40,100)]
PROFILE_EXPONENT = 4.0
PROFILE_FAMILY = 'rounded_p4_back_flat_R12_belly'


def section_coefficients(width=196,height=158):
    a=np.linspace(0,math.pi,9)
    y=np.sign(np.cos(a))*abs(np.cos(a))**(2/PROFILE_EXPONENT)*width/2
    z=abs(np.sin(a))**(2/PROFILE_EXPONENT)*height/2
    radius=min(12,width/4,height/4)
    points=list(zip(y,z));points.append((-width/2,-height/2+radius))
    for angle in (210,240,270):
        t=math.radians(angle)
        points.append((-width/2+radius+radius*math.cos(t),-height/2+radius+radius*math.sin(t)))
    points.append((width/2-radius,-height/2))
    for angle in (300,330,360):
        t=math.radians(angle)
        points.append((width/2-radius+radius*math.cos(t),-height/2+radius+radius*math.sin(t)))
    points=np.array(points)
    return points[:,0]/(width/2),points[:,1]/(height/2)


def build(center_z,pad_tip):
    doc=A.newDocument('FelineLayoutEnvelope')
    try:
        params=doc.addObject('Spreadsheet::Sheet','Parameters')
        for row,(label,value) in enumerate((('Width','196 mm'),('Height','158 mm'),
                ('CenterZ',f'{center_z} mm'),('BellyPadTip',f'{pad_tip} mm')),1):
            params.set(f'A{row}',label);params.set(f'B{row}',value);params.setAlias(f'B{row}',label)
        body=doc.addObject('PartDesign::Body','TorsoEnvelope')
        body.Label='Tułów: rezerwacja przestrzeni, nie gotowa skorupa'
        sections=[]
        for j,(x,width,height) in enumerate(STATIONS):
            sk=doc.addObject('Sketcher::SketchObject',f'CrossSection{j}')
            body.addObject(sk)
            sk.Placement=A.Placement(A.Vector(x,0,center_z),A.Rotation(A.Vector(1,1,1),120))
            sk.setExpression('Placement.Base.z','Parameters.CenterZ')
            cos,sin=section_coefficients(width,height);count=len(cos)
            points=[A.Vector(float(c*width/2),float(s*height/2),0) for c,s in zip(cos,sin)]
            for i in range(count): sk.addGeometry(Part.LineSegment(points[i],points[(i+1)%count]),False)
            for i in range(count): sk.addConstraint(Sketcher.Constraint('Coincident',i,2,(i+1)%count,1))
            for i,(c,s) in enumerate(zip(cos,sin)):
                k=sk.addConstraint(Sketcher.Constraint('DistanceX',i,1,float(c*width/2)))
                sk.setExpression(f'Constraints[{k}]',f'Parameters.Width * {c*width/392:.12g}')
                k=sk.addConstraint(Sketcher.Constraint('DistanceY',i,1,float(s*height/2)))
                sk.setExpression(f'Constraints[{k}]',f'Parameters.Height * {s*height/316:.12g}')
            sections.append(sk)
        doc.recompute()
        loft=body.newObject('PartDesign::AdditiveLoft','SharedEnvelope')
        loft.Profile=sections[0];loft.Sections=sections[1:];loft.Ruled=True
        doc.recompute()
        assert all(sk.FullyConstrained for sk in sections)
        assert body.Shape.isValid() and len(body.Shape.Solids)==1
        shape=body.Shape.copy();volume=shape.Volume
        params.set('B1','198 mm');doc.recompute()
        changed=body.Shape.copy()
        assert changed.isValid() and changed.BoundBox.YLength>shape.BoundBox.YLength+1.99
        params.set('B1','196 mm');doc.recompute()
        assert abs(body.Shape.Volume-volume)<1e-4
        # Pad footprints and load columns are reservations only. Exact frame
        # attachment/fastener/layer checks follow the shared-space gate.
        for index,(x,y) in enumerate(((-75.5,-40),(-75.5,40),(117.5,-40),(117.5,40))):
            pad=doc.addObject('Part::Cylinder',f'BellyPadReservation{index+1}')
            pad.Label=f'Podpora brzucha {index+1}: rezerwacja do ramy'
            pad.Radius=9;pad.Height=-pad_tip
            pad.Placement.Base=A.Vector(x,y,pad_tip)
            pad.setExpression('Height','-Parameters.BellyPadTip')
            pad.setExpression('Placement.Base.z','Parameters.BellyPadTip')
        doc.recompute()
        path=OUT/'FelineLayoutEnvelope.FCStd';doc.saveAs(str(path))
        return dict(native=path.relative_to(ROOT).as_posix(),sha256=sha(path),
            dimensions_mm=[shape.BoundBox.XLength,shape.BoundBox.YLength,shape.BoundBox.ZLength],
            center_z_mm=center_z,sections=STATIONS,fully_constrained_sketches=len(sections),
            cross_section_exponent=PROFILE_EXPONENT,
            profile_family=PROFILE_FAMILY,
            solids=len(shape.Solids),valid=shape.isValid(),volume_mm3=volume,
            width_parameter_test_mm=[196,198,196],pad_tip_z_mm=pad_tip,
            readiness='concept',shell_wall_thickness_verified=False,printable_panels_built=False)
    finally:
        A.closeDocument(doc.Name)


def render(meshes,report,index,filename):
    pose=report['poses'][index];drop=pose['body_drop_mm']
    data=json.loads((ROOT/'hardware/simulation/p0/e6-leg-compatibility.json').read_text())
    member_transforms={}
    for code,groups in report['membership'].items():
        axes=[next(a for a in data['axes'] if a['code']==code and a['stage']==stage) for stage in STAGES]
        tf=transforms(axes,pose['legs'][code]['angles_delta_degrees'])
        for stage,transform in zip(STAGES,tf):
            for name in groups[stage]:member_transforms[name]=transform
    fig,axs=plt.subplots(1,3,figsize=(18,7),dpi=145)
    views=[('PRZÓD',np.array([[0,0,-1],[1,0,0],[0,1,0]])),
           ('BOK',np.array([[-1,0,0],[0,0,1],[0,1,0]])),
           ('GÓRA',np.array([[-1,0,0],[0,1,0],[0,0,-1]]))]
    for ax,(title,basis) in zip(axs,views):
        polygons=[];colors=[];depth=[]
        for name,(triangles,color,kind) in meshes.items():
            t=triangles[::max(1,len(triangles)//1800)] if kind=='surface' else triangles
            if name in member_transforms: t=apply(t.reshape(-1,3),member_transforms[name]).reshape(t.shape)
            t=t.copy();t[:,:,2]-=drop
            p=t@basis
            if kind=='curve':
                ax.plot(p[:,:,:2].reshape(-1,2)[:,0],p[:,:,:2].reshape(-1,2)[:,1],
                    color='#d97928',lw=.28,alpha=.65,zorder=2)
            else:
                polygons.append(p[:,:,:2]);depth.append(p[:,:,2].mean(1))
                colors.append(np.tile(color*.85,(len(p),1)))
        triangles=np.concatenate(polygons);d=np.concatenate(depth);c=np.concatenate(colors)
        order=np.argsort(d)
        ax.add_collection(PolyCollection(triangles[order],facecolors=c[order],edgecolors='none',rasterized=True))
        for x,width,height in STATIONS:
            cos,sin=section_coefficients(width,height)
            cos=np.r_[cos,cos[0]];sin=np.r_[sin,sin[0]]
            world=np.column_stack((np.full(len(cos),x),cos*width/2,
                report['envelope_center_z_mm']+sin*height/2-drop))
            projected=world@basis
            ax.plot(projected[:,0],projected[:,1],color='#147ba9',lw=.8,zorder=3)
        for k in (0,4,8,12):
            world=np.array([[x,section_coefficients(w,h)[0][k]*w/2,report['envelope_center_z_mm']+section_coefficients(w,h)[1][k]*h/2-drop]
                            for x,w,h in STATIONS])
            p=world@basis;ax.plot(p[:,0],p[:,1],color='#147ba9',lw=1,zorder=3)
        if title!='GÓRA':ax.axhline(report['ground_rest_z_mm'],color='#303438',lw=1)
        ax.autoscale_view();ax.set_aspect('equal');ax.grid(alpha=.15)
        ax.set_title(title);ax.set_xlabel('mm');ax.set_ylabel('mm')
    fig.suptitle(f'Kot Oli: wspólna przestrzeń | opuszczenie tułowia {drop:.1f} mm',fontsize=16)
    fig.text(.5,.04,'Szare/pomarańczowe: aktualna geometria i przewody. Niebieski: projektowany obrys. Wszystkie części pokazane.',ha='center',fontsize=10)
    fig.text(.5,.015,'Widok planistyczny. Przewody pokazane w spoczynku; relokacje, ruch wiązek i prześwity pozostają OPEN.',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.07,1,.94));path=OUT/filename
    fig.savefig(path,facecolor='white');plt.close(fig)
    return path.relative_to(ROOT).as_posix()


def main():
    tick=time.monotonic()
    report=json.loads((OUT/'motion-layout.json').read_text())
    assert all(sha(ROOT/n)==h for n,h in report['source_sha256'].items())
    # Select a modest usable prefix, not the rejected deepest IK sample.
    index=max(i for i,p in enumerate(report['poses']) if p['body_drop_mm']<=95
              and all(l['foot_fit_error_mm']<=.02 and not l['mesh_floor_intrusions'] for l in p['legs'].values()))
    ground_local=report['ground_rest_z_mm']+report['poses'][index]['body_drop_mm']
    center=32.0
    native=build(center,ground_local)
    doc=A.openDocument(str(ROOT/native['native']))
    try:
        assert doc.getObject('TorsoEnvelope').Shape.isValid()
        assert abs(doc.getObject('TorsoEnvelope').Shape.Volume-native['volume_mm3'])<1e-4
        native['fresh_reopen_verified']=True
    finally:A.closeDocument(doc.Name)
    meshes={}
    with (BASE/'phase1-prototype-final/preview/triangulation-cache.pkl').open('rb') as f:
        pickle.load(f)
        while True:
            try:name,m=pickle.load(f)
            except EOFError:break
            meshes[name]=m
    report['envelope_center_z_mm']=center
    import sys
    views=[] if '--native-only' in sys.argv else [render(meshes,report,0,'standing-layout.png'),render(meshes,report,index,'lying-layout.png')]
    result=dict(status='COMMON_SPACE_CANDIDATE_NOT_SELECTED',selected=False,
        baseline_tag='phase1-open-prototype-100-2026-10-17',reference='hardware/reference/appearance/ola-cat-reference.jpg',
        source_sha256=report['source_sha256'],native=native,views=views,planning_pose_index=index,
        drop_mm=report['poses'][index]['body_drop_mm'],floor_screen='Sampled mesh only; foot residual<=0.02mm and floor intrusions absent in selected prefix.',
        physical_pass=False,full_wiring_complete=False,exact_motion_clearance=False,
        remaining=['Remove/refactor outboard galleries and upper carrier branches',
          'Allocate whole electronics/connectors/bank and complete bundles within loft',
          'Exact leg/body/support/shell moving checks including joint limits',
          'Pad-to-frame fasteners and load path','Four printable torso panels and neck shields'],
        worker_seconds=round(time.monotonic()-tick,3))
    (OUT/'layout-checkpoint.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:result[k] for k in ('status','drop_mm','views','worker_seconds')}),flush=True)


if __name__=='__main__':main()
