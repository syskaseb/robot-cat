"""Connect canonical electrical endpoints through shared open laying regions in the 19G box."""
from pathlib import Path
import json,math,numpy as np,collections,csv
P=Path(__file__).parent;F=P.parent/'day19-connected-servo-usb-and-closure';E=P.parent/'day19-simple-box-common-core'
H=next(q for q in P.parents if (q/'electronics/kicad-current/design.json').exists());A=H/'electronics/full-cat';ADD=A/'closed-prototype-add7-2026-11-16';S=json.loads((P/'installed-stations.json').read_bytes())
def rd(p):return json.loads(p.read_bytes())
def wr(n,d):(P/n).write_bytes((json.dumps(d,indent=1,ensure_ascii=False)+'\n').encode())
def v(a):return np.asarray(a,float)
def xyz(a):return np.asarray(a).round(4).tolist()
def length(path):return float(np.linalg.norm(np.diff(path,axis=0),axis=1).sum())
def bb(n):return v(S[n]['bounds']).reshape(2,3)
def centre(n):return np.mean(bb(n),axis=0)
base=rd(H/'electronics/kicad-current/design.json');add=rd(ADD/'connections.json');f=rd(F/'unit-plan.json');lay=rd(F/'service-lay.json')
ledger={};extra={};approach={}
def land(key,actor,point,zone,kind,axis=None):
    ledger[key]=dict(actor=actor,point=xyz(point),zone=zone,kind=kind)
    if axis is not None:ledger[key]['outward_axis']=axis
# Logical/physical cavity assignment from the source; orient the labelled housing at installation.
wago={q['label'].split(' ')[1]:n for n,q in S.items() if n.startswith('WAGO415') and n!='WAGO415_data_1_0'}
wago.update(G1='WAGO615_power_0_0',P_FRONT='WAGO615_power_0_1',P_SYS='PBAY_P_SYS',P_REAR='PBAY_P_REAR',P_AUX='PBAY_P_AUX')
for station in rd(P.parent/'n01-twenty-wago-port-contract.json')['stations']:
    ref=station['ref'];n=wago[ref];a,b=bb(n);mid=(a+b)/2
    long=int(np.argmax((b-a)[:2]));side=1-long
    sg=1 if (ref=='P_SYS' or (side==1 and mid[1]<0)) else -1
    if ref=='P_REAR':sg=-1
    pitch=6.5 if '615' in n or ref in ['P_SYS','P_REAR'] else 4.75
    for row in station['occupied_ports']:
        i=row['physical_port'];pt=mid.copy();pt[long]+=(i-3)*pitch;pt[side]=b[side] if sg>0 else a[side]
        axis=[0,0,0];axis[side]=sg
        land(row['endpoint'],n,pt,'bank+' if mid[1]>0 else 'bank-','labelled wire-entry face and source cavity assignment; project insertion depth to fit',axis)
# Three head/tail remote pull-downs are fitted at their JR lap between PWM and return.
owners={};physical={};extra['JR']={}
for role,k,ref,ground in [('yaw',1,'HY','G_AUX.4'),('pitch',2,'HP','G_AUX.3'),('tail',3,'TY','G_TAIL.5')]:
    jr=f['JR'][role];branches=jr['branches'];ns=['F_'+ref+'.out',ground,'R'+str(k)+'.2']
    for label,br,w in zip(['V+','GND','PWM'],branches,['XB'+str(k)+'2','XB'+str(k)+'3','XS'+str(k)+'3']):
        end=v(br['lay'][-1]);lap=v(br['lay'][-2]);land('C_'+ref+'.'+label,'JR300_'+role,lap,'upper','JR lap starts here; mates at full 19F connector, 8 mm overlap ends at '+str(xyz(end)))
        physical[w]=dict(parent='JR300_'+role,source_target=br['target'],lap_start=xyz(lap),lap_end=xyz(end),HELUseat=xyz(end),colour={'V+':'23302 red','GND':'23301 black','PWM':'23308 yellow'}[label])
    extra['JR'][role]=dict(MG=250,JR=300,debit=[12,246,25,9,8],three_body_units=[t for t,r in physical.items() if r['parent']=='JR300_'+role],local_pulldown='R'+str(k+6),between=['PWM','GND'],sleeve=20)
# Original 1608 board, Eagle component face coordinate system. Keep PCA soldered to its adjacent board.
pop=rd(A/'pwm-carrier-r3/population.json');origin=v([170,36,128.4])
def e1(x,y,z=0):return origin+v([y,-z,-x])
for t in pop['terminals']:land(t['ref'],'1608',e1(t['x'],t['y']),'logic','source plated pad '+t['source_copper_group'] if 'source_copper_group' in t else 'source plated pad')
def frame(key,n,p,zone,kind='source unit, projected approach on actual housing'):land(key,n,p,zone,kind)
# Module and housing approach regions. Port coordinates are identified at three levels:
# supplier pad, source calibrated mouth, or named footprint face whose delivered seating is unmeasured.
E2=f['E2']
for r in E2:
 for port,pt in zip(r['ends'],[r['region_spine'][0],r['region_spine'][-1]]):
    if port not in ledger:frame(port,port.split('.')[0],pt,'logic','19F E2 station')
