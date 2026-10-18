"""One frame-relative complete power chain, no rigid-template grid.

Preserve all8 occupied ends. Whole P_SYS stands below S0, F_PI lies in
the middle spine below the bank, MAIN reversed above its four down exits.
All source lengths, sleeve and full common jacket restraints precede CAD.
"""
import json,math,time,sys
from pathlib import Path
from plan_feline_n01_coupled_pi_bus import OUT,ROOT,BASE,Route,build_all_ends_unit,add,scale,sha

def build():
    tick=time.monotonic();p=build_all_ends_unit()
    ledgerpath=OUT/'n01-complete-end-allocation.json';ledger=json.loads(ledgerpath.read_text())
    ends={e['role']:e for e in ledger['endpoints']}
    def anchored(R,old,new):
        return {'rotation_rows':R,'translation_mm':[n-sum(a*b for a,b in zip(row,old)) for n,row in zip(new,R)]}
    p['F_PI'].update(centre_mm=[-50.5,0,30.9],input_mm=[-76,0,30.9],output_mm=[-25,0,30.9],
        rotation_relative_current=[[-1,0,0],[0,-1,0],[0,0,1]])
    p['relative_poses']={
        'WAGO:P_SYS_new':anchored([[0,-1,0],[0,0,-1],[1,0,0]],ends['P_SYS.5']['point_mm'],[-106,0,30.9]),
        'MAIN':anchored([[-1,0,0],[0,1,0],[0,0,-1]],ends['MAIN.VIN']['point_mm'],[-38.1,0,94.2])}
    w=Route(p['F_PI']['input_mm'],[-1,0,0]).line(30).record('W043',1.7)
    w.update(strip_mm=12,raw_required_mm=42,nominal_fit_blank_mm=45,selected_pre_fuse_limit_mm=50,
        factory_tip_removal_max_mm=8.35,source_draw_required_mm=53.35,
        supplier_shortest_including_tip_mm=84.5)
    f=Route(p['F_PI']['output_mm'],[1,0,0]).line(4).turn([0,0,1],9).turn([-1,0,0],9).line(25).record('W077',1.7)
    f.update(factory_tip_removal_max_mm=8.35,supplier_shortest_including_tip_mm=84.5,
        source_draw_required_mm=60+8.35,nominal_fit_blank_after_tip_removal_mm=60,bare_overlap_included_mm=8)
    tip16=f['end_mm'];tip18=add(tip16,[8,0,0]);x=tip16[0];z=tip16[2]
    p['splice']={'centre_mm':add(tip16,[4,0,0]),'tip16_mm':tip16,'tip18_mm':tip18,'axis':[-1,0,0],
        'sleeve_blank_mm':20,'sleeve_x_mm':[x-6,x+14],'bare_overlap_x_mm':[x,x+8],
        'jacket_grip16_x_mm':[x+16,x+25],'jacket_grip18_x_mm':[x-17,x-8],
        'outer_project_OD_mm':4.2,'clip_reservation_mm':[[x-17,-4.1,z-4.1],[x+25,4.1,z+4.1]],
        'grips_outside_sleeve':True,'grip_clear_gap_each_mm':2,'additional_splice_or_connector':False}
    r=Route(tip18,[-1,0,0]).line(25).turn([0,0,1],11.1).turn([1,0,0],11.1).line(13.8).turn([0,0,1],11.1).line(12)
    donor=r.record('W078',1.05);assert math.dist(donor['end_mm'],[-38.1,0,94.2])<1e-7
    donor.update(PCB_insertion_allowance_mm=3,raw_required_mm=donor['length_mm']+3,
        selected_retained_limit_mm=150,selected_fit_blank_mm=140,proposed_fit_blank_mm=115,one_K1474_preserved=True)
    p['routes']=[w,f,donor];p['shifts_mm']={};p['all_unit_ends']=[];p['additional_end_prefixes']=[]
    for e in ledger['endpoints']:
        if e['group'] not in p['relative_poses']:continue
        P=p['relative_poses'][e['group']];R=P['rotation_rows']
        pt=add([sum(a*b for a,b in zip(row,e['point_mm'])) for row in R],P['translation_mm'])
        d=[sum(a*b for a,b in zip(row,e['departure_axis'])) for row in R]
        length=12 if e['group']=='MAIN' else 9;radius=1.05 if e['group']=='MAIN' else 1.7 if e['wire']=='W043' else 2.1
        p['all_unit_ends'].append({'id':e['id'],'wire':e['wire'],'role':e['role'],'point_mm':pt,
            'departure_axis':d,'initial_mm':length,'radius_mm':radius,'source':'Current178end identities; whole component transform once'})
        if e['wire'] not in ('W043','W078'):
            row=Route(pt,d).line(length).record('End:'+e['id'],radius);row['logical_wire']=e['wire'];p['additional_end_prefixes'].append(row)
    assert len(p['all_unit_ends'])==8 and len(p['additional_end_prefixes'])==6
    p['shared_relief_reservations']={'P_SYS_CommonRelief':[[-106,-4.1,.8],[-97,4.1,35]],
        'MAIN_CommonRelief':[[-41.15,-3.05,82.2],[-24.55,3.05,91.2]]}
    p['necessary_length_gate']={'W043':42<=45<=50 and 45+8.35<=84.5,
        'W077':f['length_mm']<=60 and 60+8.35<=84.5,'W078':donor['raw_required_mm']<=115<=150,
        'exact_endpoint_match':True,'full_geometry_and_tools_open':True,'ready_for_changed_interface_screen':True}
    p['stock_candidate'].update(red_W078_candidate_mm=115,red_remaining_mm=660,
        positive_path_candidate_mm=45+60+115)
    p.update(unit_world_pose_pending=False,world_fixed_frame_plan=True,selected=False,N01_complete=False,
        changed_cause='Whole rigid tray grid had no conservative placement. Do not densify it. Allocate existing P_SYS below S0, long F_PI along central frame, complete solder and donor below JPWM, MAIN reversed in space between JPWM/Pi/PWM. All8ends before actual CAD; no new component or source length waiver.',
        next='One changed-interface screen with current clear axial4MTA branches, all8custom ends,24bank bends and complete BUS. Full common restraints/root/assembly/true-envelope/36motion remain gates.',
        worker_seconds=round(time.monotonic()-tick,4))
    p['source_sha256'][Path(__file__).relative_to(ROOT).as_posix()]=sha(Path(__file__))
    return p

