import FreeCAD as A,FreeCADGui as G,Part,json,math,hashlib
from pathlib import Path
from datetime import datetime,timezone
V=A.Vector;S=A.getDocument('DAY15_CONNECTED_POWER_FIT');P=Path(S.FileName).parent.parent/'day15-power-capacity';P.mkdir(exist_ok=True);D=A.newDocument('DAY15_POWER_CAPACITY');groups={}
for o in S.Objects:
 if o.TypeId=='App::DocumentObjectGroup':groups[o.Name]=D.addObject('App::DocumentObjectGroup',o.Name)
for o in S.Objects:
 if not hasattr(o,'Shape') or not hasattr(o.ViewObject,'ShapeColor'):continue
 q=D.addObject('PartDesign::Feature',o.Name);q.Shape=o.Shape;q.Label=o.Label;q.ViewObject.ShapeColor=o.ViewObject.ShapeColor;q.ViewObject.Transparency=o.ViewObject.Transparency;q.ViewObject.Visibility=o.ViewObject.Visibility
 for prop in ['AssemblyNote','Status','OriginalSource']:
  if hasattr(o,prop):q.addProperty('App::PropertyString',prop);setattr(q,prop,str(getattr(o,prop)))
 for g in S.Objects:
  if g.TypeId=='App::DocumentObjectGroup' and o in g.Group:groups[g.Name].addObject(q)
# Named local hazard only: P12 plane X=-10, upper end95.52; no print or original R24 arc moved.
z0=95.52;z1=106.;L=z1-z0;r=3.5;rho=3.4;left=-10+1.25
theta_min=math.acos(((-2)-left-rho)/r)
# Conservative analytic curvature bound: |c''| <= r*sqrt((4theta/L^2)^2+(2theta/L)^4); speed>=1.
a=16*r*r/L**4;b=16*r*r/L**4;target=(1/24)**2
y=(-a+math.sqrt(a*a+4*b*target))/(2*b);theta_max=math.sqrt(y);theta=(theta_min+theta_max)/2
assert theta_min<theta<theta_max
acc=4*theta/L**2;vel=2*theta/L;k=r*math.sqrt(acc**2+vel**4);Rbound=1/k
def angle(z):
 t=(z-z0)/L
 if t<=0:return theta
 if t<.5:return theta*(1-2*t*t)
 return 2*theta*(1-t)**2
def centre(z,sgn):
 t=angle(z);return V(-2+sgn*r*math.cos(t),sgn*r*math.sin(t),z)
grp=D.addObject('App::DocumentObjectGroup','P12_LOCAL_TWO_FULL_PROFILES_NOT_OUTER_RECTANGLE');clip=Part.makeBox(40,40,18,V(-20,-20,88));allcovers=[];records=[]
for sign in [-1,1]:
 # Exact straight lower section; curve cover consists continuous capsules with analytically bounded interpolation sag.
 nodes=[88,z0]+[z0+L*i/48 for i in range(1,49)];pieces=[];sagmax=0
 for i,(za,zb) in enumerate(zip(nodes,nodes[1:])):
  ca=centre(za,sign);cb=centre(zb,sign);v=cb-ca;sag=0 if zb<=z0 else k*(zb-za)**2/8;sagmax=max(sagmax,sag);rad=rho+sag+1e-6
  tlo=max(0,(za-z0)/L);thi=max(0,(zb-z0)/L);tpmax=4*theta/L*max(min(thi,.5),max(0,1-max(tlo,.5))) if zb>z0 else 0
  # Bound normal-disc Z reach, not the irrelevant full sphere radius at axial cell ends.
  tpmax=vel if za<=z0+L/2<=zb else max(4*theta/L*min(max(tlo,0),max(0,1-tlo)),4*theta/L*min(max(thi,0),max(0,1-thi)))
  nz=rho*r*tpmax/math.sqrt(1+(r*tpmax)**2)+sag+1e-6
  cellclip=Part.makeBox(40,40,(zb-za)+2*nz,V(-20,-20,za-nz)).common(clip)
  pieces.append(Part.makeCylinder(rad,v.Length,ca,v).common(cellclip))
  if i>0:pieces.append(Part.makeSphere(rad,ca).common(cellclip))
 cover=Part.makeCompound(pieces);assert cover.isValid();n='P12_FULL_OD6_MARGIN04_'+('LEFT' if sign<0 else 'RIGHT');o=D.addObject('PartDesign::Feature',n);o.Shape=cover;o.ViewObject.ShapeColor=(.95,.35,.08) if sign<0 else (.15,.7,.85);o.ViewObject.Transparency=30;grp.addObject(o);allcovers.append(cover)
 records.append(dict(name=n,nominal_OD=6,margin=.4,continuous_capsule_cells=len(pieces),sag_upper=sagmax,valid=True,lower_entry=[centre(88,sign).x,centre(88,sign).y,88],upper_exit=[centre(106,sign).x,centre(106,sign).y,106]))
