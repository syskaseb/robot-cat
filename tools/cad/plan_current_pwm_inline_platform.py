"""Single removable E2 fixture replaces the coupled south ground bracket.

The complete source/fuse/connector and both circuit leads share one support;
module returns pass outside the carrier rim before entering below the PCB.
"""
import json,time,math
from pathlib import Path
import plan_current_pwm_south_bypass as S
E,P=S.E,S.P
A,Part,ROOT,BASE,OUT=S.A,S.Part,S.ROOT,S.BASE,S.OUT
arc,line,wire,box,near=S.arc,S.line,S.wire,S.box,S.near

def build():
    p=S.build();r=p['routes'];r['XP03_source']['parts']=[
      line([44.5,-35,141],[78.1,-35,141]),
      arc([78.1,-23.9,141],[78.1,-35,141],[89.2,-23.9,141]),
      line([89.2,-23.9,141],[89.2,-17.6,141]),
      arc([100.3,-17.6,141],[89.2,-17.6,141],[100.3,-6.5,141])]
    for name,x,z,padx,pady,bottom in [('XP02_module',136.9,138,91.59,-11.43,81.5),('XP03_module',139.9,141,89.05,-6.35,79.3)]:
      y=-6.5;rad=11.1
      parts=[line([130.9,y,z],[x,y,z]),arc([x,y-rad,z],[x,y,z],[x+rad,y-rad,z]),
        line([x+rad,y-rad,z],[x+rad,-30.9,z]),arc([x+rad,-30.9,z-rad],[x+rad,-30.9,z],[x+rad,-42,z-rad]),
        line([x+rad,-42,z-rad],[x+rad,-42,bottom+rad]),
        arc([x+rad,-30.9,bottom+rad],[x+rad,-42,bottom+rad],[x+rad,-30.9,bottom]),
        arc([x,-30.9,bottom],[x+rad,-30.9,bottom],[x,-19.8,bottom])]
      parts+=P.input_recipe([x,-19.8,bottom],[padx+1,pady,bottom],[-1,0,0],rad)['segments']
      r[name]['parts']=parts
    p.update(status='ONE_INLINE_PLATFORM_E2_PROPOSAL_NOT_SELECTED',G_TAIL_centre_mm=[35,-35,141],G_TAIL_rotation_z_deg=90,
      invalidated=['P_REAR and G_TAIL every old physical port approach/support invalidated for whole W5. Both same electrical buses, no netlist change; no W4/W5 point retained.'])
    p['load_path_plan'][3]='No separate ground bracket: same bridge extends west tab toY-50 atX21..50; G_TAIL raised4mm to136.5bottom and retained at35/-35/141, ports EAST. All sources prewired on ONE removable fixture.'
    p['load_path_plan'][2]+=' DescentsX148/151 atY-42 bypass tail and frame screw; then90deg elbow enters belowPCB viaY-19.8. No carrier-edge cuts.'
    for name in ['XP02_source','XP03_source','XP02_module','XP03_module']:
      length=wire(r[name]['parts']).Length;bare=wire(r[name+'_bare']['parts']).Length if name+'_bare' in r else 0
      reserve=47 if name=='XP03_source' else 40 if name=='XP02_source' else 16
      p['budgets'][name]=dict(route_mm=length,bare_mm=bare,additional_allowance_mm=reserve,minimum_factory_mm=220,margin_mm=220-length-bare-reserve)
    p['source_sha256'][Path(__file__).relative_to(ROOT).as_posix()]=P.sha(Path(__file__))
    return p

def structures():
    return {'Bridge':box([21,-22,129.5,136,22,132.5]).fuse(box([21,-50,129.5,50,-22,132.5])),
      'PostA':box([23,-23,77.72,29,-17,129.5]),'PostB':box([23,17,77.72,29,23,129.5]),
      'PostC':box([117,-23,77.72,123,-17,129.5]),
      'G_TAILseat':box([25.5,-50,132.5,44.5,-20,136.5])}

def run():
    tick=time.monotonic();dest=OUT/'inline-space-checks.json';assert not dest.exists()
    p=build();(OUT/'inline-joint-plan.json').write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8')
    reader=P.SavedShapes();targets,torso=E.context(reader)
    for n in json.loads((BASE/'tail-mount-checkpoint/tail-assembly-checks.json').read_text())['tail_identities']:targets.pop('P0_'+n,None)
    structural=structures();curves={n:wire(r['parts']) for n,r in p['routes'].items()};hits=[];pairs=0
    outer=Part.makeCylinder(3.2,42,A.Vector(48.5,-6.5,138),A.Vector(1,0,0))
    allowance={'JPWM_project_allowance':box(p['housing_bounds_mm']),
      'P_REAR_project_allowance':box([24,-18.5,132.5,46,18.5,143.5]),
      'G_TAIL_project_allowance':box([25.5,-50,136.5,44.5,-20,145.5]),'F_PWM_outer_sleeve':outer}
    for n,c in curves.items():
      rad=p['routes'][n]['radius'];scene={**targets,**structural}
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
    result=dict(status='REJECTED_INLINE_PLATFORM' if hits or bad or outside else 'INLINE_PLATFORM_SPACE_CANDIDATE',contacts=hits,pairs=pairs,
      outside=outside,budget_failures=bad,budgets=p['budgets'],worker_seconds=round(time.monotonic()-tick,3),
      source_sha256={**p['source_sha256'],**reader.hashes},selected=False,physical_pass=False,E2_complete=False,
      remaining=['Native grips/hardware/tools, parameter/reopen','Actual station delivery assumptions/complete wire boundary','Stock/selection'])
    dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('status','contacts','pairs','outside','budget_failures','worker_seconds')}),flush=True)
if __name__=='__main__':run()
