import FreeCAD as A,FreeCADGui as G,Part,json,math,time,zipfile,ast
from pathlib import Path
from datetime import datetime,timezone
P=Path(__file__).parent;OUT=P.parent;V=A.Vector
def box(x,y,z,l,w,h):return Part.makeBox(l,w,h,V(x,y,z))
def cyl(x,y,z,r,h):return Part.makeCylinder(r,h,V(x,y,z))
def fuse(ss):
 s=ss[0]
 for q in ss[1:]:s=s.fuse(q)
 return s
def gap(a,b):return sum(max(0,getattr(a,k+'Min')-getattr(b,k+'Max'),getattr(b,k+'Min')-getattr(a,k+'Max'))**2 for k in ['X','Y','Z'])**.5
def write(n,d):(P/n).write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
def motionfield(s,margin=1.25):
 b=s.BoundBox;xmax=max(0,b.XMax-185);ym=max(abs(b.YMin),abs(b.YMax));xm=max(0,185-b.XMin);t=math.radians(20)
 p0=V(185,0,0);a=V(185+xmax*math.cos(t),-xmax*math.sin(t),0);b1=V(185+xmax,0,0);c=V(185+xmax*math.cos(t),xmax*math.sin(t),0)
 sector=Part.Face(Part.Wire([Part.makeLine(p0,a),Part.Arc(a,b1,c).toShape(),Part.makeLine(c,p0)]))
 base=sector.makeOffset2D(ym+margin);disc=Part.Face(Part.Wire(Part.makeCircle(math.hypot(xm,ym)+margin,V(185,0,0))))
 pr=base.extrude(V(0,0,1)).fuse(disc.extrude(V(0,0,1))).removeSplitter();bottom=[f for f in pr.Faces if f.BoundBox.ZLength<1e-6 and abs(f.BoundBox.ZMin)<1e-6];face=Part.Face(max(bottom,key=lambda f:f.Area).OuterWire)
 return face,dict(xmax=xmax,ymax=ym,negativeX=xm,range_degrees=[-20,20],margin=margin,proof='For positiveX each original bbox point is within ymax of a radial segment; swept sector Minkowski radius ymax+margin covers EVERY angle. NegativeX corners covered by rotation-invariant disk hypot(xm,ymax)+margin. Z bands from actual tail slab, not sampled poses.')
