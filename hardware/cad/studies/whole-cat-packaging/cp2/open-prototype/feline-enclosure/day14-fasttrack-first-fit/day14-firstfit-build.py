import FreeCAD as A, Part, FreeCADGui as G, json, math, hashlib, csv, time
from pathlib import Path
from datetime import datetime, timezone
T=time.perf_counter()
OUT=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day14-fasttrack-first-fit')
MECH=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical')
SIM=Path('C:/Users/Sysq/PycharmProjects/robot-cat')
V=A.Vector
idx=json.loads((OUT.parent/'day11-GUI-working-snapshot-source-index.json').read_text())['actor_names_to_objects']
old=A.getDocument('day11_WORKING_UNSELECTED_N01_0of10')
src=A.getDocument('WAVEGO_PRO_BETA_v3')
D=A.newDocument('DAY14_WAVEGO_FIRST_FIT_UNRELEASED')
rows=[]; checks=[]
groups={}
for name in ['WAVEGO_SOURCE','Shared_structure_PROPOSED','Selected_parts','Appearance_extension','Harness_regions','Ola_ENVELOPE_not_print']:
    groups[name]=D.addObject('App::DocumentObjectGroup',name)
def bb(s):
    b=s.BoundBox
    return [[b.XMin,b.YMin,b.ZMin],[b.XMax,b.YMax,b.ZMax]]
def put(name,s,kind='selected_source',source='',group='Selected_parts',color=(.2,.65,.38),trans=0,notes=''):
    o=D.addObject('PartDesign::Feature',name)
    o.Label=name
    o.Shape=s
    o.addProperty('App::PropertyString','EvidenceClass').EvidenceClass=kind
    o.addProperty('App::PropertyString','SourceIdentity').SourceIdentity=source
    o.addProperty('App::PropertyString','FitStatus').FitStatus='UNRELEASED_FIRST_FIT_NO_PHYSICAL_PASS'
    o.addProperty('App::PropertyString','AssemblyNote').AssemblyNote=notes
    o.ViewObject.ShapeColor=color;o.ViewObject.LineColor=(.12,.12,.14);o.ViewObject.Transparency=trans
    groups[group].addObject(o)
    rows.append(dict(id=name,object=o.Name,evidence=kind,source=source,bounds_mm=bb(s),volume_mm3=s.Volume,notes=notes))
    return o
def box(name,p,d,**kw): return put(name,Part.makeBox(*d,V(*p)),**kw)
def original(actor):
    o=old.getObject(idx[actor]);s=o.Shape.copy()
    s.Placement=o.getGlobalPlacement()*o.Placement.inverse()*s.Placement
    return s
def placed(actor,p,rot=None):
    s=original(actor)
    if rot:s.rotate(V(),rot[0],rot[1])
    b=s.BoundBox;s.translate(V(p[0]-b.XMin,p[1]-b.YMin,p[2]-b.ZMin))
    return s
def actual(name,actor,p,rot=None,**kw): return put(name,placed(actor,p,rot),source=actor,**kw)
def assumed(name,p,d,**kw):
    return box(name,p,d,kind='nominal_selected_or_extension_installation_envelope',color=(.36,.56,.85),**kw)
def struct(name,p,d,**kw):
    return box(name,p,d,kind='PROPOSED_shared_support_blank_not_print_ready',group='Shared_structure_PROPOSED',color=(.74,.73,.67),**kw)
