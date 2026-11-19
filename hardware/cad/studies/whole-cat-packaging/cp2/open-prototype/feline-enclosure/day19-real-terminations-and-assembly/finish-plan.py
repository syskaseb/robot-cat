"""Whole physical unit allocations. All dimensions mm. Stations are open to lay before fitting the roof."""
from pathlib import Path
import runpy,math,numpy as np,json,collections
P=Path(__file__).parent
ctx=runpy.run_path(str(P/'connections.py'));globals().update({k:v for k,v in ctx.items() if not k.startswith('__')})
src=rd(P/'connected-map.json');ends=src['endpoints'];rows={r['wire']:r for r in src['wires']}
units={};traces={};stock=[]
def note(key,p,kind):ends[key]['point']=xyz(p);ends[key]['kind']=kind
occ={(r['x'],r['y']) for r in pop['terminals']}
pad_binding={}
for r in pop['terminals']:
 if r['ref'] not in ['R1.2','R2.2','R3.2']:continue
 group=next(g for g in pop['board']['groups'] if any(abs(p['x']-r['x'])+abs(p['y']-r['y'])<.001 for p in g['pads']))
 pad=min((p for p in group['pads'] if (p['x'],p['y']) not in occ),key=lambda p:abs(p['y']-r['y']))
 pad_binding[r['ref']]=dict(resistor=[r['x'],r['y']],free_landing=[pad['x'],pad['y']],source_net=group['source_net'],world=xyz(e1(pad['x'],pad['y'])))
 note(r['ref'],e1(pad['x'],pad['y']),'free through-pad on '+group['source_net']+' shared with soldered series resistor')
units['E1_lands']=pad_binding
mp=rd(P/'main-registration.json')
for k,recs in mp['roles'].items():note(k,recs[0]['nearest_hole']+[93.5748],'source guide mapped by 12456 corresponding BRep vertices onto the supplier plated hole, z=upper solder face')
frame('MAIN.GND_OUT','MAIN_Pololu4853',[112.289,-2.82,93.5748],'power','separate return pad in physical four-pad row');ends['MAIN.GND_OUT']=ledger['MAIN.GND_OUT']
def pt(k):return ends[k]['point']
def roundpath(points,r):
    ps=[v(points[0])]
    for p in points[1:]:
        if np.linalg.norm(v(p)-ps[-1])>.0001:ps.append(v(p))
    out=[ps[0]];actual=length(ps)
    for i in range(1,len(ps)-1):
        a,b,c=ps[i-1:i+2];u=(b-a)/np.linalg.norm(b-a);w=(c-b)/np.linalg.norm(c-b);ang=math.acos(np.clip(u@w,-1,1))
        if ang<.001:continue
        tangent=min(r*math.tan(ang/2),.48*np.linalg.norm(b-a),.48*np.linalg.norm(c-b));rad=tangent/math.tan(ang/2)
        n=w-u*(w@u);n=n/np.linalg.norm(n);start=b-tangent*u
        actual+=ang*rad-2*tangent
        for t in np.linspace(0,ang,1+max(3,math.ceil(rad*ang/2))):out.append(start+rad*(u*math.sin(t)+n*(1-math.cos(t))))
    out.append(ps[-1])
    # Include straight intervals for the witness screen.
    pp=[]
    for a,b in zip(out,out[1:]):pp+=list(np.linspace(a,b,max(1,math.ceil(np.linalg.norm(b-a)/2)),endpoint=False))
    return [xyz(t) for t in pp+[out[-1]]],actual
def alloc(w,path,sku,od,r=14,extra=None):
    pp,mm=roundpath(path,r);q=rows[w];q.update(shared_approach=[xyz(p) for p in path],regional_transport_mm=round(mm,3),material_role=sku,jacket_or_section_mm=od,actual_cut_mm=None)
    traces[w]=dict(points=pp,diameter=od,kind=sku)
    if extra:q.update(extra)
    return mm
