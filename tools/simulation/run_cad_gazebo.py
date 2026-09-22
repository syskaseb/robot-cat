"""Run an isolated headless Gazebo Harmonic experiment, archive telemetry.

Run inside the project's Docker image. Uses simulation time, an independent
GZ_PARTITION, native effort-limited PID, and kills only its own process group.
No hardware bus is opened. A stepping test is not a walking certification.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import queue
import signal
import subprocess
import time
import numpy as np
from cad_model import OUT,WORLD,actuator_envelope,make_model,write_sdf
from cad_kinematics import stepping_targets,crawl_targets,smooth
from stance_search import displaced


def rpy(q):
    x,y,z,w=q
    return [math.atan2(2*(w*x+y*z),1-2*(x*x+y*y)),
            math.asin(np.clip(2*(w*y-z*x),-1,1)),
            math.atan2(2*(w*z+x*y),1-2*(y*y+z*z))]


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--mode',choices=['stand','step','crawl'],default='stand')
    parser.add_argument('--seconds',type=float,default=8)
    parser.add_argument('--stance-x',type=float,default=0.,help='foot offset relative to CAD, metres')
    parser.add_argument('--stance-z',type=float,default=0.,help='foot offset relative to CAD, metres')
    parser.add_argument('--mass',choices=['nominal','upper','lower'],default='nominal')
    parser.add_argument('--torque-cap',type=float,default=1.)
    parser.add_argument('--friction',type=float,default=.4)
    parser.add_argument('--step-seconds',type=float,default=3.)
    args=parser.parse_args()
    os.environ['GZ_PARTITION']='robot_cat_cad_'+str(os.getpid())
    from gz.transport13 import Node
    from gz.msgs10.model_pb2 import Model
    from gz.msgs10.actuators_pb2 import Actuators
    mass_options={'nominal':{},'upper':dict(petg_density=1.30,servo_g=89,bought_factor=1.25,reserve_g=180),
                  'lower':dict(petg_density=1.20,servo_g=60,bought_factor=.85,reserve_g=80)}
    model=make_model(json.loads((OUT/'geometry.json').read_text(encoding='utf8')),**mass_options[args.mass])
    feet=json.loads((OUT/'feet.json').read_text())
    names=[j['name'] for j in model['joints']]
    posed,_,neutral=displaced(model,feet,args.stance_x,args.stance_z)
    offset=[args.stance_x,0,args.stance_z]
    # Precompute IK: do not make the simulator wait on Python optimisation.
    trajectory_fn=crawl_targets if args.mode=='crawl' else stepping_targets
    trajectory=[trajectory_fn(model,feet,i*.01,step_seconds=args.step_seconds,offset=offset,support_com=posed['total']['com_m']) for i in range(max(1,int((args.seconds-3)*100)+2))] if args.mode!='stand' else []
    if trajectory:neutral=trajectory[0]
    node=Node();incoming=queue.Queue(maxsize=500)
    last_sample=[-1.]
    def callback(msg):
        t=msg.header.stamp.sec+msg.header.stamp.nsec*1e-9
        # Harmonic 8.11 ignores the newer publisher update_rate setting.
        if t-last_sample[0]<.01-1e-8:return
        last_sample[0]=t
        try:incoming.put_nowait(msg)
        except queue.Full:pass
    topic='/world/'+WORLD+'/model/robot_cat_cad/joint_state'
    assert node.subscribe(Model,topic,callback)
    motor_state={}
    def motor_callback(msg):
        t=msg.header.stamp.sec+msg.header.stamp.nsec*1e-9
        key=round(t,2)
        motor_state[key]=(t,{j.name:[j.axis1.position,j.axis1.velocity,j.axis1.force] for j in msg.joint})
        if len(motor_state)>1000:del motor_state[next(iter(motor_state))]
    assert node.subscribe(Model,'/robot_cat_cad/actuator_state',motor_callback)
    publisher=node.advertise('/robot_cat_cad/targets',Actuators)
    trials=OUT/'trials';trials.mkdir(exist_ok=True)
    stamp=time.strftime('%Y%m%d-%H%M%S')+'-'+args.mode
    worldfile=trials/(stamp+'.sdf')
    write_sdf(model,feet,args.torque_cap,args.friction,worldfile)
    records=[];result='timeout';start=time.monotonic()
    with (trials/(stamp+'.log')).open('w') as logfile:
        child=subprocess.Popen(['gz','sim','-s','-r','-v','2',str(worldfile)],stdout=logfile,stderr=subprocess.STDOUT,start_new_session=True)
        try:
            while time.monotonic()-start<max(90,args.seconds*8):
                if child.poll() is not None:
                    result='server_exited';break
                try:msg=incoming.get(timeout=.5)
                except queue.Empty:continue
                t=msg.header.stamp.sec+msg.header.stamp.nsec*1e-9
                actual={j.name:[j.axis1.position,j.axis1.velocity,j.axis1.force] for j in msg.joint}
                if set(actual)!=set(names):continue
                target={n:neutral[n]*float(smooth((t-.5)/1.5)) for n in names} if args.mode=='stand' or t<3 else trajectory[min(len(trajectory)-1,int((t-3)*100))]
                command=Actuators();command.position.extend(target[n] for n in names);publisher.publish(command)
                motor_time,motors=motor_state.get(round(t,2),motor_state.get(round(t-.01,2),(-1,{})))
                motor_fresh=abs(motor_time-t)<.015 and set(motors)==set(names)
                if motor_fresh:
                    for n in names:actual[n][2]=motors[n][2]
                p=msg.pose.position;q=msg.pose.orientation
                row=dict(t=t,position=[p.x,p.y,p.z],rpy=rpy([q.x,q.y,q.z,q.w]),joints=actual,target=target,
                         motor_fresh=motor_fresh,motor_time=motor_time,motor_joints=motors if motor_fresh else {})
                records.append(row)
                if len(records)%500==0:print('t=',round(t,2),'z=',round(p.z,4),flush=True)
                if t>1 and (p.z<.10 or max(abs(a) for a in row['rpy'][:2])>.65):
                    result='fell_or_tilted';break
                if t>=args.seconds:
                    result='duration_completed';break
        finally:
            if child.poll() is None:
                os.killpg(child.pid,signal.SIGINT)
                try:child.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    os.killpg(child.pid,signal.SIGKILL);child.wait()
    summary=dict(mode=args.mode,result=result,samples=len(records),stance_offset_m=offset,source_sha256=model['source_sha256'],
                 hard_joint_velocity_limit=False,
                 mass_kg=model['total']['mass_kg'],configuration=vars(args),
                 code_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),Path(__file__).with_name('cad_model.py'),Path(__file__).with_name('cad_kinematics.py'),Path(__file__).parent/'plugin/actuator.cc']},
                 caveats=model['warnings'],test='1 kHz effort PD + estimated 10.5 V torque-speed envelope; torque is motor command, NOT sensor feedback')
    settled=[r for r in records if r['t']>2 and r['motor_fresh']]
    summary['stale_motor_samples']=sum(not r['motor_fresh'] for r in records)
    if settled:
        summary['last_pose']=settled[-1]['position'];summary['last_rpy']=settled[-1]['rpy']
        moving=[r for r in settled if r['t']>=3]
        if len(moving)>1:
            summary['displacement_after_settle_m']=(np.array(moving[-1]['position'])-moving[0]['position']).tolist()
            summary['mean_x_speed_m_s']=summary['displacement_after_settle_m'][0]/(moving[-1]['t']-moving[0]['t'])
        summary['joints']={}
        for n in names:
            # Motor dq and torque are from the SAME PreUpdate tick, not the
            # later physics publisher sample. Otherwise envelope checks mix time.
            a=np.array([r['motor_joints'][n] for r in settled])
            errors=np.array([r['target'][n]-r['joints'][n][0] for r in settled])
            summary['joints'][n]=dict(peak_nm=float(abs(a[:,2]).max()),rms_nm=float(np.sqrt(np.mean(a[:,2]**2))),
                                     peak_speed_rad_s=float(abs(a[:,1]).max()),max_error_rad=float(abs(errors).max()),
                                     saturation_fraction=float(np.mean(abs(a[:,2])>=args.torque_cap*.999)),
                                     torque_speed_violations=int(sum(abs(v[2])>actuator_envelope(speed=v[1])['moving_limit_nm']+1e-8 for v in a)))
        summary['actuator_commands_nonzero']=any(v['peak_nm']>1e-5 for v in summary['joints'].values())
        if not summary['actuator_commands_nonzero']:summary['caveats'].append('Actuator commands missing or zero: torque results INVALID.')
        summary['peak_abs_roll_pitch_rad']=np.max(np.abs([r['rpy'][:2] for r in settled]),axis=0).tolist()
        summary['max_joint_rms_nm']=max(v['rms_nm'] for v in summary['joints'].values())
        summary['above_provisional_25pct_screen']=[n for n,v in summary['joints'].items() if v['rms_nm']>actuator_envelope()['screening_25pct_nm']]
    summary['screening_completed']=result=='duration_completed' and summary.get('actuator_commands_nonzero',False) and summary['stale_motor_samples']<len(records)*.05
    (trials/(stamp+'.json')).write_text(json.dumps(dict(summary=summary,records=records),indent=2),encoding='utf8')
    (trials/(stamp+'-summary.json')).write_text(json.dumps(summary,indent=2),encoding='utf8')
    print(json.dumps(summary,indent=2),flush=True)
    return 0 if summary['screening_completed'] else 1


if __name__=='__main__':raise SystemExit(main())