root=src.getObject('WAVEGO_PRO_BETA_v3')
S=root.Shape.copy();S.Placement=root.getGlobalPlacement()*root.Placement.inverse()*S.Placement
assert len(S.Solids)==126 and S.isValid()
base=put('WAVEGO_complete_126_source_solids',S,group='WAVEGO_SOURCE',source=str(SIM/'hardware/wavego/WAVEGO_PRO_BETA_v3.FCStd'),color=(.28,.29,.32))
for y in [-22.5,22.5]:
    s=Part.makeBox(214,10,7,V(-86,y-5,38.52))
    for x in [-80,-70,112,122]:s=s.cut(Part.makeCylinder(1.35,8,V(x,y,38.02)))
    put('Load_rail_'+str(y).replace('-','minus'),s,kind='PROPOSED_source8hole_rail',group='Shared_structure_PROPOSED',notes='Source frame through 8 existing vertical holes; M2.5 actual grip/thread/revision fit required. Not only thin cover bearing.',color=(.73,.71,.65))
struct('Deck_front_blank',[-105,-82,45.52],[135,164,3],notes='Split plate at X30, supported on both rails. Lap/4 joining screws to detail after whole review.')
struct('Deck_rear_blank',[30,-82,45.52],[130,164,3],notes='164x130 fits 256 bed. Same operating plane; no unsupported loose halves at assembly.')
for i in range(8):
    for sign in [-1,1]:
        actual('WAGO415_data_%s_%s'%(sign,i),'Station:D_FL:case',[-47+22*i,9 if sign>0 else -39,50.52],notes='One of sixteen selected 221-415; lever/port access before battery tray.')
for i,x in enumerate([-100,-73]):
    for j,y in enumerate([-39,2]):assumed('WAGO615_power_%s_%s'%(i,j),[x,y,50.52],[22,37,11],source='selected WAGO221-615 x4; current nominal case dimensions')
assumed('POST_F0_WAGO412',[-130,39,50],[13,20,10],source='Selected221-412, nominal fit envelope; verify lever and ports')
# Twelve complete fuse assemblies: the same selected CP2 + IN + OUT + ATO source parts, not bare cases.
factors=['Ref_Material_F_L1_CP2_Housing_0_0','Ref_Material_F_L1_ATO_0_0','Ref_Material_F_L1_IN_0_0','Ref_Material_F_L1_OUT_0_0']
resolved=[]
for actor in factors:
    if actor not in idx:
        candidates=[k for k in idx if 'F_L1' in k and actor.split('F_L1_')[-1].split('_0_0')[0] in k]
        if len(candidates)!=1: raise RuntimeError('Missing named fuse member '+actor+' candidates '+str(candidates))
        actor=candidates[0]
    resolved.append(actor)
fusegroup=Part.makeCompound([original(a) for a in resolved]);fusegroup.rotate(V(),V(1,0,0),90)
for side in [-1,1]:
    for i in range(6):
        s=fusegroup.copy(); b=s.BoundBox;s.translate(V(-94+24*i-b.XMin,(50 if side>0 else -78)-b.YMin,52-b.ZMin))
        put('Motor_ATO4A_%s_%s'%(side,i),s,source=' + '.join(resolved),notes='Complete selected MTA0300330 + two different TE ends + ATO4A. Vertical open bank, six per side; full factory jackets/end access required.')
for i,x in enumerate([-90,-35,20,75]):
    assumed('Leg_protected_MTA0100335_%s'%i,[x,-48.5,64],[35.5,8.1,8.9],source='selected MTA0100335 x4 actual nominal case; complete independent220mm leads/both ends retained',notes='Body shown. 220mm leads adaptive in open per-leg group; actual reach/motion not yet checked.')
for i,role in enumerate(['Pi3A','AUX4A','Yaw1A','Pitch1A','Tail1A']):
    assumed('FHAC0001_'+role,[55+23*i,56,50],[20.25,22,51],source='selected FHAC0001ZXJ full51x22x20.25 rotated vertical',notes='Open right-rear service panel. Full two factory leads each >=84.5; final installed reach unqualified.')