for ref in ['F_PI','F_AUX','F_HY','F_HP','F_TY']:
    n='PBAY_'+ref;a,b=bb(n);m=(a+b)/2;dim=int(np.argmax(b-a))
    for key,sg in [('in',-1),('out',1)]:
        if ref=='F_PI':sg=-sg
        pt=m.copy();pt[dim]=b[dim] if sg>0 else a[dim]
        axis=[0,0,0];axis[dim]=sg;land(ref+'.'+key,n,pt,'low','exit of full FHAC strain relief; separate 84.5..94.5 mm stock incl bare tip',axis)
# Source H3.1 and H3.3 only; H3.2 is NC. Both D/G share the keyed housing.
bus=v(f['installed_BUS_port_bounds']['H3']).reshape(2,3);port=bus.mean(0);port[2]=bus[1,2]
for key in ['D','G']:frame('BUS.'+key,'E19_BUS_population:H3',port,'BUS','actual H3 mouth centre, pin from design.json; common factory housing')
# K1474 full boot. Selected source design designates separate VOUT and GND landings on MAIN.
for key,dy in [('VBUS',1.75),('GND',-1.75)]:frame('PI_USB_C.'+key,'CF17_POWER_K1474_SEALED_BOOT_FULL',[-56.3,-38.9+dy,101.2],'Pi')
main=rd(A/'pi-power-usb-r4/plan.json')
for key,pt in [('VIN',[89,-13,93.6]),('VOUT',[114,3,93.6]),('GND',[111.5,3,93.6])]:frame('MAIN.'+key,'MAIN_Pololu4853',pt,'power','pad group approach; exact pad below in source registration')
for key,pt in [('VIN',[88,17.27,91.57]),('VOUT',[108,17.27,91.57]),('GND',[105.5,17.27,91.57])]:frame('AUX.'+key,'AUX_Pololu4092',pt,'power')
for key,pt in [('BAT.minus',[5,5,80]),('BAT.plus',[5,8,80]),('F0.in',[12,0,86]),('F0.out',[82,0,86]),('POST_F0.1',[106,-3,57]),('POST_F0.2',[117,-3,57]),('SPLICE_PI.16',[127,18,76]),('SPLICE_PI.18',[127,18,76])]:frame(key,key.split('.')[0],pt,'low')
for key in ['in','out']:
    n=next(n for n in S if n.startswith('S0_ring_'+key.upper()));frame('S0.'+key,n,centre(n),'operator')
for k in [2,3,5,6]:
    n=next((n for n in S if n.startswith('OP_S1_') and str(k) in n),'OP_S1_PRIMARY_CASE_CONSERVATIVE');frame('S1.'+str(k),n,centre(n),'operator','labelled switch contact; station approach')
# JR service loops, controlled by 19F. ToF and CSI unchanged optical assembly.
d19=rd(P.parent/'day19-whole-appearance-and-moving-neck-correction/whole-lay.json')
for ix,q in enumerate(f['ToF']):
    key=q['port'];pt=d19['head'][ix][0];frame(key,'VL53L5CX',pt,'head','Pololu 3417 source pad')
    frame('PCA.JP3.'+str(q['JP3']),'PCA9685_Adafruit815_PCB',d19['fixed'][ix]['centreline'][-1],'logic','matched 19D source pad')
for i in range(3):frame('PCA.CH'+str(i)+'.S','PCA9685_Adafruit815_PCB',[80+2.54*i,40,122],'logic','source header bank approach')
for key,pt in [('LOCAL.GND',e1(-8,-6)),('LOCAL.LOGIC3V3',e1(0,10)),('LOCAL.PWM5',e1(0,-4))]:frame(key,'1608',pt,'logic','distributed local copper; separate rail contacts')
for i in range(1,25):frame('U1.'+str(i),'Kamami575070',e1(-7.5 if i<=12 else 7.5,12.7+(5.5-(i-1 if i<=12 else 24-i))*1.27,8),'logic','side of selected adapter; pin label from top view, delivered solder pad identification open')
for key in ['VIN','GND','SCL','DI','SDA','CS','INT','RST','P0','P1']:
    frame('EXT_IMU.'+key,'BNO085',centre('BNO085'),'logic','source-labelled BNO085 header/pad approach')
for key in ['VIN','GND','BCLK','LRC','DIN','OUT+','OUT-']:
    frame('EXT_AMP.'+key,'MAX98357A_amp',centre('MAX98357A_amp'),'amp','labelled board terminal')
