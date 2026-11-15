import FreeCAD as A,FreeCADGui as G,Part,json,math,time,hashlib
from pathlib import Path
from datetime import datetime,timezone
V=A.Vector;T=time.perf_counter();OUT=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure');OLD=OUT/'day15-audio-module-layer';P=OUT/'day15-audio-region-proof';P.mkdir(exist_ok=True)
S=A.getDocument('DAY15_AUDIO_MODULE_LAYER');D=A.newDocument('DAY15_OCCUPIED_AUDIO_REGION');groups={}
for o in S.Objects:
 if o.TypeId=='App::DocumentObjectGroup':groups[o.Name]=D.addObject('App::DocumentObjectGroup',o.Name)
for o in S.Objects:
 if not hasattr(o,'Shape') or not hasattr(o.ViewObject,'ShapeColor'):continue
 q=D.addObject('PartDesign::Feature',o.Name);q.Shape=o.Shape;q.Label=o.Label;q.ViewObject.ShapeColor=o.ViewObject.ShapeColor;q.ViewObject.Transparency=o.ViewObject.Transparency;q.ViewObject.Visibility=o.ViewObject.Visibility
 for prop in ['Status','AssemblyNote','OriginalSource']:
  if hasattr(o,prop):q.addProperty('App::PropertyString',prop);setattr(q,prop,str(getattr(o,prop)))
 for g in S.Objects:
  if g.TypeId=='App::DocumentObjectGroup' and o in g.Group:groups[g.Name].addObject(q)
 if o.Name.startswith('AL_') and o.Name.endswith(('BAY','FIELD')):q.ViewObject.Visibility=False
ng=D.addObject('App::DocumentObjectGroup','LOCAL_7_PROFILES_NOT_WHOLE_HARNESS');cg=D.addObject('App::DocumentObjectGroup','OCCUPIED_PROFILE_PLUS_OUTER04_MARGIN');sg=D.addObject('App::DocumentObjectGroup','FEED_SECTION_7_CAPACITY_ACTUAL2_SPEAKER')
x0=-69.8;y0=30;R=14.;alpha=math.radians(35)
# Parallel-transport frame: upperYZbend U=Xconstant, V=(0,cos(t),sin(t)); no arbitraryworld-Z roll.
layout=[('I2S_BCLK',-2.7,-1.3,.8),('I2S_LRCLK',-.9,-1.3,.8),('I2S_DATA',.9,-1.3,.8),('AMP_V',2.7,-1.3,.8),('AMP_G',-4.5,-1.3,.8),('SPK_BTL_A',-.25,.95,1.05),('SPK_BTL_B',2.05,.95,1.05)]
def xbranch(u,v,z0,ang,sign):return V(x0+R-(R-u)*math.cos(ang),y0+v,z0+sign*(R-u)*math.sin(ang))
def arc(p,m,q):return Part.Arc(p,m,q).toShape()
rows=[];solids=[];covers=[]
for i,(n,u,v,r) in enumerate(layout):
 if i<5:
  a=xbranch(u,v,114,alpha,-1);b=xbranch(u,v,114,0,-1);b2=V(x0+u,y0+v,116)
  c=V(x0+u,16,130+v);mid=V(x0+u,16+(R+v)*math.sqrt(.5),116+(R+v)*math.sqrt(.5));e=V(x0+u,-27,130+v)
  edges=[arc(a,xbranch(u,v,114,alpha/2,-1),b),Part.makeLine(b,b2),arc(b2,mid,c),Part.makeLine(c,e)];normal=V(-math.sin(alpha),0,math.cos(alpha));start=a;end=e;radii=[R-u,R+v];counts='Pi5 upperturn ->AMP5 provisionalleftapproach. NO fiveextra wires through lowerfeed.'
 else:
  start=V(x0+u,y0+v,75);b=V(x0+u,y0+v,98);end=xbranch(u,v,98,alpha,1);edges=[Part.makeLine(start,b),arc(b,xbranch(u,v,98,alpha/2,1),end)];normal=V(0,0,1);radii=[R-u];counts='Speaker2 -> openfeed ->AMP2 provisionalleftapproach; neitherBTL wireground.'
 path=Part.Wire(edges);strand=[]
 for extra in [0,.4]:
  profile=Part.Wire([Part.makeCircle(r+extra,start,normal)]);s=path.makePipeShell([profile],True,False);expected=math.pi*(r+extra)**2*path.Length
  assert s.isValid() and len(s.Solids)==1 and abs(s.Volume-expected)<max(.001,expected*1e-5),(n,s.Volume,expected)
  o=D.addObject('PartDesign::Feature',('WIRE_' if extra==0 else 'COVER_')+n);o.Shape=s;o.ViewObject.ShapeColor=(.25,.65,.85) if i<5 else (.25,.75,.4);o.ViewObject.Transparency=0 if extra==0 else 80;o.ViewObject.Visibility=extra==0;(ng if extra==0 else cg).addObject(o);strand.append(s)
 solids.append(strand[0]);covers.append(strand[1]);missing=strand[0].cut(strand[1]).Volume;assert missing<1e-5
 rows.append(dict(name=n,u=u,v=v,diameter=2*r,extra_outer_margin=.4,min_core_R=min(radii),required_core_R=4*2*r,path_length_local_mm=path.Length,actual_full_wire_length=None,profile_start=list(start),profile_end=list(end),native_volume=solids[-1].Volume,coverage_missing_mm3=missing,valid=True,function=counts))
 # SAMEfull7sectioncapacity atfeed, though actual2speaker only pass thedeck opening.
 cu,cv=(-2.3,.95) if i==4 else (u,v)
 sec=Part.makeCylinder(r+.4,4,V(x0+cu,y0+cv,90));o=D.addObject('PartDesign::Feature','SECTION_'+n);o.Shape=sec;sg.addObject(o);o.ViewObject.Visibility=False
