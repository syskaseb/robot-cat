"""Rounded, recessed PETG ears. Unsupported ellipse sketches / linked migration.

Interactive native lofts are authored with structured FreeCAD MCP tools.
Inherited rear-head geometry is a named reference, not a regenerated shell.
"""
from pathlib import Path
import json
import pilot

CAD=pilot.CAD
OUT=CAD/'validation/ears'
MODULE=CAD/'modules/head/HeadEars.FCStd'
TARGET=CAD/'assembly/RobotCatEars.FCStd'
PREDECESSOR=CAD/'assembly/RobotCatTailCartridge.FCStd'
OUTER=[(150,40,8,5),(164,34,18,8),(180,35,17,9),(196,40,11,7),(207.5,45.5,3.5,3),(210,46,1.5,1.4)]
INNER=[(177,35,3,7,-126),(184,36,11.5,12,-125),(196,41,7.5,10,-124),(204,45,2,6,-123.5)]

def prepare():
    import FreeCAD as A, Part
    assert not MODULE.exists()
    MODULE.parent.mkdir(parents=True,exist_ok=True); OUT.mkdir(parents=True,exist_ok=True)
    d=A.newDocument('HeadEars'); d.Label='Rounded feline ears — PETG prototype'
    d.saveAs(str(MODULE))
    source=A.getDocument('RobotCat').getObject('HeadRear')
    ref=d.addObject('PartDesign::Feature','InheritedRearHead')
    ref.Label='Inherited rear shell — unchanged datum BRep'
    # Compound keeps the original located solid exactly while the outer
    # container has identity placement (Body.BaseFeature strips root location).
    ref.Shape=Part.makeCompound([source.Shape.copy()]); ref.Visibility=False
    ref.addProperty('App::PropertyString','SourceSHA256','Traceability')
    ref.SourceSHA256=pilot.sha(PREDECESSOR)
    # Outer roof, not the inner wall: confirmed by vertical section probes.
    patch=ref.Shape.Faces[0].common(Part.makeBox(19,110,42,A.Vector(-127,-55,143)))
    roof=d.addObject('Part::Feature','InheritedRoofPatch'); roof.Shape=patch; roof.Visibility=False
    roof.Label='Outer roof datum from inherited Face1; pinned source'
    tool=d.addObject('Part::Extrusion','RoofEnvelope'); tool.Base=roof
    tool.Dir=A.Vector(0,0,-70); tool.Solid=True; tool.Visibility=False
    d.recompute()
    print('HeadEars prepared; outer roof reference only')

def ellipse(d,body,name,z,y,major,minor,x=-117):
    import FreeCAD as A, Part, Sketcher
    s=d.addObject('Sketcher::SketchObject',name); body.addObject(s)
    s.Placement=A.Placement(A.Vector(x,y,z),A.Rotation(A.Vector(0,0,1),90))
    # Exposed ellipse axes allow native dimensional constraints (no Block).
    s.addGeometry(Part.Ellipse(A.Vector(0,0,0),max(major,minor),min(major,minor)),False)
    # The major axis always corresponds to Y; inner lower/tip profiles need
    # a 90-degree in-plane rotation when their depth is larger than width.
    swapped=minor>major
    if swapped:
        s.Placement.Rotation=A.Rotation()
    s.exposeInternalGeometry(0)
    s.addConstraint(Sketcher.Constraint('Coincident',0,3,-1,1))
    s.addConstraint(Sketcher.Constraint('Horizontal',1))
    a=s.addConstraint(Sketcher.Constraint('Distance',1,2*max(major,minor)))
    b=s.addConstraint(Sketcher.Constraint('Distance',2,2*min(major,minor)))
    width_constraint=b if swapped else a
    s.setExpression('Constraints[%d]'%width_constraint,'EarParameters.WidthScale * %s'%(2*major))
    s.setExpression('Placement.Base.z','150 mm + EarParameters.HeightScale * %s mm'%(z-150))
    d.recompute()
    assert s.FullyConstrained and s.solve()==0,(name,s.SolverMessages if hasattr(s,'SolverMessages') else s.State)
    s.Visibility=False
    return s

