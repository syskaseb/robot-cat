"""Six changed corridors from the actual cd4715c collision witnesses.

Keep the three qualified whole curves unchanged. No shortest-two retry,
no radius relaxation, and no claim of body-material clearance from this math.
"""
import copy,json,subprocess
from shared_body36_macro_routes import E,W,N,S,U,D,packed_front_prefixes,rise,straight_to,math_gate,finish,spatial_half_return
from plan_current_moving_looms import exact_quarter,exact_turn_to

PARENT='cd4715c'

def material_revision(parent,base):
    from received_curve_splice import splice
    rows={r['wire']:copy.deepcopy(r) for r in base['rows']}
    rows.update({r['wire']:copy.deepcopy(r) for r in parent['changed_rows']})
    front=packed_front_prefixes(rows);result={};failures={}
    if 'W008' not in parent['qualified_changed_routes']:
        rows['W008'],q,error=splice(rows['W008'],front['W008'],base['routes']['W008'],2,2,65.99-1.25-10)
        if q:result['W008']=q
        else:failures['W008']=error
    r=rows['W030'];end=r['free_end'];p=front['W030'];rise(p,end[2]+10)
    p.append(exact_quarter(p[-1]['end'],U,S,10))
    # WHOLE measured module: case, both case bands/heads, both factory ends
    # and their collars. The first rejection witness was not its full space.
    module=[-186,-96.6,107.3,-106,-73.65,137.75];east=module[3]+5
    diagonal=[2**-.5,-2**-.5,0];start=p[-1]['end'];radius=10
    bridge=(east-start[0]-2*radius*(1-2**-.5))/(2**-.5)
    assert bridge>0
    p.append(exact_turn_to(p[-1]['end'],S,diagonal,radius));a=p[-1]['end']
    straight_to(p,[x+bridge*v for x,v in zip(a,diagonal)])
    p.append(exact_turn_to(p[-1]['end'],diagonal,S,radius));a=p[-1]['end']
    assert abs(a[0]-east)<1e-6 and a[1]>module[4]+1.25,'Complete side shift BEFORE the whole module north edge'
    straight_to(p,[a[0],end[1]+10,a[2]]);p.append(exact_quarter(p[-1]['end'],S,E,10))
    p.append(exact_quarter(p[-1]['end'],E,U,10));rise(p,150)
    p.append(exact_quarter(p[-1]['end'],U,E,10));a=p[-1]['end']
    straight_to(p,[end[0]-20,a[1],a[2]]);p.append(exact_quarter(p[-1]['end'],E,D,10));a=p[-1]['end']
    straight_to(p,[a[0],a[1],end[2]+10]);p.append(exact_quarter(p[-1]['end'],D,E,10))
    q,error=math_gate(r,[*p,*r['receiving_parts']])
    if q:result['W030']=dict(q,architecture='FR1_single_diagonal_S_offset_around_WHOLE_FHY_then_upper_gallery',
        whole_FHY_planning_envelope_mm=module,side_gallery_x_mm=east,
        envelope_rejects_or_proposes_only_actual_material_gate_required=True)
    else:failures['W030']=error
    return rows,result,failures

