from pathlib import Path
from datetime import datetime,timezone
import json,math,hashlib,os
root=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical');out=root/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=json.loads((out/'day07-whole-physical-SOURCE-approach-Knee-link-proposal.json').read_bytes());byid={q['wire']:q for q in source['core_rows']};contract=json.loads((out/'n01-selected-piece-profile-contract.json').read_bytes())['portions'];rows=[];portions=[]
spec=[('SOURCE/FL1',40.7,['W004','W020','W019']),('SOURCE/FL2',44,['W005','W022','W021']),('DONOR/FL3',47.3,['W006','W024','W023'])]
for n,(unit,z,ids) in enumerate(spec):
 for core,dx,w in zip(['D','V','G'],[-2.75,0,2.75],ids):
  rr=1 if core=='V' else 1.55
  row=dict(wire=w,canonical_portion=w+'/body',selected_piece=contract[w+'/body']['selected_piece_id'],physical_passage_unit=unit,core=core,row_index=n,centre_XZ_mm=[-132.75+dx,z],profile_radius_mm=rr,margin_capacity_radius_mm=rr+.4,passage_Y_mm=[39.25,77],source_to_body_T=[0,-1,0],section_outward_T=[0,1,0],frame_roll_deg=0,actual_body_receiver=byid[w]['body_receiver'],physical_source_owned_joint=unit=='DONOR/FL3',region_chain=['actual_source14_or_sourceowned_donorjoint','unqualifiedmoving_Knee6_Hip3','left_passage_'+str(n)+'_'+core,core+'3_branch_loose_region','current_actual_receiver9'],fullnewfan_or_currentlengthfit=None);rows.append(row)
  piece=w+'/source_owned_donor' if unit=='DONOR/FL3' else contract[w+'/body']['selected_piece_id'];portions.append(dict(wire=w,piece_id=piece,physical_unit=unit,passes_body_section=True,body_lane=row['centre_XZ_mm']))
for w in ['W006','W024','W023']:
 portions.append(dict(wire=w,piece_id=w+'/original_source',physical_unit='SOURCE/FL3',passes_body_section=False,role='Factoryplug/source14 to movingKneejoint3x8laps/3x20sleeves/stagger/two9lands; DONORsamewirethenbody. Noextra3bodycores/splice/cut.'))
gaps=[]
for i,a in enumerate(rows):
 for b in rows[i+1:]:
  gap=math.dist(a['centre_XZ_mm'],b['centre_XZ_mm'])-a['profile_radius_mm']-b['profile_radius_mm'];gaps.append(dict(a=a['wire'],b=b['wire'],gap_mm=gap));assert gap>=.2-1e-7
for a in rows:
 x,z=a['centre_XZ_mm'];rad=a['margin_capacity_radius_mm'];assert x-rad>=-137.45-1e-7 and x+rad<=-128.05+1e-7 and z-rad>=38.75-1e-7 and z+rad<=49.25+1e-7
