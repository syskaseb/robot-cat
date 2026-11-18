import FreeCAD as A,Part,Mesh,MeshPart,json,hashlib
from pathlib import Path
D=A.ActiveDocument;P=Path(__file__).parent;V=A.Vector
def wr(n,x):(P/n).write_bytes((json.dumps(x,indent=2)+'\n').encode())
def gap(a,b):return sum(max(0,getattr(a,k+'Min')-getattr(b,k+'Max'),getattr(b,k+'Min')-getattr(a,k+'Max'))**2 for k in ['X','Y','Z'])**.5
rows=[]
for n,condition in [('D18C_TRUE_PITCH_OPTICAL_RECEIVER','EMPTY MECHANISM/HEAD ROOT DRYFIT only. Current two upper crossmembers explicitly replaced by bolted hollow front skull; no powered or wired motion. Requires full current head root2xM2x12, actual horn/bearing/camera revision test and current skull. Not standalone substitute for frozen D1 print.'),('F3_E1_REMOVABLE_EDGE_KEEPER','ONE populated E1 sample must provide actual bare PCB upper edge/no unseen component compression; mate current common carrier two fullM2x10 before wirelay. Geometry not permission to detach soldered E1/PCA kit.')]:
 o=D.getObject(n);s=o.Shape;bb=s.BoundBox;loc=s.copy();loc.translate(V(-bb.XMin,-bb.YMin,-bb.ZMin));idx={'source_object':n,'status':'BRep_ONLY_UNTIL_LOCAL_GATE','qty':1,'condition':condition,'native_source':Path(D.FileName).name,'valid':s.isValid(),'solids':len(s.Solids),'dimensions':[bb.XLength,bb.YLength,bb.ZLength],'orientation':'native XYZ translated local minXYZ0; flat contact plane on bed, support required for transverse bosses; no slicing performed','brim_support_reserve':8,'under256':max(bb.XLength,bb.YLength,bb.ZLength)+8<=256,'PETG_full_solid_g':s.Volume*.00127,'physical_PASS':False}
 s.exportBrep(str(P/(n+'.brep')))
 if s.isValid() and len(s.Solids)==1 and idx['under256']:
  me=MeshPart.meshFromShape(Shape=loc,LinearDeflection=.10,AngularDeflection=.25,Relative=False);file=P/(n+'.stl');me.write(str(file));re=Mesh.Mesh(str(file));idx.update(closed_reopened=re.isSolid(),facets=re.CountFacets,stl=file.name,sha256=hashlib.sha256(file.read_bytes()).hexdigest(),status='CONDITIONAL_EMPTY_INTERFACE_FIT_ONLY' if re.isSolid() else 'MESH_QUARANTINE_NOT_RELEASED')
 rows.append(idx)
wr('conditional-current-print-index.json',{'parts':rows,'NO_STL_RELEASE':['whole common receiver current full-neighbor gate/AMP-GPIO region unqualified','four cowls: new root neighbor checks partial, no complete seam/neck/tail closure or motion gate','two head skins: actual mechanical joints realized but head/body motion and complete optical/loom local gates open','MTA0100335 dependent carrier/closures unknown fullsample'],'wholekit_ready':False,'appearance_accepted':False,'actual_fit_cut_slack':None})
# Material effectivity, no capacity boxes or painted faces counted as print.
names=['F2_COMMON_PI_BUS_PCA_RECEIVER','F3_E1_REMOVABLE_EDGE_KEEPER','D18C_TRUE_PITCH_OPTICAL_RECEIVER','F3_HEAD_FRONT','F3_HEAD_BACK','F3_BODY_FORE_NEG','F3_BODY_FORE_POS','F3_BODY_REAR_NEG','F3_BODY_REAR_POS']
mass=[]
for n in names:
 s=D.getObject(n).Shape;com=V(0,0,0)
 for q in s.Solids:com+=q.CenterOfMass*q.Volume
 com=com/s.Volume
 mass.append({'object':n,'volume_mm3':s.Volume,'PETG_g':s.Volume*.00127,'COM':list(com),'valid':s.isValid(),'solids':len(s.Solids)})
wr('current-selected-material-not-whole-robot-mass.json',{'density_g_cm3':1.27,'current_effective_prints':mass,'sum_g':sum(q['PETG_g'] for q in mass),'excluded':['all bought-parts boxes','all flex/cooling/stock capacities','paint faces','superseded F2 skins/old ear feet','all unchanged original legs/foundation not remeasured','future still missing common panel and neck/tail closure pieces'],'meaning':'same-density modeled material SUBTOTAL, not whole robot mass/payload or physical print weight; no infill credit','still_unbuilt_load_functions':['S0/S1/monitor receivers','WAGO/MTA full common roots','MIC/TTP/speaker final retention','ToF/JR true source-to-source grips and whole motion qualification','complete body/head neck/tail closure']})
# Only actual new independent empty cap-to-source interfaces.
cap=D.getObject('F3_E1_REMOVABLE_EDGE_KEEPER').Shape
cc=[]
for n in ['F2_COMMON_PI_BUS_PCA_RECEIVER','PCA9685_Adafruit815_PCB','E1_populated_prototype_board','MAX98357A_amp','BNO085']:
 s=D.getObject(n).Shape
 if gap(cap.BoundBox,s.BoundBox)>1.25:continue
 cc.append({'name':n,'gap':cap.distToShape(s)[0],'common':cap.common(s).Volume,'classification':'matched cap roots or nominal safe E1 edge conditional physical sample; no blanket Own waiver'})
wr('current-cap-local-relations.json',cc)
print('CURRENT_USEFUL_FIT_EXPORTS',rows)
