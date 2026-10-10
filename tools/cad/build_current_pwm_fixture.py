"""Editable E2 fixture and matched carrier; preserves selected board axes.

One current candidate. Proof explicitly distinguishes nominal supplier models,
provisional delivered fits and actual retained BReps. No physical acceptance.
"""
import json,time,math,sys,tempfile,shutil
from pathlib import Path
sys.path.insert(0,str(Path(sys.executable).resolve().parent.parent/'lib'))
import plan_current_pwm_core_corridor as C
import FreeCAD as A,Part,Sketcher,Mesh,MeshPart
from open_deck_p0_supports import sketch,feature
from open_deck_p0_plate import rect,circle
from open_prototype_shared_distribution_carriers import validate
P=C.P;ROOT,BASE,OUT=C.ROOT,C.BASE,C.OUT
MODEL=OUT/'PWMBranchCurrent.FCStd'
AXES=[(26,-20),(26,20),(120,-20)]

def plan():
    p=C.build();p['P_REAR_centre_mm']=[18,0,138]
    p['routes']['XP01']['parts']=[C.line([29,-6.5,138],[51,-6.5,138])]
    p['fuse'].update(conservative_unfused_mm=48.4,XP01_nominal_fit_blank_mm=44)
    # A sleeved board tail needs its complete OD below the PCB, not just copper.
    for n,x,z,px,py,level in [('XP02_module',133,138,91.59,-11.43,81),('XP03_module',134.9,141,89.05,-6.35,79)]:
        r=11.1;y=-6.5
        parts=[C.line([123.9,y,z],[x,y,z]),C.arc([x,y,z-r],[x,y,z],[x+r,y,z-r]),
          C.line([x+r,y,z-r],[x+r,y,level+r]),C.arc([x,y,level+r],[x+r,y,level+r],[x,y,level])]
        parts+=P.input_recipe([x,y,level],[px+1,py,level],[-1,0,0],r)['segments']
        p['routes'][n]['parts']=parts
        p['routes'][n+'_bare']['parts']=[C.arc([px+1,py,level+1],[px+1,py,level],[px,py,level+1]),C.line([px,py,level+1],[px,py,85.8202])]
        b=p['budgets'][n];b['route_mm']=C.wire(parts).Length;b['bare_mm']=C.wire(p['routes'][n+'_bare']['parts']).Length
        b['margin_mm']=220-b['route_mm']-b['bare_mm']-16
    p['housing_bounds_mm']=C.build()['housing_bounds_mm']
    p['grips']=['XP01 intact29..47, land30..39 before outer sleeve41.5',
      'XP02 source intact84..93 below housing, XP03 source39..48 atG_TAIL exit',
      'Module pair: vertical side land124..133 at connector exit, two replaceable bands',
      'Board pair: independent carrier-rooted band atX128 OUTSIDE PCB footprint, never on solder/copper']
    p['phase2_gates']=['Delivered MicroFit housing/latch/cavity marks and lead OD/length','Sleeve finishedOD<=2.8 on board tails and<=6.4 fuse; replaceable support adjustment if larger',
      'XP01 complete unfused<=50mm measured, no loop;44mm nominal blank includes12mm strip','Tie tension/pull/creep/edge deburr and solder insulation dry fit','No energizing before E3/E4 acceptance']
    p['selected']=False;p['E2_complete']=False
    return p

def pad(body,name,z,loops,h):
    s=sketch(body,name+'Plan',z)
    for q in loops:rect(s,*q)
    body.Tip=feature(body,'Pad',name,s,h);return body.Tip

def pocket(body,name,z,loops,h):
    s=sketch(body,name+'Plan',z)
    for q in loops:rect(s,*q)
    body.Tip=feature(body,'Pocket',name,s,h)

def tube(parts,r):
    w=C.wire(parts);e=w.Edges[0]
    return w.makePipeShell([Part.Wire([Part.makeCircle(r,e.valueAt(e.FirstParameter),e.tangentAt(e.FirstParameter))])],True,False)

def hexagon(x,y,af):
    r=af/math.sqrt(3);pts=[A.Vector(x+r*math.cos(i*math.pi/3),y+r*math.sin(i*math.pi/3),0) for i in range(6)]
    return pts