def plan(parent,base,material_only=False):
    if material_only:return material_revision(parent,base)
    rows={r['wire']:copy.deepcopy(r) for r in base['rows']}
    rows.update({r['wire']:copy.deepcopy(r) for r in parent['changed_rows']})
    front=packed_front_prefixes(rows);result={};failures={}
    for name in ('W004','W008','W019','W022','W030','W069'):
        r=rows[name];end=r['free_end']
        if name=='W004':
            # Go EAST below Foundation before crossing the north XB22 alley;
            # rise south of FL_G, then enter its neighbour from ABOVE.
            p=front[name];rise(p,rows['W020']['free_end'][2]-20)
            p.append(exact_quarter(p[-1]['end'],U,E,10));a=p[-1]['end']
            straight_to(p,[end[0]-10,a[1],a[2]]);p.append(exact_quarter(p[-1]['end'],E,U,10))
            rise(p,end[2]-20);p.append(exact_quarter(p[-1]['end'],U,N,10));a=p[-1]['end']
            straight_to(p,[a[0],end[1]-10,a[2]]);p.append(exact_quarter(p[-1]['end'],N,U,10))
            parts=[*p,*r['receiving_parts']];label='FL1_D_under_Foundation_east_then_above_FL_G_not_XB22'
        elif name=='W008':
            # Rejoin a real unchanged positive upper corridor, not the cubic
            # through FTYCradle. Preserve all its subsequent zigzag and land.
            tail=copy.deepcopy(base['routes'][name]['parts'][3:]);r['free_end']=tail[0]['start'];r['receiver_outward_axis']=W
            r['receiving_grip_part_index']+=len(tail)-len(r['receiving_parts']);r['receiving_parts']=tail
            p=front[name];rise(p,r['free_end'][2]-10);p.append(exact_quarter(p[-1]['end'],U,E,10))
            q,error=finish(r,p,'FR1_D_rejoin_existing_upper_positive_corridor_above_FTY')
            if q:result[name]=q
            else:failures[name]=error
            continue
        elif name=='W019':
            # Return on the WEST side of the W023 witness instead of dropping
            # at its occupied x=-94.75 lane. Full cardinal elbows, not offsets
            # to a spline whose real radius would remain below R10.
            p=front[name];rise(p,end[2]+10);p.append(exact_quarter(p[-1]['end'],U,N,10));a=p[-1]['end']
            straight_to(p,[a[0],end[1]+20,a[2]]);p.append(exact_quarter(p[-1]['end'],N,E,10));a=p[-1]['end']
            straight_to(p,[end[0]+10,a[1],a[2]]);p.append(exact_quarter(p[-1]['end'],E,D,10));a=p[-1]['end']
            straight_to(p,[a[0],a[1],end[2]+10]);p.append(exact_quarter(p[-1]['end'],D,S,10));a=p[-1]['end']
            straight_to(p,[a[0],end[1]+10,a[2]]);p.append(exact_quarter(p[-1]['end'],S,W,10));straight_to(p,end)
            parts=[*p,*r['receiving_parts']];label='FL1_G_return_inside_W023_occupied_drop_lane'
        elif name=='W030':
            # Cross the FR3 bundle in a raised OUTBOARD gallery. Do not raise
            # the initial vertical column through the retained head shell.
            p=front[name];rise(p,end[2]+10);p.append(exact_quarter(p[-1]['end'],U,S,10));a=p[-1]['end']
            straight_to(p,[a[0],end[1]+10,a[2]]);p.append(exact_quarter(p[-1]['end'],S,E,10))
            p.append(exact_quarter(p[-1]['end'],E,U,10));rise(p,150)
            p.append(exact_quarter(p[-1]['end'],U,E,10));a=p[-1]['end']
            straight_to(p,[end[0]-20,a[1],a[2]]);p.append(exact_quarter(p[-1]['end'],E,D,10));a=p[-1]['end']
            straight_to(p,[a[0],a[1],end[2]+10]);p.append(exact_quarter(p[-1]['end'],D,E,10))
            parts=[*p,*r['receiving_parts']];label='FR1_G_outboard_upper_gallery_before_FR3_crossing'
        elif name=='W022':
            # Cross W066 ABOVE, descend only north of the accepted GPIO entry.
            # The actual9mm grip is unchanged, no hidden E1 modification.
            p=copy.deepcopy(r.get('source_parts',[r['source_land']]));rise(p,90);p.append(exact_quarter(p[-1]['end'],U,S,10))
            temp=copy.deepcopy(r);temp['free_end']=[end[0],end[1]+20,100];temp['receiver_outward_axis']=N;temp['receiving_parts']=[]
            q,error=finish(temp,p,'FL2_high_crossing_before_north_GPIO_descent')
            if not q:failures[name]=error;continue
            p=q['parts'];p.append(exact_quarter(p[-1]['end'],S,D,10));a=p[-1]['end']
            straight_to(p,[a[0],a[1],end[2]+10]);p.append(exact_quarter(p[-1]['end'],D,S,10))
            parts=[*p,*r['receiving_parts']];label='FL2_above_W066_then_drop_north_of_GPIO'
        else:
            # A real 3D S-shift moves off W066's x137/z150 lane BEFORE the
            # long north run, then the R10 return reaches the unchanged land.
            import numpy as np
            p=copy.deepcopy(r['source_parts']);p.append(exact_quarter(p[-1]['end'],W,U,10));p.append(exact_quarter(p[-1]['end'],U,N,10))
            a=p[-1]['end'];v=np.asarray([end[0]-a[0],0,end[2]-a[2]]);v=(v/np.linalg.norm(v)).tolist()
            p.append(exact_quarter(p[-1]['end'],N,v,10));p.append(exact_quarter(p[-1]['end'],v,N,10))
            spatial_half_return(p,end,N);parts=[*p,*r['receiving_parts']];label='RL1_S_shift_before_W066_then_spatial_half_return'
        q,error=math_gate(r,parts)
        if q:result[name]=dict(q,architecture=label)
        else:failures[name]=error
    return rows,result,failures

if __name__=='__main__':
    from pathlib import Path
    root=Path(__file__).resolve().parents[2];folder='hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/body-harness-checkpoint/'
    parent=json.loads(subprocess.check_output(['git','show',PARENT+':'+folder+'body36-shared-macro-layout.json'],cwd=root))
    base=json.loads((root/folder/'body36-recovery-layout.json').read_text());rows,proposals,failures=plan(parent,base)
    print(json.dumps(dict(candidates={n:dict(guide_mm=q['guide_mm'],spare_mm=q['spare_before_trim_mm']) for n,q in proposals.items()},failures=failures)))
