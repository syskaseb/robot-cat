"""Fresh relocated whole-robot E1 geometry, links and native joint audit."""
from pathlib import Path
import json,sys,tempfile,shutil,math,time
import pilot
import author_ears as task
import integrate_tail_cartridge as previous
from validate_ears import common,write

def files():
    return [task.TARGET,task.MODULE,previous.MODULE]+[p for p in previous.old_files() if p!=pilot.TARGET]

def hashes():
    return {p.relative_to(pilot.ROOT).as_posix():pilot.sha(p) for p in files()}

def close(A):
    for n in list(A.listDocuments()):A.closeDocument(n)

def native(A,d,plan):
    asm=d.getObject('RobotCatAssembly24');sim=d.getObject('RobotConnectionTest35')
    wrappers={r['name']:d.getObject('Rigid_'+r['name']) for r in plan['components']}
    initial={n:w.Placement.copy() for n,w in wrappers.items()}
    refs={}
    for n in wrappers:
        s=pilot.global_shape(d.getObject(n));count=len(s.Vertexes)
        refs[n]=(s.Placement,{i:s.getElement('Vertex'+str(i)).Point for i in sorted({1,max(1,count//2),count})})
    temp=sum('TEMP' in d.getObject(r['name']).DesignStatus.upper() for r in plan['joints'])
    assert len(wrappers)==335 and len(plan['joints'])==334 and temp==25
    for r in plan['joints']:
        j=d.getObject(r['name']);assert j.JointType==r['type']
        assert j.Reference1[0]==wrappers[r['parent']] and j.Reference2[0]==wrappers[r['child']]
    rows=[];peaks={}
    try:
        asm.generateSimulation(sim);assert asm.numberOfFrames()==22
        for i in range(22):
            asm.updateForFrame(i);gap=fixed=axis=error=0.
            for r in plan['joints']:
                j=d.getObject(r['name']);p=j.Reference1[0].Placement*j.Placement1;q=j.Reference2[0].Placement*j.Placement2
                gap=max(gap,(p.Base-q.Base).Length);theta=(p.Rotation.inverted()*q.Rotation).Angle
                if r['type']=='Fixed':fixed=max(fixed,theta)
                else:
                    axis=max(axis,p.Rotation.multVec(A.Vector(0,0,1)).getAngle(q.Rotation.multVec(A.Vector(0,0,1))))
                    peaks[r['name']]=max(peaks.get(r['name'],0),math.degrees(theta))
            for n,w in wrappers.items():
                s=pilot.global_shape(d.getObject(n));place,pts=refs[n]
                assert s.Placement.isSame(w.Placement*place,1e-5),n
                for k,v in pts.items():error=max(error,(s.getElement('Vertex'+str(k)).Point-w.Placement.multVec(v)).Length)
            assert max(gap,fixed,axis,error)<1e-5
            rows.append(dict(frame=i,gap_mm=gap,fixed_rad=fixed,axis_rad=axis,geometry_mm=error))
            print('E1 native frame',i,flush=True)
        assert len(peaks)==13 and abs(peaks['Rev_TailYaw29']-30)<1e-5
        assert all(abs(v-3)<1e-5 for n,v in peaks.items() if n!='Rev_TailYaw29')
    finally:
        for n,p in initial.items():wrappers[n].Placement=p
        d.recompute();assert asm.solve()==0
    assert all(w.Placement.isSame(initial[n],1e-5) for n,w in wrappers.items())
    return dict(frames=rows,peaks_deg=peaks,restored=True,components=335,fixed=321,revolute=13,temporary=temp,
                limitation='Head-to-neck motion remains an inherited TEMP fixed lock. This tests native kinematics, not dynamics.')

def main():
    import FreeCAD as A,Part
    assert not A.GuiUp and not A.listDocuments()
    sys.path.insert(0,str(Path(A.getHomePath())/'Mod/Assembly'))
    sys.path.insert(0,str(pilot.ROOT/'tools/freecad/skorupa'))
    from inheritance30 import compare_text
    from tail_module import compare_boolean_history,mappings
    oldplan=json.loads((previous.OUT/'assembly-plan.json').read_text())
    plan=json.loads((task.OUT/'assembly-plan.json').read_text())
    inherited={r['name'] for r in oldplan['components']}-{'EarL','EarR','EarInsetL','EarInsetR','HeadRear'}
    assert len(inherited)==324
    old=pilot.document(A,task.PREDECESSOR)
    expected={n:pilot.global_shape(old.getObject(n)).cleaned().exportBrepToString() for n in inherited}
    oldj={r['name']:(str(old.getObject(r['name']).Placement1),str(old.getObject(r['name']).Placement2)) for r in oldplan['joints'] if r['child'] not in ['EarL','EarR','EarInsetL','EarInsetR']}
    close(A);print('Predecessor serialized and closed',flush=True)
    original=hashes()
    with tempfile.TemporaryDirectory(prefix='robot-cat-ears-') as tmp:
        root=Path(tmp)
        for p in files():
            dest=root/p.relative_to(pilot.CAD);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
        d=pilot.document(A,root/task.TARGET.relative_to(pilot.CAD));d.recompute()
        docs=list(A.listDocuments().values())
        assert len(docs)==11 and all(Path(o.FileName).resolve().is_relative_to(root) for o in docs),[(o.Name,o.FileName) for o in docs]
        assert not any('Invalid' in o.State for doc in docs for o in doc.Objects)
        comparison=[];shapes={r['name']:pilot.global_shape(d.getObject(r['name'])) for r in plan['components']}
        for n in sorted(inherited):
            s=shapes[n]
            try:r=compare_text(expected[n],s.cleaned().exportBrepToString())
            except AssertionError:
                allowed={name for name,(owner,_,_) in mappings().items() if owner=='tail/TailSupport'}|set(previous.ADDED)|set(previous.REPLACEMENTS)
                assert n in allowed,n
                oldshape=Part.Shape();oldshape.importBrepFromString(expected[n]);r=compare_boolean_history(oldshape,s)
            comparison.append({'name':n,**r})
        for n,frames in oldj.items():assert frames==(str(d.getObject(n).Placement1),str(d.getObject(n).Placement2))
        print('324 inherited parts and joint frames unchanged',flush=True)
        links=[]
        for r in plan['components']:
            o=d.getObject(r['name'])
            if o.TypeId=='App::Link':
                src=o.LinkedObject;path=Path(src.Document.FileName).resolve();assert path.is_relative_to(root)
                links.append(dict(name=o.Name,owner=path.relative_to(root).as_posix(),source=src.Name))
        assert len(links)==65
        module=d.getObject('EarL').LinkedObject.Document
        for name,src in {'EarL':'EarL','EarR':'EarR','HeadRear':'RearHead',**{n:n for n in task.FASTENERS}}.items():
            compare_text(shapes[name].cleaned().exportBrepToString(),module.getObject(src).Shape.cleaned().exportBrepToString())
        # New geometry against the existing robot; old invalid-shell results
        # remain limited-scope rather than promoted to a strict clearance proof.
        contacts=[];candidates=[]
        for n in ['EarL','EarR']+task.FASTENERS:
            box=shapes[n].optimalBoundingBox(False,False)
            for other in sorted(inherited):
                if not box.intersect(shapes[other].BoundBox):continue
                obox=shapes[other].optimalBoundingBox(False,False)
                if not box.intersect(obox):continue
                vol=common(shapes[n],shapes[other]);candidates.append([n,other,vol])
                if vol>1e-4:contacts.append([n,other,vol])
        assert not contacts,contacts
        # Link propagation into all three mating parts in a relocated assembly.
        var=d.getObject('EarInterface').LinkedObject;v=var.HoleRadius
        before={n:shapes[n].Volume for n in ['EarL','EarR','HeadRear']}
        try:
            var.HoleRadius=1.3;module.recompute();d.recompute()
            deltas={n:pilot.global_shape(d.getObject(n)).Volume-b for n,b in before.items()}
            assert all(v<-.001 for v in deltas.values())
        finally:var.HoleRadius=v;module.recompute();d.recompute()
        motion=native(A,d,plan)
        report=dict(file_sha256=original,tool_sha256=pilot.sha(Path(__file__)),fresh_process=True,relocated_documents=11,
                    outside_dependencies=False,links=links,geometry_comparison=comparison,unchanged_joint_frames=len(oldj),
                    collision_candidates=candidates,new_intersections=contacts,linked_hole_parameter_delta_mm3=deltas,
                    native=motion,print_ready=False,cad_saved=False,legacy_head_bop_passed=False)
        close(A)
    assert hashes()==original
    write('assembly.json',report)
    print('E1 whole-robot prototype checks passed; inherited geometry gate remains FAIL',flush=True)

if __name__=='__main__':main()
