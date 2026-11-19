"""Stock assignment by physical parent. Reuse original graph without inventing connector pinouts."""
from pathlib import Path
import json,numpy as np,math
P=Path(__file__).parent;E=P.parent/'day19-simple-box-common-core'
H=next(q for q in P.parents if (q/'electronics/kicad-current/design.json').exists())
def rd(p):return json.loads(p.read_bytes())
def wr(n,x):(P/n).write_bytes((json.dumps(x,ensure_ascii=False,indent=1)+'\n').encode())
a=rd(H/'electronics/full-cat/closed-prototype-add7-2026-11-16/connections.json');lay=rd(P/'service-lay.json')
old=rd(E/'installed-looms.json')
roles={n.split('_')[-1]:v for n,v in lay['fixed'].items() if n.startswith('JR_')}
roles['pitch']=next(r for r in lay['pitch_transfer'] if r['yaw']==0)
jr={}
for role,q in roles.items():
    nets=next(r['nets'] for r in old['rows'] if r['unit']=='JR300_'+role)
    jr[role]=dict(stock=300,mated_pair=lay['pairs'][role],connector=12,transport_and_return=246,fan=25,insulated_land=9,proper_lap=8,sleeve_covering_existing_length=20,branches=[dict(target=t,lay=p,actual_body_continuation_cut_mm=None) for t,p in zip(nets,q['branches'])],accessible_change_of_shape='between co-yaw mate and fixed fan; no intermediate clamp' if role=='pitch' else 'static open gallery before outer cap',actual_slack=None)
pj=[]
for q in lay['pitch_transfer']:
    ds=q['analytic_lengths'];pj.append(dict(yaw=q['yaw'],inner_radius=q['inner_R'],return_arc_mm=ds[-2],entry_mm=ds[-3],exit_mm=ds[-1],two_legs_available_before_fan=2*min(ds[-3],ds[-1]),meaning='geometric length in paired straight legs of this return; sample in a free unrestrained chamber, not measured available slack'))
tof=[dict(q,sku=sku,color=col,port=a['connections'][next(i for i,x in enumerate(a['connections']) if x['id']==q['wire'])]['b']) for q,sku,col in zip(lay['ToF']['debits'],['23302','23301','23308','23308'],['red','black','yellow SDA','yellow SCL'])]
# These station coordinates allocate open shared routing to the PCB outline; delivered
# crimp seating, conductor lengths at the specific pads and hand-laid slack are open.
routes={'IMU':[[-75,24,113],[-55,33,123],[15,34,121],[41,32,111]],'I2S':[[-75,24,113],[-45,29,122],[12,21,125],[28,-20,125],[81,-34,133]],'TOUCH':[[-75,24,113],[-56,33,130],[-48,33,148],[-13,1,168],[-10,-16,174],[-8,-18,193]]}
gpio=[]
for parent in a['gpio_stock_allocation_proposal']['pairs']:
    portions=[]
    for pin in parent['pi_H_ends']:
        sig=a['pi_new_project_assignments'][str(pin)];k='I2S' if sig.startswith('I2S') else 'TOUCH' if sig.startswith('TOUCH') else 'IMU'
        path=routes[k];length=sum(np.linalg.norm(np.subtract(b,c)) for b,c in zip(path[1:],path[:-1]));portions.append(dict(Pi_H=pin,function=sig,corridor=path,station_transport_mm=round(length,2)))
    gpio.append(dict(parent=parent['physical_unit'],stock=600,portions=portions,remainder_for_both_end_approaches_terminations_slack_and_one_division=round(600-sum(q['station_transport_mm'] for q in portions),2),actual_cut=None,qualification='planning centre distances to installed module regions, local pad detail and actual stock unmeasured'))
wr('unit-plan.json',dict(MG={k:q for k,q in lay['fixed'].items() if k.startswith('MG_')},JR=jr,JR_pitch_return=pj,DATA500=lay['fixed']['DATA500'],FFC200=lay['FFC'],ToF=tof,bulk_scenario_by_sku_mm={'23302':667,'23301':654,'23308':1328},bulk_stock_measured=None,E2=lay['E2'],gpio_five_distinct_parents=gpio,other_groups=old['side_groups'],note='USB_AUDIO uses independent upper black USB port and ReSpeaker USB-C. Its stock and delivered boots are unknown. Prior four-leg BUS spine ends at old station; reallocation needed from body side to upper deck headers. Short P_SYSâ€“F_PI and P_REARâ€“F_AUX, soldered PCAâ€“E1, K1474 and Delock remain fixed.',actual_fit_cut_slack=None))

plan=rd(P/'unit-plan.json')
ports=rd(E/'installed-bus.json')['ports'];bus={}
for name,bb in ports.items():
    a=np.array(bb[:3]);b=np.array(bb[3:])
    coords=[(np.array([140,67.5,184])+np.array([-1,-1,1])*(q-np.array([92.804,78.11,133.77]))).tolist() for q in [a,b]]
    bus[name]=np.r_[np.min(coords,axis=0),np.max(coords,axis=0)].tolist()
plan['installed_BUS_port_bounds']=bus
plan['four_leg_BUS_transfer']=dict(prior_leg_stations=old['side_groups'][2]['spine'][:5],proposed_shared_rise=[[108,-51,88],[122,-44,131],[141,28,147],[146,60,168],[146,60,186]],ports=bus,qualification='upper passage through open BUS service window, branch to connector matching source wiring graph. Full header insertion, corner radius, occupancy with speaker and reserve per delivered lead remain open')
plan['other_groups'][2]['spine_status']='superseded after lower leg stations by four_leg_BUS_transfer'
wr('unit-plan.json',plan)
