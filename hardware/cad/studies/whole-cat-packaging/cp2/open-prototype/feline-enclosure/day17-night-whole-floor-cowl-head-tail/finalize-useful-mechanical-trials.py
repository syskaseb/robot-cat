import FreeCAD as A,Part,Mesh,MeshPart,json,math,time
from pathlib import Path
D=A.ActiveDocument;V=A.Vector;P=Path(__file__).parent
def box(x,y,z,a,b,c):return Part.makeBox(a,b,c,V(x,y,z))
def put(n,x):(P/n).write_bytes((json.dumps(x,indent=2,ensure_ascii=False)+'\n').encode())
def obj(n,s):
 o=D.getObject(n) or D.addObject('PartDesign::Feature',n);o.Shape=s;return o
def bounds(s):
 b=s.BoundBox;return[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
def run():
 t=time.perf_counter();D.save();op=D.getObject('OP_COMMON_REMOVABLE_OPERATOR_PANEL');q=op.Shape
 # Full external monitorfasteners: both sourcecase andcomplete nuts/washers retained.
 for x in [106,149]:q=q.fuse(box(x,-97.5,124,2,15,9))
 bar=box(100,-94,133,57,7,2)
 for i,(x,dx) in enumerate([(103.5,-3.5),(153.5,3.5)]):
  q=q.fuse(box(x-3.5,-96,125.5,7,11,7.5));hole=Part.makeCylinder(1.15,15,V(x,-90.5,123));q=q.cut(hole).cut(box(x-4,-93.15,126,8,5.3,2.1));bar=bar.cut(hole)
  for o in D.Objects:
   if o.Name.startswith('OP_MONITOR_M2_'+str(i)+'_'):
    s=o.Shape.copy();s.translate(V(dx,0,0));o.Shape=s
 op.Shape=q.removeSplitter();D.getObject('OP_MONITOR_REMOVABLE_TOPKEEPER').Shape=bar.removeSplitter()
 # TTP completejoint moves asoneinterface to fullwasher/nut bearing; gap1.25 toMICprint.
 n1=D.getObject('RG_FRONT_GRID_WITH_INTEGRAL_HEAD_RECEIVER');q=n1.Shape.cut(box(-67,20.5,141.5,19,.75,3.5));q=q.fuse(box(-67,21.25,141.5,19,7.5,3.5));tray=D.getObject('TOUCH_REMOVABLE_SAFE_EDGE_TRAY');tr=tray.Shape.fuse(box(-70,14,145,29,12.5,2))
 for i,x in enumerate([-65,-50]):
  hole=Part.makeCylinder(1.15,12,V(x,23.75,138));q=q.cut(hole);tr=tr.cut(hole)
  for o in D.Objects:
   if o.Name.startswith('TOUCH_M2x8_'+str(i)+'_'):
    s=o.Shape.copy();s.translate(V(0,.75,0));o.Shape=s
 n1.Shape=q.removeSplitter();tray.Shape=tr.removeSplitter()
 # Wholemonitor moved+2X earlier: truefullfield aperture is updated, not inherited oldwindow.
 for n in ['FC_F_NEG','FC_R_NEG']:
  o=D.getObject(n);o.Shape=o.Shape.cut(box(106.75,-145,104.75,43.5,62,27.5)).removeSplitter()
 D.recompute();D.save();put('final-interface-functional-completion.json',{'monitor_fullsets_external_X':[103.5,153.5],'minfullwasher_to_case_Xgap':2,'fullM2x10_stack':'unchanged10/head2/2washers.5/fullnut1.6/tip1.1nominal','TTP_axes_Y':23.75,'TTP_MICprint_foreign_gap':1.25,'TTP_fullwasher_andnut_supported':True,'wholekit':False,'physicalPASS':False,'time':time.perf_counter()-t})
 # Critical actual source cases only; parent matrix remains incomplete, never promoted.
 rows=[]
 for n,qn in [('FC_F_NEG','Pi_GPIO1992_factory_female'),('FC_F_NEG','Pi_USB_DATA_Delock_mating'),('FC_F_NEG','Pi_components_and_cooling'),('FC_F_POS','Speaker'),('SPEAKER_REMOVABLE_BASKET_RIM_TRIAL_KEEPER','FC_F_POS'),('OP_COMMON_REMOVABLE_OPERATOR_PANEL','Monitor_MOD05015')]:
  s=D.getObject(n).Shape;other=D.getObject(qn).Shape;valid=s.isValid() and other.isValid();g=s.distToShape(other)[0] if valid else None;matched=n.startswith('OP_');rows.append({'part':n,'neighbor':qn,'valid':valid,'gap':g,'required':0 if matched else 1.25,'common':s.common(other).Volume if valid and g<1.25 else 0,'fixture_nominalcontact':matched})
  put('critical-final-interface-checks.json',{'rows':rows,'completed':len(rows)==6,'wholePASS':False})
 # Fullsource tailroot remains; only continuation moves above samecurrentrearcover.
 angle=math.radians(15);xmin=140+(184-140)*math.cos(angle)-(268-130)*math.sin(angle);zmin=130-(208-140)*math.sin(angle)+(186-130)*math.cos(angle)
 put('tail-continuation-continuous-cover-bound.json',{'source_control_hull_conservative_X':[184,208],'Z':[186,268],'Yaxis':[140,0,130],'range':[-15,15],'continuous_minX':xmin,'continuous_minZ':zmin,'frontcowl_maxX':87.6,'rearcowl_maxZ':165,'rearvertical_gap_bound':zmin-165,'scope':'ONLYnewcontinuation; unchangedsourcejournal/fulloriginalmaterial retained. Conservative axis-aligned hull then continuous sin/cosbounds; not completeoriginaltailhardwaremotionPASS.','tip_threeposes_source':'head-parting-and-hollow-tail.json','physicalPASS':False})
 # Save every actualnew member asBRep. STLs only limitedemptymechanicalfixturetrials, notwholekit.
 groups=['FC_F_NEG','FC_F_POS','FC_R_NEG','FC_R_POS','HC_FRONT_HOLLOW_MASK','HC_BACK_LOWER','HC_BACK_UPPER','TAIL_ROTATING_HOLLOW_REAL_ROOT','RG_FRONT_GRID_WITH_INTEGRAL_HEAD_RECEIVER','RG_REAR_GRID_WITH_STEPPED_RECEIVING_CROSSMEMBER','FORE_MTA_FIXED_COMMON_POSTS_AND_LOWER','OP_COMMON_REMOVABLE_OPERATOR_PANEL','OP_MONITOR_REMOVABLE_TOPKEEPER','TOUCH_REMOVABLE_SAFE_EDGE_TRAY','SPEAKER_REMOVABLE_BASKET_RIM_TRIAL_KEEPER']
 out=[]
 exportset={'TAIL_ROTATING_HOLLOW_REAL_ROOT','RG_FRONT_GRID_WITH_INTEGRAL_HEAD_RECEIVER','RG_REAR_GRID_WITH_STEPPED_RECEIVING_CROSSMEMBER','TOUCH_REMOVABLE_SAFE_EDGE_TRAY','OP_MONITOR_REMOVABLE_TOPKEEPER'}
 for i,n in enumerate(groups):
  o=D.getObject(n);s=o.Shape.copy();b=s.BoundBox;row={'object':n,'qty':1,'valid':s.isValid(),'solids':len(s.Solids),'volume_mm3':s.Volume,'PETG1p27_equivalent_g':s.Volume*.00127,'world_bounds':bounds(s),'status':'BREP_ONLY_ASSEMBLY_OR_CURRENT_NEIGHBORS_OPEN','orientation':'sourceXYZ+minXYZto0; support/brimallocation8mm','maxXYZ_plus8brim':max(b.XLength,b.YLength,b.ZLength)+8}
  s.exportBrep(str(P/(n+'.brep')))
  if n in exportset and row['valid'] and row['solids']==1 and row['maxXYZ_plus8brim']<=256:
   s.translate(V(-b.XMin,-b.YMin,-b.ZMin));m=MeshPart.meshFromShape(Shape=s,LinearDeflection=.16,AngularDeflection=.3,Relative=False);row.update(mesh_closed=m.isSolid(),mesh_volume=m.Volume,facets=m.CountFacets,local_translation=[-b.XMin,-b.YMin,-b.ZMin])
   if m.isSolid() and m.Volume>0:
    f=P/(n+'.stl');m.write(str(f));r=Mesh.Mesh(str(f));row.update(reopened_closed=r.isSolid(),reopened_volume=r.Volume)
    if r.isSolid():row['status']='OPTIONAL_CONDITIONAL_EMPTY_MECHANICAL_DRYFIT_NOT_WIRED_ROBOT_RELEASE'
  out.append(row);put('current-print-index.json',{'parts':out,'density_g_cm3':1.27,'cursor':i+1,'all':len(groups),'wholekit':False,'physicalPASS':False,'actualcut':None,'actualinstalledslack':None,'release_scope':'Emptystructure/individualfitfixtureonly; no currentbody/headSTL because fullcurrentneighbor/motion/FFC/MTAdependentclosureOPEN. TTPandspeaker safeannulus/rim onephysicalsampleFIT3.','seconds':time.perf_counter()-t})
 D.save();print(json.dumps({'exports':[r['object'] for r in out if 'DRYFIT' in r['status']],'critical':rows,'seconds':time.perf_counter()-t}))
run()
