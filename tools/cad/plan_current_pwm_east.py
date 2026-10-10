"""Third E2 proposal changes architecture, not another scalar offset.

One inline P_REAR/fuse/JPWM station, with both module leads descending past
the PCB's east end. Full current tail and S1 references are included.
"""
import math,json,time
from pathlib import Path
import plan_current_pwm_branch as P
A,Part,ROOT,BASE=P.A,P.Part,P.ROOT,P.BASE
OUT=P.OUT
arc,line,wire,box,near=P.arc,P.line,P.wire,P.box,P.near

def build():
    p=P.build();r={
      'XP01':dict(parts=[line([46,-6.5,138],[58,-6.5,138])],radius=1.05),
      'XP02_source':dict(parts=[line([78.4,-6.5,138],[100.3,-6.5,138])],radius=.925)}
    from xb11_upstream_route import rounded
    pts=[[140,-50.5,96],[140,-30,96],[140,-30,138],[77,-30,138],[77,-3.5,138],[100.3,-3.5,138]]
    w=rounded([A.Vector(*q) for q in pts],11.1)
    def serial(e):
      if isinstance(e.Curve,Part.Line):return line(P.xyz(e.valueAt(e.FirstParameter)),P.xyz(e.valueAt(e.LastParameter)))
      return dict(kind='arc',start=P.xyz(e.valueAt(e.FirstParameter)),mid=P.xyz(e.valueAt((e.FirstParameter+e.LastParameter)/2)),end=P.xyz(e.valueAt(e.LastParameter)))
    r['XP03_source']=dict(parts=[serial(e) for e in w.Edges],radius=.925)
    for name,y,x,padx,pady in [('XP02_module',-6.5,140,91.59,-11.43),('XP03_module',-3.5,143,89.05,-6.35)]:
      parts=[line([134.9,y,138],[x,y,138]),arc([x,y,126],[x,y,138],[x+12,y,126]),
        line([x+12,y,126],[x+12,y,93.5]),arc([x,y,93.5],[x+12,y,93.5],[x,y,81.5])]
      parts+=P.input_recipe([x,y,81.5],[padx+1,pady,81.5],[-1,0,0],11.1)['segments']
      r[name]=dict(parts=parts,radius=.925)
      r[name+'_bare']=dict(parts=[arc([padx+1,pady,82.5],[padx+1,pady,81.5],[padx,pady,82.5]),
        line([padx,pady,82.5],[padx,pady,85.8202])],radius=math.sqrt(.518/math.pi))
    p.update(routes=r,status='EAST_INLINE_E2_PROPOSAL_NOT_SELECTED',source_station_pose_unchanged=False,
      P_REAR_centre_mm=[35,0,138],P_REAR_rotation_z_deg=90,housing_bounds_mm=[102.6,-11,132.5,132.6,1,144.5],
      factory_leads=dict(red_source='2147612113 225+/-5mm',black_source='2147611114 300+/-5mm',
        red_module='2147632113 225+/-5mm',black_module='2147631113 225+/-5mm'),
      module_factory_basis=dict(url='https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/214/214763/2147631111_sd.pdf',
        retrieved_utc='2026-10-10T00:54:41Z',male_20AWG_225_tolerance_mm=5,selection_not_purchase=True),
      invalidated=['P_REAR new centre35/0/138 and90degreeorientation: all five ports/four unselected MAIN source approaches and supports must be rebound in W5. No W5 point retained.'])
    p['fuse'].update(body_start=[64,-6.5,138],axis=[1,0,0],outer_sleeve_start=[48.5,-6.5,138])
    for name,minimum,reserve in [('XP02_source',220,40),('XP03_source',295,47),('XP02_module',220,16),('XP03_module',220,16)]:
      length=wire(r[name]['parts']).Length;bare=wire(r[name+'_bare']['parts']).Length if name+'_bare' in r else 0
      p['budgets'][name]=dict(route_mm=length,bare_mm=bare,additional_allowance_mm=reserve,minimum_factory_mm=minimum,margin_mm=minimum-length-bare-reserve)
    p['load_path_plan']=[
      'Inline removable bridge X21..136/Y-22..22/Z129.5..132.5. Three carrier-rooted pillars X26/Y+/-20 andX120/Y-20, all outside PCB fields.',
      'P_REAR tape body retention behind levers; fuse sleeved seats and XP01 intact-insulation ties independent of body adhesive.',
      'JPWM horizontal X, latch exposed on north side. Independently retained housing and four wire exits. Board-end descents atX152/155, never through U1.',
      'G_TAIL current pose140/-60/96 on separate south bracket rooted128/-35, independently restrained black entry.',
      'PWM pad grips below board: individual insulation only, verified source pad holes/under-PCB gap, no clamp on copper.']
    p['source_sha256'][Path(__file__).relative_to(ROOT).as_posix()]=P.sha(Path(__file__))
    return p

