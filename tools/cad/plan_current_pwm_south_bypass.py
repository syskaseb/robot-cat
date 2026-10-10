"""Whole east/south bypass of the retained tail, no tail geometry changes."""
import json,time,math
from pathlib import Path
import plan_current_pwm_east as E
P=E.P;A,Part,ROOT,BASE,OUT=E.A,E.Part,E.ROOT,E.BASE,E.OUT
arc,line,wire,box,near=E.arc,E.line,E.wire,E.box,E.near

def build():
    p=E.build();r=p['routes'];from xb11_upstream_route import rounded
    pts=[[140,-50.5,96],[140,-30,96],[140,-30,141],[89.2,-30,141],[89.2,-6.5,141],[100.3,-6.5,141]]
    edges=rounded([A.Vector(*q) for q in pts],11.1).Edges
    r['XP03_source']['parts']=[line(P.xyz(e.valueAt(e.FirstParameter)),P.xyz(e.valueAt(e.LastParameter))) if isinstance(e.Curve,Part.Line)
      else dict(kind='arc',start=P.xyz(e.valueAt(e.FirstParameter)),mid=P.xyz(e.valueAt((e.FirstParameter+e.LastParameter)/2)),end=P.xyz(e.valueAt(e.LastParameter))) for e in edges]
    for name,x,z,padx,pady,bottom in [('XP02_module',134,138,91.59,-11.43,81.5),('XP03_module',137,141,89.05,-6.35,79.3)]:
      y=-6.5;radius=11.1
      parts=[line([130.9,y,z],[x,y,z]),arc([x,y-radius,z],[x,y,z],[x+radius,y-radius,z]),
        line([x+radius,y-radius,z],[x+radius,-18.9,z]),
        arc([x+radius,-18.9,z-radius],[x+radius,-18.9,z],[x+radius,-30,z-radius]),
        line([x+radius,-30,z-radius],[x+radius,-30,bottom+radius]),
        arc([x,-30,bottom+radius],[x+radius,-30,bottom+radius],[x,-30,bottom])]
      parts+=P.input_recipe([x,-30,bottom],[padx+1,pady,bottom],[-1,0,0],radius)['segments']
      r[name]['parts']=parts
      r[name+'_bare']['parts']=[arc([padx+1,pady,bottom+1],[padx+1,pady,bottom],[padx,pady,bottom+1]),
        line([padx,pady,bottom+1],[padx,pady,85.8202])]
    p.update(status='INLINE_SOUTH_BYPASS_E2_PROPOSAL_NOT_SELECTED',housing_bounds_mm=[102.6,-12.5,133.5,128.6,-.5,145.5],
      housing_orientation='Mating axisX; circuit1 Z138, circuit2 Z141. Model26x12x12 is provisional mated allowance, catalogue overall24.77; actual exit coords delivery-fit gate.',
      factory_leads=dict(red_source='2147612113 225+/-5mm',black_source='2147611113 225+/-5mm',
        red_module='2147632113 225+/-5mm',black_module='2147631113 225+/-5mm'))
    for name in ['XP02_source','XP03_source','XP02_module','XP03_module']:
      length=wire(r[name]['parts']).Length;bare=wire(r[name+'_bare']['parts']).Length if name+'_bare' in r else 0
      reserve=47 if name=='XP03_source' else 40 if name=='XP02_source' else 16
      p['budgets'][name]=dict(route_mm=length,bare_mm=bare,additional_allowance_mm=reserve,minimum_factory_mm=220,margin_mm=220-length-bare-reserve)
    p['load_path_plan'][2]='26mm mated connector allowance, two vertically stacked3mm cavities. Module exits turn south atX145.1/148.1 before descent, outside retained tail. Black underside level79.3/red81.5 avoid crossing each other.'
    p['load_path_plan'][3]='G_TAIL south bracket cantilever, two carrier screws106/116,Y-35. Root columnX103..119 avoids retained tail integral ground-seat area; existing tail never cut.'
    p['source_sha256'][Path(__file__).relative_to(ROOT).as_posix()]=P.sha(Path(__file__))
    return p

