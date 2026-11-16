import FreeCAD as A,FreeCADGui as G,json
from pathlib import Path
from PySide import QtCore
D=A.ActiveDocument;P=Path(__file__).parent;O=P.parent
before={'name':D.Name,'label':D.Label,'file':D.FileName,'objects':len(D.Objects),'modified':G.activeDocument().Modified}
def rows(names):
 out=[]
 for n in dict.fromkeys(names):
  o=D.getObject(n)
  if o is None or not hasattr(o,'Shape') or hasattr(o,'Group'):continue
  b=o.Shape.BoundBox;out.append({'name':n,'label':o.Label,'bounds_mm':[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax],'type':o.TypeId})
 return out
def group(names,classification):
 a=rows(names)
 if not a:return {'members':[],'bounds_mm':None,'classification':classification}
 b=[min(q['bounds_mm'][i] for q in a) for i in range(3)]+[max(q['bounds_mm'][i] for q in a) for i in range(3,6)]
 return {'members':a,'bounds_mm':b,'size_mm':[b[i+3]-b[i] for i in range(3)],'classification':classification,'available_empty_layer':None,'packing_minimum_claim':False}
cache=json.loads((O/'day16-whole-power-entry-and-full-CSI/rough-mass-readonly/actual-cached-geometry-read.json').read_text())
base=[r['name'] for r in cache['base_solids']]
selection=json.loads((O/'day16-low-light-whole-correction/same-density-complete-correction-mass.json').read_text());currentprints=[r['name'] for r in selection['rows']]
wg=['WAGO415_data__1_'+str(i) for i in range(8)]+['WAGO415_data_1_'+str(i) for i in range(1,8)]+['PBAY_P_AUX']
mtapos=['Motor_ATO4A_1_'+str(i) for i in range(6)];mtaneg=['Motor_ATO4A__1_'+str(i) for i in range(6)]
inline=[o.Name for o in D.Objects if ('2411' in o.Name or '2411' in o.Label) and hasattr(o,'Shape') and not hasattr(o,'Group')]
head=[n for n in currentprints if any(q in n for q in ['HEAD_','YAW_','PITCH_','OLA_','Ola_','EYE_','ORBIT_'])]+['MG92B_Head_yaw','MG92B_Head_pitch','Yaw608_120','Yaw608_134','Pitch688','Camera3_NoIR_Wide','VL53L5CX']
tail=[n for n in currentprints if n.startswith('TAIL_') or n=='LOW_TAIL_COMMON_SOURCE_ROOT']+['MG92B_Tail','Tail608']
g={
 'retained_original_WAVEGO_complete_including_legs':group(base,'originalsource126 unchanged byconstruction; fullstandingbase bounds NOT torso constraint'),
 'original_MainFrame_pair':group(['Part__Feature002','Part__Feature111'],'actual source native structures'),
 'P01_existing_load_rails':group(['P01_load_rail','P01_load_rail_instance2'],'actual retainedprintedsource interface'),
 'two_new_load_grids':group(['LOW_FRONT_LOAD_GRID','LOW_REAR_LOAD_GRID'],'OWNunbuilt geometry VARIABLE, frame overhang not boughtrestriction'),
 'MTA0300330_positive_complete6':group(mtapos,'six full sourcehousing+TEIN+TEOUT+ATO; full71.43sourceassemblyspan not justplasticbody'),
 'MTA0300330_negative_complete6':group(mtaneg,'same complete6; no lead220/84.5claim'),
 'all12MTA_complete':group(mtapos+mtaneg,'source completeunits repositioned, no suppliercasecut'),
 'WAGO415_two8_rows':group(wg,'16selectedphysicalinstances, includesP_AUX asreplacement not duplicate'),
 'four_WAGO615_power':group(['WAGO615_power_0_0','WAGO615_power_0_1','PBAY_P_SYS','PBAY_P_REAR'],'4fullsamepotential5chamberinstances; ownerlogicalassignment not mfgnumbering'),
 'power9_allocated_cases':group(['PBAY_P_AUX','PBAY_P_SYS','PBAY_P_REAR','PBAY_POST_F0','PBAY_F_PI','PBAY_F_AUX','PBAY_F_HY','PBAY_F_HP','PBAY_F_TY'],'chosen projectcaseposes VARIABLE, genuineparts not optional'),
 'fiveFHAC_complete_cases':group(['PBAY_F_PI','PBAY_F_AUX','PBAY_F_HY','PBAY_F_HP','PBAY_F_TY'],'casesonly; full10wireends not represented by casebounds'),
 'inline2411_native_references':group(inline,'effectivity UNRESOLVED unless mapping2peractualleg source; do not count oldrow as purchasedimmutablepose'),
 'MTA0100335_placeholders':group(['Leg_protected_MTA0100335_'+str(i) for i in range(4)],'UNBOUND placeholder, NOT actualsupplierfullbody/lid/tether/fuse/leads'),
 'MTA0100335_reserved_fields':group(['LOW_MINIVAL_UNBOUND_SPACE_'+str(i) for i in range(4)],'own uncertaintycapacity, not measuredmaterial andnot certified sufficient'),
 'Pi_complete_ports_cooling':group(['Pi4B_actual_PCB','Pi_components_and_cooling','Pi_USB_DATA_Delock_mating','Pi_GPIO1992_factory_female'],'whole sourcePCB+ports/cooling conservativefields; physicalmating/CSIunknowns explicit'),
 'battery':group(['Battery_GEA223S30X6GT'],'selectedwholepacksource nominal actualpackFIT'),
 'Pi_plus_battery':group(['Pi4B_actual_PCB','Pi_components_and_cooling','Pi_USB_DATA_Delock_mating','Pi_GPIO1992_factory_female','Battery_GEA223S30X6GT'],'current side-by-sidearrangement, unionBBox not infeasible/minimum proof'),
 'logic_boards_wholefamily':group(['MAIN_Pololu4853','MAIN_UNSHRUNK_FAMILY_SCOPE','AUX_Pololu4092','AUX_FULL9p5_POPULATED_SCOPE','PCA9685_Adafruit815_PCB','E1_populated_prototype_board','BUS25514_installed'],'fullAUX9.5 andsolderedE1kit retained; currentlayer VARIABLE allports affectedifmove'),
 'audio_sensor_stationary':group(['Speaker','MAX98357A_amp','BNO085','ReSpeakerLite_on_REMOVABLE_back','TTP223_touch'],'allselectedextras retained; groupBBox not realcontinuouscapacity'),
 'S0_whole11_and_S1_monitor':group(['S0_body','S0_key','S0_neck','S0_nut_IN_0_0','S0_nut_OUT_0_0','S0_ring_IN_0_0','S0_ring_OUT_0_0','S0_stud_IN_0_0','S0_stud_OUT_0_0','S0_washer_IN_0_0','S0_washer_OUT_0_0','S1_NKK_S821_installed','Monitor_MOD05015'],'wholecase/key/steel actualretained, not hideoperator/material'),
 'current_head_complete':group(head,'wholecurrentretainedmechanism+shellsource andCAM/ToF; no joint/groupduplicates'),
 'current_Y_tail_complete':group(tail,'whole3rdMG/hornjournal/bearing/sourcecoupler, no substituteZwag'),
 'current_closed_skin_material':group(['LC_CURVED_BODY_'+s for s in ['F_NEG','F_POS','R_NEG','R_POS']],'OWNproposal, currentenvelope not immutablepartsconstraint')}