assumed('F0_FHAC0002_30A',[-130,-35,49],[26,70,35],source='selected FHAC0002ZXJ+30A; conservative installation assumption, not exact bought material')
actual('Battery_GEA223S30X6GT','BatterySelectedNominal',[-2,-17.5,65],notes='106.5x35x21.5 selected nominal. 2 selected straps, unplug XT60/balance before vertical lift; skin/mic panel removes first.')
struct('Battery_tray_shared',[-5,-21,62],[113,42,3],notes='Supported off deck on two side standoffs, removable to expose WAGO. Two strap slots and corner stops to detail.')
for x in [5,95]:
    for y in [-25,21]:struct('Tray_standoff_%s_%s'%(x,y),[x,y,48.52],[5,4,13.48])
assumed('XT60H_mated_with_boots',[5,-47,79],[50,24,18],source='selected XT60H pair mating/wire allowance',notes='Battery-side plug/lead flexible, no rigid support over battery extraction.')
actual('Pi4B_actual_PCB','Ref_Material_Pi4NominalPCB_0_0',[-98,-38,98.52],rot=(V(0,0,1),180),notes='Actual PCB only. Four standoffs from deck; USB/data/mates separately allocated.')
assumed('Pi_components_and_cooling',[-98,-38,100.12],[85,56,26],source='Pi selected physical PCB + conservative populated cooling envelope',trans=68)
assumed('Pi_USB_DATA_Delock_mating',[-124,-44,98.52],[26,26,24],source='Lanberg500 + selected current Delock60047; installation datum pending',trans=65)
assumed('Pi_GPIO1992_factory_female',[-88,-47,107],[52,16,23],source='Selected1992+factory female ends, installed assembly envelope',trans=65)
actual('PCA9685_Adafruit815_PCB','Ref_Material_PWM9685NominalPCB_0_0',[-95,38,94],rot=(V(1,0,0),90),notes='62.23x25.4 source board vertical on common shelf, header/mating verification required.')
assumed('BUS25514_installed',[-80,-4,126],[42,33,24],source='Current selected25514 PCB33.024x42.024 plus provisional component/mating height; source actual board available')
assumed('E1_populated_prototype_board',[-25,38,94],[50,10,30],source='selected Adafruit1608/1208, translator, 78L05, caps, Harwin headers/resistors; coarse populated-board fit',notes='Not old GrovePWM module. Electrical source wiring unchanged.')
actual('MAIN_Pololu4853','Ref_Material_MAIN_CurrentMainSupplierReference_0_0',[61,22,94],notes='Source selected PCB/component reference, not historical 46.52 support.')
actual('AUX_Pololu4092','Ref_Material_AUX4092NominalPCB_0_0',[99,22,94])
assumed('S1_NKK_S821_installed',[71,47,116],[22,22,40],source='selected S821 including lever/tool nominal reserve')
actual('Monitor_MOD05015','Station:Monitor:case',[115,20,125],rot=(V(0,0,1),90),notes='Nominal41x25x12; visible rear top window. Balance connector/factory reach remain physical fit.')
# Normalize the WHOLE selected S0 using the actual cylindrical neck axis, all 11 materials together.
s0actors=[k for k in idx if k.startswith('Ref_Material_S0_') and k.endswith('_0_0')]
assert len(s0actors)==11, s0actors
neck=original(next(k for k in s0actors if 'neck' in k));key=original(next(k for k in s0actors if '_key_' in k))
cyl=[f.Surface for f in neck.Faces if isinstance(f.Surface,Part.Cylinder)]
axis=max(cyl,key=lambda c:c.Radius).Axis
if (key.CenterOfMass-neck.CenterOfMass).dot(axis)<0:axis=-axis
rot=A.Rotation(axis,V(0,0,1));pl=A.Placement(V(),rot)
s0shapes=[]
for a in s0actors:
    s=original(a);s.Placement=pl*s.Placement;s0shapes.append(s)
q=Part.makeCompound(s0shapes);b=q.BoundBox;shift=V(107-b.XMin,-68-b.YMin,48.52-b.ZMin)
for a,s in zip(s0actors,s0shapes):
    s.translate(shift);put('S0_'+a.split('S0_')[1].split('_CP2')[0],s,source=a,notes='Full11 bought body/key/neck/8metal, one actual-neck rigid rotation to +Z. No sourceXML applied twice.')
