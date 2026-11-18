import FreeCAD as A,Part,json,pathlib,math,Mesh,MeshPart
D=A.ActiveDocument;P=pathlib.Path(__file__).parent;V=A.Vector
def bb_gap(a,b):return math.sqrt(sum(max(0,getattr(a,k+'Min')-getattr(b,k+'Max'),getattr(b,k+'Min')-getattr(a,k+'Max'))**2 for k in ['X','Y','Z']))
def write(n,x):(P/n).write_bytes((json.dumps(x,indent=2)+'\n').encode())
fixed=D.getObject('D18C_COMMON_PI_OPEN_CARRIER').Shape
maj=json.loads((P/'final-major-bounds.json').read_text());r=[]
for n in maj:
 if n in ['Pi4B_actual_PCB','Pi_components_and_cooling']:continue
 o=D.getObject(n)
 if bb_gap(fixed.BoundBox,o.Shape.BoundBox)<1.25:
  r.append(dict(a='D18C_COMMON_PI_OPEN_CARRIER',b=n,gap=fixed.distToShape(o.Shape)[0],common=fixed.common(o.Shape).Volume))
for o in D.Objects:
 if o.Name.startswith('CF17_PI_') and o.ViewObject.Visibility and 'PRIMARY' not in o.Name:
  r.append(dict(a='D18C_COMMON_PI_OPEN_CARRIER',b=o.Name,common=fixed.common(o.Shape).Volume,interface='four primary throughsets / washer bearing / preloaded nut sidefeeds; no foreign waiver'))
foreign=[D.getObject('P01_load_rail').Shape,D.getObject('P01_load_rail_instance2').Shape]
source=D.getObject('WAVEGO_complete_126_source_solids').Shape.Solids
operations=[]
for i,(x,y) in enumerate([(-80,34),(-38,-34),(-38,34)]):
 ops=[('complete_bolt_insertion',Part.makeCylinder(1.5,41.02,V(x,y,20)).fuse(Part.makeCylinder(2.75,25.02,V(x,y,20)))),('driver_before_modules',Part.makeCylinder(4.25,27.02,V(x,y,15)))]
 for n,s in ops:
  for j,t in enumerate(foreign+source):
   if bb_gap(s.BoundBox,t.BoundBox)<1.25:operations.append(dict(root=i,operation=n,foreign=('P01_'+str(j)) if j<2 else 'source_WAVEGO_solid_'+str(j-2),gap=s.distToShape(t)[0],common=s.common(t).Volume))
moving=[];receiver=D.getObject('D18C_TRUE_PITCH_OPTICAL_RECEIVER').Shape
for pitch in [-10,0,10]:
 Ry=A.Rotation(V(0,1,0),pitch);T=A.Placement(V(-135,0,121)-Ry.multVec(V(-135,0,121)),Ry);s=receiver.copy();s.transformShape(T.toMatrix())
 for n in ['HEAD_YAW_FORK_FIXED_PITCH_HOUSING','Pitch688','MG92B_Head_pitch','YAW_FIXED_OUTER_RACE_CAP']:
  t=D.getObject(n).Shape
  if bb_gap(s.BoundBox,t.BoundBox)<5:moving.append(dict(pitch=pitch,foreign=n,gap=s.distToShape(t)[0],common=s.common(t).Volume))
write('essential-material-affected-checks.json',dict(fixed=r,full_bolt_and_tool_operations=operations,moving=moving,numeric_cull='Only new fixed carrier/three whole joint operations against actual rigid legs/foundation and named receiving head neighbors; no old world matrix replay',intentional_interfaces=['P02 matched receiving feet zero-common face contacts','4 Pi M2.5 threaded throughsets/pad-bearing','M2 complete crosspin torque engagement']))
hard=[x for x in r if x.get('common',0)>1e-6]+[x for x in operations+moving if x['common']>1e-6]
clearance=[x for x in r if 'gap' in x and x['gap']<1.25-1e-6]+[x for x in operations+moving if x['gap']<1.25-1e-6]
index=[]
for name in ['D18C_TRUE_PITCH_OPTICAL_RECEIVER','D18C_COMMON_PI_OPEN_CARRIER','D18C_P02_THREE_ROOT_THROUGH_VERSION']:
 o=D.getObject(name);s=o.Shape;bb=s.BoundBox;loc=s.copy();loc.translate(V(-bb.XMin,-bb.YMin,-bb.ZMin));status='HOLD_IF_AFFECTED_INTERFACE_NEGATIVE';out=dict(source_object=name,source_volume_mm3=s.Volume,source_valid=s.isValid(),source_solids=len(s.Solids),dimensions_mm=[bb.XLength,bb.YLength,bb.ZLength],orientation='native XYZ, local minimum XYZ=0',brim_support_reserve_mm=8,under256_with_reserve=max(bb.XLength,bb.YLength,bb.ZLength)+8<=256,qty=1)
 if not hard and not clearance and s.isValid() and len(s.Solids)==1 and out['under256_with_reserve']:
  mesh=MeshPart.meshFromShape(Shape=loc,LinearDeflection=.12,AngularDeflection=.3,Relative=False);file=P/(name+'.stl');mesh.write(str(file));read=Mesh.Mesh(str(file));out.update(stl=file.name,closed_reopened=read.isSolid(),facets=read.CountFacets,status='CONDITIONAL_UNPOWERED_MECHANICAL_FIT_ONLY' if read.isSolid() else 'MESH_OPEN_QUARANTINE_NOT_RELEASED')
 else:out['status']=status
 index.append(out)
write('conditional-print-index.json',dict(parts=index,hard_material_failures=hard,clearance_failures=clearance,whole_kit=False,physical_PASS=False,dependency='P00 axes/thread before empty base; actual Pi annuli/crosspin horn+bearing revision/tool coupon before tightening; no wired closed-cat release'))
print('MATERIAL_GATES',len(r),len(operations),len(moving),'hard',len(hard),'clearance',len(clearance));print('PRINT',[(x['source_object'],x['status']) for x in index])
