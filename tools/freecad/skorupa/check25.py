"""Audit the MCP-built flat guard, its fasteners and service/motion envelope.

Uses an independent headless FreeCAD process; never changes v24.
"""
from pathlib import Path
import json,math
import FreeCAD as A
import Part,MeshPart
from collections import Counter
from probe21 import world,visible_names
from build22 import sha,V,cyl,hexagon,ANCHORS,union

ROOT=Path(__file__).resolve().parents[3]; OUT=ROOT/'hardware/skorupa/v25'
SOURCE=ROOT/'hardware/skorupa/v24/Kot_v24_ASSEMBLY.FCStd'
CHANGED=['Belly22']+['BellyScrew'+key for x,y,key in ANCHORS]

def main():
    source=A.openDocument(str(SOURCE)); vis=visible_names(SOURCE)
    targets={o.Name:world(o) for o in source.Objects if o.Name in vis and o.isDerivedFrom('Part::Feature') and not o.Shape.isNull() and o.Name not in CHANGED}
    design=A.openDocument(str(OUT/'BellyDesign25.FCStd')); guard=world(design.getObject('Belly25'))
    sketches=[dict(name=o.Name,fully_constrained=o.FullyConstrained) for o in design.Objects if o.TypeId=='Sketcher::SketchObject']
    assert len(sketches)==3 and all(r['fully_constrained'] for r in sketches)
    shapes={'Belly22':guard}; report=dict(source_sha256=sha(SOURCE),sketches=sketches,parts=[],collisions=[],bearings=[],tool_collisions=[],removal_samples=[],motion_samples=[],
        scope='Changed guard and fasteners only. Sampled kinematics, not full gait/strength/thermal certification. Battery service remains unresolved.')
    for x,y,key in ANCHORS:
        # Max-head ISO10642 envelope. Length includes head, unlike socket cap screws.
        shapes['BellyScrew'+key]=union([Part.makeCone(3.36,1.5,1.86,V(x,y,-5.7)),cyl(1.5,14.14,V(x,y,-3.84))])
    for n,s in shapes.items():
        assert s.isValid() and len(s.Solids)==1 and s.Volume>0,n
        s.check(True); p=OUT/(('Belly25' if n=='Belly22' else n+'25')+'.brep');s.exportBrep(str(p))
        report['parts'].append(dict(source_name=n,file=p.name,sha256=sha(p),volume_mm3=s.Volume,valid=True,solids=1))
        for other,t in targets.items():
            if s.BoundBox.intersect(t.BoundBox):
                v=s.common(t).Volume
                if v>.001: report['collisions'].append([n,other,v])
        print('Static test',n,flush=True)
    for i,(n,s) in enumerate(shapes.items()):
        for other,t in list(shapes.items())[i+1:]:
            if s.BoundBox.intersect(t.BoundBox):
                v=s.common(t).Volume
                if v>.001: report['collisions'].append([n,other,v])
    def bearing(label,s,test):
        f=s.common(test).Volume/test.Volume
        report['bearings'].append(dict(check=label,material_fraction=f))
        assert f>.99,(label,f)
    for x,y,key in ANCHORS:
        rail=targets['SideLeft22' if y>0 else 'SideRight22']
        ring=lambda z:cyl(5.4,.1,V(x,y,z)).cut(cyl(1.8,.1,V(x,y,z)))
        bearing(key+' plate pad',guard,ring(-2.1))
        bearing(key+' rail pad',rail,ring(-2))
        bearing(key+' nut support',rail,hexagon(5.5,.1,V(x,y,6.2)).cut(cyl(1.7,.1,V(x,y,6.2))))
        # Thin conical band immediately outside the nominal screw's seating surface.
        band=Part.makeCone(3.3,2.1,1.2,V(x,y,-5.54)).cut(Part.makeCone(3.2,2,1.2,V(x,y,-5.54)))
        bearing(key+' conical head seat',guard,band)
        tool=cyl(2,30,V(x,y,-35.9))
        for n,t in targets.items():
            if tool.BoundBox.intersect(t.BoundBox):
                v=tool.common(t).Volume
                if v>.001: report['tool_collisions'].append([key,n,v])
    # Guard only, after screws are removed. Test the simple vertical path first.
    for dz in [.1,.5,1,2,5,10,15,20,30,40,60,80]:
        s=guard.copy();s.translate(V(0,0,-dz));hits=[]
        for n,t in targets.items():
            if s.BoundBox.intersect(t.BoundBox):
                v=s.common(t).Volume
                if v>.001:hits.append([n,v])
        report['removal_samples'].append(dict(down_mm=dz,collisions=hits))
        print('Removal down',dz,hits,flush=True)
    old=world(source.getObject('Belly22'))
    report['comparison']=dict(old_guard_volume_mm3=old.Volume,new_guard_volume_mm3=guard.Volume,
        solid_volume_reduction_percent=100*(1-guard.Volume/old.Volume),old_height_mm=old.BoundBox.ZLength,new_height_mm=guard.BoundBox.ZLength,
        old_lowest_screw_z_mm=-9.5,new_guard_bottom_z_mm=-5.9,new_lowest_screw_z_mm=-5.7,underbody_clearance_gain_mm=3.6,
        plate_thickness_mm=2.4,mount_pad_total_thickness_mm=3.9)
    report['connections']=[dict(name=key,axis_mm=[x,y],screw='M3x16 ISO10642',head_max_diameter_mm=6.72,head_height_mm=1.86,
        countersink_mouth_mm=7.12,countersink_depth_mm=1.86,head_recess_mm=.2,tip_z_mm=10.3,nut_top_z_mm=8.7,nominal_tip_protrusion_mm=1.6) for x,y,key in ANCHORS]
    report['clearances']=[dict(neighbor=n,gap_mm=guard.distToShape(targets[n])[0]) for n in ['Battery','BatteryCarrier23','Part__Feature005','BatteryScrewFrontL']]
    # Source angles and rigid-stage membership match the native v24 simulation.
    plan=json.loads((ROOT/'hardware/skorupa/v24/assembly-plan.json').read_text(encoding='utf-8'))
    stages={p['name']:p['stage'] for p in plan['components']}
    for frame in range(21):
        phase=math.sin(2*math.pi*frame/20);transforms={};hits=[]
        for code in ['FR','FL','RR','RL']:
            chain=A.Placement(); angle=(3 if code in ['FR','RL'] else -3)*phase
            for suffix in ['Hip','Knee','Ankle']:
                axis=next(a for a in plan['axes'] if a['code']==code and a['stage']==suffix)
                local=A.Placement(V(),A.Rotation(V(*axis['axis']),angle),V(*axis['pivot_mm']))
                chain=chain*local;transforms['Motion_'+code+'_'+suffix]=chain
        for n,original in targets.items():
            if stages[n] not in transforms: continue
            s=original.copy();s.Placement=transforms[stages[n]]*s.Placement
            for other,t in shapes.items():
                if s.BoundBox.intersect(t.BoundBox):
                    v=s.common(t).Volume
                    if v>.001:hits.append([n,other,v])
        report['motion_samples'].append(dict(frame=frame,peak_command_deg=3*phase,collisions=hits))
        print('Motion sample',frame,hits,flush=True)
    mesh=MeshPart.meshFromShape(Shape=guard,LinearDeflection=.05,AngularDeflection=.15,Relative=False)
    vertices,faces=mesh.Topology
    edges=Counter(tuple(sorted((a,b))) for f in faces for a,b in ((f[0],f[1]),(f[1],f[2]),(f[2],f[0])))
    assert all(v==2 for v in edges.values()) and mesh.isSolid()
    b=mesh.BoundBox; dims=[b.XLength,b.YLength,b.ZLength]
    assert dims[0]+16<256 and dims[1]+16<256 and dims[2]<256
    m=A.Matrix();m.move(V(-b.XMin,-b.YMin,-b.ZMin));mesh.transform(m)
    target=OUT/'stl-prototype';target.mkdir(exist_ok=True);mesh.write(str(target/'Belly25.stl'))
    report['print']=dict(size_mm=dims,triangles=len(faces),mesh_is_solid=True,non_manifold_edges=0,fits_256_with_8mm_brim=True,
        orientation='flat exterior down; verify 90-degree countersinks and PETG fit in slicer/coupon',stl_sha256=sha(target/'Belly25.stl'))
    (OUT/'validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report['comparison']),flush=True)
    assert not report['collisions'] and not report['tool_collisions'],report['collisions']
    assert all(not r['collisions'] for r in report['removal_samples']),report['removal_samples']
    assert all(not r['collisions'] for r in report['motion_samples']),report['motion_samples']
    print('PASS',flush=True)

if __name__=='__main__':main()