q=Part.makeCompound(s0shapes);s0bb=bb(q)
necknew=next(s for a,s in zip(s0actors,s0shapes) if 'neck' in a);nc=necknew.CenterOfMass
panelz=necknew.BoundBox.ZMin
panel=Part.makeBox(70,72,3,V(107,-76,panelz-3)).cut(Part.makeCylinder(12.2,5,V(nc.x,nc.y,panelz-4)))
put('Rear_S0_shared_panel_BLANK',panel,kind='PROPOSED_rear_frame_rooted_panel',group='Shared_structure_PROPOSED',notes='Neck aperture from actual upright source, source nominal M6pair laterfit. Rear crossbeam rooted at sourceX112/122; whole plate not cosmetic skin.')
for y in [-76,-7]:struct('S0_panel_endstand_'+str(y),[169,y,48.52],[8,3,max(3,panelz-48.52)])
struct('Rear_crossbeam',[112,-79,48.52],[65,161,4],notes='Rear service panel + light tail load to rear source-hole rails; geometry/load/actualfastener checks pending.')
# Four actual fixed PCB standoffs on two common simple shelves, not historical local grips.
for x in [-98,-18]:
    for y in [-38,13]:struct('Pi_standoff_%s_%s'%(x,y),[x,y,48.52],[5,5,50])
struct('Logic_common_side_shelf',[-102,31,91],[232,5,3],notes='Shared vertical-board and MAIN/AUX shelf on end standoffs; not 232mm unsupported finished beam.')
for x in [-102,25,125]:struct('Logic_shelf_post_'+str(x),[x,31,48.52],[5,5,42.48])
assumed('Speaker',[-105,-22.5,51],[100,45,21],group='Appearance_extension',source='Required appearance extension; oldlayout nominal100x45x21, exact selected revision to fit')
assumed('BNO085',[-100,-48,51],[25.6,22.7,4.6],group='Appearance_extension',source='required BNO085 oldlayout nominal; ports fit pending')
assumed('MAX98357A_amp',[-60,-39,75],[27,24,13],group='Appearance_extension',source='required amp installation envelope')
assumed('ReSpeakerLite_on_REMOVABLE_back',[-5,-17.5,140],[86,35,10],group='Appearance_extension',source='required ReSpeakerLite nominal86x35; thickness10 provision',notes='Skin/mic module removes as one before battery lift; factory lead disconnect accessible, no automatic soldered module unplug.')
assumed('TTP223_touch',[5,45,141],[25,20,8],group='Appearance_extension',source='required touch board, nominal envelope under thin isolated touch window')
assumed('Camera3_NoIR_Wide',[-232,-37.5,130.6],[12.4,25,24],group='Appearance_extension',source='required module3wide nominal, lens forward -X; CSI flexible loop through yaw/pitch required')
assumed('VL53L5CX',[-238,-13,110],[14,26,26],group='Appearance_extension',source='required ToF module nominal reserved, optical window forward')
for name,p in [('Head_yaw',[-137,-6.1,89]),('Head_pitch',[-166,-23,130]),('Tail',[173,-6.1,109])]:
    assumed('MG92B_'+name,p,[23,12.2,28],source='selected MG92B positional, nominal body23x12.2x28; tabs/shaft interface prototype fit')
    assumed('MG92B_'+name+'_bracket_space',[p[0]-5,p[1]-5,p[2]-2],[33,22.2,32],source='proposed support/tab/cable envelope',group='Harness_regions',trans=80)
for z in [120,134]:
    b=Part.makeCylinder(11,7,V(-126,0,z)).cut(Part.makeCylinder(4,7,V(-126,0,z)))
    put('Yaw608_'+str(z),b,source='selected608-2Z x3; two yaw, one tail',color=(.7,.7,.72))
