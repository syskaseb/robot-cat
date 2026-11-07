tick=time.perf_counter();cpu=time.process_time()
# Import only the already named frozen source layer; never run old audit loops.
src=Path('C:/Users/Sysq/AppData/Local/Temp/robot-cat30-astra-restore-current.py').read_text(encoding='utf-8')
exec(compile(src[src.index('restore_tick='):src.index('FourRegionProposal30=json.loads')],'frozen_U1_split_scoped_source_layer','exec'))
CurrentCanon31=json.loads((OUT/'day30-four-factory-common-regions.json').read_text(encoding='utf-8'));NamedPins31={}
def current_record_shapes31(key,names=None):
 r=CurrentCanon31[key];p=OUT/r['archive'];assert hashlib.sha256(p.read_bytes()).hexdigest()==r['archive_sha256'];result={}
 with zipfile.ZipFile(p) as z:
  for row in r['geometry']:
   if names is not None and row['name'] not in names:continue
   raw=z.read(row['entry']);assert hashlib.sha256(raw).hexdigest()==row['sha256'];s=Part.Shape();s.importBrepFromString(raw.decode('utf-8'));result[row['name']]=s
 NamedPins31[key]={'archive':r['archive'],'sha256':r['archive_sha256'],'selected_names':sorted(result)}
 return result
FunctionalFront30=current_record_shapes31('current_foreign_functional_candidate');assert len(FunctionalFront30)==37
retire_final=set(CurrentCanon31['retired_in_this_correction'])|{'CradleLowEdge:open:0','CradleLowEdge:open:1','CurrentFoundation:BankBedCurrent:-1:JPWMRooted','SharedPositiveFoundationU1','DAY18:XP02:band','DAY18:XP02:head'}
FourThirdContext30={n:s for n,s in ActiveScene30.items() if n not in retire_final and n not in FunctionalFront30}
for n,lo,hi in [('Fore',[-112.15,51.65,86.8],[-108.15,73.65,87.3]),('Rear',[-65.15,51.65,86.8],[-61.15,73.65,87.3]),('HighMiddle',[-108.15,69.65,86.8],[-65.15,73.65,87.3])]:FourThirdContext30['FHY4905:'+n]=Part.makeBox(*(np.array(hi)-lo),A.Vector(*lo))
DirectWorld30={n:s for n,s in {**FourThirdContext30,**FunctionalFront30}.items() if n not in ['FrontShared:rail_riser','FHY4905:OpenCup','FLArcBand','FLArcHead']}
DirectWorld30.update(current_record_shapes31('current_foreign_open_support_bank_milestone',{'Underdeck:RestoredBank'}))
retire={n for n in DirectWorld30 if n.startswith('Station:Bank:') and any(w in n for w in ['W020/','W022/','W024/'])}
retire.update(n for n in DirectWorld30 if n.startswith('Station:D_FL:') and n!='Station:D_FL:case')
world={n:s for n,s in DirectWorld30.items() if n not in retire and not n.startswith('Station:FL_G:')}
bank=current_record_shapes31('current_foreign_bank_complete_retention');bed=bank['Bank:open_spine'].copy()
for a,b in [(-14,-12.4),(-9.6,-8)]:bed=bed.cut(Part.makeBox(b-a,2.9,5,A.Vector(a,57.05,51)))
world['CurrentFoundation:BankBedCurrent:1']=bed;world.update({n:s for n,s in bank.items() if n.startswith('FLG:')})
flg=current_record_shapes31('current_foreign_FLG_complete_four_port');world.update({'CurrentFLG:'+n:s for n,s in flg.items()})
pier=current_record_shapes31('current_foreign_open_pier_DFL_gate');world['CurrentFoundation:BankPier:3']=pier['Pier3:open'];world['CurrentDFL:permanent']=pier['DFL:permanent_union'];world['CurrentDFL:removable']=pier['DFL:removable_outward_half']
stock=current_record_shapes31('current_foreign_complete_receiver_stock_gate',{'DFL:cap','DFL:band','DFL:head'});world.update({'CurrentDFL:'+n:s for n,s in stock.items()})
world.update({n:s for n,s in DirectWorld30.items() if n.startswith('Station:Bank:') and any(w in n for w in ['W020/','W022/','W024/'])})
north=current_record_shapes31('current_foreign_north_common_support',{'GV:band','GV:head'})
north.update(current_record_shapes31('current_foreign_north_moved_bar_receipt',{'U1:cap','U1:band','U1:head'}))
north.update(current_record_shapes31('current_foreign_north_mixed_correction1_receipt',{'Common:print'}));world.update({'CurrentNorth:'+n:s for n,s in north.items()})
cv=current_record_shapes31('current_foreign_common_bank_V_functional_space',{'W020:nominal','W020:branch_region','W022:nominal','W022:branch_region','W024:nominal','W024:branch_region','V:common_region'})
cv.update(current_record_shapes31('current_foreign_common_bank_V_correction1_receipt',{'V:new_root_material','V:functional_pressure_support'}));world.update(cv)
world.update(current_record_shapes31('current_foreign_V_loose_guide_receipt',{'V:loose_guide_band','V:loose_guide_head'}))
world.update(current_record_shapes31('current_foreign_dock_front_portal_receipt',{'Underdeck:CommonSupport'}))
u1=current_record_shapes31('current_foreign_upper_plenum_candidate',{'U1:complete_short_carrier'});world['Underdeck:PositiveFoundation']=u1['U1:complete_short_carrier']
world.update(current_record_shapes31('current_foreign_W029_full_stock_clock_receipt'))
world.update(current_record_shapes31('current_foreign_north_joint_capacity_receipt'))
G3IntegrationWorld31=world
MotionSource31=json.loads((OUT/'motion-layout.json').read_text(encoding='utf-8'));axes=json.loads((ROOT/'hardware/simulation/p0/e6-leg-compatibility.json').read_text(encoding='utf-8'))['axes']
outer=OUT/'day30-astra-service-whole-front.breps.zip';assert hashlib.sha256(outer.read_bytes()).hexdigest()=='31aa7040063701e5ebf7b2a4fb04e68f9a83e01adca153cd9c6315147af1d29f'
with zipfile.ZipFile(outer) as z:raw=z.read('service-whole/30.brep')
assert hashlib.sha256(raw).hexdigest()=='a6a6306d7f51ad208496609d0f1d6bf63d739e2b34c14d032421992daa28bc58';BodyOuter31=Part.Shape();BodyOuter31.importBrepFromString(raw.decode('utf-8'))
r={'status':'NAMED_CURRENT_CONTEXT_IMPORTED_NO_COLLISION_AUDITS','pid':os.getpid(),'session_id':85730,'MAIN_mm':datum,'U1_core':len(U1CoreNames),'foreign_context_actors':len(world),'expected_previous_context_actors':1182,'neutral_moving_sources':len(restMotion),'saved_motion_poses':len(MotionSource31['poses']),'current56_count':len(Current56),'source_pins':NamedPins31,'base_frozen_source':CP['native'],'base_source_restore_operation_seconds':18.618470299988985,'base_source_restore_process_cpu_seconds':13.4375,'operation_seconds':time.perf_counter()-tick,'process_cpu_seconds':time.process_time()-cpu,'old_collision_checks_repeated':0,'N01_complete':False}
p=OUT/'day31-astra-resumed-current-context-receipt.json';assert not p.exists();p.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print('CURRENT_CONTEXT_IMPORTED',len(world),len(restMotion),len(U1CoreNames),datum,r['operation_seconds'],r['process_cpu_seconds'],flush=True)
