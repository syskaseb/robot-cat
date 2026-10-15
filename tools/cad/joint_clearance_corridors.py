"""Whole departure/crossing corrections for four static witness conflicts.

No reduced clearance and no repeated scalar micro-shifts. Keep the four
positive changed routes. FHY input is a whole separate unresolved corridor.
"""
import copy
from shared_body36_macro_routes import E,W,N,S,U,D,packed_front_prefixes,rise,straight_to,math_gate,finish,spatial_half_return
from plan_current_moving_looms import exact_quarter

def plan(parent,base):
    rows={r['wire']:copy.deepcopy(r) for r in base['rows']}
    rows.update({r['wire']:copy.deepcopy(r) for r in parent['changed_rows']})
    front=packed_front_prefixes(rows);result={};failures={}
    for name in ('W004','W019','W022','W069'):
        if name in parent['qualified_changed_routes']:continue
        r=rows[name];end=r['free_end']
        if name=='W004':
            p=front[name]
            # Leave the V sibling's converging corner before its Z38 witness.
            p.append(exact_quarter(p[-1]['end'],U,S,10));p.append(exact_quarter(p[-1]['end'],S,U,10))
            rise(p,rows['W020']['free_end'][2]-20);p.append(exact_quarter(p[-1]['end'],U,E,10));a=p[-1]['end']
            straight_to(p,[end[0]-10,a[1],a[2]]);p.append(exact_quarter(p[-1]['end'],E,U,10))
            rise(p,end[2]-20);p.append(exact_quarter(p[-1]['end'],U,N,10));a=p[-1]['end']
            straight_to(p,[a[0],end[1]-10,a[2]]);p.append(exact_quarter(p[-1]['end'],N,U,10))
            label='FL1_D_whole_south_departure_before_V_sibling_convergence'
        elif name=='W019':
            p=front[name];rise(p,end[2]+10);p.append(exact_quarter(p[-1]['end'],U,N,10));a=p[-1]['end']
            straight_to(p,[a[0],end[1]+20,a[2]]);p.append(exact_quarter(p[-1]['end'],N,E,10));a=p[-1]['end']
            # Allocate the complete return WEST of W023, including both turns.
            straight_to(p,[end[0],a[1],a[2]]);p.append(exact_quarter(p[-1]['end'],E,D,10));a=p[-1]['end']
            straight_to(p,[a[0],a[1],end[2]+10]);p.append(exact_quarter(p[-1]['end'],D,S,10));a=p[-1]['end']
            straight_to(p,[a[0],end[1]+10,a[2]]);p.append(exact_quarter(p[-1]['end'],S,W,10));straight_to(p,end)
            label='FL1_G_whole_return_west_of_W023_including_descending_corner'
        elif name=='W022':
            p=copy.deepcopy(r.get('source_parts') or [r['source_land']])
            # Turn AWAY at the actual end of the source land, not after passing
            # W005's bend five mm farther up the old vertical column.
            p.append(exact_quarter(p[-1]['end'],U,W,10));p.append(exact_quarter(p[-1]['end'],W,U,10))
            rise(p,90);p.append(exact_quarter(p[-1]['end'],U,S,10))
            temp=copy.deepcopy(r);temp['free_end']=[end[0],end[1]+20,100];temp['receiver_outward_axis']=N;temp['receiving_parts']=[]
            q,error=finish(temp,p,'FL2_whole_west_departure_then_high_GPIO_crossing')
            if not q:failures[name]=error;continue
            p=q['parts'];p.append(exact_quarter(p[-1]['end'],S,D,10));a=p[-1]['end']
            straight_to(p,[a[0],a[1],end[2]+10]);p.append(exact_quarter(p[-1]['end'],D,S,10))
            label='FL2_west_departure_before_W005_and_north_GPIO_descent'
        else:
            p=copy.deepcopy(r['source_parts']);p.append(exact_quarter(p[-1]['end'],W,U,10));p.append(exact_quarter(p[-1]['end'],U,N,10))
            # Keep the ENTIRE U-return horizontal above W064; descend only
            # north of that feeder, rather than dropping diagonally through it.
            spatial_half_return(p,[end[0],end[1]+20,p[-1]['end'][2]],N)
            p.append(exact_quarter(p[-1]['end'],S,D,10));a=p[-1]['end']
            straight_to(p,[a[0],a[1],end[2]+10]);p.append(exact_quarter(p[-1]['end'],D,S,10))
            label='RL1_horizontal_high_return_then_far_north_drop_not_W064_diagonal'
        q,error=math_gate(r,[*p,*r['receiving_parts']])
        if q:result[name]=dict(q,architecture=label)
        else:failures[name]=error
    return rows,result,failures