b=Part.makeCylinder(11,7,V(185,0,137)).cut(Part.makeCylinder(4,7,V(185,0,137)))
put('Tail608',b,source='selected608-2Z third',color=(.7,.7,.72))
b=Part.makeCylinder(8,5,V(-155,14,141),V(0,1,0)).cut(Part.makeCylinder(4,5,V(-155,14,141),V(0,1,0)))
put('Pitch688',b,source='selected688-2RS8x16x5',color=(.7,.7,.72))
struct('Neck_shared_root',[-137,-11,48.52],[22,22,39],notes='Coarse shared two-bearing neck/load bracket on front rail crosspiece. Yaw axis(-126,0), pitch(-155,Y,141). Bearing/servo coupling geometry next after whole review.')
struct('Tail_shared_root',[171,-15,52.52],[27,30,54.48],notes='Simple removable rear bracket tied to rear crossbeam, not skin bearing.')
# Open connected harness layers. They describe grouped flexible installation space, not rigid wires or print material.
regions=[('Lower_data_open',[-48,-8,50.52],[177,16,11],'16WAGO leads branched by motor/BUS; hands lay before tray'),('Right_logic_open',[-100,29,124],[255,18,13],'GPIO/PWM/E1/MAIN/AUX; not high-current packing'),('Left_power_open',[-100,-49,74],[255,15,12],'4protectedleg220+power branches; full ends adaptive, explicit side access'),('Rear_aux_open',[130,-5,55],[25,45,60],'S0/S1/monitor/fuse factory ends, independent strains'),('USB500_loose_loop',[-100,-30,128],[170,55,10],'Separate full500USB retained, R30 project planning basis; actual mouth-to-mouth fit pending'),('Four_220_joint_exits',[-100,-78,48.52],[248,18,26],'Four INDEPENDENT full220 units; each leg joint slack to test; no cut/pool'),('E2_Molex_and_inline_WAGO',[120,1,92],[35,18,25],'Molex43025/43020 full nominal26x12x12 plus8inline221-2411 distributed at head/tail; exact local connector fit pending')]
for n,p,d,note in regions:box(n,p,d,kind='GROUP_FLEXIBLE_INSTALLATION_SPACE_NOT_CLEARANCE_PASS',group='Harness_regions',source='selected wiring graph / planning region',color=(.9,.58,.17),trans=85,notes=note)
# Rounded cosmetic volumes: simple analytic lofts; cosmetic envelope not solid production shell/mass.
def ellipsewire(x,y,z,ry,rz):
    pts=[V(x,y+ry*math.cos(2*math.pi*i/48),z+rz*math.sin(2*math.pi*i/48)) for i in range(48)]
    c=Part.BSplineCurve();c.interpolate(pts,PeriodicFlag=True)
    return Part.Wire(c.toShape())
wires=[ellipsewire(x,0,z,ry,rz) for x,ry,rz,z in [(-115,50,35,84),(-50,90,55,103),(50,90,55,103),(130,80,53,102),(170,55,35,89)]]
put('Ola_body_ENVELOPE',Part.makeLoft(wires,True,False),kind='COSMETIC_ENVELOPE_NOT_PRINT_READY',group='Ola_ENVELOPE_not_print',color=(.08,.085,.10),trans=82,notes='Open underside above49, removableback; no assumed structural skin. Rounded arched back from Ola reference.')
headw=[]
for x in [-228.9,-215,-174,-133,-119.1]:
    f=math.sqrt(max(.003,1-((x+174)/55)**2));headw.append(ellipsewire(x,0,141,65*f,50*f))
