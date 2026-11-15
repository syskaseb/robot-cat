import FreeCAD as A,FreeCADGui as G,Part,json,hashlib,time
from pathlib import Path
from datetime import datetime,timezone
V=A.Vector;T=time.perf_counter();OUT=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure');OLD=OUT/'day15-shared-module-fit';P=OUT/'day15-audio-module-layer';P.mkdir(exist_ok=True)
S=A.getDocument('DAY15_SHARED_MODULE_PROPOSAL');D=A.newDocument('DAY15_AUDIO_MODULE_LAYER');groups={};identity=[]
for o in S.Objects:
 if o.TypeId=='App::DocumentObjectGroup':groups[o.Name]=D.addObject('App::DocumentObjectGroup',o.Name)
for o in S.Objects:
 if not hasattr(o,'Shape') or not hasattr(o.ViewObject,'ShapeColor'):continue
 q=D.addObject('PartDesign::Feature',o.Name);q.Shape=o.Shape;q.Label=o.Label;q.ViewObject.ShapeColor=o.ViewObject.ShapeColor;q.ViewObject.Transparency=o.ViewObject.Transparency;q.ViewObject.Visibility=o.ViewObject.Visibility
 for prop in ['Status','AssemblyNote','OriginalSource']:
  if hasattr(o,prop):q.addProperty('App::PropertyString',prop);setattr(q,prop,str(getattr(o,prop)))
 for g in S.Objects:
  if g.TypeId=='App::DocumentObjectGroup' and o in g.Group:groups[g.Name].addObject(q)
 identity.append(dict(name=o.Name,isSame_after_assignment=q.Shape.isSame(o.Shape)))
new=D.addObject('App::DocumentObjectGroup','AUDIO_LAYER_COARSE_SUPPORT_NOT_PRINT_PARTS');fields=D.addObject('App::DocumentObjectGroup','AUDIO_CONNECTED_BAYS_SOURCE_PORT_FIT_OPEN');rows=[]
def box(p,s):return Part.makeBox(*s,V(*p))
def bb(s):
 b=s.BoundBox;return [[b.XMin,b.YMin,b.ZMin],[b.XMax,b.YMax,b.ZMax]]
def feature(n,s,role,group=new,color=(.65,.76,.83),visible=False):
 o=D.addObject('PartDesign::Feature',n);o.Shape=s;o.ViewObject.ShapeColor=color;o.ViewObject.Visibility=visible;o.addProperty('App::PropertyString','AssemblyNote').AssemblyNote=role;group.addObject(o);rows.append(dict(name=n,bounds_mm=bb(s),role=role));return o
def move_whole(name,rotation,targetmin):
 o=D.getObject(name);s=o.Shape.copy();oldbb=bb(s);vol=s.Volume
 if rotation:s.rotate(V(0,0,0),V(*rotation[0]),rotation[1])
 b=s.BoundBox;s.translate(V(targetmin[0]-b.XMin,targetmin[1]-b.YMin,targetmin[2]-b.ZMin));assert s.isValid() and abs(s.Volume-vol)<1e-5;o.Shape=s
 return dict(object=name,old_bounds=oldbb,new_bounds=bb(s),volume_mm3=vol,rigid_no_scale=True)