# Keep the verified three factory leads and the 246 mm run of each JR. Reorient only
# the 25 mm pitch fan on the body side, so its lap and a returning body lead fit the side entrance.
body={};jrplans={};fhac={}
for role,k,ref in [('yaw',1,'HY'),('pitch',2,'HP'),('tail',3,'TY')]:
    q=f['JR'][role];raw=lay['pitch_transfer'][2] if role=='pitch' else lay['fixed']['JR_'+role];start=v(raw['fan'])
    branches=[]
    for i,b in enumerate(q['branches']):
        if role=='pitch':
            angle=(i-1)*.36;normal=v([0,-math.cos(angle),math.sin(angle)]);t=v([-1,0,0]);r=15.2
            arc=[start+r*(math.sin(a)*t+(1-math.cos(a))*normal) for a in np.linspace(0,math.pi/2,23)]
            tip=arc[-1]+(25-r*math.pi/2)*normal;path=arc+[tip,tip+9*normal,tip+17*normal];u=normal
        else:path=[v(p) for p in b['lay']];u=(path[-1]-path[-2])/8
        net=b['target'];w=['XB'+str(k)+'2','XB'+str(k)+'3','XS'+str(k)+'3'][i]
        branches.append(dict(wire=w,target=net,points=[xyz(p) for p in path],lap=[xyz(path[-2]),xyz(path[-1])],length_debits=[25,9,8]))
        body[w]=dict(start=path[-1],u=u,role=role,net=net);key='C_'+ref+'.'+['V+','GND','PWM'][i];note(key,path[-2],'JR free-end proper lap begins here; 8 mm copper overlaps body end once')
    jrplans[role]=dict(parent='JR300_'+role,stock=300,plug=12,transport_and_reserve=246,fan=25,land=9,lap=8,sleeve=20,branches=branches,MG_stock=250,MG_mate=lay['pairs'][role],selected_resistor='R'+str(k+6),pull_down_Ohm=10000)
# A holder gets two separate uncut tails. Lay spare scatter along the same accessible bend before final binding.
# A finite splice at the end of the manufacturer's shortest tail carries the body conductor.
for ref in ['F_HY','F_HP','F_TY','F_AUX','F_PI']:
    for k in ['in','out']:
        key=ref+'.'+k;s=v(pt(key));u=v(ends[key]['outward_axis']);normal=v([0,0,1])
        if ref=='F_PI' and k=='out':normal=v([0,-1,0])
        r=18.;straight=10.;tail=84.5-straight-math.pi*r/2
        a=s+straight*u;arc=[a+r*(math.sin(t)*u+(1-math.cos(t))*normal) for t in np.linspace(0,math.pi/2,25)]
        stop=arc[-1]+tail*normal
        fhac[key]=dict(case_exit=xyz(s),shortest_stock_mm=84.5,max_mm=94.5,end_or_overlap=xyz(stop),minimum_lay=[xyz(s)]+[xyz(p) for p in arc]+[xyz(stop)],bare_tip_included=True,raw_bare=[4.35,8.35],max_extra_before_termination=10,actual_cut=None)
# Source short direct pairs are decided by the real mouth and source length; the solder-splice lay above
# applies to free ends only. Select a new turn between the unchanged paired case and rail, at the measured endpoints.
for key,target in [('F_PI.in','P_SYS.5'),('F_AUX.in','P_REAR.1')]:
    v0=v(pt(key));v1=v(pt(target));fhac[key].update(direct_terminal=target,direct_terminal_point=xyz(v1),direct_chord_mm=float(np.linalg.norm(v1-v0)),minimum_lay=None,end_or_overlap=xyz(v1),route_basis='source relative case/rail poses retained; direct lead from relief to clamping cage, strip and bend checked on real lead')
