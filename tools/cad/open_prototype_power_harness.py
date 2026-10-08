"""One coupled twelve-route power harness before native replacement.

All8MTA exits,5complete prefuse inputs,4S1 routes,actual laps/221-412
roles and independent straight grip segments. Factory100mm/OD4/R6 and
entry3mm remain explicit prototype assumptions, never catalogue values.
"""
from pathlib import Path
import copy, json, math, sys
import open_prototype_receiving_gallery as G
from open_prototype_receiving_gallery_recovery import PLAN as PREVIOUS, PROOF as PREVIOUS_PROOF
from open_prototype_complete_main_space import line, quarter, half_turn, factory_reverse
from open_prototype_bundle_spines import add, mul
from open_prototype_distribution_allocation import input_recipe
from test_open_prototype_receiving_gallery import geometric_length

PLAN=G.OUT/'power-harness-plan.json'
PROOF=G.OUT/'power-harness-checks.json'
R=25.2


def shift_path(start,end,direction,radius,last=9):
    # Reuse exact S-arcs, choosing a labelled free-entry straight. Grips may
    # be on a different explicit9mm straight; entry3 is NOT a supplier datum.
    if math.dist(add(start,mul(direction,math.dist(start,end))),end)<1e-7:
        return [line(start,end)]
    recipe=input_recipe(start,add(end,mul(direction,9-last)),direction,radius)
    recipe['segments'][-1]['end']=end
    return recipe['segments']


