"""Only new twelve leg stations/four output guides against current retained set."""
import json,time,sys,hashlib,base64
from pathlib import Path
from current_body_harness_context import W,Part,ROOT,BASE,OUT,context,clipped
from open_prototype_path_preflight import screen
from open_prototype_source_group import check_path

def run():
    tick=time.monotonic();f=OUT/'leg-stations-plan.json';p=json.loads(f.read_text());pins={Path(__file__),f}
    changed=set(p['routes']);reuse={}
    if '--only-output' in sys.argv:
        name=sys.argv[sys.argv.index('--only-output')+1];assert name=='W026_CUSTOM'
        cache=OUT/'leg-retained-evidence.json';v=json.loads(cache.read_text());pins.add(cache)
        old=v['reference_plan'];g=v['reference_gate'];scripts=v['reference_scripts_base64']
        assert g['contacts'] and all(r['a']==name and r['b']=='head/Fork' for r in g['contacts'])
        assert not g['errors'] and p['stations']==old['stations']
        assert all(p['routes'][n]==r for n,r in old['routes'].items() if n!=name)
        for n,h in {**old['source_sha256'],**g['source_sha256']}.items():
            if n in scripts:assert hashlib.sha256(base64.b64decode(scripts[n])).hexdigest()==h,n
            elif n==f.relative_to(ROOT).as_posix():assert h==v['reference_plan_sha256']
            else:assert W.sha(ROOT/n)==h,n
        changed={name};reuse=dict(cases=12,outputs=sorted(set(p['routes'])-changed),head_poses=9,
          basis='Exact previous receipt completed all static and9head poses; contacts ONLY changedFL. Current cases/other3recipes and all retained input hashes identical. ChangedFL rechecked against every other curve/case/head.',
          previous_gate_seconds=g['worker_seconds'],evidence=cache.relative_to(ROOT).as_posix())
    old=[]
    def cheap_parts(parts):
        result=[]
        for seg in parts:
            if seg['kind']=='spline':result.extend(dict(kind='line',start=a,end=b) for a,b in zip(seg['points'],seg['points'][1:]) if a!=b)
            else:result.append(seg)
        return result
    for tag,keys in [('mta-interface',['factory_routes']),('main-source',['routes']),('s1-output',['routes']),('source-receiving',['routes','factory_routes'])]:
        fp=OUT/(tag+'-plan.json');pins.add(fp);data=json.loads(fp.read_text())
        for key in keys:old += [dict(wire=tag+'/'+n,OD_mm=v['radius_mm']*2,segments=v['parts']) for n,v in data[key].items()]
    for folder,file in [('aux-wiring-checkpoint','whole-layout-plan.json'),('head-supply-checkpoint','coupled-plan.json'),('tail-wiring-checkpoint','current-plan.json'),('pwm-branch-checkpoint','final-plan.json')]:
        fp=BASE/folder/file;pins.add(fp)
        old += [dict(wire=folder+'/'+n,OD_mm=v['radius']*2,segments=cheap_parts(v['parts'])) for n,v in json.loads(fp.read_text())['routes'].items() if 'reserved' not in n and n!='F_HY_input_prefix']
    override=p.get('factory_override',{})
    if override:old=[r for r in old if r['wire']!='mta-interface/W026_FACTORY']
    new=[dict(wire=n,OD_mm=v['radius_mm']*2,segments=v['parts']) for n,v in p['routes'].items()]
    if override:new.append(dict(wire='W026_FACTORY',OD_mm=4.2,segments=override['parts']))
    for row in new:check_path(row['segments'],min_radius=25.2)
    pre=screen(dict(tails=old,s1_routes=new,holders=[]));names={r['wire'] for r in new}
    r=dict(status='PENDING',pairs=0,contacts=[r for r in pre['near_pairs'] if r['b'] in names and r['status']=='REJECT_PLANNING_PROXIMITY'],errors=[],selected=False,W5_complete=False,physical_pass=False,reused_qualifications=reuse,changed_output_names=sorted(changed))
    reader=None
    def write(status):
        r.update(status=status,worker_seconds=round(time.monotonic()-tick,3),source_sha256={**(reader.hashes if reader else {}),**{x.relative_to(ROOT).as_posix():W.sha(x) for x in pins}})
        (OUT/'leg-stations-checks.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8',newline='\n')
        print(json.dumps({k:r[k] for k in ('status','pairs','contacts','errors','worker_seconds')}),flush=True)
    if r['contacts']:write('REJECTED_CHEAP_OUTPUT_ROUTE_SCREEN');return
    receive=OUT/'source-receiving-checks.json';g=json.loads(receive.read_text());pins.add(receive)
    assert not g['contacts'] and not g['errors'] and g['source_sha256'][(OUT/'source-receiving-plan.json').relative_to(ROOT).as_posix()]==W.sha(OUT/'source-receiving-plan.json')
    reader,inherited,targets,retained=context();pins.update(inherited)
    sp=json.loads((OUT/'source-receiving-plan.json').read_text())
    targets.update({'P_SYS_new':W.box(sp['P_SYS']['casing_mm']),'F_PI_new':W.box(sp['F_PI']['casing_mm']),'F_PI_sleeve':W.box(sp['F_PI']['output_sleeve_mm'])})
    retained.update({n:(W.makewire(v['parts']),v['radius_mm']) for n,v in {**sp['routes'],**sp['factory_routes']}.items()})
    boxes={n:W.box(s['casing_mm']) for n,s in p['stations'].items()}
    curves={n:W.makewire(v['parts']) for n,v in p['routes'].items()}
    if override:
        j=override['joint'];s=W.box(j['local_casing_mm'])
        s.Placement=W.A.Placement(W.A.Vector(*j['factory_entry_mm']),W.A.Rotation(W.A.Vector(1,0,0),j['rotation_x_degrees']))
        assert s.isValid() and len(s.Solids)==1
        targets['W026_Joint']=s
        retained.pop('W026_FACTORY')
        curves['W026_FACTORY']=W.makewire(override['parts']);changed.add('W026_FACTORY')
    def solid(n,s,m,t):
        if not t.Solids or not W.near(s,t,0):return
        assert s.isValid() and t.isValid(),(n,m);r['pairs']+=1;v=s.common(t).Volume
        if v>1e-5:r['contacts'].append(dict(a=n,b=m,volume_mm3=v))
    def curve(n,c,rr,m,t,rad=0):
        if not W.near(c,t,rr+rad):return
        assert c.isValid() and t.isValid(),(n,m);r['pairs']+=1;q=c.distToShape(t);d=q[0]
        if d<rr+rad-1e-4:r['contacts'].append(dict(a=n,b=m,distance_mm=d,required_mm=rr+rad,witness_mm=[list(v) for v in q[1][0]] if q[1] else None))
    for n,s in ([] if reuse else boxes.items()):
        for m,t in {**targets,**{k:v for k,v in boxes.items() if k>n}}.items():solid(n,s,m,t)
        for m,(c,rr) in retained.items():curve(m,c,rr,n,s)
    print('Leg station cases',len(r['contacts']),'contacts',flush=True)
    if override:
        s=targets['W026_Joint']
        for m,t in {**targets,**boxes}.items():
            if m!='W026_Joint':solid('W026_Joint',s,m,t)
        for m,(c,rad) in {**retained,**{n:(c,2.1) for n,c in curves.items() if n not in changed}}.items():curve(m,c,rad,'W026_Joint',s)
    if r['contacts']:write('REJECTED_LEG_STATION_CASES');return
    assigned={'W026_CUSTOM':'FL_P','W037_CUSTOM':'FR_P','W045_CUSTOM':'RL_P','W053_CUSTOM':'RR_P'}
    for n,c in curves.items():
        if n not in changed:continue
        row=override if n=='W026_FACTORY' else p['routes'][n];rr=row['radius_mm']
        for m,(t,rad) in {**retained,**{k:(v,2.1) for k,v in curves.items() if k>n or k not in changed}}.items():curve(n,c,rr,m,t,rad)
        for m,t in {**targets,**boxes}.items():
            if not t.Solids:continue
            if n=='W026_FACTORY':cc=clipped(c,True,3) if m=='MTA/FL' else clipped(c,False,3) if m=='W026_Joint' else c
            else:cc=clipped(c,False,3) if m==assigned[n] else clipped(c,True,min(3,row['parts'][0]['length_mm'])) if m==n.removesuffix('_CUSTOM')+'_Joint' else c
            curve(n,cc,rr,m,t)
        print('Leg output',n,'contacts',len(r['contacts']),flush=True)
    if not r['contacts']:
        for yaw in (-15,0,15):
            for pitch in (-10,0,5):
                for m,t in W.F.H.head(reader,yaw,pitch).items():
                    if m=='Foundation' or not t.Solids:continue
                    for n,s in ([] if reuse else boxes.items()):solid(n,s,'head/'+m,t)
                    for n,c in curves.items():
                        if n in changed:curve(n,c,2.1,'head/'+m,t)
                    if override:solid('W026_Joint',targets['W026_Joint'],'head/'+m,t)
    write('LEG_STATIONS_AND_MAIN_OUTPUT_SPACE_ONLY_FANS_NATIVE_OPEN' if not r['contacts'] else 'REJECTED_LEG_OUTPUT_SHARED_LAYOUT')
if __name__=='__main__':run()
