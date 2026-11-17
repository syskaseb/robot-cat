import FreeCAD as A,FreeCADGui as G,Part,math,json
from pathlib import Path
P=Path(__file__).parent;D=A.ActiveDocument;V=A.Vector
put=lambda n,j:(P/n).write_bytes((json.dumps(j,indent=2)+'\n').encode())
def bx(x,y,z,l,w,h):return Part.makeBox(l,w,h,V(x,y,z))
D.save()
base=D.getObject('CF17_SHARED_FIXED_PI_BUS_POWER_CARRIER');b=base.Shape.copy();old=b.copy()
# ACTUAL 2sourcePCA panel crossings at rootbeam: shorten rib tails only.
rel=[bx(-47,20,131.4,5,3.6,2.6),bx(2,20,131.4,5,3.6,2.6)]
# Preserve active AMP shelf! Open board centre and bottomleft area, retain fourposts and perimeter.
window=bx(-45.3,-19.6,93.2,44.6,3.2,36.4)
posts=[]
for x in [-41.5,-4.5]:
 for z in [97,125]:
  q=Part.makeCylinder(2.75,6,V(x,-19.5,z),V(0,1,0));q=q.fuse(bx(min(x,-45.3) if x< -20 else x,-19.5,z-1.5,abs(x-(-45.3 if x< -20 else -.7)),3,3));posts.append(q)
cut=window
for q in posts:cut=cut.cut(q)
for q in rel+[cut]:b=b.cut(q)
# AMP shelf current95.5..102 behindboardlowerleft: real side-open relief, protected fourpostislands untouched.
ampclear=bx(-29.25,-19.6,94.25,25.5,6.2,12)
# This opening goes to rightedge at lower BUS receiver and leaves topframe continuous.
b=b.cut(ampclear).removeSplitter();base.Shape=b
# Obsolete single Pi-land on A17 replaced bynewfourpostcarrier; floor/root/PCA below134 preserved.
src=D.getObject('A17_INTEGRAL_FRONT_DECK_AND_N1');s=src.Shape.copy();prior=s.copy();ret=bx(-69.25,19.75,140.25,9.5,9.5,30)
s=s.cut(ret).removeSplitter();src.Shape=s
put('actual-common-interface-functional-completion.json',{'scope':'complete same commoncarrier, notnewpose/boardfamily','newcarrier_valid':b.isValid(),'newcarrier_solids':len(b.Solids),'A17_valid':s.isValid(),'A17_solids':len(s.Solids),'A17_removedV':prior.Volume-s.Volume,'A17_removed_bounds':str(prior.cut(s).BoundBox),'A17_floor_below134_missing':prior.common(bx(-150,-100,0,260,210,134)).cut(s).Volume,'retired_function':'oldUNBUILTPi_positivecornerland(near-64.5,+24.5), replaced bynewsourcefourposts+complete8sets, notboughtroot/cut','source_active_AMP_shelf':'retained unchanged; newBUS receiver side-open window clears sourcewhole shelf, no deleteaudio load','BUS_board_support':'actualfour primaryholeposts retained, centreopen to sourcecomponentregion; annulus/underside physicalcoupon needed; boundingaggregate notliteralplastic.','carrier_root_common_after':b.common(s).Volume,'carrier_changedV':b.Volume-old.Volume,'samePETG_delta_g':(b.Volume-old.Volume+s.Volume-prior.Volume)*.00127,'rootbearing_faceZ134':'unchanged fulltwo sourceislands; ribs stillpositive tobeam above134'})
# Correct section roll continuity at two regionalToF junctions; same C/G/route/R, no curvefamily/posechange.
q=(P/'real-moving-ToF-and-frame-channel.py').read_text(encoding='utf-8');q=q[:q.index('D.save();rr=[]')]
q=q.replace('w=hr(Z,y,p);wires.append','w=hr(Z,y,p)*(1-t)+V(0,1,0)*t;wires.append')
q=q.replace('secwire(c,t,V(1,0,0),10.4)','secwire(c,t,V(0,math.cos(a),math.sin(a)),10.4)')
ns={'__file__':str(P/'real-moving-ToF-and-frame-channel.py')};exec(compile(q,'same_ToF_crosssection_frames','exec'),ns)
rr=[]
for y,p in [(0,0),(-20,10),(20,10)]:
 shape,r=ns['curve'](y,p);n='CF17_ToF4_OCCUPIED_'+str(y).replace('-','m')+'_'+str(p);D.getObject(n).Shape=shape;r.update(valid=shape.isValid(),solids=len(shape.Solids));rr.append(r)
put('ToF4-section-frame-continuity.json',{'samepositions_R_recipe':True,'fields':rr,'note':'analyticRbound previouslyreported is neutralpath/constantoffset conservativebound, notfulltorsion/percore continuousmotion proof; gradualroll nowexplicit inprofile. Full4cutplanningupper390.171/round395 covers9sourceposes+end20, actualcutsNULL. Physicaldeliveredheader/sourcecontact andmovingrollmustqualify.'})
D.recompute();D.save();print(json.dumps({'carrier':[b.isValid(),len(b.Solids),b.Volume],'A17':[s.isValid(),len(s.Solids),s.Volume],'rootcommon':b.common(s).Volume}))
