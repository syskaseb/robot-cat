"""One coupled source group, preserving S1, not a wiring acceptance.

All twenty stations, eight MTA tails, four S1 routes and both five FHAC
exits are allocated together. Downstream output routes and native grips are
explicitly OPEN. Manufacturer minima and project allowances stay separate.
"""
from datetime import datetime, timezone
from pathlib import Path
import json, math, sys, time
from open_prototype_wiring_endpoints import ROOT, BASE, read, sha
from open_prototype_entry_chambers import occupancy
from open_prototype_distribution_allocation import input_recipe
from open_prototype_complete_main_space import line, quarter, half_turn
from open_prototype_power_harness import shift_path

OUT=BASE/'wiring-checkpoint'
PLAN=OUT/'source-group-plan.json'
PROOF=OUT/'source-group-gate.json'
EAST=[1,0,0];WEST=[-1,0,0];UP=[0,0,1];DOWN=[0,0,-1]
NORTH=[0,1,0];SOUTH=[0,-1,0]

def add(a,b):return [x+y for x,y in zip(a,b)]
def sub(a,b):return [x-y for x,y in zip(a,b)]
def mul(a,n):return [x*n for x in a]
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def unit(a):return mul(a,1/math.sqrt(dot(a,a)))

def segment_geometry(p):
    """Actual three-point circle, including shallow S bends, not hardcoded90deg."""
    if p['kind']=='line':
        d=unit(sub(p['end'],p['start']))
        return math.dist(p['start'],p['end']),d,d,None
    a,m,b=p['start'],p['mid'],p['end'];u=sub(m,a);v=sub(b,a);n=cross(u,v)
    assert dot(n,n)>1e-12,'Degenerate arc'
    c=add(a,mul(add(mul(cross(v,n),dot(u,u)),mul(cross(n,u),dot(v,v))),1/(2*dot(n,n))))
    r=math.dist(a,c);na=unit(n)
    def angle(x,y):return math.acos(max(-1,min(1,dot(unit(sub(x,c)),unit(sub(y,c))))))
    return r*(angle(a,m)+angle(m,b)),unit(cross(na,sub(a,c))),unit(cross(na,sub(b,c))),r

def check_path(parts,start=None,end=None,min_radius=None):
    total=0;previous=None;last=None
    for p in parts:
        size,first,final,r=segment_geometry(p);total+=size
        if last is not None:
            assert math.dist(last,p['start'])<1e-6,'Disconnected path'
            assert dot(previous,first)>1-1e-7,'Kink between segments'
        if min_radius and r:assert r>=min_radius-1e-6,(r,min_radius)
        previous=final;last=p['end']
    if start:assert math.dist(start,parts[0]['start'])<1e-6
    if end:assert math.dist(end,last)<1e-6
    return total

def compose(start,commands):
    parts=[];p=start
    for kind,*args in commands:
        q=line(p,args[0]) if kind=='line' else quarter(p,*args) if kind=='quarter' else half_turn(p,*args)
        parts.append(q);p=q['end']
    return parts

