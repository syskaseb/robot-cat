"""Changed receiving cases first, then exact new curves and retained material."""
import json,time
from pathlib import Path
from current_body_harness_context import W,Part,ROOT,BASE,OUT,context,clipped

def run():
    tick=time.monotonic();f=OUT/'source-receiving-plan.json';p=json.loads(f.read_text())
    # Never load the heavy native scene when a known NEW route pair already
    # rejects. Old/old receipt-qualified near pairs are not rerun or re-scored.
    from open_prototype_path_preflight import screen
    from open_prototype_source_group import check_path
    old=[];prepins={f,Path(__file__)}
    def planning_parts(parts):
        result=[]
        for seg in parts:
            if seg['kind']=='spline':
                # Saved interpolation stations are ONLY a cheap rejection
                # aid; actual retained spline/BRep still runs below.
                result.extend(dict(kind='line',start=a,end=b) for a,b in zip(seg['points'],seg['points'][1:]) if a!=b)
            else:result.append(seg)
        return result
    for filename,key in [('main-source-plan.json','routes'),('s1-output-plan.json','routes'),('mta-interface-plan.json','factory_routes')]:
        fp=OUT/filename;prepins.add(fp);data=json.loads(fp.read_text())
        old += [dict(wire=n,OD_mm=v['radius_mm']*2,segments=v['parts']) for n,v in data[key].items()]
    for folder,filename in [('aux-wiring-checkpoint','whole-layout-plan.json'),('head-supply-checkpoint','coupled-plan.json'),('tail-wiring-checkpoint','current-plan.json'),('pwm-branch-checkpoint','final-plan.json')]:
        fp=BASE/folder/filename;prepins.add(fp)
        old += [dict(wire=folder+'/'+n,OD_mm=v['radius']*2,segments=planning_parts(v['parts']))
          for n,v in json.loads(fp.read_text())['routes'].items() if 'reserved' not in n and n!='F_HY_input_prefix']
    new=[dict(wire=n,OD_mm=v['radius_mm']*2,segments=v['parts']) for n,v in {**p['routes'],**p['factory_routes']}.items()]
    for row in new:check_path(row['segments'],min_radius=25.2 if row['wire'] in p['routes'] else 6)
    prepins.update(ROOT/'tools/cad'/name for name in ('open_prototype_path_preflight.py','open_prototype_source_group.py'))
    pre=screen(dict(tails=old,s1_routes=new,holders=[]));names={x['wire'] for x in new}
    rejected=[x for x in pre['near_pairs'] if x['b'] in names and x['status']=='REJECT_PLANNING_PROXIMITY']
    if rejected:
        r=dict(status='REJECTED_CHEAP_NEW_ROUTE_PREFLIGHT_NATIVE_SCENE_NOT_LOADED',contacts=rejected,errors=[],pairs=0,
          worker_seconds=round(time.monotonic()-tick,3),selected=False,W5_complete=False,physical_pass=False,
          source_sha256={x.relative_to(ROOT).as_posix():W.sha(x) for x in prepins})
        (OUT/'source-receiving-checks.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8',newline='\n')
        print(json.dumps(r),flush=True);return
    reader,pins,targets,retained=context();pins.update(prepins)
    rows={**p['routes'],**p['factory_routes']};curves={n:W.makewire(r['parts']) for n,r in rows.items()}
    boxes={'P_SYS_new':W.box(p['P_SYS']['casing_mm']),'F_PI_new':W.box(p['F_PI']['casing_mm']),
           'F_PI_sleeve':W.box(p['F_PI']['output_sleeve_mm'])}
    r=dict(status='PENDING',pairs=0,contacts=[],errors=[],selected=False,W5_complete=False,physical_pass=False)
    def write(status):
        r.update(status=status,worker_seconds=round(time.monotonic()-tick,3),source_sha256={**reader.hashes,**{x.relative_to(ROOT).as_posix():W.sha(x) for x in pins}})
        (OUT/'source-receiving-checks.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8',newline='\n')
        print(json.dumps({k:r[k] for k in ('status','contacts','errors','pairs','worker_seconds')}),flush=True)
    def pair(n,c,rr,name,t,rad=0):
        if not W.near(c,t,rr+rad):return
        assert c.isValid() and t.isValid(),(n,name)
        r['pairs']+=1;result=c.distToShape(t);d=result[0]
        if d<rr+rad-1e-4:r['contacts'].append(dict(a=n,b=name,distance_mm=d,required_mm=rr+rad,
          closest_mm=[list(v) for v in result[1][0]] if result[1] else None))
    def solid(n,s,name,t):
        if not t.Solids or not W.near(s,t,0):return
        assert s.isValid() and t.isValid(),(n,name);r['pairs']+=1;hit=s.common(t);assert hit.isValid()
        if hit.Volume>1e-5:r['contacts'].append(dict(a=n,b=name,volume_mm3=hit.Volume))
    for n,s in boxes.items():
        for name,t in {**targets,**{k:v for k,v in boxes.items() if k>n}}.items():solid(n,s,name,t)
        for name,(c,rr) in retained.items():pair(name,c,rr,n,s)
    print('Receiving complete cases',len(r['contacts']),'contacts',flush=True)
    if r['contacts']:write('REJECTED_RECEIVING_COMPLETE_CASES');return
    for n,c in curves.items():
        for a,b in zip(c.Edges,c.Edges[1:]):
            gap=(a.valueAt(a.LastParameter)-b.valueAt(b.FirstParameter)).Length;dot=a.tangentAt(a.LastParameter).dot(b.tangentAt(b.FirstParameter))
            if gap>1e-5 or dot<1-1e-5:r['errors'].append(dict(wire=n,gap=gap,dot=dot))
        for name,(t,rad) in {**retained,**{k:(v,rows[k]['radius_mm']) for k,v in curves.items() if k>n}}.items():pair(n,c,rows[n]['radius_mm'],name,t,rad)
    if r['contacts'] or r['errors']:write('REJECTED_RECEIVING_MUTUAL_PREFLIGHT');return
    for n,c in curves.items():
        rr=rows[n]['radius_mm']
        for name,t in {**targets,**boxes}.items():
            if not t.Solids:continue
            cc=c
            if name=='P_SYS_new' and n in ('W067','W068'):cc=clipped(c,True,3)
            elif name=='P_SYS_new' and n=='W043':cc=clipped(c,False,3)
            elif name=='F_PI_new' and n in ('W043','W077_PREFIX'):cc=clipped(c,True,3)
            elif name=='F_PI_sleeve' and n=='W077_PREFIX':continue # Explicit same-conductor factory/solder sleeve.
            elif n in p['rings'] and name=='current/'+p['rings'][n]['native']:
                cc=clipped(c,False,6 if n=='W067' else 3)
            pair(n,cc,rr,name,t)
        print('Receiving route',n,'contacts',len(r['contacts']),flush=True)
    if not r['contacts'] and not r['errors']:
        for yaw in (-15,0,15):
            for pitch in (-10,0,5):
                for name,t in W.F.H.head(reader,yaw,pitch).items():
                    if name=='Foundation' or not t.Solids:continue
                    for n,s in boxes.items():solid(n,s,'head/'+name,t)
                    for n,c in curves.items():pair(n,c,rows[n]['radius_mm'],'head/'+name,t)
            print('Receiving head yaw',yaw,'contacts',len(r['contacts']),flush=True)
    write('RECEIVING_INPUTS_AND_FUSE_PREFIX_SPACE_ONLY_W5_OPEN' if not r['contacts'] and not r['errors'] else 'REJECTED_SOURCE_RECEIVING_SHARED_ALLOCATION')
if __name__=='__main__':run()