def build_fitted():
    p=build();dx=-2.45;z=41.1
    p['F_PI'].update(centre_mm=[-50.5+dx,0,z],input_mm=[-25+dx,0,z],output_mm=[-76+dx,0,z],
        rotation_relative_current=[[1,0,0],[0,1,0],[0,0,1]])
    start=p['F_PI']['input_mm'];end=[7+dx,4,48.5];L=end[0]-start[0];H=math.hypot(end[1],end[2]-start[2])
    R=6;theta=math.acos(1-H/(2*R));land=(L-2*R*math.sin(theta))/2;u=[0,end[1]/H,(end[2]-start[2])/H];v=[1,0,0]
    q=add(start,scale(v,land));a=add(q,add(scale(v,R*math.sin(theta)),scale(u,R*(1-math.cos(theta)))))
    b=add(a,add(scale(v,R*math.sin(theta)),scale(u,R*(1-math.cos(theta)))))
    m1=add(q,add(scale(v,R*math.sin(theta/2)),scale(u,R*(1-math.cos(theta/2)))))
    m2=add(a,add(scale(v,R*(math.sin(theta)-math.sin(theta/2))),scale(u,R*(math.cos(theta/2)-math.cos(theta)))))
    w={'wire':'W043','radius_mm':1.7,'end_mm':end,'end_direction':v,'parts':[
        {'kind':'line','start':start,'end':q,'length_mm':land},
        {'kind':'arc','start':q,'mid':m1,'end':a,'radius_mm':R,'length_mm':R*theta},
        {'kind':'arc','start':a,'mid':m2,'end':b,'radius_mm':R,'length_mm':R*theta},
        {'kind':'line','start':b,'end':end,'length_mm':land}]}
    w.update(length_mm=sum(c['length_mm'] for c in w['parts']),strip_mm=12,nominal_fit_blank_mm=50,
        source_draw_required_mm=58.35,supplier_shortest_including_tip_mm=84.5,minimum_end_straight_mm=land)
    w['raw_required_mm']=w['length_mm']+12;assert land>=9 and w['raw_required_mm']<=50
    u=[0,-24/25,7/25]
    f=Route(p['F_PI']['output_mm'],[-1,0,0]).line(4).turn(u,12.5).turn([1,0,0],12.5).line(25).record('W077',1.7)
    f.update(factory_tip_removal_max_mm=8.35,supplier_shortest_including_tip_mm=84.5,
        source_draw_required_mm=78.35,nominal_fit_blank_after_tip_removal_mm=70,bare_overlap_included_mm=8)
    tip16=f['end_mm'];tip18=add(tip16,[-8,0,0]);x,y,zz=tip16
    p['splice']={'centre_mm':add(tip16,[-4,0,0]),'tip16_mm':tip16,'tip18_mm':tip18,'axis':[1,0,0],
        'sleeve_blank_mm':20,'sleeve_x_mm':[x-14,x+6],'bare_overlap_x_mm':[x-8,x],
        'jacket_grip16_x_mm':[x-25,x-16],'jacket_grip18_x_mm':[x+8,x+17],
        'outer_project_OD_mm':4.2,'clip_reservation_mm':[[x-25,y-4.1,zz-4.1],[x+17,y+4.1,zz+4.1]],
        'clip_parts':[[[x-25,y-4.1,zz-4.1],[x-16,y+4.1,zz+4.1]],
            [[x+8,y-4.1,zz-4.1],[x+17,y+4.1,zz+4.1]],
            [[x-25,y+2.1,zz-4.1],[x+17,y+4.1,zz+4.1]]],
        'clip_cause':'Two full end cuffs connected on inboard side; no filled bridge across retained P0 front mount or compressed solder sleeve.',
        'grips_outside_sleeve':True,'grip_clear_gap_each_mm':2,'additional_splice_or_connector':False}
    r=Route(tip18,[1,0,0]).line(25).turn([0,0,1],11.1);r.line(87.5-r.p[2]);donor=r.record('W078',1.05)
    donor.update(PCB_insertion_allowance_mm=3,raw_required_mm=donor['length_mm']+3,
        selected_retained_limit_mm=150,proposed_fit_blank_mm=80,one_K1474_preserved=True)
    ledger=json.loads((OUT/'n01-complete-end-allocation.json').read_text());ends={e['role']:e for e in ledger['endpoints']}
    def anchored(R,old,new):return {'rotation_rows':R,'translation_mm':[n-sum(a*b for a,b in zip(row,old)) for n,row in zip(new,R)]}
    p['relative_poses']={'WAGO:P_SYS_new':anchored([[0,1,0],[-1,0,0],[0,0,1]],ends['P_SYS.5']['point_mm'],end),
        'MAIN':anchored([[1,0,0],[0,-1,0],[0,0,-1]],ends['MAIN.VIN']['point_mm'],donor['end_mm'])}
    p['routes']=[w,f,donor];p['all_unit_ends']=[];p['additional_end_prefixes']=[]
    for e in ledger['endpoints']:
        if e['group'] not in p['relative_poses']:continue
        P=p['relative_poses'][e['group']];R=P['rotation_rows'];pt=add([sum(a*b for a,b in zip(row,e['point_mm'])) for row in R],P['translation_mm'])
        d=[sum(a*b for a,b in zip(row,e['departure_axis'])) for row in R];length=12 if e['group']=='MAIN' else 9
        radius=1.05 if e['group']=='MAIN' else 1.7 if e['wire']=='W043' else 2.1
        p['all_unit_ends'].append({'id':e['id'],'wire':e['wire'],'role':e['role'],'point_mm':pt,'departure_axis':d,'initial_mm':length,'radius_mm':radius})
        if e['wire'] not in ('W043','W078'):
            row=Route(pt,d).line(length).record('End:'+e['id'],radius);row['logical_wire']=e['wire'];p['additional_end_prefixes'].append(row)
    mainends=[e for e in p['all_unit_ends'] if e['role'].startswith('MAIN.')];xs=[e['point_mm'][0] for e in mainends]
    p['shared_relief_reservations']={'P_SYS_CommonRelief':[[end[0]-9,end[1]-4.1,end[2]-4.1],[end[0],end[1]+26+4.1,end[2]+4.1]],
        'MAIN_CommonRelief':[[min(xs)-3.05,y-3.05,75.5],[max(xs)+3.05,y+3.05,84.5]]}
    p['necessary_length_gate'].update(W043=w['raw_required_mm']<=50,W077=f['length_mm']<=70 and 78.35<=84.5,
        W078=donor['raw_required_mm']<=80<=150)
    p['stock_candidate'].update(red_W078_candidate_mm=80,red_remaining_mm=695,positive_path_candidate_mm=200)
    p['changed_cause']='Whole source circuit reversed: P_SYS inside frame above battery rather than through fore hinges; F_PI input has full two-arc source S, output uses oblique R12.5 return; two separate sleeve-external cuffs joined inboard. MAIN receives all4ends above bank while JPWM stays unchanged. No new SKU/extra splice/length waiver.'
    p['source_sha256'][Path(__file__).relative_to(ROOT).as_posix()]=sha(Path(__file__))
    return p

