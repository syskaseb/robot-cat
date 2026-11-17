import FreeCAD as A,FreeCADGui as G,Part,json,math,time
from pathlib import Path
P=Path(__file__).parent;D=A.ActiveDocument;V=A.Vector;t0=time.perf_counter()
put=lambda n,j:(P/n).write_bytes((json.dumps(j,indent=2)+'\n').encode())
def bx(x,y,z,a,b,c):return Part.makeBox(a,b,c,V(x,y,z))
def cy(x,y,z,r,h,axis=V(0,0,1)):return Part.makeCylinder(r,h,V(x,y,z),axis)
def add(n,s,col=(.2,.22,.24),scope='PRINT_MATERIAL_LOCALQUALIFICATION_PENDING'):
 o=D.getObject(n) or D.addObject('PartDesign::Feature',n);o.Shape=s;o.ViewObject.ShapeColor=col;o.ViewObject.Visibility=True
 if not hasattr(o,'Scope'):o.addProperty('App::PropertyString','Scope')
 o.Scope=scope;return o
D.save();base=D.getObject('CF17_SHARED_FIXED_PI_BUS_POWER_CARRIER');old=base.Shape.copy();hood=D.getObject('FU17_LATE_FIXED_SHOULDER_HOOD');h=hood.Shape.copy()
feet=[bx(-36.5,-22.5,132,7,7,55),bx(-36.5,21,134,7,7,53)]
for f in feet:base.Shape=base.Shape.fuse(f)
rib=bx(-36.5,-48,187,7,85,3);h=h.fuse(rib)
# Actual2M2x12/fullwasher/nutset, realopenfeed andfull6mmneck above nut; no virtualsolidnut.
def ring(x,y,z):return cy(x,y,z,2.5,.3).cut(cy(x,y,z,1.1,.3))
def nut(x,y,z):
 pts=[V(x+4/math.sqrt(3)*math.cos(math.pi/6+i*math.pi/3),y+4/math.sqrt(3)*math.sin(math.pi/6+i*math.pi/3),z) for i in range(6)];return Part.Face(Part.Wire(Part.makePolygon(pts+[pts[0]]).Edges)).extrude(V(0,0,1.6)).cut(cy(x,y,z,.9,1.6))
for i,y in enumerate([-19,24.5]):
 base.Shape=base.Shape.cut(cy(-33,y,177.8,1.1,10)).cut(bx(-35.7,y-2.7,178.0,8,5.4,3))
 h=h.cut(cy(-33,y,186.9,1.1,4))
 add('FU17_HOOD_'+str(i)+'_fullM2x12',cy(-33,y,178.3,1,12).fuse(cy(-33,y,190.3,1.9,2)),(.66,.67,.69),'STANDARD_DEMAND_NEEDED_UNCONFIRMED')
 add('FU17_HOOD_'+str(i)+'_topwasher',ring(-33,y,190),(.66,.67,.69),'STANDARD_DEMAND_NEEDED_UNCONFIRMED');add('FU17_HOOD_'+str(i)+'_bottomwasher',ring(-33,y,180.7),(.66,.67,.69),'STANDARD_DEMAND_NEEDED_UNCONFIRMED');add('FU17_HOOD_'+str(i)+'_fullnut',nut(-33,y,179.1),(.66,.67,.69),'STANDARD_DEMAND_NEEDED_UNCONFIRMED')
hood.Shape=h
put('actual-fixed-hood-root-and-parting.json',{'base':[base.Shape.isValid(),len(base.Shape.Solids)],'hood':[h.isValid(),len(h.Solids)],'newfeet_source_positive_contact':[f.common(old).Volume for f in feet],'newcrossrib_hood_positive_contact':rib.common(D.getObject('FU17_LATE_FIXED_SHOULDER_HOOD').Shape).Volume,'base_hood_common':base.Shape.common(h).Volume,'completejoint':'2fullM2x12 underhead190.3->tip178.3; .3topwasher+3rib+6footroof+.3bottomwasher+fullnut1.6 =10.2, tip.8pastfullnut179.1. No boughttrim. Fullwasher5 admittedby5.4slot/openXfeed, wholebeforebanks/Pi','load':'hood->realrib->twofullsets andbearingfeet->actualBUSupperrail/beam oncommoncarrier->2existingA17roots/P01. No bodycosmeticloadforPi','useful_upperfoot_section':'7x7 outsideactual5.4nutfeed,6roof, lowerfull7x7pillar. Prototypecoupon/standloadnotstrengthPASS'})
# Real matched latebodyparting only on OWNforecowls; 2mmventseam, no sourcefloor/boughtcut.
window=bx(-135,-50,155,227,89,100);brows=[]
for n in ['FC_F_NEG','FC_F_POS']:
 o=D.getObject(n);s=o.Shape.copy();s.exportBrep(str(P/('source87c_'+n+'.brep')))
 try:
  q=s.cut(window)
  if not q.isNull() and q.isValid():o.Shape=q;brows.append({'n':n,'selected':True,'solids':len(q.Solids),'sourceV':s.Volume,'newV':q.Volume,'outsidewindow_missing':s.cut(window).cut(q).Volume})
  else:brows.append({'n':n,'selected':False,'cause':'kernel/unqualified; sourcepreserved'})
 except Exception as e:brows.append({'n':n,'selected':False,'cause':str(e),'sourcepreserved':True})