# Body continuations pass the lifted lids through an open slot at the negative shoulder, then follow
# either the protected lower supply corridor, the grounding bank or the back of the populated 1608.
for w,k in body.items():
    s=k['start'];u=k['u'];target=k['net'];a=s+12*u
    if k['role']=='pitch':
        path=[s,a,[-76,-57,181],[-55,-58,179],[-49,-54,161]]
    else:
        path=[s,a,[a[0]-14,-35, s[2]],[-23,-46,178],[-22,-47,154]]
    if target.startswith('F_'):
        end=v(fhac[target]['end_or_overlap']);path+=[[0,-43,149],[end[0],-41,149],end+[0,0,12],end]
    elif target.startswith('G_'):
        end=v(pt(target));axis=v(ends[target]['outward_axis']);path+=[[23,-45,139],[end[0],-44,137],end+16*axis,end]
    else:
        end=v(pt(target));path+=[[40,-39,149],[133,-31,150],[143,18,149],[end[0],23,end[2]],end]
    od=2.1;mm=alloc(w,path,physical[w]['colour'],od)
    # 8mm of HELU overlaps JR; 9 mm jacket land is part of the 12 mm free departure already drawn.
    terminal=11 if target.startswith('G_') else 8 if target.startswith('F_') else 4
    blank=5*math.ceil((mm+8+terminal+30)/5)
    rows[w].update(from_JR_to=target,JR_lap_debit_on_HELU=8,other_termination_mm=terminal,reserve_and_trim_mm=30,proposed_blank_mm=blank)
# A single source plug at H3. Two cores share the entire approach, branch on the -Y bank.
s=v(pt('BUS.D'));H3=[s,s+[0,0,14],[s[0],s[1],218],[s[0],42,218],[s[0],42,156],[199,34,140],[199,-41,140],[162,-45,139]]
for w,n in [('W002','D_FL.1'),('W003','G2.4')]:
    e=v(pt(n));path=H3+[[e[0],-45,139],e+v([0,17,0]),e]
    mm=alloc(w,path,'D/G only, common keyed SR-Cable 5264 parent',2.4,16)
    rows[w].update(one_parent='BUS_DG_ONE_FACTORY_CABLE',end_debits_project_mm=[16,11],unrestrained_housing_service_mm=35,planned_keep_mm=math.ceil(mm+27+35),stock_mm=900,cut_after_dry_fit=True)
units['BUS900']=dict(common_plug=1,pins={'H3.1':'W002 D','H3.3':'W003 G','H3.2':'V contact removed per source'},common_stations=[xyz(p) for p in H3],single_parent_stock=900,required_axial_length=max(rows[w]['planned_keep_mm'] for w in ['W002','W003']),two_core_kept_mm=[rows[w]['planned_keep_mm'] for w in ['W002','W003']],extra_wire_credit=0,unused_ports=['DC1','H1','H2','H4','H5'])
# K1474 is a selected factory pair; W078 is its 210 mm input portion, never a second cable.
for w,key,g in [('W079','VBUS','MAIN.VOUT'),('W080','GND','MAIN.GND_OUT')]:
    a=v(pt('PI_USB_C.'+key));b=v(pt(g));path=[a,[63,a[1],a[2]],[87,a[1],115],[b[0],a[1],115],[b[0],b[1],115],b]
    mm=alloc(w,path,'K1474 18AWG paired factory output to MAIN',3,18)
    rows[w].update(boot_in_parent_mm=25,local_end_allowance_mm=5,service_mm=20,proposed_keep_mm=math.ceil(mm+25+5+20))
sp=v(fhac['F_PI.out']['end_or_overlap']);note('SPLICE_PI.18',sp,'16/18 stepped solder transition on the factory F_PI output');note('SPLICE_PI.16',sp,'same physical joint')
mm=alloc('W078',[sp,sp+v([0,-11,0]),[106,-29,79],[94,-29,93],[100,-17,106],[112.289,-9.82,106],pt('MAIN.VIN')],'K1474 retained 18AWG MAIN input portion',3,16)
rows['W078'].update(stock=210,ends_project=[8,5],service=15,required=math.ceil(mm+13+15))
units['K1474']=dict(one_raw_pair_nominal_mm_per_core=1000,power_pair_kept=[rows[w]['proposed_keep_mm'] for w in ['W079','W080']],separate_input_portion_mm=210,input_required=rows['W078']['required'],actual_cut=None)
# A top-mounted touch lid, removable audio assemblies and fixed output ports share the transverse hatch.
for w in ['EXT023','EXT024']:
    a=v(pt(rows[w]['ends'][0]));b=v(pt(rows[w]['ends'][1]));alloc(w,[a,[96,-26,148],[117,-20,151],[139,4,151],[139,55,148],b],'HELU 0.5 BTL separate marked pair',2.1)