# Fieldnames only for separately budgeted factoryunits if not actual geometry binding.
factoryrefs=[{'name':o.Name,'label':o.Label} for o in D.Objects if any(q in (o.Name+' '+o.Label) for q in ['214761','214763','K1474','W078','CSI200','USB_AUDIO','Grove'])]
(P/'cached-current-wholegroups.json').write_bytes((json.dumps({'source_native':before,'groups':g,'factory_unit_native_reference_names':factoryrefs,'method':'ONE READONLY cached bounds/name/group aggregation; NOBOP/mesh/section/recompute/save/geometrychanges; groupShapeaggregatesexcluded','whole_acceptance':False},indent=2)+'\n').encode())
def restore():
 D.Label=before['label'];G.activeDocument().Modified=before['modified']
 (P/'readonly-native-state.json').write_bytes((json.dumps({'UTC':__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),'file':D.FileName,'objects':len(D.Objects),'label':D.Label,'modified':G.activeDocument().Modified,'pending':None,'compute':'IDLE','GUI_PID':17796,'native_save_called':False,'geometry_changed':False},indent=2)+'\n').encode())
QtCore.QTimer.singleShot(1500,restore)
print(json.dumps({'groups':len(g),'physicalWAGO415_instances':len(g['WAGO415_two8_rows']['members']),'inline_reference_count':len(inline),'cached_readonly':True}))
