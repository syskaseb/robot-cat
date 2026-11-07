# Complete common V: real ends/stock + connected occupied regions + functional support.
# Exact three source branches are bounded to the real S0/TE/F_PI/P_SYS hazard, not123freewires.
_t=time.monotonic();_c=time.process_time();packet_path=OUT/'day30-four-factory-common-regions.json'
packet=json.loads(packet_path.read_text(encoding='utf-8'));q=packet['current_foreign_common_bank_loadpath_proposal']
assert packet['current_foreign_common_bank_loadpath_review']['decision']=='GO'
assert packet['current_foreign_short_U1_functional_loadpath']['status']=='SHORT_U1_SOURCE_ROOT_GV_SCOPED_RECEIVED'
v=q['V3_receivers'];CentralVParts30={};CentralVSpecs30={}
def central_S30(a,b,t):
 a=np.array(a,float);b=np.array(b,float);t=np.array(t,float);delta=b-a;dx=float(delta@t);h=delta-dx*t;H=float(np.linalg.norm(h));u=h/H;angle=2*math.atan2(H,dx);R=(dx*dx+H*H)/(4*H)
 one,p,nt=_matharc(a,t,u,R,angle);two,p,nt=_matharc(p,nt,math.sin(angle)*t-math.cos(angle)*u,R,angle)
 assert np.linalg.norm(p-b)<1e-6
 return [one,two],R
for spec in v['critical_exit_branches']:
 n=spec['wire'];a=np.array(spec['port']);land=np.array(spec['full9_end']);t=np.array([0.,-1,0]);rows=[uf_line30(a,land)]
 one,p,t=_matharc(land,t,[0,0,-1],12.4,math.radians(spec['first_down_angle_deg']));rows.append(one)
 two,p,t=_matharc(p,t,spec['second_quarter_bend_axis'],12.4,math.pi/2);rows.append(two)
 assert np.linalg.norm(p-np.array(spec['two_arc_end']))<1e-6
 if n=='W020':
  p2=np.array([-23.4,p[1],p[2]]);rows.append(uf_line30(p,p2));p=p2
 turn,p,t=_matharc(p,t,[0,1,0],12.4,math.pi/2);rows.append(turn)
 if n=='W022':
  tail,R=central_S30(p,[-11,p[1]+32,p[2]],[0,1,0]);assert R>=12.4;rows.extend(tail);p=np.array(tail[-1]['end'])
 elif n=='W024':
  tail,R=central_S30(p,[-11,p[1]+20,p[2]],[0,1,0]);assert R>=12.4;rows.extend(tail);p=np.array(tail[-1]['end'])
 end=np.array([-11,35.5,p[2]]);assert end[1]>=p[1];rows.append(uf_line30(p,end))
 CentralVParts30[n+':nominal']=uf_pipe30(rows,1)
 CentralVParts30[n+':branch_region']=uf_pipe30(rows[1:],1.4)
 CentralVSpecs30[n]=dict(parts=rows,length_mm=sum(r['length_mm'] for r in rows),minimum_R_mm=min(r['radius_mm'] for r in rows if r['kind']=='arc'),true_port=spec['port'],full9_unchanged=True,region_own_seam_at_Y35p5_not_terminal=True)
# Existing6core guide -> V peel -> central7.2x2.8 pack. No double occupancy at branches.
rows,R=ufS30([-74.55,95.1,66.75],[-51.7,90.2,66.75]);assert R>=12.4
rows.append(uf_line30([-51.7,90.2,66.75],[-23.4,90.2,66.75]))
turn,p,t=_matharc([-23.4,90.2,66.75],[1,0,0],[0,-1,0],12.4,math.pi/2);rows.append(turn)
run=math.sqrt(4*14.6*7.9-7.9**2);target=np.array([-11,77.8-run,58.85]);ss,R=central_S30(p,target,[0,-1,0]);assert abs(R-14.6)<1e-6;rows.extend(ss);rows.append(uf_line30(target,[-11,35.5,58.85]))
CentralVParts30['V:common_region']=rect_region30(rows,-1.4,1.4,-3.6,3.6)
CentralVSpecs30['common']=dict(parts=rows,centre_length_mm=sum(r['length_mm'] for r in rows),profile_mm=[2.8,7.2],cores=['W020','W022','W024'],inner_wire_R_mm=12.4,loose_hand_laid_not_manufacturing_cut=True)
cells={n:bx30(*b) for n,b in v['support']['cells'].items()}
newroot=fuse30(list(cells.values()));caps={n:s for n,s in DirectWorld30.items() if n.startswith('Station:Bank:') and any(w in n for w in ['W020/','W022/','W024/']) and n.endswith(':split_cap_exterior')};assert len(caps)==3
CentralVParts30['V:new_root_material']=newroot
CentralVParts30['V:functional_pressure_support']=fuse30([newroot]+[retention.isolated(s) for s in caps.values()])
start=len(NorthSupportRows30)
for n,s in caps.items():support_pair(newroot,s,'centralV_root | '+n,root=True)
for number in [1,2,3]:
 host='CurrentFoundation:BankPad:Ref_Material_F_L'+str(number)+'_CP2_Housing_0_0:0'
 support_pair(newroot,DirectWorld30[host],'centralV_root | actual_pad:'+str(number),root=True)