put('Ola_head_ENVELOPE',Part.makeLoft(headw,True,False),kind='COSMETIC_ENVELOPE_NOT_PRINT_READY',group='Ola_ENVELOPE_not_print',color=(.08,.085,.10),trans=75)
for sign in [-1,1]:
    ear=Part.makeLoft([ellipsewire(-183,sign*42,183,20,16),ellipsewire(-178,sign*48,207,10,15),ellipsewire(-172,sign*51,219,2.5,4)],True,False)
    put('Ola_ear_'+str(sign),ear,kind='COSMETIC_ENVELOPE',group='Ola_ENVELOPE_not_print',color=(.12,.12,.14),trans=35)
    ring=Part.makeCylinder(13,2,V(-232,sign*28,146),V(1,0,0)).cut(Part.makeCylinder(10,2,V(-232,sign*28,146),V(1,0,0)))
    put('Ola_eye_gold_'+str(sign),ring,kind='COSMETIC_REFERENCE',group='Ola_ENVELOPE_not_print',color=(.83,.59,.15))
put('Ola_muzzle',Part.makeSphere(18,V(-229,0,122)),kind='COSMETIC_ENVELOPE',group='Ola_ENVELOPE_not_print',color=(.13,.13,.15),trans=30)
put('Ola_nose',Part.makeSphere(6,V(-245,0,126)),kind='COSMETIC_REFERENCE',group='Ola_ENVELOPE_not_print',color=(.04,.04,.05))
tailw=[Part.Wire(Part.makeCircle(r,V(x,0,z),V(1,0,1))) for x,z,r in [(185,142,8),(210,165,7),(229,199,5),(233,214,3)]]
put('Ola_tail_ENVELOPE',Part.makeLoft(tailw,True,False),kind='COSMETIC_ENVELOPE',group='Ola_ENVELOPE_not_print',color=(.09,.09,.11),trans=25)
D.recompute(); A.setActiveDocument(D.Name);G.activeDocument().activeView().viewAxonometric();G.activeDocument().activeView().fitAll()
for name in groups:groups[name].ViewObject.Visibility=True
G.activeDocument().activeView().setAnimationEnabled(False) if hasattr(G.activeDocument().activeView(),'setAnimationEnabled') else None
checks.append(dict(hazard='BASE_NEUTRAL_VS_NEW_DECK',base_zmax=S.BoundBox.ZMax,deck_zmin=45.52,neutral_vertical_separation_mm=45.52-S.BoundBox.ZMax,status='NEUTRAL_HEIGHT_BOUND_ONLY_motion_and_anchor_contact_not_pass'))
batt=D.getObjectsByLabel('Battery_GEA223S30X6GT')[0].Shape
checks.append(dict(hazard='S0_WHOLE11_VS_BATTERY',s0_bounds=s0bb,case_axis_original=list(axis),neck_panel_z=panelz,gap_mm=q.distToShape(batt)[0],common_mm3=q.common(batt).Volume,status='ACTUAL_SOURCE_GEOMETRY_NEUTRAL_PAIR_ONLY'))
source_paths=[SIM/'hardware/wavego/WAVEGO_PRO_BETA_v3.FCStd',SIM/'hardware/wavego/WAVEGO_PRO_BETA_v3_motion.FCStd',MECH/'hardware/electronics/kicad-current/selected-components.csv',MECH/'hardware/electronics/kicad-current/design.json',MECH/'hardware/reference/appearance/ola-cat-reference.jpg',SIM/'hardware/wavego/layout/components.json',OUT.parent/'day11-GUI-working-snapshot-source-index.json']
sources=[dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size) for p in source_paths if p.exists()]
selection=list(csv.DictReader((MECH/'hardware/electronics/kicad-current/selected-components.csv').open(encoding='utf-8-sig')))
plan=dict(status='ONE_UNRELEASED_WHOLE_FIRST_FIT_FOR_REVIEW_NOT_PRINT_OR_PHYSICAL_PASS',created_utc=datetime.now(timezone.utc).isoformat(),coordinate_frame='Unscaled WAVEGO source world; front-X, up+Z; source aggregateworld once126solids. Prior localleaf bound table is NOT global.',document=D.Name,native_file='first-fit.FCStd',base=dict(solids=len(S.Solids),volume_mm3=S.Volume,bounds_mm=bb(S),source_retained_without_scaling=True),new_deck_mm=dict(x=[-105,160],y=[-82,82],z=[45.52,48.52],split_x=30),body_envelope_mm=dict(x=[-115,170],y=[-90,90],z=[48,158]),rows=rows,checks=checks,sources=sources,selected_rows=selection,selected_rows_count=len(selection),source_shape_reuse='Only selected bought shapes from old1311 reference, no old printed mounts or world poses. Transform once then relocate as WHOLE components.',appearance_extension='Userrequired camera/ToF/BNO/audio/touch added using oldnominal envelopes; not in current electricalCSV, revision/electricalintegration unqualified.',assembly_order=['A+B: verify source8hole revision, clamp/load path; fit 2rails and splitdeck on open base','A: mount lower WAGO/power and open12motorfuse banks; B: preterminate/sourcegraph benchkit, retain4independent220/bothends','Mount speaker/BNO/amp and shared logic shelf, then Pi/PCA/E1/BUS/MAIN/AUX; driverbeforewires, insulatedstand-offs','Install S0 rear structuralpanel/terminalguard, five auxiliaryfuses/S1/monitor, fixedlead strains; no load carried by wires','Fit removablebatterytray and2straps, battery unplugged; XT60/balance access; lowerWAGO maintenance by tray removal','Fit 3MG/bearings/head/tail, camera/ToF and CSI/servo adaptive loops; route selected500USB whole, head/tailproof test pending','Lay grouped harness openly, perleg movement/slack checks and sourcebudget audit only changed actualpaths; add terminalguards','Last: removable back/microphone skin and head/tail cosmetics; battery lifts vertically after removableback, occasionalrepair partial disassembly'],uncertainties=[dict(id='FIT1',question='Owned WAVEGO revision, 8hole engagement, added payload and hip clearance',check='8hole 1:1 template / small root coupon, weigh whole kit, hand-cycle all 12 joints with platform before any powered trial',no_claim='No new kinematic/fullpayload approval'),dict(id='FIT2',question='Fullselected connector/factorylead reach and protection assembly',check='Openbench dryfit sourcegraph: four separate220 bothends,12motorfuses TE+ATO, all WAGO, fiveFHAC leads>=84.5, K1474 allocations210 input vs350Pi, fullUSB500+Delock, PiGPIO30reserve, balance/mating and actualR/OD; adjust shared layers rather than cut/extend',no_claim='Installed cut/route/stock/slack NULL; all source factoryends and budgets retained'),dict(id='FIT3',question='Head/tail bearing linkage, optical/CSI and Ola mass/proportion',check='One open head/tail mockup with 3MG/3x608/688, weigh lever and hand-turn head then skin cardtemplate; verify all sensor revisionports',no_claim='No production strength/complete skin/print readiness')],mass_note='No actual payload weigh-in. Expect roughly0.9..1.4kg added including protection/cables/prints; this is a risk estimate, not calculated mass or servo capability.',old_history='Old N01rev1 remains0/10 archived; no priorscore or geometryPASS transferred by name. Old55/R35.1/framehomes not automatic new constraints. Existing electricalgraph and proper physical stock accounting preserved.',wall_seconds=time.perf_counter()-T)
(OUT/'layout.json').write_bytes((json.dumps(plan,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
D.Label='DAY14 WAVEGO FIRST FIT — UNRELEASED / one arrangement'
D.recompute();D.saveAs(str(OUT/'first-fit.FCStd'))
print(json.dumps(dict(saved=str(OUT/'first-fit.FCStd'),objects=len(D.Objects),rows=len(rows),s0_bounds=s0bb,checks=checks,elapsed=time.perf_counter()-T)))
