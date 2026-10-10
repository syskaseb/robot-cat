"""Whole inline stage and two gripped exits use the measured inner corridor.

Retained tail core starts atX151/Y+-20, small forward boss atX146/Y+-4.
AtY-6.5 the descentsX144.1/146 have space; no low southern wing crossing.
Shift the complete inline electrical station7mm west to allow9mm exit grips.
"""
import json,time
import plan_current_pwm_inline_platform as I
P=I.P;A,Part,ROOT,BASE,OUT=I.A,I.Part,I.ROOT,I.BASE,I.OUT
line,arc,wire,box,near=I.line,I.arc,I.wire,I.box,I.near

def build():
    p=I.build()
    for n in ('XP01','XP02_source','XP03_source'):
        for q in p['routes'][n]['parts']:
            for k in ('start','mid','end'):
                if k in q:q[k][0]-=7
    for n,x,z,px,py,bottom in [('XP02_module',133,138,91.59,-11.43,81.5),('XP03_module',134.9,141,89.05,-6.35,79.3)]:
        r=11.1;y=-6.5
        parts=[line([123.9,y,z],[x,y,z]),arc([x,y,z-r],[x,y,z],[x+r,y,z-r]),
          line([x+r,y,z-r],[x+r,y,bottom+r]),arc([x,y,bottom+r],[x+r,y,bottom+r],[x,y,bottom])]
        parts+=P.input_recipe([x,y,bottom],[px+1,py,bottom],[-1,0,0],r)['segments']
        p['routes'][n]['parts']=parts
    p.update(P_REAR_centre_mm=[28,0,138],G_TAIL_centre_mm=[28,-35,141],housing_bounds_mm=[95.6,-12.5,133.5,121.6,-.5,145.5])
    p['fuse']['body_start'][0]-=7;p['fuse']['outer_sleeve_start'][0]-=7
    for n in ('XP02_source','XP03_source','XP02_module','XP03_module'):
        b=p['budgets'][n];b['route_mm']=wire(p['routes'][n]['parts']).Length
        b['margin_mm']=220-b['route_mm']-b['bare_mm']-b['additional_allowance_mm']
    p['load_path_plan']=['One fixture: P_REAR/G_TAIL atX28, fuse+X and mated connector95.6..121.6. Three roots26/Y+-20,120/Y-20.',
      'Independent source insulation retention, fuse sleeve seats; no clamp on bare leads.',
      '9.1/11mm straight module exits before R11.1 descents atX144.1/146,Y-6.5. Both below-board returns inside tail core; no south wing crossing.',
      'G_TAIL4mm raised on same platform, all five ports face EAST.',
      'Actual pad ends and PCB-side insulation grips qualified next; no unknown U1 pinout.']
    p['source_sha256'][P.Path(__file__).relative_to(ROOT).as_posix()]=P.sha(P.Path(__file__))
    return p

def structures():
    s=I.structures();s['Bridge']=box([14,-22,129.5,129,22,132.5]).fuse(box([14,-50,129.5,43,-22,132.5]))
    s['G_TAILseat']=box([18.5,-50,132.5,37.5,-20,136.5]);return s

def run():
    tick=time.monotonic();dest=OUT/'core-corridor-space-checks.json';assert not dest.exists()
    p=build();(OUT/'core-corridor-joint-plan.json').write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8')
    reader=P.SavedShapes();targets,torso=I.E.context(reader)
    for n in json.loads((BASE/'tail-mount-checkpoint/tail-assembly-checks.json').read_text())['tail_identities']:targets.pop('P0_'+n,None)
    structural=structures();curves={n:wire(r['parts']) for n,r in p['routes'].items()};hits=[];pairs=0
    outer=Part.makeCylinder(3.2,42,A.Vector(41.5,-6.5,138),A.Vector(1,0,0))
    allowance={'JPWM_project_allowance':box(p['housing_bounds_mm']),'P_REAR_project_allowance':box([17,-18.5,132.5,39,18.5,143.5]),
      'G_TAIL_project_allowance':box([18.5,-50,136.5,37.5,-20,145.5]),'F_PWM_outer_sleeve':outer}
    for n,c in curves.items():
      rad=p['routes'][n]['radius'];scene={**targets,**structural}
      if n.startswith('XP03'):scene['F_PWM_outer_sleeve']=outer
      for other,s in scene.items():
        if not near(c,s,rad):continue
        if n.endswith('_bare') and other=='PWM1608NominalPCB':continue
        d=min(c.distToShape(t)[0] for t in s.Solids);pairs+=1
        if d<rad-1e-5:hits.append(dict(a=n,b=other,distance_mm=d,required_mm=rad))
    for i,a in enumerate(curves):
      for b in list(curves)[i+1:]:
        if a.removesuffix('_bare')==b.removesuffix('_bare'):continue
        req=p['routes'][a]['radius']+p['routes'][b]['radius']
        if near(curves[a],curves[b],req):
          d=curves[a].distToShape(curves[b])[0];pairs+=1
          if d<req-1e-5:hits.append(dict(a=a,b=b,distance_mm=d,required_mm=req))
    for a,s in {**structural,**allowance}.items():
      for b,t in targets.items():
        if not near(s,t,0):continue
        v=sum(x.common(y).Volume for x in s.Solids for y in t.Solids);pairs+=1
        if v>1e-5:hits.append(dict(a=a,b=b,volume_mm3=v))
    outside=[]
    for n,s in {**structural,**allowance}.items():
      v=s.cut(torso).Volume
      if v>1e-5:outside.append(dict(name=n,volume_mm3=v))
    bad=[n for n,b in p['budgets'].items() if b['margin_mm']<0]
    result=dict(status='REJECTED_CORE_CORRIDOR' if hits or bad or outside else 'CORE_CORRIDOR_SPACE_CANDIDATE',contacts=hits,pairs=pairs,outside=outside,
      budget_failures=bad,budgets=p['budgets'],worker_seconds=round(time.monotonic()-tick,3),source_sha256={**p['source_sha256'],**reader.hashes},selected=False,E2_complete=False,physical_pass=False)
    dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:result[k] for k in ('status','contacts','pairs','outside','budget_failures','budgets','worker_seconds')}),flush=True)
if __name__=='__main__':run()