def build_backbone_free():
    p=build_fitted();s=p['splice'];delta=-6.1
    for key in ('centre_mm','tip16_mm','tip18_mm'):s[key][0]+=delta
    for key in ('sleeve_x_mm','bare_overlap_x_mm','jacket_grip16_x_mm','jacket_grip18_x_mm'):s[key]=[x+delta for x in s[key]]
    for box in [s['clip_reservation_mm']]+s['clip_parts']:
        for v in box:v[0]+=delta
    u=[0,-24/25,7/25]
    f=Route(p['F_PI']['output_mm'],[-1,0,0]).line(10.1).turn(u,12.5).turn([1,0,0],12.5).line(25).record('W077',1.7)
    assert math.dist(f['end_mm'],s['tip16_mm'])<1e-7
    f.update(factory_tip_removal_max_mm=8.35,supplier_shortest_including_tip_mm=84.5,
        source_draw_required_mm=83.35,nominal_fit_blank_after_tip_removal_mm=75,bare_overlap_included_mm=8)
    r=Route(s['tip18_mm'],[1,0,0]).line(25).turn([0,0,1],11.1);r.line(91-r.p[2]);d=r.record('W078',1.05)
    d.update(PCB_insertion_allowance_mm=3,raw_required_mm=d['length_mm']+3,
        selected_retained_limit_mm=150,proposed_fit_blank_mm=80,one_K1474_preserved=True)
    p['routes']=[p['routes'][0],f,d]
    P=p['relative_poses']['MAIN'];P['translation_mm'][0]+=delta;P['translation_mm'][2]+=3.5
    for e in p['all_unit_ends']:
        if e['role'].startswith('MAIN.'):
            e['point_mm'][0]+=delta;e['point_mm'][2]+=3.5
    for row in p['additional_end_prefixes']:
        if any(e['id']==row['wire'].removeprefix('End:') and e['role'].startswith('MAIN.') for e in p['all_unit_ends']):
            for part in row['parts']:
                for key in ('start','mid','end'):
                    if key in part:part[key][0]+=delta;part[key][2]+=3.5
            row['end_mm'][0]+=delta;row['end_mm'][2]+=3.5
    lo,hi=p['shared_relief_reservations']['MAIN_CommonRelief']
    for v in (lo,hi):v[0]+=delta;v[2]+=3.5
    p['backbone_changes']={
        'LowerRail0':[[-83,-23,39.72],[108,-17,42.72]],
        'Post-69_-1':[[-83,-43,41.72],[-77,-37,84.3]],
        'UpperStrip-1':[[-83,-30,81.3],[107,-10,84.3]],
        'PCBrootPi4_0_0':[[-3,-27.5,83.3],[3,-21.5,91.9]],
        'PCBrootPi4_0_1':[[27,-27.5,83.3],[33,-21.5,91.9]],
        'ForeNegativeLowerCrossbar':[[-83,-43,39.72],[-77,-17,42.72]],
        'ForeNegativeUpperCrossbar':[[-83,-43,81.3],[-77,-17,84.3]],
        'ForeNegativeBankConnection':[[-72,-23,81.3],[-66,-17,88]]}
    p['backbone_load_path']='New outboard fore post overlaps lower/upper crossbars by1/3mm; lower rail returns to received free-span clamps. Lowered negative upper strip feeds existing bank arm through whole vertical connection and extended Pi roots. Actual contacts still must be checked; not native or strength proof.'
    p['changed_cause']='After2central source trials, change the COMMON BACKBONE that caused10of11 reported overlaps, not keep protecting arbitrary posts/strip. Preserve complete P_SYS and F_PI poses and prefuse curve; longer complete factory output gives donor vertical axis left of real TE-IN bounds. Main plane91 derives from TEtop74.194+wire1.05+gap1.25+12land and retained JPWMtop86. No scalar rerun of old backbone.'
    p['necessary_length_gate'].update(W077=f['length_mm']<=75 and 83.35<=84.5,W078=d['raw_required_mm']<=80<=150)
    p['stock_candidate']['positive_path_candidate_mm']=205
    p['source_sha256'][Path(__file__).relative_to(ROOT).as_posix()]=sha(Path(__file__))
    return p

if __name__=='__main__':
    backbone_free='--backbone-free' in sys.argv
    fitted='--frame-fitted' in sys.argv
    dest=OUT/('n01-central-spine-power-plan-r3.json' if backbone_free else 'n01-central-spine-power-plan-r2.json' if fitted else 'n01-central-spine-power-plan.json');assert not dest.exists()
    p=build_backbone_free() if backbone_free else build_fitted() if fitted else build();dest.write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'gate':p['necessary_length_gate'],'lengths':{r['wire']:r['length_mm'] for r in p['routes']},'selected':False}))
