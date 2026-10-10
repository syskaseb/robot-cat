"""Receive prepared E2 native model; finish bands, fasteners and export gates.

Never rebuild the already-qualified paths. Historical feature snapshots are
excluded by ownership, not by suppressing a contact with actual material.
"""
import json,time,math,sys,tempfile,shutil
from pathlib import Path
sys.path.insert(0,str(Path(sys.executable).resolve().parent.parent/'lib'))
import FreeCAD as A,Part,Mesh,MeshPart
import build_current_pwm_fixture as B
from open_prototype_shared_distribution_carriers import validate
P,C=B.P,B.C;ROOT,BASE,OUT=B.ROOT,B.BASE,B.OUT
MODEL=OUT/'PWMBranchSelected.FCStd'

def last_parts(parts,length):
    out=[]
    for q in reversed(parts):
      e=C.wire([q]).Edges[0];take=min(length,e.Length);u=e.LastParameter-(e.LastParameter-e.FirstParameter)*take/e.Length
      if q['kind']=='line':new=C.line(P.xyz(e.valueAt(u)),q['end'])
      else:new=dict(kind='arc',start=P.xyz(e.valueAt(u)),mid=P.xyz(e.valueAt((u+e.LastParameter)/2)),end=q['end'])
      out.insert(0,new);length-=take
      if length<1e-7:break
    assert length<1e-7;return out

