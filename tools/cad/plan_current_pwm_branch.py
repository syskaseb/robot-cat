"""One complete current E2 spatial proposal, before any native mount edits.

Preserve the selected electrical circuit. Exact curves and current physical
geometry screen the joint layout; no bbox-only collision verdict or selection.
"""
from pathlib import Path
import sys, json, math, time
from datetime import datetime, timezone
sys.path.insert(0, str(Path(sys.executable).resolve().parent.parent/'lib'))
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT, SavedShapes, sha
from open_prototype_distribution_allocation import input_recipe

BASE=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype'
OUT=BASE/'pwm-branch-checkpoint'

def xyz(v):return [v.x,v.y,v.z]
def line(a,b):return dict(kind='line',start=a,end=b)
def arc(c,a,b):
    c,a,b=map(lambda q:A.Vector(*q),(c,a,b));r=(a-c).Length
    assert abs((b-c).Length-r)<1e-7
    return dict(kind='arc',start=xyz(a),mid=xyz(c+((a-c)+(b-c)).normalize()*r),end=xyz(b))
def wire(parts):
    return Part.Wire([Part.makeLine(A.Vector(*q['start']),A.Vector(*q['end'])) if q['kind']=='line'
      else Part.Arc(A.Vector(*q['start']),A.Vector(*q['mid']),A.Vector(*q['end'])).toShape() for q in parts])
def box(b):return Part.makeBox(*[b[i+3]-b[i] for i in range(3)],A.Vector(*b[:3]))
def near(s,t,r):
    a,b=s.BoundBox,t.BoundBox
    return sum(max(0,getattr(a,k+'Min')-getattr(b,k+'Max'),getattr(b,k+'Min')-getattr(a,k+'Max'))**2 for k in 'XYZ')<=(r+1e-6)**2

