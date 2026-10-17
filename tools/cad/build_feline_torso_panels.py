"""One native four-panel torso candidate with a bounded dorsal arch.

No controls/leg holes are guessed here. Actual changed wall interfaces are
received next and define whole access bays, not per-contact micro-notches.
"""
import json,time
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part,Sketcher
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from build_feline_layout_envelope import STATIONS,section_coefficients

# Highest roof112 preserves the160mm envelope. No wider lateral belly.
# Roof budgets preserve current board/header heights; S0/S1 have deliberate
# control-aperture gates. Body floor remainsZ-48, lowWAGO bearing fit OPEN.
TOPS=[100,112,112,110,109,110,99,72]


def main():
    tick=time.monotonic();target=OUT/'FelineTorsoPanels.FCStd'
    assert not target.exists(),'Receive current panel candidate before rebuilding'
    doc=A.newDocument('FelineTorsoPanels');report=dict(status='BUILDING_TORSO_PANEL_CANDIDATE',
        selected=False,physical_pass=False,wall_interface_complete=False,parts=[])
    manifest=OUT/'torso-panels-native.json'
    def save():
        report['worker_seconds']=round(time.monotonic()-tick,3);manifest.write_text(json.dumps(report,indent=2)+'\n')
    try:
        p=doc.addObject('Spreadsheet::Sheet','Parameters')
        for i,(name,value) in enumerate([('Wall',2),('SeamGap',.4),('SplitX',21)],1):
            p.set(f'A{i}',name);p.set(f'B{i}',f'{value} mm');p.setAlias(f'B{i}',name)
        sketches=[]
        def loft(name,inner=False):
            body=doc.addObject('PartDesign::Body',name);sections=[]
            for j,((x,w,_),top) in enumerate(zip(STATIONS,TOPS)):
                height=top+48;center=(top-48)/2
                cy,cz=section_coefficients(w,height)
                coords=np.column_stack((cy*w/2,cz*height/2))
                offsets=np.zeros_like(coords)
                if inner:
                    for i,v in enumerate(coords):
                        e1=v-coords[i-1];e2=coords[(i+1)%len(coords)]-v
                        n1=np.array([-e1[1],e1[0]])/np.linalg.norm(e1)
                        n2=np.array([-e2[1],e2[0]])/np.linalg.norm(e2)
                        offsets[i]=np.linalg.solve(np.array([n1,n2]),[1,1])
                    if j==0:x-=3
                    if j==len(STATIONS)-1:x+=3
                sk=doc.addObject('Sketcher::SketchObject',name+'Section'+str(j));body.addObject(sk)
                sk.Placement=A.Placement(A.Vector(x,0,center),A.Rotation(A.Vector(1,1,1),120))
                points=coords+2*offsets
                vectors=[A.Vector(float(y),float(z),0) for y,z in points];count=len(points)
                for i in range(count):sk.addGeometry(Part.LineSegment(vectors[i],vectors[(i+1)%count]),False)
                for i in range(count):sk.addConstraint(Sketcher.Constraint('Coincident',i,2,(i+1)%count,1))
                for i in range(count):
                    for axis,kind in ((0,'DistanceX'),(1,'DistanceY')):
                        k=sk.addConstraint(Sketcher.Constraint(kind,i,1,float(points[i,axis])))
                        if inner:sk.setExpression(f'Constraints[{k}]',f'{coords[i,axis]:.15g} mm + Parameters.Wall * {offsets[i,axis]:.15g}')
                sections.append(sk);sketches.append(sk)
            doc.recompute();f=body.newObject('PartDesign::AdditiveLoft',name+'Loft')
            f.Profile=sections[0];f.Sections=sections[1:];f.Ruled=True
            doc.recompute();assert body.Shape.isValid() and len(body.Shape.Solids)==1
            return body
        outer=loft('OuterNative');inner=loft('InnerNative',True)
        shell=doc.addObject('Part::Cut','ShellWall');shell.Base=outer;shell.Tool=inner
        doc.recompute();assert shell.Shape.isValid() and len(shell.Shape.Solids)==1
        assert all(s.FullyConstrained for s in sketches)
        for front in (True,False):
            for left in (True,False):
                name=('Front' if front else 'Rear')+('Left' if left else 'Right')+'Panel'
                box=doc.addObject('Part::Box',name+'SplitTool');box.Height=170;box.Placement.Base.z=-50
                if front:
                    box.Placement.Base.x=-142;box.setExpression('Length','Parameters.SplitX - Parameters.SeamGap / 2 + 142 mm')
                else:
                    box.setExpression('Placement.Base.x','Parameters.SplitX + Parameters.SeamGap / 2')
                    box.setExpression('Length','184 mm - Parameters.SplitX - Parameters.SeamGap / 2')
                if left:
                    box.setExpression('Placement.Base.y','Parameters.SeamGap / 2');box.setExpression('Width','100 mm - Parameters.SeamGap / 2')
                else:
                    box.Placement.Base.y=-100;box.setExpression('Width','100 mm - Parameters.SeamGap / 2')
                ob=doc.addObject('Part::Common',name);ob.Base=shell;ob.Tool=box
                doc.recompute();s=ob.Shape;assert s.isValid() and len(s.Solids)==1,name
                assert not s.check(True),name
                b=s.BoundBox;assert max(b.XLength,b.YLength,b.ZLength)<=252,name
                report['parts'].append(dict(object=name,extents_mm=[b.XLength,b.YLength,b.ZLength],
                    volume_mm3=s.Volume,native_editable_dependencies=True))
                save()
        original={r['object']:doc.getObject(r['object']).Shape.Volume for r in report['parts']}
        p.set('B1','2.4 mm');doc.recompute()
        assert all(doc.getObject(n).Shape.isValid() and doc.getObject(n).Shape.Volume>v for n,v in original.items())
        p.set('B1','2 mm');doc.recompute()
        assert all(abs(doc.getObject(n).Shape.Volume-v)<1e-4 for n,v in original.items())
        for ob in (outer,inner,shell):
            ob.addProperty('App::PropertyString','ScopeStatus');ob.ScopeStatus='Candidate only; actual leg/control/service/mount interfaces still OPEN'
        doc.saveAs(str(target));doc_name=doc.Name;A.closeDocument(doc_name);doc=None
        d=A.openDocument(str(target))
        try:
            assert all(d.getObject(n).Shape.isValid() and abs(d.getObject(n).Shape.Volume-v)<1e-4 for n,v in original.items())
        finally:A.closeDocument(d.Name)
        report.update(status='FOUR_EDITABLE_TORSO_PANEL_CANDIDATES_CHANGED_INTERFACES_OPEN',
            native=target.relative_to(ROOT).as_posix(),native_sha256=sha(target),fresh_reopen=True,
            fully_constrained_sketches=len(sketches),wall_parameter_test_mm=[2,2.4,2],
            nominal_section_wall_mm=2,actual_minimum_3d_wall_not_yet_verified=True,
            roof_stations_x_z_mm=[[row[0],z] for row,z in zip(STATIONS,TOPS)],
            lowest_z_mm=-48,maximum_width_mm=196,maximum_envelope_height_mm=160,
            open=['Whole leg-motion openings','S0/S1 control access','Neck/tail closures',
                'Actual3D minimum thickness at longitudinal tapers','Frame mounting and seams',
                'Unchanged module cases and61known approaches vs new walls',
                'Full moving wiring and service'],
            exports_built=False,source_sha256={Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__)),
                'tools/cad/build_feline_layout_envelope.py':sha(ROOT/'tools/cad/build_feline_layout_envelope.py')})
        save();print(json.dumps(report),flush=True)
    except Exception as exc:
        report.update(status='TORSO_PANEL_CANDIDATE_INCOMPLETE',error=str(exc));save()
        if doc:doc.saveAs(str(OUT/'FelineTorsoPanels.partial.FCStd'))
        raise
    finally:
        if doc and doc.Name in A.listDocuments():A.closeDocument(doc.Name)


if __name__=='__main__':main()
