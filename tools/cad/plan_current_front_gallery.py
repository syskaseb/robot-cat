"""Coupled front receiving topology, preserving the frozen rejected baseline.

Move both power cases and their complete six fans away from leg motion.
Two full R25.2 lateral transfers below existing inline/MTA cases replace the
old outer descents. This is a proposal, not selection or a native frame cut.
"""
import copy,json,math,time
from pathlib import Path
from plan_current_main_sources import ROOT,OUT,R,U,D,N,S,E,straight,turn,offset,SHA
from plan_current_bank_inputs import entry,shift,turn as fan_turn,check_path

def plan():
    files=[OUT/(n+'.json') for n in ('leg-stations-plan','bank-input-plan','leg-gallery-motion-rejection','main-pi-plan')]
    old,bank,rejection,main=[json.loads(f.read_text()) for f in files]
    assert rejection['reference_gate']['status']=='REJECTED_PROJECT_LEG_GALLERY_MOTION'
    stations={};ports={};routes={}
    for leg,wid,sign,ids in [('FL','W026',1,['W027','W028','W029']),('FR','W037',-1,['W038','W039','W040'])]:
        name=leg+'_P';station=copy.deepcopy(old['stations'][name])
        # P0 side-wall material reaches Y49.34 at the case mouth height.
        # Use the complete OUTER gallery at Y75, not another hole in P0.
        # X40 (rather than old X-60) separates both cases from front knees.
        # Southern fan goes outside the retained USB U-return (-73.1), not
        # between its vertical legs. Asymmetry is intentional routing space.
        centre_y=75 if leg=='FL' else -93
        dx=40-station['centre_mm'][0];dy=centre_y-station['centre_mm'][1]
        station['centre_mm'][0]+=dx;station['centre_mm'][1]+=dy
        for index in (0,3):station['casing_mm'][index]+=dx
        for index in (1,4):station['casing_mm'][index]+=dy
        for k,point in station['ports'].items():
            point[0]+=dx;point[1]+=dy;ports[name+'.'+k]=dict(point_mm=point,wire=old['ports'][name+'.'+k]['wire'])
        # Same common rail: receive main power at the EAST-most spare mouth,
        # like the retained rear banks, so WEST-going fan cores do not cross
        # the main input stem. Physical1 becomes NC, not another conductor.
        station['ports']['1'],station['ports']['5']=station['ports']['5'],station['ports']['1']
        station['logical_to_physical_common_rail_cavity'].update({'1':5,'5':1})
        for k in ('1','5'):ports[name+'.'+k]['point_mm']=station['ports'][k]
        stations[name]=station
        # Upper qualified portion is unchanged through its final DOWN turn.
        count=8 if leg=='FL' else 9
        q=copy.deepcopy(old['routes'][wid+'_CUSTOM']['parts'][:count])
        target=station['ports']['1'];outside=q[-1]['end'][1];v=S if sign>0 else N
        # Entire upper transfer clears the front mount/riser footprint before
        # descending. No structural P0/riser cuts. Outside rail stays beyond
        # the ATO row; lower S fan ends outside LowerCarrier's protected core.
        straight(q,[q[-1]['end'][0],outside,180 if leg=='FL' else 165]);turn(q,D,E)
        straight(q,[target[0]-R,outside,q[-1]['end'][2]]);turn(q,E,D)
        straight(q,[target[0],outside,85]);offset(q,D,v,abs(outside-target[1]))
        assert q[-1]['end'][2]-target[2]>=9
        straight(q,target);check_path(q,min_radius=R)
        routes[wid+'_CUSTOM']={**old['routes'][wid+'_CUSTOM'],'parts':q,'guide_mm':sum(s['length_mm'] for s in q)}
        for i,n in enumerate(ids):
            row=bank['routes'][n];role=row['endpoints'][0];start=ports[role]['point_mm'];end=row['parts'][-1]['end']
            dx=end[0]-start[0];dy=end[1]-start[1];length=math.hypot(dx,dy);v=[dx/length,dy/length,0]
            land=[9,14,19][i]
            q=entry(start,U,land)
            if length<24.8:shift(q,U,v,length)
            else:
                fan_turn(q,U,v);straight(q,[end[0]-12.4*v[0],end[1]-12.4*v[1],q[-1]['end'][2]]);fan_turn(q,v,U)
            assert end[2]-q[-1]['end'][2]>=9-1e-7
            straight(q,end);check_path(q,min_radius=12.4)
            routes[n]={**row,'parts':q,'guide_mm':sum(s['length_mm'] for s in q)}
    return dict(status='COUPLED_CENTRAL_FRONT_GALLERY_PLAN_ONLY',stations=stations,ports=ports,routes=routes,
      selected=False,W5_complete=False,physical_pass=False,
      retains='Ten unchanged receiving cases, six rear input fans, two rear output guides and all source/factory/joint interfaces. Frozen old receipts remain history, not acceptance of this overlay.',
      reason='Central X-60/Y+/-15 entered front mounts/neck risers; X40/Y+/-50 entered P0 side walls at the low mouth height. Allocate the WHOLE two-case/six-fan/two-output family at X40/Y+/-75 outside those walls and away from front knee X-100. Six fans stay outside the lower-carrier core and USB lanes. Native P0/riser/side-wall load paths retained, no new body width.',
      required_passages='Actual material gate must identify any Foundation interruption of two complete R25.2 transfer curves. No automatic structural clearance cut, no native selected geometry yet.',
      source_sha256={f.relative_to(ROOT).as_posix():SHA(f) for f in [Path(__file__),*files]})

if __name__=='__main__':
    t=time.monotonic();p=plan();p['planning_seconds']=time.monotonic()-t
    (OUT/'front-gallery-plan.json').write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(stations=len(p['stations']),routes={n:round(v['guide_mm'],3) for n,v in p['routes'].items()},seconds=p['planning_seconds'])))