def sections(body_name,side,inner=False):
    import FreeCAD as A
    d=A.getDocument('HeadEars'); b=d.getObject(body_name)
    rows=INNER if inner else OUTER
    names=[]
    for i,row in enumerate(rows):
        z,y,a,c,*x=row
        s=ellipse(d,b,('Bowl' if inner else 'Outer')+side+str(i),z,(-1 if side=='L' else 1)*y,a,c,x[0] if x else -117)
        names.append(s.Name)
    print(json.dumps(names))

def seated(body_name,side):
    import FreeCAD as A
    d=A.getDocument('HeadEars'); b=d.getObject(body_name)
    t=d.addObject('PartDesign::Body','RoofCutTool'+side)
    base=d.addObject('PartDesign::Feature','RoofCutReference'+side); t.addObject(base)
    base.Shape=d.getObject('RoofEnvelope').Shape.copy(); t.Tip=base
    cut=b.newObject('PartDesign::Boolean','ConformalSeat'+side)
    cut.Type=1; cut.Group=[t]; cut.Refine=True
    d.recompute(); assert not cut.Shape.isNull() and len(cut.Shape.Solids)==1
    for o in [t,base,d.getObject('RoofEnvelope')]:o.Visibility=False
    for o in b.Group:
        if hasattr(o,'Visibility'):o.Visibility=False
    cut.Visibility=b.Visibility=True
    b.ViewObject.DisplayModeBody='Tip'; b.ViewObject.ShapeColor=(.12,.13,.14)
    b.Tip=cut
    print(side,'volume',b.Shape.Volume,'bbox',b.Shape.BoundBox)

def constrain_circle(sketch, radius_expression=None):
    """MCP circle creation currently returns zero actual constraints."""
    import Sketcher
    assert sketch.ConstraintCount==0
    for i,g in enumerate(sketch.Geometry):
        sketch.addConstraint(Sketcher.Constraint('DistanceX',i,3,g.Center.x))
        sketch.addConstraint(Sketcher.Constraint('DistanceY',i,3,g.Center.y))
        c=sketch.addConstraint(Sketcher.Constraint('Radius',i,g.Radius))
        if radius_expression:sketch.setExpression('Constraints[%d]'%c,radius_expression)
    sketch.Document.recompute(); assert sketch.FullyConstrained

def unite_bosses():
    import FreeCAD as A
    d=A.getDocument('HeadEars'); bodies=[]
    for side in ['L','R']:
        for i in range(2):
            b=d.getObject('EarBoss'+side+str(i))
            constrain_circle(d.getObject('Boss'+side+str(i)+'Profile'))
            t=d.addObject('PartDesign::Body','BossRoofTool'+side+str(i))
            ref=t.newObject('PartDesign::Feature','BossRoofRef'+side+str(i))
            ref.Shape=d.getObject('RoofEnvelope').Shape.copy();t.Tip=ref
            cut=b.newObject('PartDesign::Boolean','ConformalBoss'+side+str(i))
            cut.Type=2;cut.Group=[t];cut.Refine=True
            d.recompute();assert len(b.Shape.Solids)==1
            t.Visibility=False;bodies.append(b)
    head=d.getObject('RearHead')
    fuse=head.newObject('PartDesign::Boolean','RearHeadBearingSeats')
    fuse.Type=0;fuse.Group=bodies;fuse.Refine=True
    d.recompute();assert len(head.Shape.Solids)==1
    for b in bodies:b.Visibility=False
    print('Four conformal screw-bearing bosses fused to inherited rear shell')

def constrain_holes(name):
    import FreeCAD as A
    constrain_circle(A.getDocument('HeadEars').getObject(name),'EarParameters.HoleRadius')

