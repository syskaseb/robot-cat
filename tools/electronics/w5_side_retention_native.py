"""Build editable Carrier and four-bay Cover only after coupled receipt.

Native boxes/cylinders and one-way links preserve the selected part owners.
The receipt must contain the final FR wing blueprint, not the rejected R1.
Whole assembly, motion and stock remain later gates; no physical fit is claimed.
"""
from pathlib import Path
from datetime import datetime,timezone
import json
import shutil
import tempfile
import w5_side_retention_coupled as C
from servo_fuse_inputs_r1 import save,sha

ROOT=C.ROOT;OUT=C.R.N.BASE/'w5-side-retention-native-r1'
CAD=ROOT/'hardware/cad/studies/w5-side-retention-native-r1'
RECEIVED=C.R.N.BASE/'w5-side-retention-received-r2/checks.json'
PARENT=ROOT/'hardware/cad/studies/w5-harness-passages-qualified-r1/WholeHarnessPassages.FCStd'


def main():
    import FreeCAD as A,Part,MeshPart
    begin=datetime.now(timezone.utc);assert not (OUT/'checks.json').exists()
    proof=json.loads(RECEIVED.read_text(encoding='utf-8'))
    assert proof['status']=='COUPLED_SIDE_RECEIVED_CLEAR_NATIVE_PENDING'
    assert not proof['hits'] and not proof['errors'] and proof['cover_solids']==1
    pins=[Path(__file__),RECEIVED]
    for rel,digest in {**proof['source_sha256'],**proof['files']}.items():
        assert sha(ROOT/rel)==digest,rel;pins.append(ROOT/rel)
    bp_path=ROOT/proof['native_blueprint'];bp=json.loads(bp_path.read_text(encoding='utf-8'))
    assert bp['raw_boxes']['FR_GBearingAndOutletWing'][0]==-78.8
    OUT.mkdir(parents=True,exist_ok=True);CAD.mkdir(parents=True,exist_ok=True)
    parent=A.openDocument(str(PARENT))
    d=A.newDocument('WholeHarnessSideRetention');target=CAD/'WholeHarnessSideRetention.FCStd';d.saveAs(str(target))
    param=d.addObject('App::VarSet','SideRetentionParameters')
    for name,value in (('GrooveAllowance',.2),('BayAllowance',.4)):
        param.addProperty('App::PropertyLength',name);setattr(param,name,value)
    param.addProperty('App::PropertyString','InterfaceStatus')
    param.InterfaceStatus='Nominal prototype; tightening/pullout/creep/fit phase2'
    def box(name,b):
        q=d.addObject('Part::Box',name)
        q.Length,q.Width,q.Height=[b[i+3]-b[i] for i in range(3)]
        q.Placement.Base=A.Vector(*b[:3]);return q
    tools={}
    for name,b in bp['tool_boxes'].items():tools[name]=box(name,b)
    for name,row in bp['grooves'].items():
        q=d.addObject('Part::Cylinder',name)
        q.setExpression('Radius',str(row['base_radius_mm'])+' mm + SideRetentionParameters.GrooveAllowance')
        q.Height=row['height_mm']
        q.Placement=A.Placement(A.Vector(*row['origin_mm']),A.Rotation(A.Vector(0,0,1),A.Vector(*row['axis'])))
        tools[name]=q
    # Geometric bounds below are only a dependency filter, not a collision
    # verdict. The native Boolean and final receipt qualify actual material.
    def intersects(a,b):return all(a[i]<=b[i+3] and b[i]<=a[i+3] for i in range(3))
    tool_bounds=dict(bp['tool_boxes'])
    for name,row in bp['grooves'].items():
        p=row['origin_mm'];end=[p[i]+row['axis'][i]*row['height_mm'] for i in range(3)]
        tool_bounds[name]=[min(p[i],end[i])-row['base_radius_mm']-.3 for i in range(3)]+[
                           max(p[i],end[i])+row['base_radius_mm']+.3 for i in range(3)]
    roots=[]
    for name,b in bp['raw_boxes'].items():
        raw=box(name+'Raw',b)
        local=[tools[n] for n,tb in tool_bounds.items() if intersects(b,tb)]
        if local:
            cutters=d.addObject('Part::Compound',name+'LocalTools');cutters.Links=local
            q=d.addObject('Part::Cut',name+'Slotted');q.Base=raw;q.Tool=cutters;q.Refine=False
        else:q=raw
        roots.append(q)
    source=parent.getObject('SourceCarrierHarnessFinished');assert source is not None
    link=d.addObject('App::Link','ReceivedHarnessCarrier');link.setLink(source);link.LinkPlacement=source.Placement
    carrier=d.addObject('Part::MultiFuse','SideRetentionCarrierFinished');carrier.Shapes=[link,*roots];carrier.Refine=False
    source=parent.getObject('SourceCoverHarnessFinished');assert source is not None
    link=d.addObject('App::Link','ReceivedHarnessCover');link.setLink(source);link.LinkPlacement=source.Placement
    bays=[]
    for name,b in bp['cover_bays'].items():
        q=box(name,b)
        for axis,size,i in (('x','Length',0),('y','Width',1),('z','Height',2)):
            q.setExpression(size,str(b[i+3]-b[i]-.8)+' mm + 2 * SideRetentionParameters.BayAllowance')
            q.setExpression('Placement.Base.'+axis,str(b[i]+.4)+' mm - SideRetentionParameters.BayAllowance')
        bays.append(q)
    tool=d.addObject('Part::Compound','FourSideServiceBays');tool.Links=bays
    cut=d.addObject('Part::Cut','CoverFourBays');cut.Base=link;cut.Tool=tool;cut.Refine=False
    bridges=[box(name,b) for name,b in bp['cover_bridges'].items()]
    cover=d.addObject('Part::MultiFuse','SideRetentionCoverFinished');cover.Shapes=[cut,*bridges];cover.Refine=False
    finals={'SourceCarrier':carrier,'SourceCover':cover};d.save()
    state=dict(status='SIDE_NATIVE_PENDING',started_utc=begin.isoformat(),selected=False,W1_complete=False,W5_complete=False,physical_pass=False)
    def checkpoint(stage,**extra):
        state.update(stage=stage,updated_utc=datetime.now(timezone.utc).isoformat(),**extra)
        save(OUT/'progress.json',state);print('SIDE_NATIVE',stage,flush=True)
    checkpoint('editable_tree_saved',integral_roots=len(roots),native_tools=len(tools),cover_bays=len(bays))
    d.recompute();nominal={}
    for name,q in finals.items():
        s=q.Shape;assert s.isValid() and len(s.Solids)==1,(name,len(s.Solids))
        assert not (s.check(True) or []),name;nominal[name]=s.Volume
    assert abs(nominal['SourceCover']-proof['cover_after_mm3'])<max(1e-5,nominal['SourceCover']*1e-8)
    checkpoint('nominal_valid',nominal_mm3=nominal)
    param.GrooveAllowance=.3;param.BayAllowance=.5;checkpoint('parameter_probe_started');d.recompute()
    probe={}
    for name,q in finals.items():
        s=q.Shape;assert s.isValid() and len(s.Solids)==1,name
        probe[name]=s.Volume;assert probe[name]<nominal[name],name
    param.GrooveAllowance=.2;param.BayAllowance=.4;checkpoint('restore_started',probe_mm3=probe);d.recompute()
    dimensions={}
    for name,q in finals.items():
        s=q.Shape;assert s.isValid() and len(s.Solids)==1,name
        assert abs(s.Volume-nominal[name])<max(1e-5,nominal[name]*1e-8),name
        assert not (s.check(True) or []),name
        s.exportBrep(str(CAD/(name+'_CANDIDATE_WORLD.brep')))
        mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
        assert mesh.isSolid() and mesh.countComponents()==1,name
        b=mesh.BoundBox;dims=[b.XLength,b.YLength,b.ZLength];assert max(dims)+6<=256,(name,dims)
        dimensions[name]=dims;mesh.translate(-b.XMin,-b.YMin,-b.ZMin)
        mesh.write(str(CAD/(name+'_UNSELECTED_x1.stl')))
    for q in d.Objects:
        if q not in finals.values() and q.ViewObject:q.ViewObject.Visibility=False
    d.save();checkpoint('closed_exports_saved',dimensions_mm=dimensions)
    deps=list(dict.fromkeys(Path(q.FileName) for q in A.listDocuments().values() if q.FileName and Path(q.FileName)!=target))
    assert all(p.is_relative_to(ROOT) for p in deps)
    for name in list(A.listDocuments()):A.closeDocument(name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-side-retention-') as td:
        tmp=Path(td)
        for p in [target,*deps]:
            dest=tmp/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
        moved=A.openDocument(str(tmp/target.relative_to(ROOT)));moved.recompute()
        for name,obj in (('SourceCarrier','SideRetentionCarrierFinished'),('SourceCover','SideRetentionCoverFinished')):
            s=moved.getObject(obj).Shape
            assert s.isValid() and len(s.Solids)==1 and abs(s.Volume-nominal[name])<max(1e-5,nominal[name]*1e-8),name
        assert all(Path(q.FileName).is_relative_to(tmp) for q in A.listDocuments().values())
        for name in list(A.listDocuments()):A.closeDocument(name)
    finish=datetime.now(timezone.utc);pins+=deps
    state.update(status='SIDE_NATIVE_PARAMETER_EXPORT_REOPEN_COMPLETE',solids_per_part=1,BOP_errors=0,
        restored=True,closed_STLs=True,relocated_reopen=True,nominal_mm3=nominal,probe_mm3=probe,
        parameter_probes=dict(GrooveAllowance=[.2,.3,.2],BayAllowance=[.4,.5,.4]),
        dimensions_mm=dimensions,body_ties=8,insulation_ties=35,new_separate_prints=0,new_screws=0,
        two_linked_editable_parts=True,whole_mount_wall_motion_assembly_stock_selection_pending=True,
        finished_utc=finish.isoformat(),worker_wall_seconds=(finish-begin).total_seconds(),
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in dict.fromkeys(pins)},
        files={p.relative_to(ROOT).as_posix():sha(p) for p in CAD.iterdir() if p.suffix.lower() in ('.fcstd','.stl','.brep')})
    save(OUT/'checks.json',state);checkpoint('complete')


if __name__=='__main__':main()