pr=json.loads((out/'day07-SOURCE-D9-anchored-south-return-and-BUS-D-coallocation-proposal.json').read_bytes());newroute=pr['route_OUTWARD_from_receiver'];newroute[2]['Q'][0]=-100.4;newroute[2]['length_mm']=newroute[2]['P'][0]+100.4;newroute[3]['P'][0]=-100.4;newroute[3]['centre'][0]=-100.4;newroute[3]['Q'][0]=-135.5;newroute[4]['P'][0]=newroute[4]['Q'][0]=-135.5;newroute[5]['P'][0]=newroute[5]['Q'][0]=-135.5
r=dict(id='day07-SOURCE-ninecore-left-entry-lane-roll-whole-proposal',status='ONE_ALL_NINE_PHYSICAL_ENTRY_LANE_ALLOCATION_BEFORE_LOCAL_D_TEST',selected=False,N01_complete=False)
r.update(cause='PrevioussoloDusedsharedtripletaccountingcentre asphysicalDport. AssignALL9DVGprofiles/threephysicalbodyrows, notnudgeDandforget8. No boughtsourceport/holder/grip/PCB moved.',source_field='day07-SOURCE-left-end-body-passage-bounded-disposition.json',source_field_sha256=sha(out/'day07-SOURCE-left-end-body-passage-bounded-disposition.json'),field_bounds_mm=[[-137.45,39.25,38.75],[-128.05,77,49.25]],field_full_XZ_mm=[9.4,10.5],rows=rows,all12_physical_portions=portions,physical_units=['SOURCE/FL1','SOURCE/FL2','SOURCE/FL3','DONOR/FL3'],pairwise_nominal_profile_gaps=gaps,minimum_nominal_profile_gap_mm=min(q['gap_mm'] for q in gaps))
r['margin_scope']='Full3.1/2/3.1profiles kept/.2physicalplanninggaps/.4outercapacitymargin. IndividualmarginhalooverlapisNOTdoubleallocatedphysicalcores; entirefieldboundsrespected/nofillfactor.'
r['local_branch_counts']={'D3':dict(IDs=['W004','W005','W006'],initial_XZ_full_mm=[3.9,10.5]),'V3':dict(IDs=['W020','W022','W024'],initial_XZ_full_mm=[2.8,9.4]),'G3':dict(IDs=['W019','W021','W023'],initial_XZ_full_mm=[3.9,10.5])}
r['roll_and_fans']='Zero-roll/T-Yinsidefield. Y39.25bodybranchaccountingseam NOTterminal/extra9/forcedtangent; outsidefieldD3/G3/V3repack/tangent/R35.1/entryfan/movinglegrollUNQUALIFIED. DoNOTforce9throughDport.'
r['D9_whole_return']=newroute;r['new_D_body_proposed_mm']=9.25+sum(q.get('length_mm',q.get('length_range_mm',[0])[0]) for q in newroute)
r['new_D_body_debit_scope']='RecomputednewplanONLY; no recoveredprefix/cut/wholefit/stockcredit. SOURCEFL2E55DinsideU125.2, no added55 again.'
r['stock_and_retention']='CurrentBUSW002/W003full9/root/cap/band/headretained/notSOURCEown/exacttiesanduncuttailsOPEN; SOURCE4ties/MODULE2/actualD9+.25/G24.25/Vstraight9/currentfactoryportsunchanged.'
r['assembly']='LayconnectedsourcekitOFFPETG; retainSOURCEFL3original/donorspliceholder. Hiprow0/continuousFL2row1/donorrow2, Douter/Vmiddle/Ginner beforeloosecapture/closure. Noelectricalpinreassignment/grip/pullthroughsolderedMODULE. Alloutsidebodyfan/sourceleglaystillOPEN.'
r['first_gate']='NEWninefullmarginprofile subsets inside actualfield114 ONLY(no1443/4515replay). ThenNEWassignedDlanedrop vsactualS1screw5/fulllocalS0S1metal: outsidefieldcurvedcapacitycannotinheritfixedboxproof. No oldDcentre/U30/S119replay.'
r['scope']='Physicalassignment/connectedbranchplanONLY. Actualnewleg+fanvariation/E55each/independentbranchspace/root/fullstock/850/900MAX3/actualends/AUminfit/slackOPEN beforematerial/V3. FL2NOlap4/FL3properjoinlap4only/no splice/cut/pool/20fittrimslack.'
r['source_pins']=[dict(path=n,sha256=sha(out/n)) for n in ['day07-SOURCE-D9-BUS-coallocation-bounded-disposition.json','day07-SOURCE-left-end-body-passage-bounded-disposition.json','day07-whole-physical-SOURCE-approach-Knee-link-proposal.json','n01-selected-piece-profile-contract.json']];r['written_utc']=datetime.now(timezone.utc).isoformat()
p=out/'day07-SOURCE-ninecore-left-entry-lane-roll-whole-proposal.json';assert not p.exists();p.write_bytes((json.dumps(r,indent=2)+'\n').encode());print(p.name,sha(p),'IDs',len(rows),'portions',len(portions),'mingap',r['minimum_nominal_profile_gap_mm'],'body',r['new_D_body_proposed_mm'])
card=root/'hardware/HOBBY_COMPLETION_PLAN.md';raw=card.read_bytes();i=raw.index(b'## Historia poprzednich okien');pre=raw[:i].decode();tail=raw[i:];j=pre.index('\n',pre.index('## Bieżąca'))+1
fact='\nSOURCE_ALL9_ENTRY_PROPOSAL: '+p.name+' SHA'+sha(p)+'. ALL9IDs/12portions/4MAX3: SOURCEFL1Z40.7/FL2Z44/DONORFL3Z47.3; eachDouterX-135.5/Vmiddle-132.75/Ginner-130. OriginalFL3threeportionsstayKneejointnotextra3bodycores. Full3.1/2/3.1/minprofilegap.2/.4halosinside9.4x10.5, zero-rollY39.25..77. No physicalport/pinreassignment. D3/V3/G3local3notall9Dport; alloutsidefans/newlegslackOPEN. FIRSTnineNEWsubsetsfield114 thenonlyNEWassignedDdrop/S1screw5+localneighbors. Not sourceport/PCB/holderoffset; no oldDcentre/4515/1443/21motion replay/AUminfitNULL/N010.\n'
pre=pre[:j]+fact+pre[j:];assert card.read_bytes()==raw;q=card.with_suffix('.owner65plan.tmp');q.write_bytes(pre.encode()+tail);os.replace(q,card)