def constrain_rectangle(name):
    import FreeCAD as A, Sketcher
    s=A.getDocument('HeadEars').getObject(name)
    # MCP rectangle dimensions leave the position free.
    if not s.FullyConstrained:
        p=s.Geometry[0].StartPoint
        s.addConstraint(Sketcher.Constraint('DistanceX',0,1,p.x))
        s.addConstraint(Sketcher.Constraint('DistanceY',0,1,p.y))
    s.Document.recompute();assert s.FullyConstrained

FASTENERS=[f'Ear{k}{s}{i}' for s in ['L','R'] for i in range(2) for k in ['Bolt','Nut']]
PHYSICAL=['EarL','EarR','RearHead']+FASTENERS

def finish():
    import FreeCAD as A, Part, math
    d=A.getDocument('HeadEars')
    for side,y in [('L',-32),('R',32)]:
        for i,x,seat,nutz in [(0,-122,163.5,173.5),(1,-112,157.5,167.5)]:
            datum=d.addObject('PartDesign::CoordinateSystem','EarMount'+side+str(i))
            datum.Placement=A.Placement(A.Vector(x,y,seat),A.Rotation())
            bolt=d.addObject('Part::Feature','EarBolt'+side+str(i))
            # Nominal M2x12 envelope, not an invented supplier STEP or thread.
            bolt.Shape=Part.makeCylinder(1,12,A.Vector(x,y,seat)).fuse(Part.makeCylinder(2.1,2,A.Vector(x,y,seat-2)))
            points=[A.Vector(x+4/math.sqrt(3)*math.cos(k*math.pi/3),y+4/math.sqrt(3)*math.sin(k*math.pi/3),nutz) for k in range(6)]
            nut=d.addObject('Part::Feature','EarNut'+side+str(i))
            nut.Shape=Part.Face(Part.makePolygon(points+[points[0]])).extrude(A.Vector(0,0,1.6)).cut(Part.makeCylinder(1,1.6,A.Vector(x,y,nutz)))
            for o in [bolt,nut]:
                o.addProperty('App::PropertyString','SupplierStatus','Traceability')
                o.SupplierStatus='Nominal M2 envelope; exact supplier, recess and fit unverified'
                o.ViewObject.ShapeColor=(.62,.65,.68)
    for o in d.Objects:
        if hasattr(o,'Visibility'):o.Visibility=False
    for n in PHYSICAL:
        o=d.getObject(n);o.Visibility=True
        if o.TypeId=='PartDesign::Body':
            o.ViewObject.DisplayModeBody='Tip';o.ViewObject.ShapeColor=(.278431,.309804,.34902)
            o.ViewObject.Deviation=.06;o.ViewObject.AngularDeflection=8
        o.addProperty('App::PropertyString','MaterialSpec','Traceability');o.MaterialSpec='PETG' if n in PHYSICAL[:3] else 'STEEL nominal'
        o.addProperty('App::PropertyString','PartRevision','Traceability');o.PartRevision='E1'
        o.addProperty('App::PropertyString','DesignStatus','Traceability');o.DesignStatus='Prototype. Modeled 2x M2x12 per ear; print, clamp load and exact hardware unverified.'
    d.getObject('RearHead').Label='Rear head with concealed ear screw seats — PETG E1'
    d.getObject('EarL').Label='Left rounded one-piece pinna — PETG E1'
    d.getObject('EarR').Label='Right rounded one-piece pinna — PETG E1'
    d.Label='Rounded feline ears and rear shell — E1 PROTOTYPE'
    d.recompute()
    sketches=[o for o in d.Objects if o.TypeId=='Sketcher::SketchObject']
    assert all(s.FullyConstrained and s.solve()==0 for s in sketches)
    assert all(not d.getObject(n).Shape.isNull() and len(d.getObject(n).Shape.Solids)==1 for n in PHYSICAL)
    d.saveAs(str(MODULE))
    print('Saved',len(sketches),'fully constrained sketches;',len(PHYSICAL),'physical parts')