def build():
    routes={
      'XP01':dict(parts=[line([75.3,22.5,138],[75.3,34.5,138])],radius=1.05),
      'XP02_source':dict(parts=[line([75.3,54.9,138],[75.3,69.9,138]),
        arc([75.3,69.9,126],[75.3,69.9,138],[75.3,81.9,126]),
        arc([75.3,69.9,126],[75.3,81.9,126],[75.3,69.9,114]),
        line([75.3,69.9,114],[75.3,67.3,114])],radius=.925),
      'XP03_source':dict(parts=input_recipe([140,-50.5,96],[78.3,67.3,114],[0,1,0],11.1)['segments'],radius=.925)}
    for name,startx,turnx,endy,padx,pady in [
      ('XP02_module',75.3,69,-25,91.59,-11.43),
      ('XP03_module',78.3,66,-29,89.05,-6.35)]:
        parts=input_recipe([startx,32.7,114],[turnx,endy,81.5],[0,-1,0],11.1)['segments']
        r=(padx-turnx)/2;c=[turnx+r,endy,81.5]
        parts += [arc(c,[turnx,endy,81.5],[turnx+r,endy-r,81.5]),
          arc(c,[turnx+r,endy-r,81.5],[padx,endy,81.5]),
          line([padx,endy,81.5],[padx,pady-1,81.5])]
        routes[name]=dict(parts=parts,radius=.925)
        routes[name+'_bare']=dict(parts=[arc([padx,pady-1,82.5],[padx,pady-1,81.5],[padx,pady,82.5]),
          line([padx,pady,82.5],[padx,pady,85.8202])],radius=math.sqrt(.518/math.pi))
    budgets={}
    for name,minimum,reserve in [('XP02_source',220,4+6+30),('XP03_source',295,11+6+30),
      ('XP02_module',145,6+10),('XP03_module',145,6+10)]:
        length=wire(routes[name]['parts']).Length
        bare=wire(routes[name+'_bare']['parts']).Length if name+'_bare' in routes else 0
        budgets[name]=dict(route_mm=length,bare_mm=bare,additional_allowance_mm=reserve,
          minimum_factory_mm=minimum,margin_mm=minimum-length-bare-reserve)
    return dict(status='JOINT_E2_PROPOSAL_NOT_SELECTED',selected=False,physical_pass=False,E2_complete=False,
      source_station_pose_unchanged=True,P_REAR_centre_mm=[68.8,11.5,138],G_TAIL_centre_mm=[140,-60,96],
      housing_bounds_mm=[70.8,35,108,82.8,65,120],routes=routes,budgets=budgets,
      fuse=dict(sku='0242.100UAT1',body_start=[75.3,40.5,138],axis=[0,1,0],body_length_mm=8.4,
        body_radius_mm=1.51,input_lead_mm=10,output_lead_mm=10,input_overlap_mm=4,output_overlap_mm=4,
        outer_sleeve_start=[75.3,25,138],outer_sleeve_length_mm=42,outer_OD_mm=6.4,
        inner_blank_mm=[20,20],outer_blank_mm=50,individual_inner_finished_mm=14,
        conservative_unfused_mm=12+18+8.4,limit_mm=50,XP01_nominal_fit_blank_mm=24),
      factory_leads=dict(red_source='2147612113 225+/-5mm',black_source='2147611114 300+/-5mm',
        red_module='2147632112 150+/-5mm',black_module='2147631112 150+/-5mm'),
      load_path_plan=[
        'Replaceable north bridge on UpperCarrier, new two M3 anchors X52/100,Y35. Posts rise from77.72 to129.5; plate3mm supports P_REAR at132.5.',
        'Separate P_REAR body retention behind levers; fuse sleeve seats atY28/62 with independent insulation ties, not adhesive as wire relief.',
        'Mated housing cradle below bridge, two housing ties outside latch and independently tied source/module wires; open-top bench assembly.',
        'G_TAIL separate south bracket: carrier anchor X138,Y-35 to body bottom91.5, no wire forces through glue.',
        'Two underside PWM pad-end grips on UpperCarrier, no clamp on copper or solder joint. PCB pad map retained from Adafruit1608 source.'],
      service_plan=[
        'Battery and USB absent. Unclamp P_REAR.4 and G_TAIL.3, park insulated ends; support wiring before cutting dedicated ties.',
        'Release housing ties and latch, disconnect JPWM; remove bridge/return bracket before PCB service. No connected swept-wire removal claim.',
        'All local supports screw to matched carrier; assemble captive nuts before PCB, connect PWM board on bench and then seat on posts.'],
      assumptions=['Project mated housing30x12x12 and lead exits, not manufacturer cavity coordinates; delivered fit/continuity gate.',
        'Nominal factory length minima220/295/145; source leads trimmed only after complete physical fit, untinned WAGO end.',
        'WireOD1.85/R11.1 and sleeved fuseOD6.4 are project maxima; delivered dimensions/thermal/E3 coordination remain gates.',
        'No unknown external U1 pinout used. Other whole-cat wiring remains OPEN.'],
      invalidated=['Any unselected source-family wire/support reservation occupying this bridge must be rebound before W5 selection.'],
      source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in [
        BASE/'current-phase1-score.json',BASE/'mounting-checkpoint/current-M5-manifest.json',
        BASE/'wiring-checkpoint/source-group-allocation.json',
        ROOT/'hardware/electronics/full-cat/pwm-carrier-r3/population.json',
        ROOT/'hardware/electronics/full-cat/pwm-complete-e2-r1/electrical-design.json',Path(__file__)]})