def build():
    p=G.read(PREVIOUS);old=copy.deepcopy(p);proof=G.read(PREVIOUS_PROOF)
    for path,h in proof['source_sha256'].items():
        if path!='tools/cad/open_prototype_receiving_gallery.py':assert G.sha(G.ROOT/path)==h,path
    p['runner_previous_source_snapshot']='20feaab; refactored runner pinned below, geometry inputs unchanged'
    ports={r['role']:r for r in p['ports']}
    changed=set()
    for row in p['distribution']:
        role=row['role'];destination={'P_AUX':[-40,50,138],
            'G2':[113,62.25,120],'D_RR':[113,-62.25,96]}.get(role)
        if not destination:continue
        delta=[destination[i]-row['centre_mm'][i] for i in range(3)]
        row['centre_mm']=destination;changed.add(row['native'])
        for port in p['ports']:
            if port['role'].split('.')[0]==role:port['point_mm']=add(port['point_mm'],delta)
    exchanges=[('FL_P.1','FL_P.5'),('FR_P.1','FR_P.5'),('P_AUX.4','P_AUX.5'),('P_SYS.2','P_SYS.5')]
    for a,b in exchanges:
        assert ports[a]['occupied'] and not ports[b]['occupied'],(a,b)
        ports[a]['occupied']=False;ports[b]['occupied']=True
    p['port_mapping']=[dict(original=r['role'],current=next((b for a,b in exchanges if a==r['role']),
        next((a for a,b in exchanges if b==r['role']),r['role']))) for r in old['ports']]
    p['port_mapping_original_snapshot']='20feaab; includes previous P_FRONT3/5 exchange'
    p['same_bus_additional_exchanges']=exchanges
    holders=[]
    for name,inlet,axis,target in [('F_PI',[110,40,125],[-1,0,0],'P_SYS.5'),
        ('F_AUX',[110,-40,125],[-1,0,0],'P_REAR.3'),
        ('F_HY',[-3,50,110],[1,0,0],'P_AUX.2'),
        ('F_HP',[-3,25,110],[1,0,0],'P_AUX.3'),
        ('F_TY',[-3,0,110],[1,0,0],'P_AUX.5')]:
        parts=shift_path(inlet,ports[target]['point_mm'],mul(axis,-1),6)
        if name in ('F_HY','F_HP','F_TY'):
            first=math.dist(parts[0]['start'],parts[0]['end']);delta=mul(mul(axis,-1),3-first)
            parts[0]['end']=add(parts[0]['start'],mul(mul(axis,-1),3))
            for part in parts[1:-1]:
                for k in ('start','mid','end'):
                    if k in part:part[k]=add(part[k],delta)
            parts[-1]['start']=add(parts[-1]['start'],delta)
        strip=14 if name in ('F_PI','F_AUX') else 11;limit=50 if strip==14 else 84.5
        centre=geometric_length(parts);assert centre+strip<=limit,(name,centre+strip,limit)
        out=add(inlet,mul(axis,51));a=add(out,mul(axis,3));output=[line(out,a)]
        if name=='F_TY':
            q=quarter(a,axis,[0,-1,0],6);output.append(q)
            a=add(q['end'],[0,-29,0]);output.append(line(q['end'],a))
            q=quarter(a,[0,-1,0],[0,0,-1],6)
        else:q=quarter(a,axis,[0,0,-1],6)
        output.append(q);cut=add(q['end'],[0,0,-18]);output.append(line(q['end'],cut))
        holders.append(dict(holder=name,input_mm=inlet,axis=axis,target=target,
            input_parts=parts,input_centreline_mm=centre,input_blank_mm=centre+strip,input_limit_mm=limit,
            output_mm=out,output_parts=output,cut_mm=cut,sleeve_mm=26.5,
            sleeve_factory_mm=17.25,sleeve_extension_mm=9.25,new_insulation_mm=18.25,
            output_load_continuation_open=True))
    p['holders']=holders
    for m in p['mts']:
        if m['native'] in ('MTA_FL_CP2','MTA_FR_CP2'):
            m['centre_mm']=[-5,40.5 if 'FL' in m['native'] else-40.5,88];changed.add(m['native'])
    p['main_targets'].update(W026='FL_P.5',W037='FR_P.5')
    feeds=[]
    for leg,ident,role in [('FL','W041','P_FRONT.2'),('FR','W042','P_FRONT.5'),
                         ('RL','W044','P_REAR.5'),('RR','W052','P_REAR.2')]:
        m=next(r for r in p['mts'] if r['native']=='MTA_'+leg+'_CP2')['centre_mm']
        front=leg in ('FL','FR');sign=1 if leg in ('FL','RL') else -1;d=[-1 if front else 1,0,0]
        start=add(m,mul(d,17.5));a=add(start,mul(d,9))
        y=sign*10 if front else (44 if leg=='RL' else 10);z=138 if front else 112
        reverse=factory_reverse(a,d,[0,y-m[1],z-m[2]])
        cut=add(reverse[-1]['end'],mul(d,-17));factory=[line(start,a)]+reverse+[line(reverse[-1]['end'],cut)]
        t=mul(d,-1);newstart=add(cut,mul(t,-8));target=ports[role]['point_mm']
        if front:extension=shift_path(newstart,target,t,R)
        else:
            a=add(newstart,mul(t,26));turn=half_turn(a,t,[0,target[1]-y,target[2]-z])
            extension=[line(newstart,a),turn,line(turn['end'],target)]
        feeds.append(dict(id=ident,side='source',leg=leg,target=role,factory_parts=factory,
            extension_parts=extension,joint=dict(kind='solder_lap',sku='TE5053142077',lap_mm=8,
                sleeve_mm=26,factory_sleeve_mm=17,extension_sleeve_mm=9,
                centreline_cut_mm=cut,axis=t,maximum_expanded_OD_mm=9.5),
            factory_blank_mm=geometric_length(factory)+8,
            independent_factory_grip='First9mm before bend',
            independent_HELU_grip='Straight9mm after sleeve or before terminal S-curve',
            additional_FL_extension_is_candidate_not_selected=True))
    for leg,ident,role in [('FL','W026','FL_P.5'),('FR','W037','FR_P.5'),
                         ('RL','W045','RL_P.1'),('RR','W053','RR_P.1')]:
        m=next(r for r in p['mts'] if r['native']=='MTA_'+leg+'_CP2')['centre_mm']
        front=leg in ('FL','FR');sign=1 if leg in ('FL','RL') else-1;d=[1 if front else-1,0,0]
        start=add(m,mul(d,17.5));cut=[65,sign*40.5,90] if front else[45,-12 if leg=='RL' else-40,130]
        factory=shift_path(start,cut,d,6);newstart=add(cut,[0,-sign*6.5,0]);target=ports[role]['point_mm']
        approach=[target[0]+R,sign*37.3,67.99]
        if front:extension=shift_path(newstart,approach,mul(d,-1),R)
        else:
            a=add(newstart,[30,0,0]);turn=half_turn(a,[1,0,0],[0,approach[1]-a[1],approach[2]-a[2]])
            extension=[line(newstart,a),turn,line(turn['end'],approach)]
        q=quarter(approach,[-1,0,0],[0,sign,0],R)
        extension.extend([q,line(q['end'],target)])
        feeds.append(dict(id=ident,side='output',leg=leg,target=role,factory_parts=factory,
            extension_parts=extension,factory_blank_mm=geometric_length(factory)+11,
            joint=dict(kind='WAGO221-412',installed_existing_role=leg+'_OUTPUT',
                factory_port_mm=cut,extension_port_mm=newstart,
                case_x_mm=sorted([cut[0],cut[0]+13*d[0]]),
                case_y_mm=[cut[1]-sign*3.25-9.15,cut[1]-sign*3.25+9.15],
                case_z_mm=[cut[2]-4.075,cut[2]+4.075]),
            independent_factory_grip='Last9mm before connector',
            independent_HELU_grip='Straight9mm before final R25.2 bend',
            free_WAGO_entry_straight_mm=3,entry_is_project_allowance_not_catalog=True))
    for f in feeds:assert f['factory_blank_mm']<=100,(f['id'],f['factory_blank_mm'])
    p['feeds']=feeds;p['S1_ring_rotation']=[]
    for r in p['S1']:
        ring=r['ring'];n=int(ring['role'].split('.')[1]);cx=120.2 if n in (2,3) else 132.2
        cz=85 if n in (2,5) else 73;up=n in (2,5);d=[0,0,1 if up else -1]
        p['S1_ring_rotation'].append(dict(native=ring['native'],pivot=[cx,33,cz],
            old_departure=ring['departure'],new_departure=d,wire=r['id']))
        ring['point_mm']=[cx,33,cz+(22.123 if up else-22.123)];ring['departure']=d
        s=ring['point_mm'];a=add(s,mul(d,3));parts=[line(s,a)]
        if up:
            turn=half_turn(a,d,[-80,16 if n==2 else 10,0]);parts.append(turn);a=turn['end']
            if n==5:
                b=add(a,[0,0,-9]);parts.append(line(a,b));a=b
            q=quarter(a,[0,0,-1],[1,0,0],R);parts.append(q)
            parts+=shift_path(q['end'],ports[r['target']]['point_mm'],[1,0,0],R,9 if n==2 else 3)
        else:
            q=quarter(a,[0,0,-1],[-1,0,0],R);parts.append(q)
            if n==3:
                b=[-1.4,33,q['end'][2]];parts.append(line(q['end'],b))
            else:
                b=[30,-13,q['end'][2]];parts+=shift_path(q['end'],b,[-1,0,0],R)
            q=quarter(b,[-1,0,0],[0,0,1],R);parts.append(q)
            b=[q['end'][0],q['end'][1],114.8 if n==3 else 94.8]
            parts.append(line(q['end'],b));q=quarter(b,[0,0,1],[1,0,0],R);parts.append(q)
            parts+=shift_path(q['end'],ports[r['target']]['point_mm'],[1,0,0],R)
        r['full_parts']=parts;r['entry_mm']=ports[r['target']]['point_mm']
        r['full_route_and_replacement_of_legacy_920mm_open']=True
        r['ring_entry_straight_mm']=3;r['independent_grip']='Explicit9mm straight on route, not WAGO lever or guessed ring bearing'
    p.update(status='ONE_COMPLETE12_POWER_ROUTE_HYPOTHESIS_NATIVE_AND_REST_OF_BODY_OPEN',
        proposed_levels=dict(front_MTA=88,central_sources=110,Pi_AUX_sources=125,
            main_front_receiving=140,rear_MTA=147,signal_galleries=[120,96]),
        source_sha256={str(x.relative_to(G.ROOT)).replace('\\','/'):G.sha(x) for x in
            (PREVIOUS,PREVIOUS_PROOF,Path(__file__),Path(G.__file__),G.MOUNTS,G.CONTEXT)})
    p['invalidated'].extend(['Front MTA and5source native seats',
        'G2/D_RR/PA/PSYS receiving supports and all affected port fanouts',
        'Four S1 terminal orientations/bearing and connected service require new qualification'])
    p['preserved']=['P0/E6/15drives/MG92B/325x200x160/MAIN46.52/bankR47',
        'Rear MTA poses and every purchased role/quantity; delivery gates retained']
    changed.update(m['native'] for m in p['mts'] if m['native'] in ('MTA_FL_CP2','MTA_FR_CP2'))
    changed.update(r['native'] for r in p['S1_ring_rotation'])
    for h in holders:changed.update(h['holder']+'/'+s for s in ('case','input','output','sleeve','new_insulation','ATO_tool_budget'))
    for f in feeds:changed.update(f['id']+'/'+s for s in ('factory','extension','joint','sleeve'))
    changed.update(r['id']+'/full' for r in p['S1'])
    changed.update(f['id']+'/entry9mm' for f in feeds)
    changed.update(r['id']+'/'+s for r in p['S1'] for s in ('ring9mm','entry9mm'))
    return p,proof,changed


if __name__=='__main__':
    p,reuse,changed=build()
    print(json.dumps(dict(holders=[(h['holder'],h['input_blank_mm']) for h in p['holders']],
        feeds=[(f['id'],f['factory_blank_mm']) for f in p['feeds']],
        full_S1=4,main_routes=8,ports=len(p['ports']),occupied=sum(x['occupied'] for x in p['ports']))),flush=True)
    if '--preflight' not in sys.argv:G.main(p,PLAN,PROOF,reuse,changed)