def integrate():
    """New checkpoint, exact inherited wrappers, explicit mating datums."""
    import FreeCAD as A, FreeCADGui as G, JointObject
    d=A.getDocument('RobotCat');m=A.getDocument('HeadEars')
    assert Path(d.FileName).resolve()==PREDECESSOR.resolve() and not TARGET.exists()
    backup=CAD/'_before-ear-integration';backup.mkdir(exist_ok=False)
    d.saveCopy(str(backup/'RobotCat-live.FCStd'))
    oldhash=pilot.sha(PREDECESSOR)
    oldplan=json.loads((CAD/'validation/tail-cartridge-integration/assembly-plan.json').read_text())
    plan=json.loads(json.dumps(oldplan))
    replacements={'EarL':'EarL','EarR':'EarR','HeadRear':'RearHead'}
    removed=['EarInsetL','EarInsetR']
    d.saveAs(str(TARGET))
    for n,src in replacements.items():
        wrapper=d.getObject('Rigid_'+n)
        assert wrapper.Placement.isSame(A.Placement(),1e-5)
        old=d.getObject(n)
        # No native joint references the physical leaf, only the wrapper.
        assert set(o.Name for o in old.InList)=={wrapper.Name},(n,[o.Name for o in old.InList])
        d.removeObject(n)
        link=d.addObject('App::Link',n);link.setLink(m.getObject(src));link.LinkTransform=False
        link.LinkPlacement=A.Placement();wrapper.addObject(link);link.Visibility=True
        link.Label=m.getObject(src).Label
    for n in removed:
        d.removeObject('Fix_'+n);d.removeObject(n);d.removeObject('Rigid_'+n)
    plan['components']=[r for r in plan['components'] if r['name'] not in removed]
    plan['joints']=[r for r in plan['joints'] if r['child'] not in removed]
    def joint(name,parent_name,child_name,datum,existing=False):
        group=d.getObject('Joints');p=d.getObject('Rigid_'+parent_name);c=d.getObject('Rigid_'+child_name)
        j=d.getObject(name) if existing else group.newObject('App::FeaturePython',name)
        if not existing:JointObject.Joint(j,0)
        j.Detach1=j.Detach2=True;j.Reference1=(p,['','']);j.Reference2=(c,['',''])
        j.Placement1=p.Placement.inverse()*datum;j.Placement2=c.Placement.inverse()*datum
        if 'DesignStatus' not in j.PropertiesList:j.addProperty('App::PropertyString','DesignStatus','Traceability')
        j.DesignStatus='E1 physical 2x M2x12 ear mount, nominal hardware; PETG clamp and fit not yet qualified'
        if not existing:JointObject.ViewProviderJoint(j.ViewObject)
        j.Visibility=False
    for side in ['L','R']:
        name='Fix_Ear'+side
        joint(name,'HeadRear','Ear'+side,m.getObject('EarMount'+side+'0').Placement,True)
        r=next(r for r in plan['joints'] if r['name']==name);r['parent']='HeadRear';r['status']='E1 modeled bolted prototype'
    for n in FASTENERS:
        source=m.getObject(n);wrapper=d.addObject('App::Part','Rigid_'+n)
        d.getObject('RobotCatAssembly24').addObject(wrapper)
        link=d.addObject('App::Link',n);link.setLink(source);link.LinkTransform=False;link.LinkPlacement=source.Placement
        wrapper.addObject(link);wrapper.Visibility=link.Visibility=True
        side=n[-2];i=n[-1];parent='HeadRear' if 'Bolt' in n else 'Ear'+side
        joint('Fix_'+n,parent,n,m.getObject('EarMount'+side+i).Placement)
        plan['components'].append({'name':n,'label':source.Label,'stage':'Chassis'})
        plan['joints'].append({'name':'Fix_'+n,'parent':parent,'child':n,'type':'Fixed','status':'E1 modeled bolt/nut'})
    anchor=d.addObject('App::Link','EarInterface');anchor.setLink(m.getObject('EarParameters'));anchor.Visibility=False
    d.recompute();assert d.getObject('RobotCatAssembly24').solve()==0
    assert len(plan['components'])==335 and len(plan['joints'])==334
    assert all(d.getObject('Rigid_'+r['name']).Placement.isSame(A.Placement(),1e-5) for r in plan['components'])
    d.Label='Robot cat — rounded feline ears E1 — PROTOTYPE'
    d.save();assert pilot.sha(PREDECESSOR)==oldhash
    plan.update(entry=TARGET.relative_to(pilot.ROOT).as_posix(),source_sha256=pilot.sha(TARGET),print_ready=False)
    (OUT/'assembly-plan.json').write_text(json.dumps(plan,indent=2),encoding='utf-8',newline='\n')
    report={'assembly_sha256':pilot.sha(TARGET),'module_sha256':pilot.sha(MODULE),'predecessor_sha256':oldhash,
        'replaced':replacements,'removed':removed,'added':FASTENERS,'components':335,'fixed':321,'revolute':13,'temporary':25,
        'note':'Only the two ears and their removed decorative inserts cease being TEMP. Inherited head-to-neck/chassis locks remain unqualified.',
        'print_ready':False}
    (OUT/'migration.json').write_text(json.dumps(report,indent=2),encoding='utf-8',newline='\n')
    A.setActiveDocument(d.Name)
    # Front three-quarter view; normal FreeCAD isometric looks at the tail.
    G.activeDocument().activeView().setCameraOrientation(A.Rotation(A.Vector(1,-1,0),A.Vector(.38,.38,1),A.Vector(-1,-1,.76),'ZXY').Q)
    G.activeDocument().activeView().fitAll()
    print('Integrated 335 parts, 321 Fixed + 13 Revolute, 25 inherited TEMP')