def run():
    assert not MODEL.exists(),'Receive existing candidate first'
    tick=time.monotonic();p=plan();reader=P.SavedShapes();targets,torso=C.I.E.context(reader)
    for n in json.loads((BASE/'tail-mount-checkpoint/tail-assembly-checks.json').read_text())['tail_identities']:targets.pop('P0_'+n,None)
    source=A.openDocument(str(BASE/'mounting-checkpoint/CurrentBoardMounts.FCStd'))
    d=A.newDocument('PWMBranchCurrent');r=dict(status='PENDING',contacts=[],pairs=0,selected=False,E2_complete=False,physical_pass=False)
    print('Building one native matched carrier/fixture',flush=True)
    try:
      old=source.getObject('UpperCarrier001');carrier=d.copyObject(old,True);d.recompute()
      carrier.Label='Current upper carrier with E2 receiving interface'
      pad(carrier,'E2ReceivingPaths',74.72,[(21,-25,104,10),(21,15,10,10)],3)
      pad(carrier,'E2BoardBandFoot',74.72,[(116,-16,17,7)],3)
      # Required below-board sleeve clearance removes material, not another route.
      pocket(carrier,'E2BlackSleeveTrough',77.72,[(86,-8.35,20,4)],.42)
      pocket(carrier,'E2BoardBandSlot',77.72,[(126.6,-12,2.8,10)],.945)
      pad(carrier,'E2BoardBandBack',77.72,[(124,-11.5,9,2.1)],6.5)
      s=sketch(carrier,'E2ReceivingBoresPlan',77.72)
      for x,y in AXES:circle(s,x,y,3.4)
      carrier.Tip=feature(carrier,'Pocket','E2ReceivingBores',s,3)
      body=d.addObject('PartDesign::Body','E2Fixture')
      par=d.addObject('App::VarSet','E2Parameters');par.addProperty('App::PropertyLength','FloorThickness');par.FloorThickness=2.8
      pad(body,'E2BridgeFloor',129.5,[(4,-24,125,48)],'E2Parameters.FloorThickness')
      pad(body,'E2BridgeWestTab',129.5,[(14,-50,36,27)],'E2Parameters.FloorThickness')
      pad(body,'E2Posts',77.72,[(x-4,y-4,8,8) for x,y in AXES],51.78)
      pad(body,'E2GroundSeat','129.5 mm + E2Parameters.FloorThickness',[(18.5,-50,19,30)],4)
      pad(body,'E2FuseSeats',132.3,[(44,-10.5,5,8),(77,-10.5,5,8)],2.5)
      pad(body,'E2InputLand',132.3,[(30,-9.5,9,6)],4.65)
      pad(body,'E2SourceLand',132.3,[(84,-9.5,9,6)],4.775)
      pad(body,'E2GroundLeadLand',132.3,[(39,-38,10,6)],7.775)
      pad(body,'E2ConnectorSeat',132.3,[(95.6,-12.5,26,12)],1)
      pad(body,'E2ModuleSideLand',132.3,[(124,-10.5,9,3.075)],10.7)
      # Side-loaded M3 nuts bear on4mm PETG, not a guessed self-tapping thread.
      s=sketch(body,'E2RootBoresPlan',84.32)
      for x,y in AXES:circle(s,x,y,3.4)
      body.Tip=feature(body,'Pocket','E2RootBores',s,6.6)
      s=sketch(body,'E2NutPocketsPlan',84.32)
      for x,y in AXES:
        pts=hexagon(x,y,5.7)
        for i in range(6):
          k=s.addGeometry(Part.LineSegment(pts[i],pts[(i+1)%6]),False);s.addConstraint(Sketcher.Constraint('Block',k))
      body.Tip=feature(body,'Pocket','E2NutPockets',s,2.6)
      pocket(body,'E2NutSideLoading',84.32,[(x,y-2.85,4.2,5.7) for x,y in AXES],2.6)
      # Open slots before components are seated; bands never traverse levers.
      for name,z,loops,depth in [
        ('E2FuseBandSlots',132.3,[(x,-12,2.8,11) for x in (44.6,77.6)],1.6),
        ('E2InputBandSlot',136,[(33.1,-11,2.8,9)],1.6),
        ('E2SourceBandSlot',136,[(87.1,-11,2.8,9)],1.6),
        ('E2GroundBandSlot',139,[(42.1,-39,2.8,8)],1.6)]:pocket(body,name,z,loops,depth)
      d.recompute()
      diagnosis=[dict(name=o.Name,state=list(o.State),valid=o.Shape.isValid(),solids=len(o.Shape.Solids),volume=o.Shape.Volume)
        for b in (carrier,body) for o in b.Group if o.TypeId.startswith('PartDesign::') and hasattr(o,'Shape')]
      (OUT/'native-operation-receipt.json').write_text(json.dumps(dict(operations=diagnosis,worker_seconds=time.monotonic()-tick),indent=2)+'\n',encoding='utf-8')
      validate(d,[carrier,body])
      actual={carrier.Name:carrier.Shape,body.Name:body.Shape};delta=carrier.Shape.cut(old.Shape)
      # All target PCB supports stay fixed; new material only against retained mounts.
      for name,s in [('Fixture',body.Shape),('CarrierAdded',delta)]:
        for other,t in targets.items():
          if other=='UpperCarrier001' or not C.near(s,t,0):continue
          v=sum(a.common(b).Volume for a in s.Solids for b in t.Solids);r['pairs']+=1
          if v>1e-5:r['contacts'].append(dict(a=name,b=other,volume=v))
      curves={n:C.wire(row['parts']) for n,row in p['routes'].items()}
      # Exact PCB assigned holes. No blanket bare-wire/PCB exception.
      pcb=targets['PWM1608NominalPCB'].copy();padholes=[]
      pop=json.loads((ROOT/'hardware/electronics/full-cat/pwm-carrier-r3/population.json').read_text())
      for group in pop['board']['groups']:
        for q in group['pads']:
          if abs(float(q.get('x',999)))<.001 and abs(float(q.get('y',999))+11.43)<.001 or abs(float(q.get('x',999))+2.54)<.001 and abs(float(q.get('y',999))+6.35)<.001:padholes.append(q)
      assert len(padholes)==2,padholes
      for q in padholes:pcb=pcb.cut(Part.makeCylinder(float(q['drill'])/2,3,A.Vector(float(q['x'])+91.59,float(q['y']),82.5)))
      targets['PWM1608NominalPCB']=pcb
      outer=Part.makeCylinder(3.2,42,A.Vector(41.5,-6.5,138),A.Vector(1,0,0))
      allowance={'P_REAR':C.box([7,-18.5,132.5,29,18.5,143.5]),'G_TAIL':C.box([18.5,-50,136.5,37.5,-20,145.5]),'JPWM':C.box(p['housing_bounds_mm']),'F_PWM_sleeve':outer}
      for n,c in curves.items():
        rad=p['routes'][n]['radius']
        for other,s in {**targets,**actual}.items():
          if not C.near(c,s,rad):continue
          dist=min(c.distToShape(t)[0] for t in s.Solids);r['pairs']+=1
          if dist<rad-1e-5:r['contacts'].append(dict(a=n,b=other,distance=dist,required=rad))
      names=list(curves)
      for i,a in enumerate(names):
        for b in names[i+1:]:
          if a.removesuffix('_bare')==b.removesuffix('_bare'):continue
          req=p['routes'][a]['radius']+p['routes'][b]['radius']
          if not C.near(curves[a],curves[b],req):continue
          dist=curves[a].distToShape(curves[b])[0];r['pairs']+=1
          if dist<req-1e-5:r['contacts'].append(dict(a=a,b=b,distance=dist,required=req))
      # Keep references separate from editable printed bodies.
      for n,s in {**allowance,**{n:tube(row['parts'],row['radius']) for n,row in p['routes'].items()}}.items():
        o=d.addObject('Part::Feature',n);o.Shape=s
      r['native_names']={'carrier':carrier.Name,'fixture':body.Name};r['pad_holes']=padholes
      r['source_sha256']={**reader.hashes,Path(__file__).relative_to(ROOT).as_posix():P.sha(Path(__file__))}
      r['native_validity']=validate(d,[carrier,body]);r['budgets']=p['budgets']
      r['worker_seconds']=round(time.monotonic()-tick,3)
      r['status']='CONTACTS_REQUIRE_RECEIPT' if r['contacts'] else 'NATIVE_FIXTURE_PREPARED_MORE_GATES_OPEN'
      d.recompute();d.saveAs(str(MODEL));r['model_sha256']=P.sha(MODEL)
      (OUT/'current-plan.json').write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8')
      (OUT/'native-checks.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
      print(json.dumps(r),flush=True)
    finally:
      for doc in list(A.listDocuments().values()):A.closeDocument(doc.Name)
if __name__=='__main__':run()