union=fuse30([CentralVParts30['V:functional_pressure_support'],BankRetentionBed30])
# Existing P_SYS three actual current departure constructions are compulsory operands.
for w in PsysSource30['wires']:
 t=PsysSource30['parts']['wire:'+w['endpoint']]
 for n,s in CentralVParts30.items():
  if bbox_lower_bound(s.BoundBox,t.BoundBox)<1.25:support_pair(s,t,n+' | current_PSYS:'+w['wire'],1.25)
for n,s in CentralVParts30.items():
 if n.endswith(':nominal') or n.endswith(':region') or n.endswith('_region'):
  support_pair(s,newroot,n+' | own_functional_root',.2)
for n,s in DirectWorld30.items():
 if n.startswith('Station:Bank:') and any(w in n for w in ['W020/','W022/','W024/']) and n.endswith((':band_budget',':head_budget')):
  support_pair(newroot,s,'centralV_root | full_original_stock:'+n,.2)
  for key,a in CentralVParts30.items():
   if key.endswith(':nominal') and bbox_lower_bound(a.BoundBox,s.BoundBox)<1.25:support_pair(a,s,key+' | original_stock:'+n,.2)
# Whole bought/reserved ports, sourcecase and family before changed foreign breadth.
for n,s in DirectWorld30.items():
 if not ('S0_' in n or n.startswith('Ref_Material_F_L') or n in ['F_PI:registered_casing_reservation','Station:P_SYS:case']):continue
 for key,a in CentralVParts30.items():
  if key=='V:new_root_material' or key.endswith('_region') or key.endswith(':branch_region'):continue
  if bbox_lower_bound(a.BoundBox,s.BoundBox)>=1.25:continue
  own=(key.split(':')[0],n) in [('W020','Ref_Material_F_L1_CP2_OUT_0_0'),('W022','Ref_Material_F_L2_CP2_OUT_0_0'),('W024','Ref_Material_F_L3_CP2_OUT_0_0')]
  own=own or (key=='V:functional_pressure_support' and n in ['Ref_Material_F_L1_CP2_OUT_0_0','Ref_Material_F_L2_CP2_OUT_0_0','Ref_Material_F_L3_CP2_OUT_0_0','Ref_Material_F_L1_CP2_Housing_0_0','Ref_Material_F_L2_CP2_Housing_0_0','Ref_Material_F_L3_CP2_Housing_0_0'])
  support_pair(a,s,key+' | '+n,0 if own else 1.25)
rowsown=NorthSupportRows30[start:];hold=any(r['hold'] for r in rowsown) or len(union.Solids)!=1
archive=OUT/'day30-astra-common-bank-v-functional-space.breps.zip';assert not archive.exists();manifest=[]
with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
 for n,s in CentralVParts30.items():
  strict30(s);raw=s.exportBrepToString().encode('utf-8');entry=str(len(manifest))+'.brep';z.writestr(entry,raw);manifest.append(dict(name=n,entry=entry,sha256=hashlib.sha256(raw).hexdigest(),bounds_mm=saved_bounds(s)))
 z.writestr('manifest.json',json.dumps(manifest).encode('utf-8'))
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 for m in manifest:
  s=Part.Shape();s.importBrepFromString(z.read(m['entry']).decode('utf-8'));strict30(s)
r=dict(status='CENTRAL_V_FUNCTIONAL_SPACE_HOLD' if hold else 'CENTRAL_V_SOURCE_ROOT_ORIGINAL_STOCK_SCOPED_RECEIVED',rows=rowsown,recipes=CentralVSpecs30,union_solids=len(union.Solids),archive=archive.name,archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),geometry=manifest,reused_stock_names=[n for n in DirectWorld30 if n.startswith('Station:Bank:') and any(w in n for w in ['W020/','W022/','W024/'])],new_loose_guide_stock_and_bed_passage_NOT_YET_BUILT=True,operation_seconds=time.monotonic()-_t,process_cpu_seconds=time.process_time()-_c,N01_complete=False)
packet=json.loads(packet_path.read_text(encoding='utf-8'));packet['current_foreign_common_bank_V_functional_space']=r
raw=json.dumps(packet,ensure_ascii=False,indent=2).encode('utf-8');assert len(raw)<5000000;tmp=packet_path.with_suffix('.astra.tmp');tmp.write_bytes(raw);tmp.replace(packet_path)
print('CENTRAL_V_FUNCTIONAL',r['status'],'HOLDS',[x for x in rowsown if x['hold']],'lengths',{n:x.get('length_mm',x.get('centre_length_mm')) for n,x in CentralVSpecs30.items()},'wall',r['operation_seconds'],'cpu',r['process_cpu_seconds'],flush=True)