def checkpoint():
    import FreeCAD as A
    m=A.getDocument('HeadEars');d=A.getDocument('RobotCat')
    m.Label='Rounded feline ears and rear shell — E1 PROTOTYPE'
    m.recompute();m.saveAs(str(MODULE));d.recompute();d.saveAs(str(TARGET))
    p=json.loads((OUT/'assembly-plan.json').read_text());p['source_sha256']=pilot.sha(TARGET)
    (OUT/'assembly-plan.json').write_text(json.dumps(p,indent=2),encoding='utf-8',newline='\n')
    p=json.loads((OUT/'migration.json').read_text());p.update(assembly_sha256=pilot.sha(TARGET),module_sha256=pilot.sha(MODULE))
    (OUT/'migration.json').write_text(json.dumps(p,indent=2),encoding='utf-8',newline='\n')
    print('E1 working checkpoint updated, historical CAD untouched')

def repair_backup_links():
    """MCP temporary document backup can leave stale PropertyXLink paths.

    Reset references to the already-open canonical owner without saving that
    historical owner. Reassigning the identical target alone does not clear
    the cached external-file path.
    """
    import FreeCAD as A
    d=A.getDocument('RobotCat');rows=[]
    owners=[A.getDocument('TailCartridge'),A.getDocument('HeadEars')]
    assert all(Path(o.FileName).resolve().is_relative_to(CAD) for o in owners)
    for o in d.Objects:
        if o.TypeId=='App::Link' and o.LinkedObject and o.LinkedObject.Document in owners:
            target=o.LinkedObject;pose=o.LinkPlacement.copy();mode=o.LinkTransform
            o.setLink(None);o.setLink(target);o.LinkTransform=mode;o.LinkPlacement=pose
            rows.append(o.Name)
    d.recompute();assert d.getObject('RobotCatAssembly24').solve()==0
    d.saveAs(str(TARGET))
    p=json.loads((OUT/'assembly-plan.json').read_text());p['source_sha256']=pilot.sha(TARGET)
    (OUT/'assembly-plan.json').write_text(json.dumps(p,indent=2),encoding='utf-8',newline='\n')
    p=json.loads((OUT/'migration.json').read_text());p['assembly_sha256']=pilot.sha(TARGET);p['backup_path_rebound_links']=rows
    (OUT/'migration.json').write_text(json.dumps(p,indent=2),encoding='utf-8',newline='\n')
    print('Rebound canonical R4 owner:',rows)
