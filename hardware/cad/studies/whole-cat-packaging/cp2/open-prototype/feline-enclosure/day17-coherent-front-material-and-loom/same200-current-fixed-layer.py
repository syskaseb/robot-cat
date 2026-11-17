import FreeCAD as A,FreeCADGui as G,Part,json,math,time
from pathlib import Path
P=Path(__file__).parent;D=A.ActiveDocument;V=A.Vector;R=13.5;Z=V(0,0,1);Pe=V(-80.5,-16.5,152.1)
put=lambda n,j:(P/n).write_bytes((json.dumps(j,indent=2)+'\n').encode())
def unit(v):v=V(v);v.normalize();return v
def pose(q,y,p):
 q=V(q);o=V(-135,0,121);q=o+A.Rotation(V(0,1,0),p).multVec(q-o);o=V(-106,0,127);return o+A.Rotation(Z,y).multVec(q-o)
def hrot(q,y,p):return A.Rotation(Z,y).multVec(A.Rotation(V(0,1,0),p).multVec(q))
def family(y,p):
 C=pose(V(-206.85,0,155.4),y,p);t=hrot(Z,y,p);wh=hrot(V(0,-1,0),y,p);th=math.radians(abs(p));sections=[];Lsteer=R*th
 def sec(c,t,w):sections.append((V(c),unit(t),unit(w)))
 if th>1e-8:
  n=unit(Z-t*math.cos(th));b=unit(t.cross(n));cen=C+n*R
  for i in range(7):
   rr=A.Rotation(b,math.degrees(th*i/6));sec(cen+rr.multVec(C-cen),rr.multVec(t),wh)
 else:sec(C,t,wh)
 Cs=sections[-1][0];dxy=V(Pe.x-Cs.x,Pe.y-Cs.y,0);d=dxy.Length;u=unit(dxy);wb=u.cross(Z)
 if wb.dot(wh)<0:wb=-wb
 # Exact whole SAMEunit: only bridge height changes to hold centre190+ends10.
 H0=(190-Lsteer+Cs.z+Pe.z-d-(math.pi-4)*R)/2
 # Same bight family, unit closure includes full-width distributed roll, not
 # a different path/scalar trial. Monotone length equation inverted numerically.
 ph1=math.atan2(Z.dot(wh.cross(wb)),wh.dot(wb));we=V(0,-1,0);ph2=math.atan2((-Z).dot(wb.cross(we)),wb.dot(we))
 fixed=Lsteer+d-2*R+math.pi*R
 def edgelen(h):return fixed+math.hypot(h-R-Cs.z,8.42*ph1)+math.hypot(h-R-Pe.z,8.42*ph2)
 lo=max(Cs.z,Pe.z)+R;hi=H0
 for jj in range(44):
  mid=(lo+hi)/2
  if edgelen(mid)>190:hi=mid
  else:lo=mid
 H=(lo+hi)/2
 l1=H-R-Cs.z;l2=H-R-Pe.z
 def twistline(a,b,t,w0,w1):
  angle=math.atan2(t.dot(w0.cross(w1)),w0.dot(w1));count=max(3,math.ceil((b-a).Length/3),math.ceil(abs(angle)/.03))
  for i in range(1,count+1):sec(a+(b-a)*(i/count),t,A.Rotation(t,math.degrees(angle*i/count)).multVec(w0))
 E=V(Cs.x,Cs.y,H-R);twistline(Cs,E,Z,wh,wb);axis=Z.cross(u);cen=E+u*R
 for i in range(1,32):
  rr=A.Rotation(axis,90*i/31);sec(cen+rr.multVec(E-cen),rr.multVec(Z),wb)
 A1=sections[-1][0];B1=V(Pe.x,Pe.y,H)-u*R;twistline(A1,B1,u,wb,wb);cen=V(Pe.x,Pe.y,H-R)-u*R
 for i in range(1,32):
  rr=A.Rotation(axis,90*i/31);sec(cen+rr.multVec(B1-cen),rr.multVec(u),wb)
 twistline(sections[-1][0],Pe,-Z,wb,V(0,-1,0))
 edge=[]
 for sign in [-1,1]:edge.append(sum(((sections[i][0]+sections[i][2]*8.4*sign)-(sections[i-1][0]+sections[i-1][2]*8.4*sign)).Length for i in range(1,len(sections))))
 return {'yaw':y,'pitch':p,'camera_C0':list(C),'bridge_H':H,'free_leg_mm':[l1,l2],'middle_straight':d-2*R,'steering_arc':Lsteer,'quarter_arcs':math.pi*R,'exact_center_sum':Lsteer+l1+l2+(d-2*R)+math.pi*R,'enddebit_once':10,'whole_sameunit':200,'exact_fullwidth_roll_debit':edgelen(H),'roll_debit_vs_center':edgelen(H)-(Lsteer+l1+l2+d-2*R+math.pi*R),'source_unit_closed_with_ends':edgelen(H)+10,'sampled_widthedge_lengths':edge,'straight_twist_and_delivered_strip':'Small distributed roll at realverticalfreelegs, no fixedguide isolatesreserve. ActualdeliveredFFCtorsion/profile/mouth mustqualify; no manufacturedcontinuousPASS.'},sections
