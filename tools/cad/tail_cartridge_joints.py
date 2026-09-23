"""Explicit datum-frame native Fixed joints: MCP face-only mating cannot retain these frames."""
import json
from pathlib import Path
import sys
import pilot
from tail_cartridge_service import OUT,TARGET,PRINTS

PARTS=PRINTS+[f'Cartridge{k}{i}' for k in ('Bolt','Nut') for i in range(4)]


def author():
    import FreeCAD as A
    assert A.GuiUp
    sys.path.insert(0,str(Path(A.getHomePath())/'Mod/Assembly'))
    import JointObject
    d=A.ActiveDocument
    assert d.Name=='TailCartridgeService'
    asm=d.getObject('CartridgeBenchAssembly');group=d.getObject('Joints')
    assert asm and group and len(group.Group)==1
    before={n:d.getObject(n).Placement for n in PARTS}
    for name in PARTS[1:]:
        parent=d.getObject('SupportedRoot34' if name.startswith('CartridgeNut') else 'LowerRetainerPETG')
        child=d.getObject(name)
        joint=group.newObject('App::FeaturePython','Fix_'+name)
        JointObject.Joint(joint,0)
        joint.Detach1=True;joint.Detach2=True
        joint.Reference1=(parent,['','']);joint.Reference2=(child,['',''])
        datum=A.Placement(A.Vector(171,-6,94),A.Rotation())
        joint.Placement1=parent.Placement.inverse()*datum
        joint.Placement2=child.Placement.inverse()*datum
        joint.addProperty('App::PropertyString','DesignStatus','Traceability')
        joint.DesignStatus='Bench model of four nominal M2x10 bolted stack; not physical approval, not servo coupling'
        JointObject.ViewProviderJoint(joint.ViewObject);joint.Visibility=False
    asm.addProperty('App::PropertyString','DesignStatus','Traceability')
    asm.DesignStatus='11 parts, 10 Fixed, grounded lower retainer. Horn is an unjointed reference outside assembly. NOT INSTALLED.'
    d.recompute();result=asm.solve()
    print('solve',result)
    for n in PARTS:
        p=d.getObject(n).Placement
        assert (p.Base-before[n].Base).Length<1e-6
        assert abs((p.Rotation*before[n].Rotation.inverted()).Angle)<1e-6
    # Persist only the deliberately authored study.
    d.Label='Tail cartridge service R2 - BENCH ONLY';d.save()


def audit():
    import FreeCAD as A
    assert not A.GuiUp and not A.listDocuments()
    try:
        d=pilot.document(A,TARGET);asm=d.getObject('CartridgeBenchAssembly')
        assert asm and len(asm.Group)>=11
        joints=[o for o in d.getObject('Joints').Group if 'JointType' in o.PropertiesList]
        assert len(joints)==10 and all(str(j.JointType)=='Fixed' for j in joints)
        horn=d.getObject('CommunityHornEnvelope')
        assert horn not in asm.Group
        initial={n:d.getObject(n).Placement for n in PARTS}
        shapes={n:pilot.global_shape(d.getObject(n)) for n in PARTS}
        rows=[]
        for index,n in enumerate(PARTS[1:]):
            obj=d.getObject(n)
            obj.Placement=A.Placement(A.Vector(.8,-.5,.6),A.Rotation(A.Vector(0,0,1),3))*initial[n]
            d.recompute();result=asm.solve()
            errors={m:{'translation_mm':(d.getObject(m).Placement.Base-initial[m].Base).Length,
                       'rotation_rad':abs((d.getObject(m).Placement.Rotation*initial[m].Rotation.inverted()).Angle)} for m in PARTS}
            assert max(v['translation_mm'] for v in errors.values())<1e-5,errors
            assert max(v['rotation_rad'] for v in errors.values())<1e-5,errors
            rows.append({'perturbed_part':n,'solve_result':str(result),'max_translation_error_mm':max(v['translation_mm'] for v in errors.values()),'max_rotation_error_rad':max(v['rotation_rad'] for v in errors.values())})
        gaps=[]
        for j in joints:
            p=d.getObject(j.Reference1[0].Name).Placement*j.Placement1
            q=d.getObject(j.Reference2[0].Name).Placement*j.Placement2
            gaps.append({'joint':j.Name,'gap_mm':(p.Base-q.Base).Length,'rotation_rad':abs((p.Rotation*q.Rotation.inverted()).Angle)})
        assert all(r['gap_mm']<1e-5 and r['rotation_rad']<1e-5 for r in gaps)
        for n,s in shapes.items():
            restored=pilot.global_shape(d.getObject(n))
            assert restored.cut(s).Volume<1e-5 and s.cut(restored).Volume<1e-5
        report={'study_sha256':pilot.sha(TARGET),'tool_sha256':pilot.sha(Path(__file__)),
                'native_solver_tested':True,'parts':PARTS,'fixed_joints':10,'grounded':1,
                'joint_gaps':gaps,'perturbation_recovery':rows,'horn_jointed':False,
                'servo_motion_tested':False,'main_robot_changed':False,'print_ready':False,
                'scope':'Native solver retention of bolted bench stack, not MG92B actuation or physical assembly/strength approval.'}
        (OUT/'joint-audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8',newline='\n')
        print(json.dumps(report),flush=True)
    finally:
        for n in list(A.listDocuments()):A.closeDocument(n)


if __name__=='__main__':{'author':author,'audit':audit}[sys.argv[1]]()
