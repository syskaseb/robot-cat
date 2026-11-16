import FreeCAD as A,FreeCADGui as G,Part,json,math,time,zipfile,xml.etree.ElementTree as E
from pathlib import Path
from datetime import datetime,timezone
D=A.ActiveDocument;P=Path(__file__).parent;V=A.Vector;B=lambda x,y,z,l,w,h:Part.makeBox(l,w,h,V(x,y,z));vol=lambda s:0.0 if s.isNull() else s.Volume
T=time.perf_counter();r=dict(utc=datetime.now(timezone.utc).isoformat(),checks=[],holds=[],physical_pass=False,wholekit_ready=False,actual_cut_fit_slack=None)
# SAMEwholebankload replacement: obsoleteprojectupperoverhang52..95 -> actualdropweb/bottomdogleg.
bank=D.getObject('BANK_PANEL_NEG');oldbank=bank.Shape.copy();bank.Shape=oldbank.cut(B(52,-86,98.63,43,6,10));r['bank_old_overhang_retired']=vol(oldbank)-vol(bank.Shape)
# Currentnominalreceivingpockets, notrawairBBoxcuts: trimONLYpositivecommonwiththechosenfullcasefields.
p11=D.getObject('P11_rear_gate');before=p11.Shape.copy();removed=[]
for n in ['PBAY_P_SYS','PBAY_P_REAR','PBAY_F_PI','PBAY_F_AUX','PBAY_F_HY','PBAY_F_HP','PBAY_F_TY','PBAY_P_AUX']:
 s=D.getObject(n).Shape;c=p11.Shape.common(s)
 if vol(c)>1e-6:p11.Shape=p11.Shape.cut(c);removed.append(dict(case=n,actual_positive_common_relieved=vol(c)))
r['functional_receiver_reliefs']=removed
# One truePOST XZstockloop avoidsforcingY-directednylonintotheF0sidegap. Sameunit/role, actualnylonfeedcut.
ny=D.getObject('PB_TIE_POST_NYLON');ny.Shape=B(-133.2,18.75,60.4,20.4,2.5,14.8).cut(B(-132,18.74,61.6,18,2.52,12.4));D.getObject('PB_TIE_POST_HEAD').Shape=B(-130,16.5,75.2,4.8,4.5,3.5);D.getObject('P10_front_gate').Shape=D.getObject('P10_front_gate').Shape.cut(ny.Shape)
D.recompute();D.save();G.getDocument(D.Name).Modified=False
# ProtecttheWHOLEactual6windowpanel: localnominalsource material vsnewfunctionalbank, notwhole123audit.
S=P.parent/'day16-functional-power-bay'/'functional-power-bay.FCStd'
with zipfile.ZipFile(S) as z:
 root=E.fromstring(z.read('Document.xml'))
 for o in root.findall('.//ObjectData/Object'):
  if o.get('name')=='BANK_PANEL_NEG':
   f=o.find("./Properties/Property[@name='Shape']/Part").get('file');old=Part.Shape();old.importBrepFromString(z.read(f).decode());break
protected=old.common(B(-96,-80.4,100.63,148,32.8,2));r['bank_full6window_panel_missing']=vol(protected.cut(bank.Shape))
for n in ['P11_rear_gate','P10_front_gate','BANK_PANEL_NEG','PB_TWO_615_REMOVABLE_KEEPER']:
 s=D.getObject(n).Shape;r['checks'].append(dict(kind='actualmaterial',part=n,valid=s.isValid(),solids=len(s.Solids),volume=vol(s)))
for n in ['PBAY_P_SYS','PBAY_P_REAR','PBAY_F_PI','PBAY_F_AUX','PBAY_F_HY','PBAY_F_HP','PBAY_F_TY','PBAY_P_AUX']:
 s=D.getObject(n).Shape;c=s.common(p11.Shape);r['checks'].append(dict(kind='chosen_case_vs_newP11',case=n,valid=c.isNull() or c.isValid(),common=vol(c),matched_fixture_nominal_NOT_namewaiver=True))
