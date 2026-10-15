"""Joint outboard-root/inboard-S source architecture, not another root offset.

Place fixed grips at approved torso edge planes, stagger left/right free-wire
planes together, and turn the free flex through the central underframe space
before its spatial U. The S is a nominal free-wire shape, NOT a rigid guide or
an imaginary additional restraint. Retained source approaches/ends stay fixed.
"""
import copy,json,math,time
import numpy as np
import current_body_fanout_material as M
from open_prototype_path_preflight import samples
from pathlib import Path
from plan_near_axis_hip_sources import OUT,ROOT,SHA,endpoints,build,line,self_screen
from plan_current_moving_looms import add,mul,exact_turn_to
DOWN=[0,0,-1]


def run():
    tick=time.monotonic();pf=OUT/'body-underframe-near-axis-plan.json';prior=json.loads(pf.read_text())
    rows=copy.deepcopy(prior['hips']);rejected=[];R=31.5;options={}
    front=math.ceil(-120+4.4+.5);rear=math.floor(205-4.4-.5)
    for row in rows:
        is_front=row['physical_leg'].startswith('Front');right=row['physical_leg'].endswith('Right')
        x=(front+16*right) if is_front else (rear-16*right)
        row['previous_fixed_anchor_world_mm']=row['fixed_anchor_world_mm']
        row['fixed_anchor_world_mm']=[x,*row['fixed_anchor_world_mm'][1:]]
        side=1 if row['fixed_anchor_world_mm'][1]>0 else -1;inward=[0,-side,0]
        a=add(row['fixed_anchor_world_mm'],mul(DOWN,9));choices=[]
        for shift in (63.,72.,81.,90.,99.):
            prefix=[exact_turn_to(a,DOWN,inward,R)]
            if shift>2*R:prefix.append(line(prefix[-1]['end'],add(prefix[-1]['end'],mul(inward,shift-2*R))))
            prefix.append(exact_turn_to(prefix[-1]['end'],inward,DOWN,R))
            free=prefix[-1]['end'];prefix_mm=sum(p['length_mm'] for p in prefix)
            for beta in (0,-10,10,-20,20,-30,30,-45,45,-60,60):
                accepted=0
                for length in range(125,301,5):
                    # Reject cheap boundary poses BEFORE checking all31.
                    feasible=True
                    for h in (0,-15,15):
                        _,b,v,_=endpoints(row,h)
                        if any(build(free,b,v,length+d,beta_degrees=beta) is None for d in (-5,0,5)):
                            feasible=False;break
                    if not feasible:continue
                    poses=[]
                    for h in range(-15,16):
                        _,b,v,m=endpoints(row,h);middle=build(free,b,v,length,beta_degrees=beta)
                        if middle is None or any(build(free,b,v,length+d,beta_degrees=beta) is None for d in (-5,5)):break
                        parts=[line(row['fixed_anchor_world_mm'],a),*prefix,*middle,line(b,m)]
                        if self_screen(parts) is not None:break
                        poses.append(dict(angle=h,parts=parts))
                    if len(poses)==31:
                        choices.append((shift,prefix,prefix_mm,length,poses,beta));accepted+=1
                        if accepted==2 or len(choices)>=8:break
                if len(choices)>=8:break
            if len(choices)>=8:break
        if not choices:
            rejected.append(dict(loom=row['loom'],reason='No robust31pose compound spatial construction in bounded family'))
            row['poses']=[];continue
        options[row['loom']]=choices
        shift,prefix,prefix_mm,length,poses,beta=choices[0]
        row.update(poses=poses,free_entry_parts=prefix,free_entry_nominal_mm=prefix_mm,spatial_length_mm=length,
            flex_length_mm=prefix_mm+length,guide_mm=prefix_mm+length+18,inboard_shift_mm=shift,bridge_beta_degrees=beta,
            fixed_lands=[dict(id=row['loom']+'/Hip/Fixed',parts=[poses[15]['parts'][0]],owner='Body')],
            moving_lands=[dict(id=row['loom']+'/Hip/Moving',parts=[poses[15]['parts'][-1]],owner='Hip')])
        print('joint inboard-S options',row['loom'],len(choices),flush=True)
    # Source families must coexist BEFORE the whole-assembly material gate.
    axes=json.loads((ROOT/'hardware/simulation/p0/e6-leg-compatibility.json').read_text())['axes']
    clouds={};pair_receipts=[]
    def cloud(row,index):
        key=(row['loom'],index)
        if key not in clouds:
            poses=options[row['loom']][index][4];out=[]
            for pose in poses:
                if pose['angle'] not in (-15,0,15):continue
                parts=pose['parts']+M.B.moved_parts(row['source_parts'],row['source'],pose['angle'],0,axes)
                out.append(np.asarray([p for _,p in samples(parts,step=3)]))
            clouds[key]=out
        return clouds[key]
    if not rejected:
        for front_group in (True,False):
            pair=[r for r in rows if r['physical_leg'].startswith('Front')==front_group];left,right=pair
            viable=[]
            for i,aa in enumerate(options[left['loom']]):
                for j,bb in enumerate(options[right['loom']]):
                    gap=min(float(np.sqrt(((p[:,None,:]-q[None,:,:])**2).sum(axis=2).min())) for p in cloud(left,i) for q in cloud(right,j))
                    if gap>=8:viable.append((aa[5]!=bb[5],abs(aa[5])+abs(bb[5]),aa[2]+aa[3]+bb[2]+bb[3],i,j,gap))
            if not viable:
                rejected.append(dict(looms=[left['loom'],right['loom']],reason='No jointly separated sampled family in bounded options; NOT geometric impossibility'))
                continue
            _,_,_,i,j,gap=min(viable)
            for row,index in ((left,i),(right,j)):
                shift,prefix,prefix_mm,length,poses,beta=options[row['loom']][index]
                row.update(poses=poses,free_entry_parts=prefix,free_entry_nominal_mm=prefix_mm,spatial_length_mm=length,
                    flex_length_mm=prefix_mm+length,guide_mm=prefix_mm+length+18,inboard_shift_mm=shift,bridge_beta_degrees=beta,
                    fixed_lands=[dict(id=row['loom']+'/Hip/Fixed',parts=[poses[15]['parts'][0]],owner='Body')],
                    moving_lands=[dict(id=row['loom']+'/Hip/Moving',parts=[poses[15]['parts'][-1]],owner='Hip')])
            pair_receipts.append(dict(looms=[left['loom'],right['loom']],options=[i,j],minimum_sampled_mm=gap,planning_reserve_mm=1.75))
    result=copy.deepcopy(prior);result.update(status='REJECTED_INBOARD_S_SOURCE_MATH' if rejected else 'JOINT_INBOARD_S_SOURCE_MATH_ONLY_MATERIAL_ARMS_OPEN',
        hips=rows,rejected=rejected,joint_pair_receipts=pair_receipts,options_per_family={k:len(v) for k,v in options.items()},
        root_derivation=dict(approved_X_limits_mm=[-120,205],nominal_band_radial_mm=4.4,extra_edge_mm=.5,
            left_root_edge_planes_X_mm=[front,rear],right_root_plane_stagger_mm=16,body_Y_Z='Retained underframe layer'),
        changed_cause='Simple two-arc U crossed the lower leg/other source families. New four-arc free-flex topology moves its U into central underframe space, with joint staggered left/right planes. No lower radius, extra connector, invisible guide or added band.',
        source_sha256={f.relative_to(ROOT).as_posix():SHA(f) for f in (pf,Path(__file__),Path(__file__).with_name('plan_near_axis_hip_sources.py'),Path(__file__).with_name('spatial_down_up_flex.py'))},
        worker_seconds=round(time.monotonic()-tick,3),selected=False,W5_complete=False,physical_pass=False)
    (OUT/'body-inboard-s-hip-plan.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],rejected=rejected,worker_seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':run()
