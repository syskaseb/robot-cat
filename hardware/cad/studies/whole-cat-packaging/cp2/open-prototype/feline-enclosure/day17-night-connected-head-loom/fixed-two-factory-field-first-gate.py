import FreeCAD as A,FreeCADGui as G,Part,json,math,time,datetime
from pathlib import Path
D=A.ActiveDocument;P=Path(__file__).parent;V=A.Vector;t0=time.perf_counter()
def put(n,d):(P/n).write_bytes((json.dumps(d,indent=2)+'\n').encode())
def bb(s):
 b=s.BoundBox;return[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
def lower(a,b):
 a=bb(a);b=bb(b);return sum(max(0,a[i]-b[i+3],b[i]-a[i+3])**2 for i in range(3))**.5
def pipe(face,ys,yf,z,ell,r):
 p=V(face,ys,z);q=V(face+ell,ys,z);u=V(face+ell+16,(ys+yf)/2,z);w=V(face+ell,yf,z);e=V(face,yf,z)
 path=Part.Wire([Part.makeLine(p,q),Part.Arc(q,u,w).toShape(),Part.makeLine(w,e)])
 profile=Part.Wire(Part.makeCircle(r,p,V(1,0,0)))
 return path.makePipeShell([profile],True,False)
def run():
 P.mkdir(exist_ok=True);D.Label='NIGHT CONNECTED HEAD LOOM AND TWO FACTORY FIELDS - UNSELECTED';D.saveAs(str(P/'connected-head-loom.FCStd'))
 # Sourceposes are fixed in this chunk. Both units use SAME14once and full
 # min/max raw stock. The wires are planned occupied solids, not deliveredwire.
 fields=[]
 for role,face,ys,yf,z,ends in [('W043',-4,-67,-35,130,['PBAY_P_SYS','PBAY_F_PI']),('XA01',100,-54,-22,64,['PBAY_P_REAR','PBAY_F_AUX'])]:
  for raw in [84.5,94.5]:
   ell=(raw-14-math.pi*16)/2
   for scope,r,col in [('NOMINAL_OD3p1',1.55,(.85,.34,.14)),('ALLOCATED_OD3p1_PLUSp4',1.95,(.85,.56,.15))]:
    s=pipe(face,ys,yf,z,ell,r);name='CF_'+role+'_raw'+str(raw).replace('.','p')+'_'+scope;o=D.addObject('PartDesign::Feature',name);o.Shape=s;o.ViewObject.ShapeColor=col;o.ViewObject.Transparency=30 if r>1.55 else 0;o.ViewObject.Visibility=raw==84.5 and r>1.55
    fields.append({'role':role,'n':name,'raw':raw,'scope':scope,'radius':r,'centerR':16,'straight_each':ell,'exact_outside_length':2*ell+math.pi*16,'sameunit_strip_once':14,'raw_sum':14+2*ell+math.pi*16,'bounds':bb(s),'valid':s.isValid(),'solids':len(s.Solids),'volume':s.Volume,'connected_case_ends':ends})
 put('two-full-unit-fields-construction.json',{'fields':fields,'source_pose':'37de33a5 rigidposes unchanged','electrical':'W043 P_SYSlogical5/F_PI.in; XA01 P_REARlogical1/F_AUX.in factoryONLY, notXA02extension','cavity_mapping':'source37de middleCprojectnominal not manufacturerpitch; otherA/B/D/E mustremain unique, no new chamber/graph','source_mouth':'selectedreferenceendfaces+X/sourceheightmidplane project assumption ONEphysicalFIT; notcataloguecoordinate','source_radius':'16>=priorproject12.4, no shrink; allocatedfullprofile r1.95 retains .4outer and foreign1.25','uncertainty':'raw84.5..94.5includesbare; actualstrip/delivery/pinmouth remainphysicalspecific; no extra5/rawnewcut','alllengths':'not all-E matrix; fullfamily max geometricdisplacement5frommin if using14 target. No allfamilyPASS from2samples.'})
 D.recompute();D.save()
 # Known full F0 source shape is a conservative installation case field,
 # NOT supplier-exact molded plastic. Classify before interpreting contact.
 f0=D.getObject('F0_FHAC0002_30A');meta={}
 for k in f0.PropertiesList:
  try:
   value=getattr(f0,k)
   if isinstance(value,str):meta[k]=value
  except Exception:pass
 put('F0-operand-source-classification.json',{'object':f0.Name,'bounds':bb(f0.Shape),'valid':f0.Shape.isValid(),'metadata':meta,'constructor':'day14-firstfit-build.py assumed F0 26x70x35, conservativeinstallation notexactboughtmaterial. Current37de rotateswholefield.','interpretation':'positivecommon rejects chosenwire/F0allocatedcoexistence; cannotcallactualdeliveredwirecontact oreraseprotectedfieldbylabel. Actualcasebody/decomposition wouldneedtargetedsourcebinding before dependentfit.'})
 names=['PBAY_F_PI','PBAY_P_SYS','PBAY_F_AUX','PBAY_P_REAR','F0_FHAC0002_30A','PBAY_P_AUX','PCA9685_Adafruit815_PCB','E1_populated_prototype_board','BUS25514_installed','BNO085','S1_NKK_S821_installed','Monitor_MOD05015','S0_body','S0_key','Battery_GEA223S30X6GT','Pi_components_and_cooling','Pi_GPIO1992_factory_female','XT60H_mated_with_boots','Speaker']
 names += [o.Name for o in D.Objects if o.Name.startswith('Motor_ATO4A') and o.ViewObject.Visibility]
 results=[];first=None
 # Both unit minimumraw cases first; qualification of max/family only if
 # this necessary minimumcase survives. No bypass after firstfalsifier.
 for role in ['W043','XA01']:
  row=next(r for r in fields if r['role']==role and r['raw']==84.5 and r['radius']==1.95);s=D.getObject(row['n']).Shape
  for n in names:
   if n in row['connected_case_ends']:continue
   q=D.getObject(n)
   if not q:continue
   l=lower(s,q.Shape);result={'field':row['n'],'part':n,'bbox_lower':l,'required':1.25,'source_field_not_deliveredcontact':n=='F0_FHAC0002_30A'}
   if l>=1.25:result.update(method='actualsourceboundlower',pass_scoped=True)
   else:
    d=s.distToShape(q.Shape)[0];common=s.common(q.Shape);result.update(method='namedactualshape',gap=d,common_volume=common.Volume,common_valid=common.isValid(),pass_scoped=d>=1.25-1e-7)
   results.append(result);put('fixed-full-field-first-falsifier.json',{'rows':results,'first_falsifier':first,'accepted_whole':False,'remaining_maxraw_and_continuous_family':'UNRECEIVEDunlessnumericsubset/lowercoversqualify'})
   if not result['pass_scoped']:
    first=result;put('fixed-full-field-first-falsifier.json',{'rows':results,'first_falsifier':first,'accepted_whole':False,'remaining_maxraw_and_continuous_family':'FROZEN_NORESUME','whole_consequence':'currentfunctionalpair/F0coallocation isHOLD. No scalarpairmove/newcurve inthischunk. Notdeliveredcontact/stockshortage/allpathsclaim.'});break
  if first:break
 if first:
  nom=next(r for r in fields if r['role']==first['field'].split('_')[1] and r['raw']==84.5 and r['radius']==1.55);s=D.getObject(nom['n']).Shape;q=D.getObject(first['part']).Shape;c=s.common(q)
  put('same-pair-nominal-profile-classification.json',{'field':nom['n'],'part':first['part'],'nominalgap':s.distToShape(q)[0],'nominalcommon':c.Volume,'valid':c.isValid(),'why':'distinguish requirednominalprofile frommarginonly failure; notsecondroute/pose/radius','not_deliveredcontact_if_operand_isF0installation':True})
 print(json.dumps({'objects':len(D.Objects),'first':first,'finitechecks':len(results),'seconds':time.perf_counter()-t0}))
run()