section=Part.makeCompound([D.getObject('SECTION_'+n).Shape for n,_,_,_ in layout]);section.exportBrep(str(P/'feed-full7-capacity.brep'));Part.makeCompound(solids).exportBrep(str(P/'nominal-local-profiles.brep'));Part.makeCompound(covers).exportBrep(str(P/'occupied-plus-margin.brep'))
plan=dict(status='SAVED_BEFORE_NAMED_LOCAL_CHECK',created_utc=datetime.now(timezone.utc).isoformat(),parent_manifest=dict(path=str(OLD/'manifest.json'),sha256=hashlib.sha256((OLD/'manifest.json').read_bytes()).hexdigest()),document=D.Name,objects=len(D.Objects),centre_vertical=[x0,y0],turn_Rcentre=R,normal_frame='Bishop/parallel U=X, Vradial inYZ, Ttangent. IndividualXZbranches analytictransport; roundprofiles, no arbitraryroll.',upper_turn=dict(start_z=116,end_z=130,y_centre=16,source_bound_derivation='Pi coolingtop126.12 +1.25 +2.1profileextent+.4margin =>129.87 lower. Capbottom135.5 -1.25 -2.0-.4=>131.85 upper. Choose130 once, R14 ->116start.'),profiles=rows,feed_cut_mm=[[-75,23,90],[-63,43,94]],section_capacity='7nominalmixedprofiles+.4outer margin; actualfeedoccupancyONLY2speaker;5I2Sabovejunction. No fictitious7wires everywhere/extraBOM.',interfaces=dict(Pi_approach='x0+u/Y-27/Z130+v, -Yapproach stops4mm beforefull1992envelopeY-31; actualexit/pinout/30reserveunchangedFIT2',AMP_approach='Two35deg analyticbranches terminateleft offullAMPbody; actualheader/padlocations/normalsUNKNOWN. ProvisionalAMPleftfaceaccessibleassumption, notmanufacturerdatum.',speaker_approach='Two verticalapproachendframesZ75/Y30.95 nearfullspeaker+Yside; actualterminal/leadlengthunqualifiedFIT2.'),raw_outer_reserve='AL_AMP_FREE_TURN_BAY gap0/common0 preservedparentraw. Emptycorner ofreserve not physicalwire. No partposition/material/profile/margin changed.',source_material_changes=False,whole_harness_pass=False,physical_pass=False,print_release=False,actual_cut_slack_length=None,build_wall_seconds=time.perf_counter()-T)
(P/'proposal.json').write_bytes((json.dumps(plan,ensure_ascii=False,indent=2)+'\n').encode());D.Label='DAY15 occupied audio region — checks pending';D.recompute();A.setActiveDocument(D.Name);G.activeDocument().activeView().viewAxonometric();G.activeDocument().activeView().fitAll();D.saveAs(str(P/'audio-region-proof.FCStd'));print(json.dumps({'saved_before_tests':D.FileName,'objects':len(D.Objects),'profiles':rows,'seconds':plan['build_wall_seconds']}))