def run():
    tick=time.monotonic();OUT.mkdir(exist_ok=True);assert not (OUT/'space-checks.json').exists()
    p=build();(OUT/'joint-plan.json').write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8')
    bad=[n for n,b in p['budgets'].items() if b['margin_mm']<0]
    result=dict(status='PENDING',contacts=[],pairs=0,budget_failures=bad,selected=False,physical_pass=False)
    reader=SavedShapes();targets={}
    mount=BASE/'mounting-checkpoint/CurrentBoardMounts.FCStd'
    proof=json.loads((BASE/'mounting-checkpoint/current-M5-checks.json').read_text())
    for n in proof['physical_objects']:
        if n in reader.doc(mount):targets[n]=reader.shape(mount,n)
    ctx=BASE/'OpenPrototypePlan.FCStd'
    for n in reader.doc(ctx):
        if n.startswith(('P0_','S0_','F_L','F_R')) and 'Tool' not in n and 'Driver' not in n:
            try:targets[n]=reader.shape(ctx,n)
            except ValueError:pass
    tail=BASE/'tail-mount-checkpoint/TailAssemblyCurrent.FCStd'
    # Current whole tail rather than stale pre-CP2 bracket.
    tc=json.loads((BASE/'tail-mount-checkpoint/manifest.json').read_text())
    # Current tail physical identities are pinned separately; avoid constructions.
    for n in reader.doc(tail):
        if n in ('CurrentTailSupport','TailRoot','MG92BCase','LowerCarrier'):targets['tail/'+n]=reader.shape(tail,n)
    torso=reader.shape(ctx,'TorsoEnvelope')
    targets['JPWM_project_allowance']=box(p['housing_bounds_mm'])
    structural={
      'Bridge':box([47,-1,129.5,105,67,132.5]),
      'PostA':box([49,32,77.72,55,38,129.5]),
      'PostB':box([97,32,77.72,103,38,129.5]),
      'ReturnBracket':box([134,-70,88.5,146,-32,91.5]),
      'ReturnPost':box([135,-38,77.72,141,-32,88.5])}
    curves={n:wire(r['parts']) for n,r in p['routes'].items()}
    for name,curve in curves.items():
        rad=p['routes'][name]['radius']
        for other,s in {**targets,**structural}.items():
            if not near(curve,s,rad):continue
            # Only the bare wire's assigned pad penetrates PCB material. PCB
            # pad-hole reference and exact terminal volume still required.
            if name.endswith('_bare') and other=='PWM1608NominalPCB':continue
            if other=='JPWM_project_allowance':continue # both factory leads intentionally terminate at housing
            d=min(curve.distToShape(t)[0] for t in s.Solids);result['pairs']+=1
            if d<rad-1e-5:result['contacts'].append(dict(a=name,b=other,distance_mm=d,required_mm=rad))
    names=list(curves)
    for i,a in enumerate(names):
      for b in names[i+1:]:
        if a.removesuffix('_bare')==b.removesuffix('_bare'):continue
        ra=p['routes'][a]['radius'];rb=p['routes'][b]['radius']
        if near(curves[a],curves[b],ra+rb):
          d=curves[a].distToShape(curves[b])[0];result['pairs']+=1
          if d<ra+rb-1e-5:result['contacts'].append(dict(a=a,b=b,distance_mm=d,required_mm=ra+rb))
    for a,s in structural.items():
      for b,t in targets.items():
        if not near(s,t,0):continue
        v=sum(x.common(y).Volume for x in s.Solids for y in t.Solids);result['pairs']+=1
        if v>1e-5:result['contacts'].append(dict(a=a,b=b,volume_mm3=v))
    result.update(status='REJECTED_SHARED_PROPOSAL' if result['contacts'] or bad else 'ROUTES_AND_SUPPORT_SPACE_ONLY',
      budgets=p['budgets'],source_sha256={**p['source_sha256'],**reader.hashes,
        (OUT/'joint-plan.json').relative_to(ROOT).as_posix():sha(OUT/'joint-plan.json')},
      worker_seconds=round(time.monotonic()-tick,3),finished_utc=datetime.now(timezone.utc).isoformat(),
      remaining=['Native bodies/grips/hardware/tool/latch/removal','Actual terminal pad envelopes/fuse sleeve/current stations','Boundary/print/export/stock selection'])
    (OUT/'space-checks.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('status','contacts','pairs','budget_failures','worker_seconds')}),flush=True)
if __name__=='__main__':run()
