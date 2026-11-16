import FreeCAD as A,FreeCADGui as G,Part,json,time,zipfile,xml.etree.ElementTree as E
from pathlib import Path
from datetime import datetime,timezone
from PySide import QtCore
D=A.ActiveDocument;P=Path(__file__).parent;V=A.Vector;B=lambda x,y,z,l,w,h:Part.makeBox(l,w,h,V(x,y,z));vol=lambda s:0.0 if s.isNull() else s.Volume
r=dict(utc=datetime.now(timezone.utc).isoformat(),technical_same_geometry_recovery='MixedtupleShapeColor causedMCProllback; restoreonlySAMEintendedreceiverpocket andobsoleteoverhangretirement. No newcurve/casefamily.',parts=[],casecontacts=[],sourceprotected=[])
p11=D.getObject('P11_rear_gate');before=p11.Shape.copy();c=before.common(D.getObject('PBAY_P_SYS').Shape);p11.Shape=before.cut(c);r['P_SYS_actual_receiver_relief']=vol(c)
bank=D.getObject('BANK_PANEL_NEG');b0=bank.Shape.copy();bank.Shape=b0.cut(B(52,-86,98.63,43,6,10));r['explicit_old_overhang_removed']=vol(b0)-vol(bank.Shape)
# Qualified source panelmaterial, exactsame6manufacturerclipwindows retained.
S=P.parent/'day16-functional-power-bay'/'functional-power-bay.FCStd'
with zipfile.ZipFile(S) as z:
 for o in E.fromstring(z.read('Document.xml')).findall('.//ObjectData/Object'):
  if o.get('name')=='BANK_PANEL_NEG':
   f=o.find("./Properties/Property[@name='Shape']/Part").get('file');old=Part.Shape();old.importBrepFromString(z.read(f).decode());break
r['six_clip_window_panel_missing']=vol(old.common(B(-96,-80.4,100.63,148,32.8,2)).cut(bank.Shape))
for tag,q in [('MAINroot35',B(95,28,101,12,14,9)),('AUXroot49',B(95,42,101,12,14,9)),('actualbaseNEG_below54',B(85,-89,48,26,10,6)),('actualbasePOS_below54',B(85,79,48,26,10,6))]:r['sourceprotected'].append(dict(name=tag,missing=vol(before.common(q).cut(p11.Shape))))
for n in ['P11_rear_gate','P10_front_gate','BANK_PANEL_NEG','PB_TWO_615_REMOVABLE_KEEPER']:
 s=D.getObject(n).Shape;r['parts'].append(dict(name=n,valid=s.isValid(),solids=len(s.Solids),volume=vol(s)))
for n in ['PBAY_P_SYS','PBAY_P_REAR','PBAY_F_PI','PBAY_F_AUX','PBAY_F_HY','PBAY_F_HP','PBAY_F_TY','PBAY_P_AUX']:
 c=D.getObject(n).Shape.common(p11.Shape);r['casecontacts'].append(dict(case=n,common=vol(c),valid=c.isNull() or c.isValid()))
r['bankfixedparting_common']=vol(bank.Shape.common(p11.Shape));r['615keeper_fixedparting_common']=vol(D.getObject('PB_TWO_615_REMOVABLE_KEEPER').Shape.common(p11.Shape))
# Onlygenuinelychangedfullrearbanksteel vsS0 and3fullFHAC. Certifiednumericlowerbounds sufficient when>=1.25.
ss=[o.Shape for o in D.Objects if o.Name.startswith('BANK__1_REAR_') and hasattr(o,'Shape')];whole=Part.makeCompound(ss);r['new_bank_steel']=[]
for n in ['PBAY_F_HY','PBAY_F_HP','PBAY_F_TY','S0_body','CLOSED_BODY_rear_negative']:
 q=D.getObject(n).Shape;a=whole.BoundBox;b=q.BoundBox;lo=sum(max(0,getattr(a,k+'Min')-getattr(b,k+'Max'),getattr(b,k+'Min')-getattr(a,k+'Max'))**2 for k in ['X','Y','Z'])**.5
 if lo>=1.25:r['new_bank_steel'].append(dict(other=n,numeric_lower=lo,clear=True))
 else:
  c=whole.common(q);v=vol(c);g=0 if v>1e-6 else whole.distToShape(q)[0];r['new_bank_steel'].append(dict(other=n,common=v,gap=g,valid=c.isNull() or c.isValid(),clear=v<1e-6 and g>=1.25))
# Two useful ACTUAL sections. No empty makePlane orientation assumption.
sections=[]
for tag,x,names in [('POS_POWER',111,['P11_rear_gate','PB_TWO_615_REMOVABLE_KEEPER','PBAY_P_SYS']),('NEG_BANK_LOWER_ROOT',96,['P11_rear_gate','BANK_PANEL_NEG','BANK__1_REAR_M3x25_FULL','PBAY_F_HP'])]:
 plane=Part.Face(Part.makePolygon([V(x,y,z) for y,z in [(-110,40),(110,40),(110,145),(-110,145),(-110,40)]]))
 for n in names:
  s=D.getObject(n).Shape.section(plane);sections.append(dict(tag=tag,x=x,name=n,lines=[[[q.y,q.z] for q in e.discretize(Number=14)] for e in s.Edges]))
(P/'actual-realized-sections.json').write_text(json.dumps(sections)+'\n');r['wholekit_ready']=False;r['physical_pass']=False;r['actual_fit_cut_slack']=None;r['W043_hold_reused']='functional-and-short-unit-gates.json/45.962517596382575 toF_AUX; CASES/routeidentityunchanged';r['remaining']=['wholepowernotaccepted/W043fieldHOLD','newcomplete2M2keeper/7T18Istock/tool andP_AUX/POSTantislideproof notallqualified','source4fullMINIVALunits pendingparent/nooldboxPASS','headmotion/decs/BNO/inline/speaker/S1monitor/wholewireclosureOPEN']
(P/'final-realization-and-effectivity.json').write_text(json.dumps(r,indent=2)+'\n')
for o in D.Objects:
 if o.Name.startswith('CLOSED_BODY') or o.Name.startswith('TIE_FHAC_'):o.ViewObject.Visibility=False
G.activeDocument().activeView().viewIsometric();G.activeDocument().activeView().fitAll();G.activeDocument().activeView().redraw()
def savefinal(d=D,p=P):
 import FreeCADGui as gui,json
 from datetime import datetime,timezone
 d.Label='DAY16 P11 POWER RETENTION - W043 FIELD HOLD - NO PRINT RELEASE';d.recompute();d.save();gui.getDocument(d.Name).Modified=False
 (p/'actual-native-final-save.json').write_text(json.dumps(dict(utc=datetime.now(timezone.utc).isoformat(),pid=17796,objects=len(d.Objects),label=d.Label,document=d.Name,saved=True,modified=False,pending=None,IDLE=True),indent=2)+'\n')
QtCore.QTimer.singleShot(2000,savefinal)
print(json.dumps(r))
