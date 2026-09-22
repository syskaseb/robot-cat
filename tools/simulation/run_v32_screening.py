"""Bounded, reproducible Gazebo-only parameter sweep. No hardware interface.

Exploratory falls are results, not erased trials. Baseline failures return an
error; all stdout, telemetry and configuration remain available for review.
"""
import argparse,hashlib,itertools,json,subprocess,sys,time
from pathlib import Path
from cad_model import ROOT,OUT,REVISION

def configurations(suite):
    base=[dict(tag='stand',mode='stand',seconds=8,mass='nominal',step_seconds=1,friction=.4,torque_cap=1),
          dict(tag='crawl-nominal',mode='crawl',seconds=15,mass='nominal',step_seconds=1,friction=.4,torque_cap=1),
          dict(tag='crawl-upper',mode='crawl',seconds=15,mass='upper',step_seconds=1,friction=.4,torque_cap=1)]
    sweep=[]
    for step,mass in itertools.product([.75,.5,.25,.15],['nominal','upper']):
        sweep.append(dict(tag=f'speed-{step}-{mass}',mode='crawl',seconds=15,mass=mass,step_seconds=step,friction=.4,torque_cap=1))
    for mu,mass in itertools.product([.25,.6],['nominal','upper']):
        sweep.append(dict(tag=f'friction-{mu}-{mass}',mode='crawl',seconds=15,mass=mass,step_seconds=.5,friction=mu,torque_cap=1))
    for mass in ['nominal','upper']:
        sweep.append(dict(tag=f'cap-0.65-{mass}',mode='crawl',seconds=15,mass=mass,step_seconds=1,friction=.4,torque_cap=.65))
    return base if suite=='baseline' else sweep if suite=='sweep' else base+sweep

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--suite',choices=['baseline','sweep','all'],default='baseline')
    parser.add_argument('--max-wall-seconds',type=float,default=1200)
    args=parser.parse_args();assert REVISION in ('v32','v33')
    cad=ROOT/'hardware/skorupa'/REVISION
    source=cad/json.loads((cad/'assembly-plan.json').read_text())['cad_filename']
    digest=hashlib.sha256(source.read_bytes()).hexdigest()
    assert json.loads((OUT/'geometry.json').read_text())['source_sha256']==digest
    assert json.loads((OUT/'model.json').read_text())['source_sha256']==digest
    trials=OUT/'trials';trials.mkdir(exist_ok=True);start=time.monotonic();rows=[];cases=configurations(args.suite)
    output=OUT/(args.suite+'-suite.json')
    for case in cases:
        if time.monotonic()-start>=args.max_wall_seconds:break
        assert hashlib.sha256(source.read_bytes()).hexdigest()==digest,'CAD changed during sweep'
        previous=set(trials.glob('*-summary.json'))
        command=[sys.executable,str(Path(__file__).with_name('run_cad_gazebo.py')),'--stance-x=-0.03','--stance-z=-0.005']
        for key,value in case.items():
            if key!='tag':command+=['--'+key.replace('_','-'),str(value)]
        print('RUN',case['tag'],flush=True)
        result=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        stamp=time.strftime('%Y%m%d-%H%M%S')
        logfile=trials/(stamp+'-'+case['tag']+'-runner.log');logfile.write_text(result.stdout,encoding='utf8')
        produced=set(trials.glob('*-summary.json'))-previous
        row=dict(configuration=case,exit_code=result.returncode,stdout=logfile.name)
        if len(produced)==1:
            p=produced.pop();r=json.loads(p.read_text());assert r['source_sha256']==digest
            row.update(summary=p.name,result=r['result'],screening_completed=r['screening_completed'],
                samples=r['samples'],stale_motor_samples=r['stale_motor_samples'],
                max_joint_rms_nm=r.get('max_joint_rms_nm'),displacement_after_settle_m=r.get('displacement_after_settle_m'))
        else:row.update(result='runner_error',screening_completed=False,summary=None)
        rows.append(row)
        report=dict(source_sha256=digest,suite=args.suite,planned_cases=len(cases),completed_cases=len(rows),
            wall_seconds=time.monotonic()-start,mechanical_release=False,continuous_torque_certified=False,
            scope=__doc__,trials=rows)
        output.write_text(json.dumps(report,indent=2),encoding='utf8')
        print(json.dumps(row),flush=True)
        if row['result']=='runner_error':return 2
    if len(rows)!=len(cases):return 2
    if args.suite=='baseline' and not all(r['screening_completed'] for r in rows):return 1
    return 0

if __name__=='__main__':raise SystemExit(main())