old=D.getObject('POWER_BAT2_VERTICAL_AND_NORTH_TURN');old.ViewObject.Visibility=False
# Preserve upper arc exactly as source region subset, from its straight->arc junction106 onwards.
arcpart=old.Shape.common(Part.makeBox(40,60,40,V(-20,-10,106)));assert arcpart.isValid();o=D.addObject('PartDesign::Feature','P12_UNCHANGED_R24_UPPER_ARC_REGION');o.Shape=arcpart;o.ViewObject.ShapeColor=(.9,.6,.1);o.ViewObject.Transparency=65;grp.addObject(o)
section=Part.makePlane(30,25,V(-15,-12.5,94),V(0,0,1));sectionobjs=[]
for name,s in [('P12_actual_section',D.getObject('P12_common_deck_speaker').Shape)]+[(x['name']+'_section',q) for x,q in zip(records,allcovers)]:
 sec=s.section(section);q=D.addObject('PartDesign::Feature',name);q.Shape=sec;q.ViewObject.LineWidth=3;grp.addObject(q);sectionobjs.append(name)
plan=dict(status='SAVED_BEFORE_LOCAL_TEST',utc=datetime.now(timezone.utc).isoformat(),source_manifest_sha256=hashlib.sha256((Path(S.FileName).parent/'manifest.json').read_bytes()).hexdigest(),source_commit='e475013adb5639c482fb333b7348aa59ade0e21a',physical_decision='Whether actual two full profiles plus gap/margin can be handlaid through P12 constriction without print change; old outer rectangle overstates corner occupancy.',why_local_exact='Plane alone cannot qualify actual P12 edge or normal-profile cover during local roll; only this 18mm approach is represented individually, not whole harness.',unchanged=dict(printed_material=True,metal=True,module_poses=True,original_R24_arc=True,XT60_full_capacity=True,audio_R12=True),open_region=dict(actual_P12_edge_X=-10,required_clearance=1.25,left_limit=-8.75,upper_P12_Z=95.52,straight_to_arc_Z=106),packing=dict(two_OD=6,centre_spacing=7,nominal_gap=1,outer_margin=.4,allocated_gap=.2,entry_roll_degrees=math.degrees(theta),theta_interval_deg=[math.degrees(theta_min),math.degrees(theta_max)],method='constant roll to top of actual P12; C1 piecewise quadratic angle returns to original X-packed R24 arc. Continuous normal circular profiles bounded by capsules, not rectangle subtraction.',minimum_R_analytic=Rbound,curvature_upper=k,centre_speed_z_lower=1,normal_nonlocal_separation='dist^2>=49+(1-r^2*theta_prime_max^2)*dz^2>=49 because r*theta_prime_max<1; nominalgap1 and allocatedgap.2 retained',r_theta_prime_max=r*vel),profiles=records,sections=sectionobjs,physical_unknowns='True battery exits/length/balance/F0/G1/unmatingtravel remain FIT2, no physical cut/extension/slack or manufacturer datum',actual_fit_cut_slack=None)
(P/'capacity-plan.json').write_bytes((json.dumps(plan,ensure_ascii=False,indent=2)+'\n').encode());D.Label='DAY15 power capacity — same material — local proof pending';D.recompute();D.saveAs(str(P/'power-capacity.FCStd'));print(json.dumps(dict(saved=D.FileName,objects=len(D.Objects),theta_interval=plan['packing']['theta_interval_deg'],chosen_roll=math.degrees(theta),Rbound=Rbound)))