def run():
 D=A.ActiveDocument;t0=time.perf_counter();P.mkdir(exist_ok=True)
 # Read only four original skins, not old whole model rehydration or duplicated actors.
 z=zipfile.ZipFile(OUT/'day16-closed-whole-layout/closed-whole-layout.FCStd');old={}
 for n in ['CLOSED_BODY_front_negative','CLOSED_BODY_front_positive','CLOSED_BODY_rear_negative','CLOSED_BODY_rear_positive']:
  q=Part.Shape();q.importBrepFromString(z.read(n+'.Shape.brp').decode());old[n]=q
 decknames=['P02_front_deck','P03_rear_deck_integrated_load_yoke'];original={n:D.getObject(n).Shape.copy() for n in decknames};axes=[(x,y) for x in [-70,70,145] for y in [-72,72]]
 # Complete all-neighbor receiving-zone allocation BEFORE cuts.
 plan=dict(utc=datetime.now(timezone.utc).isoformat(),basis='Whole actual P01/P02/P03 + all four P05 and full H03; one under-deck keyed receiver, NOT dd5 top lip',axes=axes,bearing_planes=dict(receiver_top46p02=True,deck_top48p52=True,remaining_deck_web2p5=True),fastener=dict(type='M3x10 socket full headD5.5/k3, shaftD3, 2washersOD7/t0.5, fullnutAF5.5/h2.4',headZ=[40.12,43.12],shaftZ=[43.12,53.12],bottomwasherZ=[43.12,43.62],receiverZ=[43.62,46.02],deckwebZ=[46.02,48.52],topwasherZ=[48.52,49.02],nutZ=[49.02,51.42],tip_beyond_fullnut1p7=True,count=6,status='NEEDED_UNCONFIRMED_NO_PURCHASE'),source_foundation_holes_and_bought_parts_retained=True,parting='four actual skin prints keyed in six open-sided deck recesses; integral captive-nut cages in NEW own deck versions, nuts/washers preloaded before modules',tail_project=dict(axis=[185,0,'Z'],range=[-20,20],supplier_travel_not_claimed=True))
 faces=[]
 for x,y in axes:
  n=decknames[0] if x<30 else decknames[1];s=original[n];zs=[]
  for f in s.Faces:
   b=f.BoundBox
   if b.ZLength<1e-6 and f.isInside(V(x,y,b.ZMin),1e-6,True):zs.append(b.ZMin)
  faces.append(dict(owner=n,axis=[x,y],actual_horizontal_faces_Z=zs))
 plan['actual_faces']=faces;write('receiving-interface-plan.json',plan)
 # Actual projection of retained decks; 1mm prism union normalizes coplanar storage, not a design variant.
 fs=[]
 for s in original.values():
  for f in s.Faces:
   b=f.BoundBox
   if b.ZLength<1e-6 and f.Area>20:
    w=f.OuterWire.copy();w.translate(V(0,0,-b.ZMin));q=Part.Face(w)
    if q.normalAt(0,0).z<0:q.reverse()
    fs.append(q.extrude(V(0,0,1)))
 pr=fuse(fs).removeSplitter();bottom=[f for f in pr.Faces if f.BoundBox.ZLength<1e-6 and abs(f.BoundBox.ZMin)<1e-6];fp=Part.Face(max(bottom,key=lambda f:f.Area).OuterWire);outer=fp.makeOffset2D(3.65);guard=fp.makeOffset2D(1.25);inner=fp.makeOffset2D(-3)
 # New own printed versions; bought frame and original packet files NOT edited.
 cuts={n:[] for n in decknames};cages={n:[] for n in decknames};tabs=[];steel=[];bores=[];sourceguards=[]
 for i,(x,y) in enumerate(axes):
  n=decknames[0] if x<30 else decknames[1];sy=1 if y>0 else -1;lo=65.8 if sy>0 else -86.2
  cut=box(x-6.2,lo,30,12.4,20.4,16.02);bore=cyl(x,y,38,1.7,18);cuts[n]+=[cut,bore];bores.append(bore)
  tab=box(x-6,66 if sy>0 else -86,43.62,12,20,2.4);tabs.append(tab)
  cage=box(x-5,y-5,48.52,10,10,5.2)
  lower=cyl(x,y,48.52,3.7,.6).fuse(box(x-3.7,y if sy>0 else y-5.2,48.52,7.4,5.2,.6))
  pocket=box(x-2.85,y-3.4,49.02,5.7,6.8,2.7).fuse(box(x-2.85,y if sy>0 else y-5.2,49.02,5.7,5.2,2.7))
  cages[n].append(cage.cut(lower.fuse(pocket)).cut(bore))
  shaft=cyl(x,y,43.12,1.5,10).fuse(cyl(x,y,40.12,2.75,3))
  for tag,shape in [('M3x10_FULL',shaft),('lowerwasher',cyl(x,y,43.12,3.5,.5).cut(cyl(x,y,43.1,1.6,.55))),('upperwasher',cyl(x,y,48.52,3.5,.5).cut(cyl(x,y,48.5,1.6,.55)))]:steel.append((f'BASE{i}_{tag}',shape))
  r=5.5/math.sqrt(3);vs=[V(x+r*math.cos(math.pi/6+k*math.pi/3),y+r*math.sin(math.pi/6+k*math.pi/3),49.02) for k in range(6)]
  steel.append((f'BASE{i}_fullnut',Part.Face(Part.makePolygon(vs+[vs[0]])).extrude(V(0,0,2.4)).cut(cyl(x,y,49,1.525,2.45))))
 for n in decknames:
  q=original[n].cut(fuse(cuts[n]));q=fuse([q]+cages[n]);D.getObject(n).Shape=q;D.getObject(n).Label='NEW V16 keyed skin receiver / '+n
 deck=fuse([D.getObject(n).Shape for n in decknames])
 skirt=outer.cut(guard).extrude(V(0,0,4.52));skirt.translate(V(0,0,41.5));lip=outer.cut(inner).extrude(V(0,0,2.4));lip.translate(V(0,0,43.62));receiver=fuse([skirt,lip]+tabs).cut(deck).cut(fuse(bores))
 for o in D.Objects:
  if o.Name.startswith('P05'):
   b=o.Shape.BoundBox;sourceguards.append(cyl((b.XMin+b.XMax)/2,(b.YMin+b.YMax)/2,30,5.5,80))
 receiver=receiver.cut(fuse(sourceguards))
 remove=guard.extrude(V(0,0,22));remove.translate(V(0,0,30))
 # Reuse EXACT original outer loft recipe ONLY as clipping volume for fixed tail chute, not a new silhouette.
 mod=ast.parse((OUT/'day16-closed-whole-layout/build-whole.py').read_text());fn=next(n for n in mod.body if isinstance(n,ast.FunctionDef) and n.name=='rr');ns={'V':V,'Part':Part,'math':math};exec(compile(ast.Module(body=[fn],type_ignores=[]),'<source exact rr>','exec'),ns)
 bodyouter=Part.makeLoft([ns['rr'](x,y,z) for x,y,z in [(-145,90,158),(-112,102,179),(60,102,183),(150,102,175),(205,60,149)]],True,False)
 tail=D.getObject('Ola_tail_ENVELOPE').Shape;field,proof=motionfield(tail);full=field.extrude(V(0,0,84));full.translate(V(0,0,134))
 local=tail.common(box(160,-35,144,100,70,5));rootfield,rootproof=motionfield(local);floor=field.makeOffset2D(2.4).extrude(V(0,0,2.4));floor.translate(V(0,0,145.25));rootvoid=rootfield.extrude(V(0,0,8));rootvoid.translate(V(0,0,143));floor=floor.cut(rootvoid)
 wall=field.makeOffset2D(2.4).cut(field).extrude(V(0,0,75));wall.translate(V(0,0,145.25));chute=wall.fuse(floor).common(bodyouter).cut(cyl(135.5,-29.278,147,34,50))
 regions={'front_negative':box(-150,-120,20,175,120,220),'front_positive':box(-150,0,20,175,120,220),'rear_negative':box(25,-120,20,190,130,220),'rear_positive':box(25,10,20,190,110,220)}
 for n,s in old.items():
  reg=regions[n.replace('CLOSED_BODY_','')];q=s.cut(remove).fuse(receiver.common(reg));q=q.cut(full).fuse(chute.common(reg));D.getObject(n).Shape=q
 group=D.addObject('App::DocumentObjectGroup','V16_BASE_SIX_COMPLETE_JOINTS')
 for n,s in steel:
  o=D.addObject('PartDesign::Feature',n);o.Shape=s;o.ViewObject.ShapeColor=(.7,.7,.73);group.addObject(o)
 D.Label='DAY16 WHOLE BASE RECEIVER + GUARDED TAIL20 / CHECKPOINT';D.recompute();D.saveAs(str(P/'base-receiver-tail.FCStd'))
 result=dict(utc=datetime.now(timezone.utc).isoformat(),one_coherent_receiver_revision=True,tail_range_project=[-20,20],tail_continuous_cover=proof,tail_root_cover=rootproof,source_bought_and_P01_P05_H03_unchanged=True,checks=[],failures=[],physical_pass=False,wholekit_ready=False,actual_fit_cut_slack=None)
 # One finite new interface screen, no old world/motion proof replay.
 for n in list(old)+decknames:
  s=D.getObject(n).Shape;row=dict(kind='material',part=n,valid=s.isValid(),solids=len(s.Solids),volume=s.Volume);result['checks'].append(row)
  if not s.isValid() or len(s.Solids)!=1:result['failures'].append(row)
 for x,y in axes:
  n=decknames[0] if x<30 else decknames[1];skin=next(D.getObject(k).Shape for k in old if ('front' if x<30 else 'rear') in k and ('positive' if y>0 else 'negative') in k)
  # Physical finite bearing area from COPLANAR FACES, not a fused-volume demand on separate parts.
  aa=[f for f in skin.Faces if f.BoundBox.ZLength<1e-6 and abs(f.BoundBox.ZMin-46.02)<1e-5];bb=[f for f in D.getObject(n).Shape.Faces if f.BoundBox.ZLength<1e-6 and abs(f.BoundBox.ZMin-46.02)<1e-5];area=sum(a.common(b).Area for a in aa for b in bb)
  result['checks'].append(dict(kind='actual_face_bearing',axis=[x,y],area=area))
  if area<1e-5:result['failures'].append(dict(kind='No proved bearing area',axis=[x,y]))
 targets=[o for o in D.Objects if hasattr(o,'Shape') and not o.Shape.isNull() and o.Name.startswith(('P01','P05','H03','H04'))]
 for n in old:
  s=D.getObject(n).Shape
  for o in targets:
   if gap(s.BoundBox,o.Shape.BoundBox)>1.25:continue
   c=s.common(o.Shape);g=s.distToShape(o.Shape)[0];row=dict(kind='new_skin_retained_foundation',part=n,other=o.Name,gap=g,common=c.Volume,valid=c.isValid());result['checks'].append(row)
   if not c.isValid() or c.Volume>1e-5 or g<1.25-1e-5:result['failures'].append(row)
 for ang in [-20,0,20]:
  q=tail.copy();q.rotate(V(185,0,0),V(0,0,1),ang)
  for n in ['CLOSED_BODY_rear_negative','CLOSED_BODY_rear_positive']:
   s=D.getObject(n).Shape;c=s.common(q);g=s.distToShape(q)[0];row=dict(kind='tail_actual_local_witness_plus_continuous_cover',angle=ang,part=n,gap=g,common=c.Volume,valid=c.isValid());result['checks'].append(row)
   if not c.isValid() or c.Volume>1e-5 or g<1.25-1e-5:result['failures'].append(row)
 # Full hardware against actual source only where bounds permit; not compound/global126 exact.
 source=D.getObject('WAVEGO_complete_126_source_solids').Shape.Solids
 for name,s in steel:
  for i,q in enumerate(source):
   if gap(s.BoundBox,q.BoundBox)>1.25:continue
   c=s.common(q);g=s.distToShape(q)[0];row=dict(kind='new_full_steel_bought_source',part=name,source_solid=i,gap=g,common=c.Volume,valid=c.isValid());result['checks'].append(row)
   if not c.isValid() or c.Volume>1e-5 or g<1.25-1e-5:result['failures'].append(row)
 result['status']='RECEIVER_HOLD_FINITE_CAUSES_NO_NEW_FAMILY' if result['failures'] else 'LOCAL_RECEIVER_AND_TAIL20_SCOPED_REMAINING_JOINT_FUNCTION_DELTA_OPEN'
 result['seconds']=time.perf_counter()-t0;write('interface-result.json',result);D.save();G.getDocument(D.Name).Modified=False
 print(json.dumps(dict(status=result['status'],failures=result['failures'],checks=len(result['checks']),seconds=result['seconds'],objects=len(D.Objects))))
run()