# Distinct upper receptacle, mouth normal +X. The two supplier footprint fields are 18.73 mm apart.
note('PI.USB2_B',[-20,-19.39,111.1],'upper mouth on other physical stack for independent audio; physical Pi port colour/revision to confirm')
mic=rd(P/'mic-port.json') if (P/'mic-port.json').exists() else None
if mic:note('EXT_MIC.USB-C',mic['mouth'],'supplier USB1 shell face of ReSpeaker at installed transform')
b=v(pt('EXT_MIC.USB-C'));ax=v(mic['outward_axis'] if mic else [1,0,0])
audio=[pt('PI.USB2_B'),[6,-19.39,111.1],[20,-19.39,117],[20,5,145],[5,9,151],b+20*ax,b]
mm=alloc('EXT025',audio,'independent USB-A to C data AUDIO, jacket/boots project only',5)
units['USB_AUDIO']=dict(port_a='other stack upper at x=-20, y=-19.39, z=111.1',port_c=xyz(b),transport_with_approaches=mm,service_headroom=30,delivered_stock=None,factory_ends=True,qualification='match real two simultaneous boots, mic USB1 horizontal outlet and full cable length')
# Assign source E2s, stationary GPIO parent pairs, local solder and separate real optical units.
for r in f['E2']:rows[r['wire']].update(binding=r,shared_approach=r['region_spine'],regional_transport_mm=r['regional_transport_mm'],jacket_or_section_mm=2.5)
for key in ['FFC200','ToF','gpio_five_distinct_parents']:units[key]=f[key]
for pp in units['gpio_five_distinct_parents']:
    total=0
    for portion in pp['portions']:
        pin='PI.H'+str(portion['Pi_H']);w=next(w for w in add['connections'] if pin in [w['a'],w['b']]);dest=w['a'] if w['b']==pin else w['b'];p=[pt(pin)]+portion['corridor'][1:-1]+[pt(dest)]
        mm=alloc(w['id'],p,'Pololu1871 crimped portion on '+pp['parent'],1.5,10);portion['19G_transport_mm']=mm;total+=mm+12+15
    pp['two_sides_with_two_12mm_ends_and_two_15mm_lays_and_one_3mm_loss']=round(total+3,1);pp['margin_in_one_600']=round(600-3-total,1)
for i in range(11,15):
    r=units['ToF'][i-11];rows['EXT0'+str(i)].update(binding=r,regional_transport_mm=r['head']+r['fixed']+r['moving_max'],jacket_or_section_mm=2.1)
rows['EXT026'].update(binding=units['FFC200'],regional_transport_mm=190,jacket_or_section_mm='FFC flat source section')
# Counts and cross-sections in a group, independent of shared copper and stock debits.
for q in rows.values():
    if q.get('jacket_or_section_mm') is None:
        sk=' '.join(str(m.get('sku','')) for m in q['material'])
        q['jacket_or_section_mm']=5 if '12AWG' in sk else 3.5 if '18AWG' in sk or '16AWG' in sk else 2.1
        q['section_basis']='project packing diameter, delivered jacket to fit'
    if 'regional_transport_mm' not in q:q['regional_transport_mm']=q['length_to_station_faces_mm']
reg=src['regions']
for g in reg.values():
    ds=[rows[w]['jacket_or_section_mm'] for w in g['members'] if isinstance(rows[w]['jacket_or_section_mm'],(float,int))]
    g.update(connection_count=len(g['members']),max_parallel_circular_area_mm2=round(sum(math.pi*d*d/4 for d in ds),1),method='conservative parallel tally before splitting at individual ports; local board copper and FFC separately typed')
wr('whole-termination-plan.json',dict(source_counts=[134,26],endpoints=ends,regions=reg,wires=list(rows.values()),units=units,JR=jrplans,FHAC=fhac,actual_cut_fit_slack=None))
wr('named-approaches.json',traces)
print('BUS',units['BUS900']['required_axial_length'],'K1474',units['K1474'],[p['margin_in_one_600'] for p in units['gpio_five_distinct_parents']])