def run():
    assert not MODEL.exists(),'Receive final current model before rerun'
    tick=time.monotonic();r=dict(status='PENDING',contacts=[],pairs=0,selected=False,E2_complete=False,physical_pass=False)
    p=json.loads((OUT/'current-plan.json').read_text());p['fuse']['XP01_nominal_fit_blank_mm']=34
    p['phase2_gates']=[s.replace('44mm nominal','34mm nominal') for s in p['phase2_gates']]
    p['nominal_grip_liner_fit_gate']='Cable ties capture only insulation/sleeve. Delivered clamping/OD and deburred small gaps require dry fit/pull test; no rated tensile capacity inferred.'
    reader=P.SavedShapes();targets,torso=C.I.E.context(reader)
    for n in json.loads((BASE/'tail-mount-checkpoint/tail-assembly-checks.json').read_text())['tail_identities']:targets.pop('P0_'+n,None)
    source=A.openDocument(str(BASE/'mounting-checkpoint/CurrentBoardMounts.FCStd'))
    obsolete={o.Name for b in source.Objects if b.TypeId=='PartDesign::Body' for o in b.Group}
    removed={n:targets.pop(n).Volume for n in list(targets) if n in obsolete}
    r['excluded_history_features_by_native_body_ownership']=removed
    assert 'UpperFrameClearance' in removed
    d=A.openDocument(str(OUT/'PWMBranchCurrent.FCStd'));carrier=d.UpperCarrier001;body=d.E2Fixture
    try:
      d.E2BoardBandBack.Length=5.28;d.E2ModuleSideLand.Length=9.6;d.recompute()
      B.pocket(body,'E2HousingBandPassages',133.3,[(x,y,3.2,2) for x in (98.4,115.4) for y in (-14.5,0)],4)
      B.pocket(body,'E2ExitBandPassages',137.4,[(x,-11,2.8,4.2) for x in (124.6,128.6)],1.6)
      d.recompute();validate(d,[carrier,body])
      pcb=targets['PWM1608NominalPCB'].copy()
      for q in json.loads((OUT/'native-checks.json').read_text())['pad_holes']:
        pcb=pcb.cut(Part.makeCylinder(q['drill']/2,3,A.Vector(q['x']+91.59,q['y'],82.5)))
      targets['PWM1608NominalPCB']=pcb
      material={carrier.Name:carrier.Shape,body.Name:body.Shape}
      for n,s in [('Fixture',body.Shape),('CarrierAdded',carrier.Shape.cut(source.UpperCarrier001.Shape))]:
        for m,t in targets.items():
          if m=='UpperCarrier001' or not C.near(s,t,0):continue
          v=sum(a.common(b).Volume for a in s.Solids for b in t.Solids);r['pairs']+=1
          if v>1e-5:r['contacts'].append(dict(a=n,b=m,volume=v))
      curves={n:C.wire(q['parts']) for n,q in p['routes'].items()}
      insulation={n:B.tube(last_parts(p['routes'][n]['parts'],15),1.4) for n in ('XP02_module','XP03_module')}
      for n,s in insulation.items():
        for m,t in {**targets,**material}.items():
          if not C.near(s,t,0):continue
          v=sum(a.common(b).Volume for a in s.Solids for b in t.Solids);r['pairs']+=1
          if v>1e-5:r['contacts'].append(dict(a=n+'_sleeve',b=m,volume=v))
      for n,c in curves.items():
        radius=p['routes'][n]['radius']
        for m,t in {**targets,**material}.items():
          if not C.near(c,t,radius):continue
          dist=min(c.distToShape(a)[0] for a in t.Solids);r['pairs']+=1
          if dist<radius-1e-5:r['contacts'].append(dict(a=n,b=m,distance=dist,required=radius))
      hardware={};anchors=[]
      for i,(x,y) in enumerate(B.AXES):
        shank=Part.makeCylinder(1.5,12,A.Vector(x,y,74.22))
        head=Part.makeCylinder(2.75,3,A.Vector(x,y,71.22));hardware[f'E2Bolt{i}']=shank.fuse(head)
        washer=Part.makeCylinder(3.5,.5,A.Vector(x,y,74.22)).cut(Part.makeCylinder(1.6,.5,A.Vector(x,y,74.22)))
        hardware[f'E2Washer{i}']=washer
        pts=B.hexagon(x,y,5.5);nut=Part.Face(Part.Wire([Part.makeLine(pts[j],pts[(j+1)%6]) for j in range(6)])).extrude(A.Vector(0,0,2.4))
        nut.translate(A.Vector(0,0,81.72));nut=nut.cut(Part.makeCylinder(1.5,2.4,A.Vector(x,y,81.72)))
        hardware[f'E2Nut{i}']=nut
        anchors.append(dict(xy=[x,y],stack='M3x12 underhead74.22; washer0.5/carrier3/post4/nut2.4; end86.22',full_thread_engagement_mm=2.4,protrusion_mm=2.1))
        # Actual driver cylinder, staged before board and fixture installation.
        hardware[f'E2Driver{i}']=Part.makeCylinder(2,25,A.Vector(x,y,46.22))
      for n,s in hardware.items():
        for m,t in {**targets,**material}.items():
          if not C.near(s,t,0):continue
          v=sum(a.common(b).Volume for a in s.Solids for b in t.Solids);r['pairs']+=1
          if v>1e-5:r['contacts'].append(dict(a=n,b=m,volume=v))
      bands={};heads={}
      # Nominal supplier1.2mm straps, actual tension/forming retained as fit gate.
      specs=[('Fuse1',46,-11,-2,130.7,142.4),('Fuse2',79,-11,-2,130.7,142.4),
        ('Input',34.5,-10.7,-2.3,134.4,140.25),('SourceRed',88.5,-10.7,-2.3,134.4,140.125),
        ('SourceBlack',43.5,-39.2,-30.8,137.4,143.125),('Housing1',100,-14.5,1.2,128.3,146.7),('Housing2',117,-14.5,1.2,128.3,146.7),
        ('Module1',126,-11.7,-4.375,135.9,143.125),('Module2',130,-11.7,-4.375,135.9,143.125),('Board',128,-12.7,-4.3,76.775,84.2)]
      for n,x,y0,y1,z0,z1 in specs:
        s=C.box([x-1.25,y0,z0,x+1.25,y1,z1]).cut(C.box([x-1.4,y0+1.2,z0+1.2,x+1.4,y1-1.2,z1-1.2]))
        bands[n]=s;heads[n]=C.box([x-2.25,y0-3.5,(z0+z1)/2-2.4,x+2.25,y0,(z0+z1)/2+2.4])
      for n,s in {**{'band/'+n:s for n,s in bands.items()},**{'head/'+n:s for n,s in heads.items()}}.items():
        for m,t in targets.items():
          if m=='UpperCarrier001' or not C.near(s,t,0):continue
          v=sum(a.common(b).Volume for a in s.Solids for b in t.Solids);r['pairs']+=1
          if v>1e-5:r['contacts'].append(dict(a=n,b=m,volume=v))
      # Every PCB bearing collar retained; new holes and trough do not consume it.
      mountplan=json.loads((BASE/'mounting-checkpoint/board-mount-plan.json').read_text());bearing=[]
      for board,axes in mountplan['board_hole_axes_world_xy_mm'].items():
        if board in ('Pi4','BUS'):continue
        z=mountplan['pcb_bottom_planes_mm'][board]
        for x,y in axes:
          ring=Part.makeCylinder(2.15,.2,A.Vector(x,y,z-.2)).cut(Part.makeCylinder(1.2,.2,A.Vector(x,y,z-.2)))
          a=source.UpperCarrier001.Shape.common(ring).Volume;b=carrier.Shape.common(ring).Volume
          assert a>1e-5 and abs(a-b)<1e-5,(board,x,y,a,b);bearing.append(dict(board=board,xy=[x,y],retained_volume=a))
      for n,s in {**{n+'_BoardInsulation':s for n,s in insulation.items()},**hardware,**{'Band_'+n:s for n,s in bands.items()},**{'TieHead_'+n:s for n,s in heads.items()}}.items():
        o=d.addObject('Part::Feature',n.replace('/','_'));o.Shape=s
        if 'Driver' in n:o.Visibility=False
      for n in ('P_REAR','G_TAIL','JPWM'):
        d.getObject(n).setExpression('Placement.Base.z','E2Parameters.FloorThickness - 2.8 mm')
      d.recompute();baseline=body.Shape.Volume;z=d.P_REAR.Shape.BoundBox.ZMin
      d.E2Parameters.FloorThickness=3;d.recompute();validate(d,[carrier,body]);assert abs(d.P_REAR.Shape.BoundBox.ZMin-z-.2)<1e-6
      assert abs(body.Shape.Volume-baseline)>1;d.E2Parameters.FloorThickness=2.8;d.recompute();assert abs(body.Shape.Volume-baseline)<1e-5
      prints=[]
      for ob in (carrier,body):
        mesh=MeshPart.meshFromShape(Shape=ob.Shape,LinearDeflection=.08,AngularDeflection=.2,Relative=False)
        assert mesh.isSolid() and not mesh.hasNonManifolds()
        mesh.translate(-ob.Shape.BoundBox.XMin,-ob.Shape.BoundBox.YMin,-ob.Shape.BoundBox.ZMin)
        path=OUT/(ob.Name+'_x1.stl');mesh.write(str(path));b=mesh.BoundBox
        size=[b.XLength,b.YLength,b.ZLength];assert size[0]+10<256 and size[1]+10<256 and size[2]<256
        prints.append(dict(path=path.relative_to(ROOT).as_posix(),sha256=P.sha(path),object=ob.Name,quantity=1,size_mm=size,brim_mm=5,print_ready=False))
      d.saveAs(str(MODEL));name=d.Name;A.closeDocument(name)
      with tempfile.TemporaryDirectory(prefix='cat-e2-reopen-') as td:
        relocated=Path(td)/MODEL.name;shutil.copy2(MODEL,relocated);d=A.openDocument(str(relocated));validate(d,[d.UpperCarrier001,d.E2Fixture])
        assert all(o.getLinkedObject().Document==d for o in d.Objects if o.TypeId=='App::Link')
      r.update(status='E2_FINAL_GATES_REJECTED' if r['contacts'] else 'E2_NATIVE_FINAL_GATES_PREPARED',worker_seconds=round(time.monotonic()-tick,3),
        model_sha256=P.sha(MODEL),prints=prints,anchors=anchors,bearing_checks=bearing,native_parameter_and_restore=True,fresh_relocated_reopen=True,
        native_validity=validate(d,[d.UpperCarrier001,d.E2Fixture]),quantities=dict(M3x12=3,M3_nut=3,M3_washer=3,T18I_11102370=10),
        source_sha256={**reader.hashes,**{(OUT/n).relative_to(ROOT).as_posix():P.sha(OUT/n) for n in ('PWMBranchCurrent.FCStd','native-checks.json','current-plan.json')},Path(__file__).relative_to(ROOT).as_posix():P.sha(Path(__file__))})
      (OUT/'final-plan.json').write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8');(OUT/'final-checks.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
      print(json.dumps({k:r[k] for k in ('status','contacts','pairs','worker_seconds','quantities')}),flush=True)
    finally:
      for doc in list(A.listDocuments().values()):A.closeDocument(doc.Name)
if __name__=='__main__':run()
