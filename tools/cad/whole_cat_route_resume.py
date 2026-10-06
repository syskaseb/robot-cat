"""Resume OPEN routes only; richer directions, cached shape validity/bounds.

Nominal centreline search is not an exact swept pipe or restraint proof. Reuse
the saved package gate and any completed routes; never regenerate that layout.
"""
from pathlib import Path
from datetime import datetime,timezone
import hashlib
import heapq
import itertools
import json
import math
import time
import FreeCAD as A
import Part
import whole_cat_mta_common_plan as m

BASE=m.BASE
SOURCE=BASE/'mta-source-aux-plan.json'
NATIVE=BASE/'MTASourceLayoutCandidate.FCStd'
OUT=BASE/'mta-route-resume.json'
if m.HORIZONTAL:
    SOURCE=BASE/('mta-horizontal-corrected-plan.json' if m.HORIZONTAL_CORRECTED else 'mta-horizontal-receivers-plan.json')
    NATIVE=BASE/'MTAHorizontalCandidate.FCStd'
    OUT=BASE/'mta-horizontal-route-search.json'
DEADLINE=datetime.fromisoformat('2026-10-06T07:00:00+00:00')


def fine_points(s):
    n=max(2,math.ceil(s['length_mm']/.5));p=s['start_mm']
    if s['kind']=='line':return [m.add(p,m.scale(s['tangent'],s['length_mm']*i/n)) for i in range(n+1)]
    u=s['start_tangent'];v=s['end_tangent'];theta=s['angle_rad'];r=s['radius_mm']
    normal=m.scale(m.add(v,m.scale(u,-math.cos(theta))),1/math.sin(theta))
    return [m.add(p,m.add(m.scale(u,r*math.sin(theta*i/n)),
        m.scale(normal,r*(1-math.cos(theta*i/n))))) for i in range(n+1)]