put('real-body-hood-late-parting.json',{'window':str(window.BoundBox),'rows':brows,'seam':'2mm intentionalvent/clearanceslit outsidehoodsides(-48,37)andends(-133,90); removablehoodheldbyactual2M2feet. Source6bodyfloorattachments/speakerportoutsideY39/Z155 unchanged','not_whole_body_closure':'4MTAunknown andotherspecificports remainOPEN'})
# Few connected referencecapacity shapes; NOcompletefreewireloft.
info=json.loads((P/'DATA500-cached-analytic-wholeunit.json').read_text());r=info['segments']['coil_R'];outer=cy(52,-23.23,154.3,r+2.9,15.4,V(0,1,0));inner=cy(52,-23.24,154.3,r-2.9,15.42,V(0,1,0));ringregion=outer.cut(inner);add('FU17_DATA500_STOCK_RING_REGION',ringregion,(.2,.45,.8),'ONE500_SELECTED_STOCK_OCCUPIED_REGIONAL_COVER_NOT_PRINT_NOT_MASS')
# Five connected boxes are conservative analyticalsubarc covers, not cables/emptyavailableboxes.
def cover_arc_points(points,rad):
 pieces=[]
 for a,b in zip(points[:-1],points[1:]):
  v=b-a;pieces += [Part.makeCylinder(rad,v.Length,a,v/v.Length),Part.makeSphere(rad,a)]
 pieces.append(Part.makeSphere(rad,points[-1]));return Part.makeCompound(pieces)
P0=V(-12,-.66,151.1);E=V(52,-20.33,154.3-r);diff=E-P0;dx=diff.x;vv=diff-V(dx,0,0);d=vv.Length;vv/=d;R=info['segments']['entry_R'];a=math.acos(1-d/(2*R));pts=[]
for i in range(4):
 t=a*i/3;pts.append(P0+V(1,0,0)*R*math.sin(t)+vv*R*(1-math.cos(t)))
B=pts[-1]
for i in range(1,4):
 t=a*i/3;pts.append(B+V(1,0,0)*R*(math.sin(a)-math.sin(a-t))+vv*R*(math.cos(a-t)-math.cos(a)))
add('FU17_DATA500_ENTRY_CONNECTED_COVER',cover_arc_points(pts,2.9+R*(1-math.cos(a/6))),(.2,.45,.8),'ANALYTIC_S_ARC_COVER_NO_NEWUNIT')
q=V(-11.89+r,-10.73,154.3+r);ps=[V(52,-10.73,154.3+r),q]
for i in range(1,5):
 t=math.pi/2*i/4;ps.append(V(-11.89+r-r*math.sin(t),-10.73,154.3+r*math.cos(t)))
add('FU17_DATA500_RETURN_CONNECTED_COVER',cover_arc_points(ps,2.9+r*(1-math.cos(math.pi/16))),(.2,.45,.8),'ANALYTIC_STRAIGHT_QUARTER_COVER_SOURCEBOOT')
# Selectedthree-wirewholeJRunits: usablecell/caseexits mapped; no individualwireloft.
add('FU17_JR_FACTORY_PITCH_YAWGROUP_STOCK_REGION',cy(-105,-63.55,163,23.55,7.1,V(0,1,0)).cut(cy(-105,-63.56,163,16.45,7.12,V(0,1,0))),(.65,.45,.2),'ONE_FACTORY_PITCH250R20_LOOP_NOMINAL_MOVES_YAW_ONLY_NOT_PRINT')
add('FU17_JR_EXTENSION300_VARIABLE_BIGHT_REGION',cy(-14,-48.55,169,23.55,7.1,V(0,1,0)).cut(cy(-14,-48.56,169,16.45,7.12,V(0,1,0))),(.7,.5,.25),'EXISTING_PITCH300_FREEBIGHT_NO_NEWEXTENSION_FARBOARD_ONLYPHASE2')
# Whole fixedpower region avoidsDATAplug by explicit upperlayer, notbarecurve/chord.
add('FU17_POWER_OUTPUT_PAIR_UPPER_LANE',bx(-74.3,-44,146.5,45,8,24),(.8,.25,.25),'W07980_FIXEDPAIR_PROJECT_R20_S_RISE_REGION_notstockextra')
add('FU17_POWER_PAIR_UPPER_TRANSFER',bx(-34,-44,164.5,117,57,7),(.8,.25,.25),'TWO18AWG_OD3p1_GROUP7p1x3p9_upperS_andturnbeforeMAIN')
add('FU17_POWER_PAIR_DESCENT_AND_MAIN12',bx(48,-4.5,86,38,16.5,80),(.8,.25,.25),'TWOactualMAINoutputpadrow_endregions/full12each_ONCE_noW078credit')
D.recompute();D.save();print(json.dumps({'feet_realized':True,'bodyparting':brows,'DATA500regionalR':r,'seconds':time.perf_counter()-t0}))
