import FreeCAD as A,Part,json,pathlib,math,Mesh,MeshPart
D=A.ActiveDocument;P=pathlib.Path(__file__).parent;V=A.Vector
def wr(n,x):(P/n).write_bytes((json.dumps(x,indent=2)+'\n').encode())
o=D.getObject('D18C_COMMON_PI_OPEN_CARRIER');raw=o.Shape;s=raw
# Real one-piece roof shoulders connect the four posts over the full nut/washer feed; no floating standoffs.
for x in [-104.5,-46.5]:
 for y in [-24.5,24.5]:
  xmax=-42.5 if x==-46.5 and y<0 else x+5
  boss=Part.makeBox(xmax-(x-5),7,1.2,V(x-5,y-3,94.8));s=s.fuse(boss)
  s=s.cut(Part.makeCylinder(1.4,10,V(x,y,89)))
  s=s.cut(Part.makeBox(5.6,12.8,2.4,V(x-2.8,21.2 if y>0 else -34,92.1)))
  s=s.cut(Part.makeBox(6.2,12.8,.5,V(x-3.1,21.2 if y>0 else -34,94.5)))
o.Shape=s.removeSplitter();o.Shape.exportBrep(str(P/'common-Pi-carrier.brep'))
floor=D.getObject('D18C_P02_THREE_ROOT_THROUGH_VERSION').Shape;floor.exportBrep(str(P/'P02-two-side-root-version.brep'))
def gap(a,b):return math.sqrt(sum(max(0,getattr(a,k+'Min')-getattr(b,k+'Max'),getattr(b,k+'Min')-getattr(a,k+'Max'))**2 for k in ['X','Y','Z']))
major=json.loads((P/'final-major-bounds.json').read_text());r=[]
for n in major:
 if n in ['Pi4B_actual_PCB','Pi_components_and_cooling']:continue
 t=D.getObject(n).Shape
 if gap(o.Shape.BoundBox,t.BoundBox)<1.25:r.append(dict(a=o.Name,b=n,gap=o.Shape.distToShape(t)[0],common=o.Shape.common(t).Volume))
source=D.getObject('WAVEGO_complete_126_source_solids').Shape.Solids+[D.getObject(n).Shape for n in ['P01_load_rail','P01_load_rail_instance2']];ops=[]
for i,x in enumerate([-80,-38]):
 joint=[D.getObject('D18C_SIDE_ROOT_'+str(i)+'_'+n).Shape for n in ['M3x12_FULL','HEAD_WASHER','NUT_WASHER','FULL_NUT']]
 fields=[('PERMANENT_FULL_STEEL',Part.makeCompound(joint)),('FULL_BOLT_SIDE_INSERTION',Part.makeCylinder(2.75,28,V(x,26.5,64.52),V(0,1,0))),('PLUS_Y_DRIVER_BEFORE_BANKS',Part.makeCylinder(4.25,22,V(x,41.5,64.52),V(0,1,0)))]
 for kind,a in fields:
  for j,b in enumerate(source):
   if gap(a.BoundBox,b.BoundBox)<1.25:ops.append(dict(root=i,kind=kind,foreign_source_solid=j,gap=a.distToShape(b)[0],common=a.common(b).Volume))
mov=json.loads((P/'essential-material-affected-checks.json').read_text())['moving']
wr('current-essential-local-gates.json',dict(current_fixed=r,current_side_roots=ops,unchanged_receiver_moving_subset=mov,carrier_one_solid=len(o.Shape.Solids),carrier_valid=o.Shape.isValid(),floor_one_solid=len(floor.Solids),source_floor_missing=D.getObject('P02_front_deck').Shape.cut(floor).Volume,matched_floor_common=o.Shape.common(floor).Volume,roof_added_mm3=o.Shape.Volume-raw.Volume,roof_reason='full Pi nut/washer bearing needs real shoulder connection into sidebars; source four complete throughsets unchanged'))
fixedbad=[x for x in r+ops if x.get('common',0)>1e-6 or x.get('gap',10)<1.25-1e-6];movingbad=[x for x in mov if x['common']>1e-6 or x['gap']<1.25-1e-6]
index=[]
for n,bad in [('D18C_TRUE_PITCH_OPTICAL_RECEIVER',movingbad),('D18C_COMMON_PI_OPEN_CARRIER',fixedbad),('D18C_P02_THREE_ROOT_THROUGH_VERSION',fixedbad)]:
 shape=D.getObject(n).Shape;bb=shape.BoundBox;local=shape.copy();local.translate(V(-bb.XMin,-bb.YMin,-bb.ZMin));entry=dict(object=n,qty=1,status='HOLD_LOCAL_INTERFACE' if bad else 'CONDITIONAL_UNPOWERED_FIT_ONLY',valid=shape.isValid(),solids=len(shape.Solids),bounds_mm=[bb.XLength,bb.YLength,bb.ZLength],orientation='native XYZ local minimum0; support/orientation dryfit planning, no slicer',brim_support_reserve_mm=8,under256=max(bb.XLength,bb.YLength,bb.ZLength)+8<256,volume_mm3=shape.Volume,local_negatives=bad)
 if not bad and shape.isValid() and len(shape.Solids)==1 and entry['under256']:
  mesh=MeshPart.meshFromShape(Shape=local,LinearDeflection=.12,AngularDeflection=.3,Relative=False);file=P/(n+'.stl');mesh.write(str(file));read=Mesh.Mesh(str(file));entry.update(stl=file.name,closed_reopened=read.isSolid(),facets=read.CountFacets)
  if not read.isSolid():entry['status']='TECHNICAL_NONCLOSED_MESH_NOT_RELEASED'
 index.append(entry)
wr('CURRENT-conditional-print-index.json',dict(parts=index,source_earlier_index='conditional-print-index.json is RAW SUPERSEDED, do not use old statuses',whole_cat=False,physical_PASS=False,conditions=['P00 axes/thread for empty floor','Pi safe annuli/underboard/roof-feed coupon before preload','actual MG factory horn/bearing revision and full crosspin/tool loading before moving dryfit','FFC and USB source sample/ToFJR motion remains OPEN; no closed wired-cat release']))
meta={}
for n in major:
 b=D.getObject(n).Shape.BoundBox;meta[n]=dict(bounds=[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax])
wr('CURRENT-major-bounds.json',meta)
D.recompute();D.save();print('CURRENT LOCAL',len(fixedbad),len(movingbad),'carrier solids',len(o.Shape.Solids),'index',[(x['object'],x['status']) for x in index])
