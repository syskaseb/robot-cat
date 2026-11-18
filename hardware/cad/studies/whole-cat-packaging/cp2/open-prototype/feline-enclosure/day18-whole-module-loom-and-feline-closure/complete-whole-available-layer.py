import FreeCAD as A,Part,json,pathlib,math
D=A.ActiveDocument;P=pathlib.Path(__file__).parent;V=A.Vector;r=[]
def move(names,old,new,axis=(0,0,1),angle=0,role=''):
 R=A.Rotation(V(*axis),angle);T=A.Placement(V(*new)-R.multVec(V(*old)),R)
 for n in sorted(set(names)):
  o=D.getObject(n);vol=o.Shape.Volume;o.Placement=T.multiply(o.Placement);b=o.Shape.BoundBox;r.append(dict(name=n,role=role,volume_before=vol,volume_after=o.Shape.Volume,bounds=[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax],T=T.toMatrix().A))
def pref(p):return [o.Name for o in D.Objects if o.Name.startswith(p) and o.ViewObject.Visibility]
# One functional central protection core, not another rear-box port guess.
move(['F0_FHAC0002_30A'],[138,8,65.52],[43,0,86.25],role='F0 whole70x35x26 central belowAMP/BUS, aboveHP/TY; source mouth/short unfused lead remains one measured fit')
move(['XT60H_mated_with_boots'],[157,52,89],[-18.25,6.75,80.5],angle=-90,role='full50x24x18 paired-boots-and-wire capacity near actual battery/F0 entry; not exact bought material')
move(pref('OP_S1_'),[-20,-35,84],[0,-31.5,84],axis=(0,1,0),angle=90,role='whole asymmetric primary S1 case clocked on real stem axis to fit front operator bay')
move(['Monitor_MOD05015'],[0,0,0],[0,0,0],role='monitor frontchest identity retained')
move(['MAIN_Pololu4853']+pref('CB_MAIN_'),[0,0,0],[0,2,0],role='MAIN fullplane commonnegative PCB bearing/ports')
move(['AUX_FULL9p5_POPULATED_SCOPE','AUX_Pololu4092']+pref('CB_AUX_'),[0,0,0],[0,3,0],role='AUX full9.5 with underside1.8, primary holes retained')
move(['PBAY_P_SYS','PBAY_F_PI'],[0,0,0],[0,.5,0],role='whole shortpair sameR16+14 from one unit; interval deltaY38.25..38.75 chooses38.5')
for i,xx in [(0,8),(1,48)]:
 o=D.getObject('WAGO615_power_0_'+str(i));b=o.Shape.BoundBox;move([o.Name],[b.XMin,b.YMin,b.ZMin],[xx,-55.5,64],role='two entire5chamber615 innervertical commonpowerplane, lever access beforeoperator/loom')
move(['BNO085']+pref('CB_BNO_'),[0,0,0],[-75,0,1],role='full BNO with2opposed primary mounting sets on commonfront rail')
move(['MAX98357A_amp']+pref('CB_AMP_'),[0,0,0],[37,33.1,-12],role='wholeAMP with2full primary sets on centralshared plane belowPCA')
move(['ReSpeakerLite_on_REMOVABLE_back']+pref('HB_MIC_'),[0,0,0],[-89,13,0],role='wholeMIC2diagonalsets sourceunderside2.585/USB/mics open; no unused corners')
for o in D.Objects:
 if o.Name.startswith('WAGO415_data') and o.ViewObject.Visibility and o.Shape.BoundBox.XMin<0 and o.Shape.BoundBox.YMin>34:move([o.Name],[0,0,0],[0,-2,0],role='actual commonouterpositive terminal rail outsideToFlane')
# Tilt the six upper complete MTA assemblies inward, and stagger the two banks longitudinally from actual tail/bought-core bounds.
for o in D.Objects:
 if not o.Name.startswith('Motor_ATO4A_') or not o.ViewObject.Visibility:continue
 b=o.Shape.BoundBox;cy=(b.YMin+b.YMax)/2;cx=(b.XMin+b.XMax)/2;cz=(b.ZMin+b.ZMax)/2;shift=15 if cy>0 else 10
 move([o.Name],[cx,cy,cz],[cx+shift,cy-(2 if cy>0 else -2) if cz>110 else cy,cz],axis=(1,0,0),angle=(20 if cy>0 else -20) if cz>110 else 0,role='fullMTA_TE_ATO bank and upper20deg inward plane; source2mmclip datum follows whole rigid module, factoryends retained')
# Real port relief in the OWN Pi carrier only. Four PCB posts, side-root joints and all source bought material stay unchanged.
o=D.getObject('D18C_COMMON_PI_OPEN_CARRIER');old=o.Shape;guard=Part.makeBox(52.5,26.5,22,V(-44.5,-6.5,68.75));o.Shape=old.cut(guard).removeSplitter();r.append(dict(name=o.Name,role='purposeful wholeXT60 capacity receiving relief, remaining4.25mm rearbar/innerbeam roof, no boughtcut',old_volume=old.Volume,new_volume=o.Shape.Volume,valid=o.Shape.isValid(),solids=len(o.Shape.Solids)))
# New S0 needs a corner relief, not an altered MG/horn/spline. All protected shaft and real horn material stays outside the guard.
guard=Part.makeCylinder(29.75,42.5,V(115.5,-57,92),V(0,1,0));o=D.getObject('TAIL_HORN_ROOF_JOURNAL');old=o.Shape;new=old.cut(guard).removeSplitter();protected=Part.makeCylinder(4,40,V(140,-30,130),V(0,1,0));r.append(dict(name=o.Name,role='explicit nonbearing outercorner replacement for wholeS0 sideoperator; shaftØ8/horn retention preserved',removed=old.Volume-new.Volume,source_shaft_missing=old.common(protected).cut(new).Volume,unplanned_missing=old.cut(new).cut(guard).Volume,valid=new.isValid(),solids=len(new.Solids)));o.Shape=new
(P/'coherent-layer-completion-and-intended-reliefs.json').write_bytes((json.dumps(r,indent=2)+'\n').encode())
# Collect the finite missing interfaces together before any cover material.
names=list(json.loads((P/'whole-current-major-bounds.json').read_text()));C={};changed={x['name'] for x in r}
for n in names:
 o=D.getObject(n)
 if o:
  b=o.Shape.BoundBox;C[n]=[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
c=[]
for i,n in enumerate(C):
 for m in list(C)[i+1:]:
  if n.startswith('S0_') and m.startswith('S0_'):continue
  b=C[n];d=C[m];g=math.sqrt(sum(max(0,b[k]-d[k+3],d[k]-b[k+3])**2 for k in range(3)))
  if g<1.25-1e-6 and (n in changed or m in changed or n.startswith('S0_') or m.startswith('S0_')):
   s=D.getObject(n).Shape;t=D.getObject(m).Shape;c.append(dict(a=n,b=m,bbox_gap=g,actual_gap=s.distToShape(t)[0],common=s.common(t).Volume))
(P/'whole-coupled-layer-actual-gate.json').write_bytes((json.dumps(c,indent=2)+'\n').encode());(P/'CURRENT-whole-major-bounds.json').write_bytes((json.dumps(C,indent=2)+'\n').encode());D.recompute();D.save();print('COHERENT_WHOLE_LAYER_SAVED',len(r),'finite actual',c)
