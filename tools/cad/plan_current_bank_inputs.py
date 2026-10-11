"""Twelve monotonic UP/S/UP fans from one underfloor power gallery.

R47 purchased holders/TE ends remain; no overhead receiving U returns.
Candidate foundation passages are not native load-path qualification.
"""
import json,math,time
from pathlib import Path
from plan_current_main_sources import ROOT,OUT,E,W,N,S,U,D,entry,straight,finish,add,mul,curve,SHA
from open_prototype_source_group import check_path

R=12.4
def turn(q,u,v):
    a=q[-1]['end'];k=math.sqrt(.5)
    q.append(curve(a,add(add(a,mul(u,R)),mul(v,R)),
      add(add(a,mul(u,R*k)),mul(v,R*(1-k))),R,math.pi/2))

def shift(q,u,v,d):
    a=q[-1]['end'];phi=math.acos(1-d/(2*R));sn,cs=math.sin(phi),math.cos(phi)
    b=add(add(a,mul(u,R*sn)),mul(v,R*(1-cs)))
    c=add(add(b,mul(u,R*sn)),mul(v,R*(1-cs)))
    m1=add(add(a,mul(u,R*math.sin(phi/2))),mul(v,R*(1-math.cos(phi/2))))
    m2=add(add(b,mul(u,R*(sn-math.sin(phi/2)))),mul(v,R*(math.cos(phi/2)-cs)))
    q.extend((curve(a,b,m1,R,phi),curve(b,c,m2,R,phi)))

def plan():
    fp=OUT/'leg-stations-plan.json';op=OUT/'owner-plan.json'
    legplan=json.loads(fp.read_text());owners=json.loads(op.read_text())
    rows={r['id']:r for r in owners['body_conductors']}
    wires=dict(FL=['W027','W028','W029'],FR=['W038','W039','W040'],
      RL=['W046','W048','W050'],RR=['W054','W056','W058'])
    routes={}
    for leg,ids in wires.items():
        for i,wid in enumerate(ids):
            row=rows[wid];role=f'{leg}_P.{i+2}'
            assert role in (row['a'],row['b'])
            te=next(e for e in row['historical_ends'] if e['role']!=role)
            assert te['departure']==D and te['native'].endswith('_CP2_IN')
            target=legplan['ports'][role]['point_mm']
            end=te['point_mm'];dx=end[0]-target[0];dy=end[1]-target[1];d=math.hypot(dx,dy)
            # Incoming stem on the transfer side bends first; upstream stems
            # cross above it, not through it. Rear fans transfer WEST, fronts EAST.
            layer=2-i if leg in ('FL','FR') else i
            q=entry(target,U,9+5*layer)
            if d>1e-7:
                v=[dx/d,dy/d,0]
                if d<2*R:shift(q,U,v,d)
                else:
                    turn(q,U,v)
                    straight(q,[end[0]-R*v[0],end[1]-R*v[1],q[-1]['end'][2]])
                    turn(q,v,U)
            assert end[2]-q[-1]['end'][2]>=9-1e-7
            straight(q,end);parts=q
            check_path(parts,start=target,end=end,min_radius=R)
            routes[wid]=dict(parts=parts,radius_mm=1.55,SKU='LAPP0107001',
              endpoints=[role,te['role']],native_terminal=te['native'],guide_mm=sum(p['length_mm'] for p in parts),
              strip_mm=[11,7.92],TE_strip_tolerance_mm=.38,actual_cut_mm=None,
              historical_100mm_project_blank_superseded_candidate=True)
    return dict(status='TWELVE_BANK_INPUTS_MONOTONIC_UNDERFLOOR_FAN_PLAN_ONLY',
      selected=False,W5_complete=False,physical_pass=False,routes=routes,
      design='One underfloor power gallery: all12branches depart UP9mm, fan monotonically in XY with tangent-continuous R12.4 S bends and approach downward-facing TE mouths UP with >=9mm straight lands. No overhead U returns or side widening. Whole outputs/ground/data/support/service remain shared qualification, not inferred from fan fit.',
      required_foundation_passages=[dict(centre_xy_mm=[-53,y],diameter_mm=6.4,z_range_mm=[40,76],
        scope='Candidate subtractive passage only; do not overwrite selected W1 Foundation') for y in (55,69)],
      obsolete_side_attachment_removal=dict(target='LowerCarrier001',
        cut_bounds_mm=[[-20,34.9,39.5,78,95,55],[-20,-95,39.5,78,-34.9,55]],
        basis='open_prototype_distribution_mounts.py SideArms/SideRibs/SideFeet: old side WAGO carrier support only. New receiving cases supersede old20mounts. Remove outer obsolete attachments, not board carrier/core/rear columns/tail support.',
        native_status='OPEN_CANDIDATE_ONLY',protected_core_bounds_mm=[-29,-34.9,39.5,155,34.9,55]),
      assembly='Fit unpowered branches from lower gallery upward through candidate local Foundation passages before clipping TE ends to registered bank. Mount independent grip saddles to frame, never lever/adhesive wire retention. Whole load path, lever access, protection and removal proof OPEN.',
      stock='Recompute total LAPP and voltage/fault budget from full nominal cuts at selection; old100mm branch assumption is not a supplier limit nor a current acceptance.',
      open=['Actual full retained solids/curves, leg motion and every output fan',
        'Native registered bank/receiving supports, independent grip load path and installed service',
        'Foundation subtractive pilot/load-path check, parameter/reopen and whole material/electrical reconciliation'],
      source_sha256={f.relative_to(ROOT).as_posix():SHA(f) for f in (Path(__file__),fp,op,ROOT/'tools/cad/open_prototype_distribution_mounts.py')})

if __name__=='__main__':
    tick=time.monotonic();p=plan();p['planning_seconds']=time.monotonic()-tick
    (OUT/'bank-input-plan.json').write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(routes=len(p['routes']),guides_mm={n:round(r['guide_mm'],3) for n,r in p['routes'].items()},seconds=p['planning_seconds'])))