changes=[move_whole('MAX98357A_amp',((1,0,0),90),[-62,21,96]),move_whole('Speaker',None,[-113,-19.5,65.5])]
# ONE audioassemblytopology: lowerSPEAKER shelf aboveallWAGOs; uprightfullAMP oncommonLwing; backmic+touch liftsasone.
ms=[box((-113,-22,63),(100,50,2.5)),box((-104,-86,63),(6,172,2.5)),box((-17,-35,63),(4,70,2.5)),box((-17,-35,65.5),(4,4,24.5)),box((-17,31,65.5),(4,4,24.5)),box((-17,-35,88),(4,70,2)),box((-62,21,94),(3,13,2)),box((-38,21,94),(3,13,2))]
oldmaster=D.getObject('CF_COMMON_LOAD_ENVELOPE').Shape
feed=box((-75,23,89.99),(12,20,4.02));intended_base=oldmaster.cut(feed);joined=intended_base
for s in ms:joined=joined.fuse(s)
loss=[s.cut(joined).Volume for s in [intended_base]+ms];assert joined.isValid() and len(joined.Solids)==1 and max(loss)<1e-5
D.getObject('CF_COMMON_LOAD_ENVELOPE').Shape=joined
for i,s in enumerate(ms):feature('AL_added_material_'+str(i),s,'Namedmember ofSAMEcommonrigidmaterial; hiddenreference, no duplicateBOM')
capms=[box((-104,y,95.52),(6,6,42.48)) for y in [-86,80]]+[box((95,y,107),(12,6,31)) for y in [-86,80]]
# Explicitmembers keptsimple foractualcoverage andlaterflatprintparting.
capms += [box((-104,-86,135.5),(6,172,2.5)),box((95,-86,135.5),(12,172,2.5)),box((-104,-23,135.5),(211,3,2.5)),box((-104,20,135.5),(211,3,2.5)),box((-5,-20,135.5),(86,40,2.5)),box((5,20,135.5),(25,45,2.5))]
capms += [box((x,-17.5,138),(5,35,2)) for x in [-5,76]]+[box((x,45,138),(3,20,3)) for x in [5,27]]
cap=capms[0]
for m in capms[1:]:cap=cap.fuse(m)
closs=[m.cut(cap).Volume for m in capms];assert cap.isValid() and len(cap.Solids)==1 and max(closs)<1e-5
feature('AL_REMOVABLE_MIC_TOUCH_FRAME',cap,'OneCOARSEremovableuppermic/touchassembly:fourrealportalbearingfeet, factoryUSB_AUDIOdetach beforelift. M3parting/pressurekeepersOPEN; noboughtparts fused.',visible=True)
for i,m in enumerate(capms):feature('AL_cap_member_'+str(i),m,'Hiddenmemberreference; integralcapmaterialnotseparateoverlappingprints')
cover=feature('RS_USB_FULL_SOURCE_COVER',box((-9,-21.5,140),(94,43,16)),'Savedwavego studyReSpeakerPCB86x35 + assumedUSB/components ->94x43x16. Provisionalfullsourcecover, NOTexactmanufacturerbody or extraBOM.',fields,(.82,.64,.5),True);cover.ViewObject.Transparency=85
top=feature('AL_I2S_FREE_TOP_BAY',box((-70,-31,131.25),(18,65,3)),'5lowvoltageI2S/P/G insulatedprofilesnominal1.6, .2gap:flatwidth8.8 +edgeallowance within18x3. R6.4projectdryfitassumption. Connectedtoentryfields, NOTactualmanufacturermouthproof.',fields,(.9,.58,.17),True);top.ViewObject.Transparency=85
feature('AL_AMP_TO_SPEAKER_SIDE_BAY',box((-73,27.5,75),(8,5,54)),'7profiles in2rows:5signals/P/G at1.6 +2speaker at2.1, .2gap/.4margin ->7.8x4.7 inside8x5. Shared12x20openfeedcut throughLwing; laywiresBEFOREuprightPCA closesedge. Sourcejackets/actualendsFIT2, pairedBTLoutputsNEITHERground.',fields,(.9,.58,.17),True).ViewObject.Transparency=85
feature('AL_AMP_I2S_ENTRY_FIELD',box((-70,21,96),(10,13,38.25)),'ProvisionalAMPownterminalinterface overlapsfullmoduleenvelope bydesign; freespanfieldabove/side mustclearforeignmaterials. Actualheadernormal/variantOPEN.',fields,(.9,.58,.17),True).ViewObject.Transparency=85
feature('BNO_FULL_SOURCE_INSTALLATION_COVER',box((-102.2,-50.65,80),(30,28,10)),'Savedstudy30x28x10 fullinstalledconnectorallowance aroundretained25.6x22.7x4.6BNO. ProjectassumptionNOTsupplierguarantee; do not shrinkto barePCB.',fields,(.8,.6,.45),True).ViewObject.Transparency=85
# Sourceproofisprojecthistoricalcontract, notsupplierqualification orelectricalrewiring.
src=Path('C:/Users/Sysq/PycharmProjects/robot-cat/hardware/wavego/layout/components.json');d=json.loads(src.read_bytes());facts=[q for q in d['components'] if q['id'] in ['Speaker','Amplifier','ReSpeaker','Touch','IMU']]
plan=dict(status='ONE_WHOLE_AUDIO_LAYER_SAVED_BEFORE_CHANGED_GATES',created_utc=datetime.now(timezone.utc).isoformat(),parent_manifest=dict(path=str(OLD/'manifest.json'),sha256=hashlib.sha256((OLD/'manifest.json').read_bytes()).hexdigest()),document=D.Name,objects=len(D.Objects),rigid_changes=changes,source_identity=identity,new_members=rows,intended_feed_cut=dict(bounds=bb(feed),actual_removed_mm3=oldmaster.cut(intended_base).Volume,function='ONEsharedopenwirefeed, notAMPclearancetrim; roots/rails/Pi seat outsidecut unchanged; PCAedge2lands/actualretentionqualifyNEXT'),old_common_material_missing_mm3=loss[0],all_new_common_members_missing_mm3=loss[1:],uppercap_member_missing_mm3=closs,common_material_valid=joined.isValid(),common_material_solids=len(joined.Solids),uppercap_valid=cap.isValid(),uppercap_solids=len(cap.Solids),retention='Sourceclamps/steel/BUS/other57identical. Newaudioframeparting/4M3upperretainers/boardedgekeepers/actualspeakermountpattern unqualifiedESSENTIALNEXT notproductionCAD.',source_audio_contract=dict(path=str(src),sha256=hashlib.sha256(src.read_bytes()).hexdigest(),facts=facts),source_signal_contract=dict(path='C:/Users/Sysq/PycharmProjects/robot-cat/hardware/archive/electronics-wavego-20261017/README.md',scope='ARCHIVEDprojectinterfaceonly:AMP I2SGPIO18/19/21; ReSpeaker separateUSB; pairedspeakerBTL no ground. Currentfinalpinouts/cableSKUsnotqualified.'),access_order='Banks/fullends onfoundation ->placecommonframe/speakershelf ->fullspeaker+uprightAMP/otherPCB ->openGPIOI2S/pairedspeaker/USB_AUDIOlead ->removablebackmic+touchframe ->skinslate. Battery:micUSB_AUDIOdetach/topframe off ->existingBUSUSB/powerdetach/bridgeoff ->batteryunplug/lift. E1soldernevervirtuallyunplug.',stock='USB500Delock remainsONEseparateBUS cable. USB_AUDIOrequired separatelead/unboundSKUandlength; no second500credit. Four220/bothMTA/FHAC84.5/K1474unchanged, actualcut/fit/slackNULL.',physical_pass=False,print_release=False,build_wall_seconds=time.perf_counter()-T)
D.Label='DAY15 audio shared-layer proposal — changedchecks pending';D.recompute();A.setActiveDocument(D.Name);G.activeDocument().activeView().viewAxonometric();G.activeDocument().activeView().fitAll();D.saveAs(str(P/'audio-layer-proposal.FCStd'));(P/'proposal.json').write_bytes((json.dumps(plan,ensure_ascii=False,indent=2)+'\n').encode());print(json.dumps({'saved_before_checks':D.FileName,'objects':len(D.Objects),'changes':changes,'common_solids':len(joined.Solids),'cap_solids':len(cap.Solids),'seconds':plan['build_wall_seconds']}))