rows=[];store={}
for y,p in [(0,0),(-20,-10),(-20,0),(-20,10),(0,-10),(0,10),(20,-10),(20,0),(20,10)]:
 r,ss=family(y,p);rows.append(r);store[(y,p)]=ss
put('whole200-variable-bridge-family.json',{'family':'ONE rollingPi-arch between fixedPi latch andmovingcamera latch, heightanalyticfromsame200, notposegridofdesigns','profile':[16.8,1.8],'centerR':R,'project_innerR':12.5,'section_cover_extra_each':.02,'conservative_arc_innerR':R-.92,'rows':rows,'counted_stock':'one200;190 exposedneutralaxis+10endonce; no extraunit/trim/offcutpool','occupied_width_twist_status':'finite fullprofile reference/edge lengths; needs actualstrip/contactside/torsion validation. Never center-only cablePASS','range':{'yaw':[-20,20],'pitch':[-10,10]},'continuous_motion_PASS':False,'roof_neck_requires':'Bridge H changes with headmotion, newlate neckpassage/guard mustfollowfullfield; currentcovernot automaticallyclear'})
# Construct actual occupied neutral ribbon and two useful extreme families.
# No manufacturedaxes or immutablewire: reference profiles only.
g=D.getObject('N17_WHOLE_PORT_LAYER_AND_LOOM_REFERENCE_NOT_PRINT');fields=[]
for key in [(0,0),(-20,10),(20,10)]:
 ss=store[key];wires=[]
 for c,t,w in ss:
  n=unit(t.cross(w));a=w*8.42;b=n*.92;wires.append(Part.Wire(Part.makePolygon([c-a-b,c+a-b,c+a+b,c-a+b,c-a-b]).Edges))
 q=Part.makeLoft(wires,True,True);o=D.getObject('N17_FFC200_OCCUPIED_'+str(key[0]).replace('-','m')+'_'+str(key[1])) or D.addObject('PartDesign::Feature','N17_FFC200_OCCUPIED_'+str(key[0]).replace('-','m')+'_'+str(key[1]));o.Shape=q;o.ViewObject.ShapeColor=(.95,.45,.08);o.ViewObject.Transparency=40;o.ViewObject.Visibility=key==(0,0);g.addObject(o);fields.append({'object':o.Name,'pose':list(key),'valid':q.isValid(),'solids':len(q.Solids),'volume':q.Volume,'section_count':len(wires)})
put('three-occupied-family-fields.json',{'fields':fields,'NOTPRINT_NOTMASS':True,'sameunit_flex_family_not_three_cables':True})

D.recompute();D.save();print("same200_currentlayer_fields_saved")
