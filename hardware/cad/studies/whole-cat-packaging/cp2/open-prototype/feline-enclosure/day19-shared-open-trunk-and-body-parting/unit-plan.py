from common import *
from scipy.spatial import cKDTree
d=rd(G/'whole-termination-plan.json');lay=rd(P/'shared-lay.json')['allocations'];r={a['wire']:a for a in d['wires']};need=rd(H/'electronics/kicad-current/design.json')
for w,q in r.items():
 if '/' in w:
    parent,portion=w.split('/',1)
    mat=[dict(a) for a in need['body_material_portions'] if a['wire']==parent and a['portion']==portion]
    for a in mat:
        for key in ['nominal_fit_blank_mm','minimum_project_blank_mm','guide_mm']:a.pop(key,None)
        if 'MTA0100335' in a['sku']:a['retained_limit_mm']=None
    if mat:q['material']=mat
for w,q in lay.items():
 r[w].update(shared_approach=q['stations'],regional_transport_mm=q['transport_mm'],H19=q)
 if 'project_bulk_blank_mm' in q:r[w]['proposed_blank_mm']=q['project_bulk_blank_mm']
 if 'one_900_keep_incl_16_11_35' in q:r[w]['planned_keep_mm']=q['one_900_keep_incl_16_11_35']
for k,v in d['endpoints'].items():
 if k.startswith('D_FL.'):
    x,y,z=v['point'];v.update(point=[274-x,-139-y,z],outward_axis=[0,-1,0],kind='five contacts rotate together in existing keyed bank; front of case faces negative Y')
for q in r.values():
 for i,k in enumerate(q['ends']):
    if k.startswith('D_FL.') and q['wire']!='W002':
        pt=np.array(d['endpoints'][k]['point']);approach=q['shared_approach'];seg=[(pt+[0,-11,0]).tolist(),pt.tolist()]
        q['shared_approach']=(seg[::-1]+approach[1:]) if i==0 else (approach[:-1]+seg);q['regional_transport_mm']=round(float(np.linalg.norm(np.diff(q['shared_approach'],axis=0),axis=1).sum()),2);q['mouth_qualified']=True
b=rd(P/'battery-leads.json');d['units']['BUS900'].update(required_axial_length=max(r[w]['planned_keep_mm'] for w in ['W002','W003']),two_core_kept_mm=[r[w]['planned_keep_mm'] for w in ['W002','W003']],common_stations=lay['W002']['stations'][:8])
amount=[lay[w]['output_keep_incl_25_5_20'] for w in ['W079','W080']];d['units']['K1474'].update(power_pair_kept=amount,input_required=lay['W078']['required_incl_8_5_15'],gross_parent_debits_per_core_mm=[amount[0]+210,amount[1]])
for w,i in [('W079',0),('W080',1)]:r[w]['proposed_keep_mm']=amount[i]
r['W078']['required']=lay['W078']['required_incl_8_5_15']
for w in ['W001','W075']:
 tr=b['ground' if w=='W001' else 'input']['points'];r[w].update(shared_approach=tr[::5]+[tr[-1]],regional_transport_mm=round(float(np.linalg.norm(np.diff(tr,axis=0),axis=1).sum()),3))
d['endpoints']['BAT.minus'].update(point=[24,-30,102],kind='harness-side boot approach; delivered cell exit/length unknown');d['endpoints']['BAT.plus'].update(point=[12,-30,102],kind='stationary W075 solder-cup approach, 5 mm terminal debit')
for w,k in [('EXT023','+'),('EXT024','-')]:
 q=lay[w];d['endpoints']['EXT_AMP.OUT'+k].update(point=q['terminal_side_project_mouth'],kind='X1 housing at two measured mounting datums; mouth Z project');d['endpoints']['EXT_SPK.'+k].update(point=q['stations'][-1],kind='approach to underside of installed nominal speaker; delivered tab position unknown')
d['units']['E2']=rd(F/'unit-plan.json')['E2'];d['units']['source_remaining']=dict(MG_each=250,JR_each=300,DATA500=[26,448,26],FFC200=[190,10],USB_AUDIO_delivered=None)
d['units']['battery']=dict(F0_lead_with_termination=b['W075_with_5_termination_mm'],limit=50,unplug_stroke=14,mobile_bight=[q['developed_mm'] for q in b['battery_return']],stock_from_delivered_cell_unknown=True,W001_remaining_obstacle='G1.2 approach: eight sampled jacket points inside front frame')
d['H19_terminal_limitations']=['Leg body exit windows are sized for three looms; exact keyed distal port, delivered length and physical logical corner mapping must be bound before cutting.', 'R7/R8/R9 remain at their respective servo-side mates. Support each body in its existing pocket. Pair one resistor lead to the rear PWM contact and the other to the rear local signal-GND contact. Form leads to separate exposed termination tabs only, sleeve separately to the body, support by the rigid pocket rather than either crimp. Rear solderable access and tab retention with intact stock crimps unverified; no crimp insulation stripping or new part assumed.', 'F0 and five FHAC bodies are project installation fields in source-budget.json. Intersections are unresolved allocations; do not infer measured physical housing contact.', 'BNO/Grove/speaker terminal points from G include gross approach regions rather than measured pad locations. Complete actual plug assignment and stock length before build.']
d['wires']=list(r.values());wr('whole-termination-plan.json',d)
tracks=rd(P/'named-approaches.json');pts=np.vstack([q['points'] for n,q in tracks.items() if n.startswith(('XB','XS'))]);tree=cKDTree(pts)
check=[]
for q in b['battery_return']:
 for sg in [-1,1]:
    pp=np.array(q['points'])+[sg*1.87,-sg*1.87,0];pp=np.vstack([np.linspace(a,c,20) for a,c in zip(pp,pp[1:])]);v=tree.query(pp)[0];check.append(dict(lift=q['lift_mm'],side=sg,minimum_axis_distance=float(min(v)),combined_radii=3.45))
wr('split-occupancy.json',dict(JR_nine_pitch=3.2,diameter=2.1,minimum_packed_square=8.5,wires_against_hand_moving_bight=check,interpretation='closest sampled jacket centres at unclamped service bend. Negative margin requires over-under dressing and available space; does not by itself indicate a rigid collision.'))