for key in ['+','-']:frame('EXT_SPK.'+key,'Speaker',[128,75 if key=='+' else 79,152],'audio','basket terminal area; delivered revision unknown')
for key in ['1_SIG','3_VCC','4_GND']:frame('EXT_TOUCH.GROVE.'+key,'TTP223_touch',[-8,-20,193],'touch','whole keyed Grove connector; fourth core NC')
for key,n,pt,zone in [('PI.USB2_B','CF17_PI_PRIMARY_USB_A_front',[-20,-19.39,111.1],'Pi'),('EXT_MIC.USB-C','E19_ReSpeakerSource',[-37,11,162],'mic'),('PI.CAMERA_CSI15','CF17_PI_PRIMARY_CSI',[-65,0,104],'Pi'),('EXT_CAM.CSI15','Camera3_NoIR_Wide',[-192,0,150],'head')]:frame(key,n,pt,zone)
for i in range(1,41):frame('PI.H'+str(i),'CF17_POL1992_FULL_MATED_BODY',[-99.6+2.54*((i-1)//2),23 if i%2 else 25.54,115.8],'Pi','J8 numbered crimp face, datum from full 1992')
for idx,leg in enumerate(['FL','FR','RL','RR']):
    arr=['Motor_ATO4A_'+('_1_' if idx<2 else '1_')+str(j+(idx%2)*3) for j in range(3)]
    for j,n in enumerate(arr):
        m=centre(n);a,b=bb(n)
        for key,pt in [('in',a),('out',b)]:frame('F_'+leg+str(j+1)+'.'+key,n,[pt[0],m[1],m[2]],'bank+' if m[1]>0 else 'bank-','complete blade fuse unit and TE ends; indexed installation assignment')
        for key in ['V','G','D']:frame(leg+str(j+1)+'.'+key,'WAVEGO_complete_126_source_solids',[(114 if idx<2 else -84),(85 if idx%2==0 else -85),61],'leg'+leg,'retained leg loom source/body transfer; distal length is a separate retained portion')
    mt='NIGHT_MTA0100335_UNKNOWN_'+str(idx);m=centre(mt)
    for key in ['in','out']:frame('F_'+leg+'.'+key,mt,m,'bank+' if m[1]>0 else 'bank-','adjustable land; both delivered lead lengths unknown')
for w in base['wires']:
    for key in (w['a'],w['b']):
        if '_Joint.' in key:
            n=next(n for n in S if n.startswith('NIGHT_INLINE') and key[:4] in n);a,b=bb(n);m=centre(n);m[0]=a[0] if key.endswith('factory') else b[0]
            frame(key,n,m,'bank+' if m[1]>0 else 'bank-','individual inline connector end')
# Shared accessible cross-sections, local guides preserved before/after mouth. One geometric spine per group.
zones={'upper':[2,-8,184],'BUS':[160,59,186],'bank+':[57,56,122],'bank-':[57,-51,121],'low':[29,-20,71],'power':[82,7,103],'Pi':[-42,12,115],'operator':[151,-37,104],'head':[-129,18,154],'logic':[118,22,140],'amp':[75,-30,142],'touch':[-7,-17,180],'mic':[-27,14,153],'audio':[110,52,148]}
for k in ['FL','FR','RL','RR']:zones['leg'+k]=[114 if k[0]=='F' else -84,90 if k[1]=='L' else -90,66]
regions={};wiremap=[]
mat=collections.defaultdict(list)
for row in base['body_material_portions']:mat[row['wire']].append({k:v for k,v in row.items() if k in ['physical_unit','sku','portion','retained_limit_mm','termination_project_allowance_mm','terminal_allowance_project_mm']})
def route(w):
    a,b=(ledger[w[key]] for key in ['a','b']);z1,z2=a['zone'],b['zone'];rid=' / '.join(sorted([z1,z2]))
    if rid not in regions:regions[rid]=dict(zones=sorted([z1,z2]),members=[],station_spine=[zones[z] for z in sorted(set([z1,z2]))])
    pts=[a['point'],zones[z1]]+([zones[z2]] if z1!=z2 else [])+[b['point']]
    if z1==z2=='logic' and a['actor'] in ['1608','Kamami575070'] and b['actor'] in ['1608','Kamami575070']:pts=[a['point'],b['point']]
    unit=dict(wire=w['id'],ends=[w['a'],w['b']],region=rid,length_to_station_faces_mm=round(length(pts),2),shared_approach=pts,material=mat.get(w['id'],[]),actual_cut_fit_slack=None)
    if w['id'] in physical:unit['JR_body_continuation']=physical[w['id']]
    regions[rid]['members'].append(w['id']);return unit
frame('F_PWM.in','E19_FieldAxialFuse',[-41,-42,65],'low','sleeved axial fuse input')
for w in base['wires']+add['connections']:wiremap.append(route(w))
assert len(wiremap)==160 and len({q['wire'] for q in wiremap})==160
wr('connected-map.json',dict(endpoints=ledger,regions=regions,wires=wiremap,JR=extra['JR'],source_counts=[134,26],physical_PASS=False))