def build():
    tick=time.monotonic();stations=[];ports={};permutation={}
    def station(role,c,model='415',rotation='0'):
        size=[37,22,11] if model=='615' else [30,19,9]
        if rotation in ('90','-90'):size=[size[1],size[0],size[2]]
        if rotation=='X90':size=[37,11,22]
        stations.append(dict(role=role,centre_mm=c,size_mm=size,model=model,rotation=rotation,
            supplier_cavity_datum_known=False,mount_status='OPEN_MATCHED_NATIVE_RESTRAINT'))
        x,y,z=c;pitch=6.5 if model=='615' else 4.75;depth=22 if model=='615' else 19
        for n in range(1,6):
            s=(n-3)*pitch;point,dep=[x+s,y-depth/2,z],SOUTH
            if rotation=='180':point,dep=[x-s,y+depth/2,z],NORTH
            if rotation=='90':point,dep=[x+depth/2,y+s,z],EAST
            if rotation=='-90':point,dep=[x-depth/2,y-s,z],WEST
            if rotation=='X90':point,dep=[x+s,y,z-11],DOWN
            ports[f'{role}.{n}']=dict(point_mm=point,departure=dep,
                basis='Envelope-derived project entry, not a delivered cavity datum')
    for roles,y,rot in [(['FL_P','FR_P','FL_G','RL_G','RR_G'],75,'0'),
                       (['FR_G','D_FR','D_FL','RL_P','RR_P'],-75,'180')]:
        for i,n in enumerate(roles):station(n,[-62+37*i,y,67.99],rotation=rot)
    station('P_SYS',[-38,-21.9,143.323],'615','90')
    station('P_FRONT',[-49,20,131],'615','90')
    station('P_REAR',[81.8,42.5,143],'615','X90')
    station('P_AUX',[129.5,-16,142],rotation='-90')
    for n,c,model in [('G1',[-80,-42,105],'615'),('G2',[-80,-17,115],'415'),
            ('G_AUX',[34,-51,70],'415'),('G_TAIL',[108,-43,109],'415'),
            ('D_RL',[132,-40,76],'415'),('D_RR',[132,-40,91],'415')]:station(n,c,model)
    for bus,values in [('P_SYS',[2,1,4,5,3]),('P_FRONT',[5,1,2,4,3]),
                       ('P_REAR',[3,1,5,2,4]),('FL_P',[5,2,3,4,1]),('FR_P',[5,2,3,4,1])]:
        permutation.update({f'{bus}.{i}':f'{bus}.{v}' for i,v in enumerate(values,1)})
    loads=occupancy(read(OUT/'routing-scope-plan.json'),permutation)
    assert len(stations)==20 and len(ports)==100 and sum(bool(loads[p]) for p in ports)==86
    assert all(len(loads[p])<=1 for p in ports)
    endpoint=read(OUT/'endpoint-plan.json');ends=[]
    for w in endpoint['body_conductors']:
        for e in w['ends']:
            old=e['role'];current=permutation.get(old,old)
            ends.append(dict(wire=w['id'],net=w['net'],original_role=old,current_role=current,
                datum=ports.get(current),status='CANDIDATE_DATUM_NOT_COMPLETE_ROUTE'))
    assert len(ends)==160
    def bind(w,target):assert any(e['wire']==w and e['current_role']==target for e in ends),(w,target)
    mta=[];tails=[]
    for leg,x,sgn,ident,source,out,target in [
            ('FL',-47,1,'W041','P_FRONT.1','W026','FL_P.5'),
            ('FR',0,1,'W042','P_FRONT.2','W037','FR_P.5'),
            ('RL',68.8,-1,'W044','P_REAR.1','W045','RL_P.1'),
            ('RR',94.8,-1,'W052','P_REAR.5','W053','RR_P.1')]:
        start=[x,sgn*3.5,117];output=[x,sgn*38.5,117]
        mta.append(dict(role='MTA_'+leg,centre_mm=[x,sgn*21,117],size_mm=[22,35,16],
            rotation_z_deg=sgn*90,source_exit_mm=start,output_exit_mm=output))
        if leg=='FR':parts=compose(start,[('line',[0,.5,117]),('quarter',SOUTH,WEST,6),
            ('line',[-17,-5.5,117]),('quarter',WEST,UP,6),('line',[-23,-5.5,125]),
            ('quarter',UP,NORTH,6),('line',[-23,7.5,131]),('quarter',NORTH,WEST,6),('line',[-38,13.5,131])])
        elif leg=='FL':parts=compose(start,[('line',[-47,.5,117]),('quarter',SOUTH,EAST,6),
            ('line',[-17,-5.5,117]),('quarter',EAST,UP,6),('line',[-11,-5.5,125]),
            ('quarter',UP,WEST,6),('quarter',WEST,NORTH,6),('line',[-23,1,131]),
            ('quarter',NORTH,WEST,6),('line',[-38,7,131])])
        else:parts=compose(start,[('line',[x,36.5,117]),('quarter',NORTH,UP,6),('line',[x,42.5,132])])
        for wire,side,p,target_role,strip,r in [(ident,'source',parts,source,14,6),
                (out,'output',input_recipe(output,ports[target]['point_mm'],[0,sgn,0],7.5)['segments'],target,11,7.5)]:
            bind(wire,target_role);d=check_path(p,end=ports[target_role]['point_mm'],min_radius=r)
            assert d+strip<=100,(wire,d+strip)
            tails.append(dict(wire=wire,leg=leg,side=side,target=target_role,segments=p,
                centreline_mm=d,required_blank_mm=d+strip,strip_allowance_mm=strip,
                OD_mm=4,min_radius_mm=r,assumed_factory_limit_mm=100,factory_limit_not_catalog=True))
    s1=[]
    s1_specs=[('W064',3,[98.077,33,73],WEST,'P_FRONT.5'),
              ('W065',6,[132.2,33,50.877],DOWN,'P_REAR.3'),
              ('W067',2,[98.077,33,85],WEST,'P_SYS.4'),
              ('W068',5,[132.2,33,107.123],UP,'P_SYS.5')]
    for wire,terminal,start,direction,target in s1_specs:
        if wire=='W064':parts=compose(start,[('line',[77.077,33,73]),('quarter',WEST,UP,25.2),
            ('line',[51.877,33,105.8]),('quarter',UP,WEST,25.2),('line',[-38,33,131])])
        elif wire=='W065':
            parts=compose(start,[('line',[132.2,33,41.877]),('half',DOWN,[-50.4,0,0])])
            parts+=input_recipe(parts[-1]['end'],ports[target]['point_mm'],UP,25.2)['segments']
        elif wire=='W067':parts=compose(start,[('line',[81.077,33,85]),('quarter',WEST,NORTH,25.2),
            ('line',[55.877,68.2,85]),('quarter',NORTH,WEST,25.2),('line',[-16.8,93.4,85]),
            ('quarter',WEST,SOUTH,25.2),('quarter',SOUTH,UP,25.2),('line',[-42,43,118.123]),
            ('quarter',UP,EAST,25.2),('half',EAST,[0,-58.4,0]),('line',[-27,-15.4,143.323])])
        else:
            parts=compose(start,[('line',[132.2,33,118.123]),('quarter',UP,WEST,25.2)])
            parts+=input_recipe(parts[-1]['end'],ports[target]['point_mm'],WEST,25.2)['segments']
        bind(wire,target);d=check_path(parts,start,ports[target]['point_mm'],25.2)
        s1.append(dict(wire=wire,terminal=terminal,eye_mm=[120.2 if terminal in (2,3) else 132.2,33,85 if terminal in (2,5) else 73],
            barrel_mm=start,barrel_direction=direction,target=target,segments=parts,centreline_mm=d,
            OD_mm=4.2,min_radius_mm=25.2,nominal_cut_length_mm=None,
            termination_allowances='OPEN_TE_insertion_and_WAGO_strip; centreline is NOT cut length'))
    holders=[]
    for role,start,axis,target in [('F_PI',[-12,-34.9,122.323],DOWN,'P_SYS.1'),
            ('F_AUX',[111.3,42.5,117],EAST,'P_REAR.4'),
            ('F_HY',[96,-42,139],WEST,'P_AUX.2'),('F_HP',[96,-16,139],WEST,'P_AUX.3'),
            ('F_TY',[96,10,139],WEST,'P_AUX.4')]:
        if role=='F_PI':inp=compose(start,[('line',[-12,-34.9,137.323]),('quarter',UP,WEST,6),('line',[-27,-34.9,143.323])])
        elif role=='F_AUX':inp=compose(start,[('line',[94.3,42.5,117]),('quarter',WEST,UP,6),('line',[88.3,42.5,132])])
        else:inp=input_recipe(start,ports[target]['point_mm'],EAST,6)['segments']
        target_original=next(e for b in endpoint['distribution_boundary'] if role+'.in' in b['ends'] for e in b['ends'] if e!=role+'.in')
        assert permutation.get(target_original,target_original)==target,(role,target_original,target)
        blank=check_path(inp,end=ports[target]['point_mm'],min_radius=6)+(14 if role in ('F_PI','F_AUX') else 11)
        assert blank<=(50 if role in ('F_PI','F_AUX') else 84.5),(role,blank)
        output=add(start,mul(axis,51));centre=add(start,mul(axis,25.5))
        # Rotate the existing case +1mm transverse reference offset, too.
        centre=add(centre,[1,0,0] if role=='F_PI' else [0,0,1])
        if role=='F_PI':outparts=[line(output,add(output,mul(DOWN,18)))];outdir=DOWN
        elif role=='F_AUX':outparts=compose(output,[('line',[165.3,42.5,117]),('quarter',EAST,DOWN,6),('line',[171.3,42.5,93])]);outdir=DOWN
        elif role=='F_TY':outparts=compose(output,[('line',[42,10,139]),('quarter',WEST,UP,6),('quarter',UP,WEST,6),('line',[12,10,151])]);outdir=WEST
        else:outparts=[line(output,add(output,mul(WEST,18)))];outdir=WEST
        outlength=check_path(outparts,start=output,min_radius=6)
        assert outlength<=84.5
        cut=outparts[-1]['end']
        holders.append(dict(role=role,input_mm=start,output_mm=output,axis=axis,centre_mm=centre,
            size_mm=[22,20.25,51] if role=='F_PI' else [51,20.25,22],
            input_target=target,input_segments=inp,input_blank_mm=blank,
            output_segments=outparts,output_prefix_mm=outlength,
            sleeve_start_mm=sub(cut,mul(outdir,17.25)),sleeve_end_mm=add(cut,mul(outdir,9.25)),
            sleeve_OD_mm=6,covered_overlap_mm=8,
            new_insulation_end_mm=add(cut,mul(outdir,18.25)),
            joint_basis='Retained FHAC covered solder recipe26.5mm/17.25factory/9.25new/8overlap, not a new connector selection',
            output_status='PREFIX_ONLY_DOWNSTREAM_LOAD_ROUTE_AND_STOCK_OPEN',
            independent_restraint_status='OPEN_NATIVE_INPUT_OUTPUT_GRIPS',
            factory_minimum_mm=84.5,case51mm_maximum_length_basis='FHAC manufacturer50+/-1; OD4/bendR6/cross-section project assumptions'))
    return dict(status='COUPLED_SOURCE_GROUP_HYPOTHESIS_NOT_NATIVE_ACCEPTANCE',selected=False,
        stage_completed=False,W5_complete=False,physical_pass=False,
        changed_cause='Preserve S1 module and ring-bearing datums; allocate four large-radius exits with rotated source buses, reversed rear MTA and five source/output prefixes together',
        stations=stations,ports=ports,permutation=permutation,body_ends=ends,occupied_ports=86,NC_ports=14,
        mta=mta,tails=tails,s1_routes=s1,holders=holders,
        preserved=['S1 module/body/control/bearings/F0 pose','bankR47/P0/E6/15drives/MG92B/325x200x160/MAIN46.52'],
        invalidated=['20 matched station mounts','former4MTA mounts','moved5FHAC mounts','four legacy S1 blanks920mm'],
        conditional_stock_reduction='No reduction until direct factory100/side delivery assumptions and entire route/support qualify',
        open_items=['Five full protected downstream routes, all other current80body conductors and leg entries',
            'Independent native restraints, WAGO lever qualification, ATO/connected assembly/removal',
            'Complete current cut lengths/stock/native exports and source-group geometry qualification',
            'Delivered U1 pinout/S0 datums/MTA usable per-side length and FHAC/WAGO entries'],
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (Path(__file__),
            OUT/'endpoint-plan.json',OUT/'routing-scope-plan.json',OUT/'obstacle-map-current.json',
            Path(sys.modules[input_recipe.__module__].__file__),Path(sys.modules[quarter.__module__].__file__))},
        worker_seconds=round(time.monotonic()-tick,6),finished_utc=datetime.now(timezone.utc).isoformat())

if __name__=='__main__':
    result=build();assert not PLAN.exists(),'Receive existing result, no unchanged repeat'
    PLAN.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=result['status'],tails=[(t['wire'],round(t['required_blank_mm'],3)) for t in result['tails']],
        s1_centrelines=[(r['wire'],round(r['centreline_mm'],3)) for r in result['s1_routes']],
        inputs=[(h['role'],round(h['input_blank_mm'],3)) for h in result['holders']],seconds=result['worker_seconds'])),flush=True)