def context(reader):
    targets={};mount=BASE/'mounting-checkpoint/CurrentBoardMounts.FCStd'
    proof=json.loads((BASE/'mounting-checkpoint/current-M5-checks.json').read_text())
    for n in proof['physical_objects']:
      if n in reader.doc(mount):targets[n]=reader.shape(mount,n)
    ctx=BASE/'OpenPrototypePlan.FCStd'
    for n in reader.doc(ctx):
      if n.startswith(('P0_','S0_','F_L','F_R')) and not any(q in n for q in ('Tool','Driver','Tail','MG92BCase','MG92BMount')):
        try:targets[n]=reader.shape(ctx,n)
        except ValueError:pass
    tail=BASE/'tail-mount-checkpoint/TailAssemblyCurrent.FCStd'
    tp=json.loads((BASE/'tail-mount-checkpoint/tail-assembly-checks.json').read_text())
    # Assembly objects are localized under their original identity, except the
    # whole native raised support. Exact names inspected from copy receipts.
    for n in tp['tail_identities']:
      if n in reader.doc(tail):targets['tail/'+n]=reader.shape(tail,n)
    targets['tail/RaisedTailSupport']=reader.shape(tail,'RaisedTailSupport')
    allocation=json.loads((BASE/'wiring-checkpoint/source-group-allocation.json').read_text())
    pose=allocation['source_pose_allocation'];pivot=A.Vector(126.2,55.5,85)
    for n in reader.doc(ctx):
      if not n.startswith('S1_') or any(q in n.lower() for q in ('driver','service','budget')):continue
      try:s=reader.shape(ctx,n)
      except ValueError:continue
      s.rotate(pivot,A.Vector(0,0,1),pose['yaw_deg']);s.translate(A.Vector(*pose['centre_mm'])-pivot)
      targets['current/'+n]=s
    # Unknown external U1 delivered height remains a project reservation, not
    # evidence that a known supplier part collides. A route intrusion rejects
    # the proposal nonetheless: it cannot be selected until fit is known.
    u=targets['U1BoardAllowance'].BoundBox
    targets['U1_unknown_height_RESERVATION']=Part.makeBox(u.XLength,u.YLength,12,A.Vector(u.XMin,u.YMin,u.ZMax))
    return targets,reader.shape(ctx,'TorsoEnvelope')

def run():
    tick=time.monotonic();dest=OUT/'east-space-checks.json';assert not dest.exists()
    p=build();(OUT/'east-joint-plan.json').write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8')
    reader=P.SavedShapes();targets,torso=context(reader)
    structural={'Bridge':box([21,-22,129.5,136,22,132.5]),
      'PostA':box([23,-23,77.72,29,-17,129.5]),'PostB':box([23,17,77.72,29,23,129.5]),
      'PostC':box([117,-23,77.72,123,-17,129.5]),
      'ReturnBracket':box([125,-70,88.5,155,-32,91.5]),'ReturnPost':box([125,-38,77.72,131,-32,88.5])}
    curves={n:wire(r['parts']) for n,r in p['routes'].items()};hits=[];pairs=0
    for n,c in curves.items():
      rad=p['routes'][n]['radius']
      for other,s in {**targets,**structural}.items():
        if not near(c,s,rad):continue
        if n.endswith('_bare') and other=='PWM1608NominalPCB':continue
        d=min(c.distToShape(t)[0] for t in s.Solids);pairs+=1
        if d<rad-1e-5:hits.append(dict(a=n,b=other,distance_mm=d,required_mm=rad,reservation='RESERVATION' in other))
    names=list(curves)
    for i,a in enumerate(names):
      for b in names[i+1:]:
        if a.removesuffix('_bare')==b.removesuffix('_bare'):continue
        req=p['routes'][a]['radius']+p['routes'][b]['radius']
        if near(curves[a],curves[b],req):
          d=curves[a].distToShape(curves[b])[0];pairs+=1
          if d<req-1e-5:hits.append(dict(a=a,b=b,distance_mm=d,required_mm=req))
    allowance={'JPWM_project_allowance':box(p['housing_bounds_mm']),
      'P_REAR_project_allowance':box([24,-18.5,132.5,46,18.5,143.5])}
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
    result=dict(status='REJECTED_EAST_PROPOSAL' if hits or bad or outside else 'EAST_SPACE_CANDIDATE_ONLY',contacts=hits,pairs=pairs,
      outside=outside,budget_failures=bad,budgets=p['budgets'],worker_seconds=round(time.monotonic()-tick,3),
      source_sha256={**p['source_sha256'],**reader.hashes},selected=False,physical_pass=False,E2_complete=False,
      remaining=['Full sleeve/current actual station envelopes, wire boundary','Native grips/parameter/reopen/tools','Stock/selection with new P_REAR invalidation'])
    dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('status','contacts','pairs','outside','budget_failures','worker_seconds')}),flush=True)
if __name__=='__main__':run()