def structures():
    return {'Bridge':box([21,-22,129.5,136,22,132.5]),
      'PostA':box([23,-23,77.72,29,-17,129.5]),'PostB':box([23,17,77.72,29,23,129.5]),
      'PostC':box([117,-23,77.72,123,-17,129.5]),
      'ReturnBracket':box([103,-70,88.5,155,-32,91.5]),'ReturnPost':box([103,-38,77.72,119,-32,88.5])}

def run():
    tick=time.monotonic();dest=OUT/'south-space-checks.json';assert not dest.exists()
    p=build();(OUT/'south-joint-plan.json').write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8')
    reader=P.SavedShapes();targets,torso=E.context(reader)
    tail_names=json.loads((BASE/'tail-mount-checkpoint/tail-assembly-checks.json').read_text())['tail_identities']
    # Never test the superseded original tail alongside its current copy.
    for n in tail_names:targets.pop('P0_'+n,None)
    structural=structures();curves={n:wire(r['parts']) for n,r in p['routes'].items()};hits=[];pairs=0
    outer=Part.makeCylinder(3.2,42,A.Vector(48.5,-6.5,138),A.Vector(1,0,0))
    for n,c in curves.items():
      rad=p['routes'][n]['radius']
      scene={**targets,**structural}
      if n.startswith('XP03'):scene['F_PWM_outer_sleeve']=outer
      for other,s in scene.items():
        if not near(c,s,rad):continue
        if n.endswith('_bare') and other=='PWM1608NominalPCB':continue
        d=min(c.distToShape(t)[0] for t in s.Solids);pairs+=1
        if d<rad-1e-5:hits.append(dict(a=n,b=other,distance_mm=d,required_mm=rad,reservation='RESERVATION' in other))
    for i,a in enumerate(curves):
      for b in list(curves)[i+1:]:
        if a.removesuffix('_bare')==b.removesuffix('_bare'):continue
        req=p['routes'][a]['radius']+p['routes'][b]['radius']
        if near(curves[a],curves[b],req):
          d=curves[a].distToShape(curves[b])[0];pairs+=1
          if d<req-1e-5:hits.append(dict(a=a,b=b,distance_mm=d,required_mm=req))
    allowance={'JPWM_project_allowance':box(p['housing_bounds_mm']),
      'P_REAR_project_allowance':box([24,-18.5,132.5,46,18.5,143.5]),'F_PWM_outer_sleeve':outer}
    for a,s in {**structural,**allowance}.items():
      for b,t in targets.items():
        if not near(s,t,0):continue
        v=sum(x.common(y).Volume for x in s.Solids for y in t.Solids);pairs+=1
        if v>1e-5:hits.append(dict(a=a,b=b,volume_mm3=v,reservation='RESERVATION' in b or 'allowance' in a))
    outside=[]
    for n,s in {**structural,**allowance}.items():
      v=s.cut(torso).Volume
      if v>1e-5:outside.append(dict(name=n,volume_mm3=v))
    bad=[n for n,b in p['budgets'].items() if b['margin_mm']<0]
    result=dict(status='REJECTED_SOUTH_BYPASS' if hits or bad or outside else 'SOUTH_BYPASS_SPACE_CANDIDATE',contacts=hits,pairs=pairs,
      outside=outside,budget_failures=bad,budgets=p['budgets'],worker_seconds=round(time.monotonic()-tick,3),
      source_sha256={**p['source_sha256'],**reader.hashes},selected=False,physical_pass=False,E2_complete=False,
      remaining=['Native grips/hardware/tools, parameter/reopen','Actual station delivery assumptions/complete wire boundary','Stock/selection'])
    dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('status','contacts','pairs','outside','budget_failures','worker_seconds')}),flush=True)
if __name__=='__main__':run()