def main():
    started=datetime.now(timezone.utc);tick=time.monotonic()
    assert started<DEADLINE and not OUT.exists()
    old=json.loads(SOURCE.read_text(encoding='utf-8'))
    assert old['shared_package_contradictions']==[]
    pins={str(p.relative_to(m.ROOT)):m.sha(p) for p in [SOURCE,NATIVE,Path(__file__),Path(m.__file__)]}
    doc=A.openDocument(str(NATIVE));doc.recompute()
    owners=[]
    for o in doc.Objects:
        if 'Shape' not in o.PropertiesList or o.Name in ['TorsoEnvelope','BatteryNominal']:continue
        if not (any(p.Name in ['InteriorReservations','HarnessCandidate','S0TerminalCandidates',
            'S1TerminalCandidates','ServiceReservations','ATOStackCandidates'] for p in o.InList)
                or 'Category' in o.PropertiesList and o.Category!='electronics'):continue
        s=o.Shape.copy();owners.append((o.Name,s,s.BoundBox,s.isValid()))
    torso=doc.getObject('TorsoEnvelope').Shape.copy()
    assert torso.isValid() and len(torso.Solids)==1
    boundary=Part.makeCompound(torso.Shells)
    directions=[m.scale(list(v),1/math.sqrt(sum(x*x for x in v)))
        for v in itertools.product([-1,0,1],repeat=3) if v!=(0,0,0)]
    routes=list(old['routes']);open_routes=[]
    existing=[[p for s in r['segments'] for p in fine_points(s)] for r in routes]
    def plan(ep):
        began=time.monotonic();cache={};rejects={};expanded=0
        def safe(p):
            # 0.25mm point quantisation + radius2.1 + sample0.25 budget.
            # This has less DESIGN clearance than old4.1mm occupancy, not a
            # claim that the provisional wire OD or final margin is qualified.
            k=tuple(round(c*4) for c in p)
            if k in cache:return cache[k]
            q=A.Vector(*(c/4 for c in k));pad=2.6
            for name,s,bb,valid in owners:
                if name==ep['joint'] and m.length(m.minus(list(q),ep['start']))<12:continue
                if name==ep['target'] and m.length(m.minus(list(q),ep['goal']))<18:continue
                if not (bb.XMin-pad<=q.x<=bb.XMax+pad and bb.YMin-pad<=q.y<=bb.YMax+pad and bb.ZMin-pad<=q.z<=bb.ZMax+pad):continue
                if not valid or s.distToShape(Part.Vertex(q))[0]<pad:
                    rejects[name]=rejects.get(name,0)+1;cache[k]=False;return False
            if not torso.isInside(q,1e-7,True) or boundary.distToShape(Part.Vertex(q))[0]<pad:
                rejects['TorsoEnvelope']=rejects.get('TorsoEnvelope',0)+1;cache[k]=False;return False
            for curve in existing:
                if any(m.length(m.minus(list(q),v))<4.8 for v in curve):
                    rejects['Earlier_route']=rejects.get('Earlier_route',0)+1;cache[k]=False;return False
            cache[k]=True;return True
        def clear(ss):return all(safe(p) for s in ss for p in fine_points(s))
        runout=9 if ep['holder'] in ['S0','S1'] else 3
        initial=m.line(ep['start'],ep['tangent'],runout)
        if not clear([initial]):return None,dict(reason='runout_blocked',rejects=rejects)
        counter=itertools.count();heap=[];seen={}
        heapq.heappush(heap,(m.length(m.minus(ep['goal'],initial['end_mm'])),next(counter),
            initial['end_mm'],ep['tangent'],[initial],runout))
        while heap and expanded<3000 and time.monotonic()-began<45:
            if datetime.now(timezone.utc)>=DEADLINE:break
            _,_,p,u,path,cost=heapq.heappop(heap)
            k=tuple(round(c/4) for c in p)+tuple(round(c,3) for c in u)
            if seen.get(k,float('inf'))<=cost:continue
            seen[k]=cost;expanded+=1
            ending=m.suffix(p,u,ep['goal'],ep['goal_u'])
            if ending and clear(ending):return path+ending,dict(expanded=expanded,rejects=rejects)
            options=[m.line(p,u,L) for L in [9,25.2,50.4]]
            options.extend(m.arc(p,u,v) for v in directions if abs(m.dot(u,v))<1-1e-7)
            for s in options:
                if not clear([s]):continue
                h=s['tangent'] if s['kind']=='line' else s['end_tangent'];nc=cost+s['length_mm']
                heapq.heappush(heap,(nc+1.12*m.length(m.minus(ep['goal'],s['end_mm'])),next(counter),s['end_mm'],h,path+[s],nc))
        return None,dict(reason='bounded_search_open_not_impossibility',expanded=expanded,rejects=rejects)
    try:
        for ep in old['open_routes']:
            ep=dict(ep);ep.pop('info',None)
            try:ss,info=plan(ep)
            except Exception as exc:ss=None;info=dict(reason='planning_error',error=repr(exc))
            print(ep['id'],'PLANNED' if ss else 'OPEN',info.get('expanded'),flush=True)
            if ss:
                allowance=29 if ep['holder']=='S0' else 28.452 if ep['holder']=='S1' else 11+(14 if ep['target'] in ['P_FRONT_CP2','P_REAR_CP2'] else 11)
                routes.append(dict(**ep,segments=ss,extension_nominal_mm=sum(s['length_mm'] for s in ss)+allowance,
                    connector_runout_mm=9 if ep['holder'] in ['S0','S1'] else 3,runout_is_NOT_an_insulation_grip=True,info=info))
                existing.append([p for s in ss for p in fine_points(s)])
            else:open_routes.append(dict(**ep,info=info))
            # Preserve every completed search if the worker is stopped later.
            report=dict(status='NOMINAL_ROUTE_SEARCH_ONLY',selected=False,physical_pass=False,
                W1_complete=False,W5_complete=False,required_routes=old['required_routes'],routes=routes,
                open_routes=open_routes,processed_open_routes=len(routes)-len(old['routes'])+len(open_routes),
                source_sha256=pins,package_gate_reused=True,native_not_resaved=True,
                clearance_scope='2.6mm sampled nominal occupancy, reduced from previous4.1mm; no exact pipe/grip/tool/stock qualification',
                started_utc=started.isoformat(),finished_utc=datetime.now(timezone.utc).isoformat(),
                worker_wall_seconds=round(time.monotonic()-tick,3))
            OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    finally:A.closeDocument(doc.Name)
    assert m.sha(NATIVE)==pins[str(NATIVE.relative_to(m.ROOT))]


if __name__=='__main__':main()
