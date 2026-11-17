import FreeCAD as A,FreeCADGui as G,Part,json,math
from pathlib import Path
P=Path(__file__).parent;D=A.ActiveDocument;V=A.Vector;rows=[]
put=lambda n,j:(P/n).write_bytes((json.dumps(j,indent=2)+'\n').encode())
rows=json.loads((P/'final-named-neck-profile-gate.json').read_text())['rows']
parts=['CF17_SHARED_FIXED_PI_BUS_POWER_CARRIER','CF17_REMOVABLE_COMMON_E1_ROOT_KEEPER','CF17_POWER_INDEPENDENT_BOOT_AND_ADAPTER_KEEPER','A17_INTEGRAL_FRONT_DECK_AND_N1','HEAD_MOVING_SENSOR_FRAME_AND_COVER_SPINE','HC_BACK_UPPER'];pp=[]
for n in parts:
 s=D.getObject(n).Shape;s.exportBrep(str(P/(n+'.brep')));b=s.optimalBoundingBox(False,True);pp.append({'object':n,'valid':s.isValid(),'solids':len(s.Solids),'volume_mm3':s.Volume,'PETG_solid_g':s.Volume*.00127,'COM':list(sum((q.CenterOfMass*q.Volume for q in s.Solids),V())/sum(q.Volume for q in s.Solids)),'bounds_optimal':[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax],'max_plus8':max(b.XLength,b.YLength,b.ZLength)+8,'STL_release':False})
put('current-material-and-effectivity.json',{'parts':pp,'new3carrier_solid_g':sum(r['PETG_solid_g'] for r in pp[:3]),'density_g_per_cm3':1.27,'previous_A17_g':163655.02114746312*.00127,'old_bridge_replaced_V':D.getObject('CB_REMOVABLE_BUS_E1_BRIDGE').Shape.Volume,'source_frame_delta_g':json.loads((P/'moving-source-frame-functional-channel.json').read_text())['changed_mass_g_PETG1p27'],'wholemass_NOT_claimed':True,'mass_excludes_stock_fields_wires_cooling':True,'print_status':'BRep/native proofparts only; no STLrelease while fullstock/assembly/localcriticalguardchecks missing'})
# Wholeopaque visibility: actualsuppliedparts retained, analyticalfields/oldunbuiltroles hidden.
for o in D.Objects:
 if not hasattr(o,'Shape') or not hasattr(o,'Placement'):continue
 n=o.Name
 if n.startswith(('N17_','CF17_ToF4_OCCUPIED','CF17_PI_PRIMARY_','CF17_PI_SMALL','CF17_PI_MICROSD','CF17_POL1992_FACTORY_END')):o.ViewObject.Visibility=False
 if n.startswith(('HC_','FC_')) and 'PROPOSED' not in n:o.ViewObject.Visibility=True
 if o.Label.startswith(('RETIRED','UNBUILT_OLD')):o.ViewObject.Visibility=False
 if n=='Pi_components_and_cooling':o.ViewObject.Visibility=False
for n in parts:D.getObject(n).ViewObject.Visibility=True
D.getObject('CF17_ONE_COHERENT_FRONT_MATERIAL_AND_PORTS').ViewObject.Visibility=True
D.getObject('N17_WHOLE_PORT_LAYER_AND_LOOM_REFERENCE_NOT_PRINT').ViewObject.Visibility=False
D.Label='DAY17_COHERENT_FRONT_MATERIAL_AND_LOOM';D.recompute();D.save();v=G.activeDocument().activeView();d=V(-1.5,1,.65);d.normalize();r=V(0,0,1).cross(d);r.normalize();v.setCameraOrientation(A.Rotation(r,d.cross(r),d,'ZXY').Q);v.fitAll();v.redraw()
print(json.dumps({'final_local_fails':[r for r in rows if not r['clear']],'new3parts_g':sum(r['PETG_solid_g'] for r in pp[:3]),'native_saved':D.FileName}))