# Reuse sourceprotectedroot/islandactualmaterial with explicitupperunbuiltpillarfunctionalreplacement.
for tag,q in [('root35',B(95,28,101,12,14,9)),('root49',B(95,42,101,12,14,9)),('baseNEG_sourceanchor_below54',B(85,-89,48,26,10,6)),('basePOS_sourceanchor_below54',B(85,79,48,26,10,6))]:
 r['checks'].append(dict(kind='protected_actual_interface',name=tag,removed=vol(before.common(q).cut(p11.Shape))))
# Correctactualnut+washerfeed/tool anduppercap effectivity onlynewmaterial.
for y in [35,49]:
 for tag,s in [('nut',B(99.6,y-2.85,100.1,9.6,5.7,2.4)),('washer',Part.makeCylinder(3.7,.5,V(103,y,102.5)).fuse(B(103,y-3.7,102.5,6.2,7.4,.5))),('driver',Part.makeCylinder(4.25,35,V(103,y,115)))]:
  c=s.common(p11.Shape);r['checks'].append(dict(kind='root_actual_feed_tool',root=y,field=tag,common=vol(c),valid=c.isNull() or c.isValid()))
# NamedcriticalW043 routinggate: adequateR/length arithmetic didnotanswer theadjacentfullF_AUXfield.
R=12.4;dz=math.sqrt((2*R)**2-20**2);p0=V(106,67,65.125);p1=V(122,67,65.125);pm=V(122+R,77,65.125+dz/2);p2=V(122,87,65.125+dz)
path=Part.Wire([Part.makeLine(p0,p1),Part.Arc(p1,pm,p2).toShape()]);profile=Part.Wire([Part.makeCircle(1.95,p0,V(1,0,0))]);s=path.makePipeShell([profile],True,False)
o=D.addObject('PartDesign::Feature','W043_ALLOCATED_FULL_OD3p1_MARGIN04_R12p4_NOT_PRINT');o.Shape=s;o.ViewObject.ShapeColor=(1.0,.1,.05);o.ViewObject.Transparency=55
r['W043']=dict(method='oneactualcontinuousallocatedsweep, notchord/minimum/fullharness',profileOD=3.1,packingmargin=.4,Rproject_not_supplier=12.4,route_length=path.Length,termination_once=12,layreserve=5,conditional_total=path.Length+17,known_factory_min=84.5,end_region=[list(p2)],mfgmouth_verified=False,whyexact='ChosenfullF_AUXcase is immediatelybesideUturn; wholecase/enddiagramcannotqualifyoccupiedprofile throughthatcorner')
for n in ['PBAY_F_AUX','P11_rear_gate','Motor_ATO4A_1_5']:
 q=D.getObject(n).Shape;c=s.common(q);v=vol(c);g=0 if v>1e-6 else s.distToShape(q)[0];row=dict(a=o.Name,b=n,common=v,gap=g,valid=c.isNull() or c.isValid(),classification='allocatedfactorywirecapacity vsfullnominalcase oractualprint/sourceMTA, notdeliveredwirecontact');r['checks'].append(row)
 if v>1e-6 or g<1.25-1e-6:r['holds'].append(row)
r['remaining']=['wholepowernotaccepted ifW043sweepheld; nosecondcurve/casefamily','allnewfullsteel/stock/tool/initiallay notentirelyclosed','P_AUX/POSTcaseantislide/safeplastic/fullunitfit needactualnominalcaptureproof','actualfourMTA0100335fullunitbinding sourcependingparent; noPASSfromday14box','head/motion/decs andBNO/inline/speaker/S1monitor remainOPEN'];r['seconds']=time.perf_counter()-T
(P/'functional-and-short-unit-gates.json').write_text(json.dumps(r,indent=2)+'\n');D.recompute();D.save();G.getDocument(D.Name).Modified=False;print(json.dumps(r))
