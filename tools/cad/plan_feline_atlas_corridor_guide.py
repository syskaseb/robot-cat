"""A shared-space graph GUIDE, not a cable or CAD clearance approval.

Source/goal lead lengths are allowed to vary above their project minimum.
The guide avoids the atlas's sampled material/motion/service/unknown-curve
layers. Actual R30/full452 geometry and changed-interface gates remain next.
"""
import json
import math
import time
import sys
from pathlib import Path
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_tangent_routes import quarter_prefix,samples,length


def grid_graph(mask,spacing=4):
    ids=np.full(mask.shape,-1,dtype=np.int32);ids[mask]=np.arange(int(mask.sum()));row=[];col=[]
    for axis in range(3):
        a=[slice(None)]*3;b=list(a);a[axis]=slice(None,-1);b[axis]=slice(1,None)
        x=ids[tuple(a)];y=ids[tuple(b)];valid=(x>=0)&(y>=0)
        row.extend([x[valid],y[valid]]);col.extend([y[valid],x[valid]])
    row=np.concatenate(row);col=np.concatenate(col)
    return ids,row,col,np.full(len(row),spacing,dtype=float)


def main():
    tick=time.monotonic();joint='--joint-frame' in sys.argv
    src=OUT/('n01-reservation-ownership-plan.json' if joint else 'n01-shared-space-atlas-received.json');dest=OUT/('n01-joint-frame-corridor-guide.json' if joint else 'n01-atlas-corridor-guide.json')
    prior=json.loads(dest.read_text()) if dest.exists() else None
    if prior:assert prior['status']=='ATLAS_GUIDE_PENDING_CURVATURE_AND_EXACT_GEOMETRY' and not prior['selected'] and ('pairwise_source_goal_allocation' not in prior or '--representatives' in sys.argv)
    p=json.loads(src.read_text());assert p['status'] in ('SHARED_SURFACE_MOTION_SERVICE_ATLAS_PLANNING_NOT_N01','JOINT_FRAME_SURFACE_ATLAS_PLANNING_NOT_N01')
    f=ROOT/p['field'];assert sha(f)==p['field_sha256'];a=np.load(f,allow_pickle=False)
    free=a['nominal']&~a['curve_hold'];axes=[a[k] for k in ('x','y','z')];spacing=4
    ids,row,col,cost=grid_graph(free,spacing);n=int(free.sum());S=n;T=n+1
    sourcefile=OUT/'n01-joint-usb-route.json';usb=json.loads(sourcefile.read_text());start=usb['start_mm'];goal=usb['end_mm'];anchors=[];sourceanchors={};goalanchors={}
    def cell(q):
        ix=tuple(int(np.rint((q[i]-axes[i][0])/spacing)) for i in range(3))
        if any(ix[i]<0 or ix[i]>=len(axes[i]) for i in range(3)):return None
        return ix
    for r in p['USB_variable_land_anchors']:
        owner=r['owner'];i=r['domain'];first=r['first_straight_mm'];ang=i*math.pi/12
        pos=start if owner=='PiUSB' else goal;d=(-1,0,0) if owner=='PiUSB' else (0,-1,0);b=(0,math.cos(ang),math.sin(ang)) if owner=='PiUSB' else (math.cos(ang),0,math.sin(ang))
        parts=quarter_prefix(pos,d,b,first=first);points=[];travel=0
        for s in parts:
            ss=list(samples(s,1))
            for j,q in enumerate(ss):
                along=travel+s['length']*j/max(1,len(ss)-1)
                if along>=6:points.append(q)
            travel+=s['length']
        cells=[cell(q) for q in points]
        # First6mm are the nominal own-plug mating neighbourhood only.
        # This exclusion is OPEN to exact source-prefix checks, never a PASS.
        screened=all(ix is not None and bool(free[ix]) for ix in cells)
        ix=cell(parts[-1]['end'])
        item=dict(r,prefix_parts=parts,prefix_length_mm=length(parts),sampled_prefix_screen_clear=screened,
            own_boot_mating_first6mm_excluded_from_coarse_screen=True,prefix_exact_qualification_open=True)
        anchors.append(item)
        if not screened or ix is None or ids[ix]<0:continue
        node=int(ids[ix]);bucket=sourceanchors if owner=='PiUSB' else goalanchors
        if node not in bucket or item['prefix_length_mm']<anchors[bucket[node]]['prefix_length_mm']:bucket[node]=len(anchors)-1
    graph=coo_matrix((cost,(row,col)),shape=(n,n)).tocsr()
    snodes=list(sourceanchors);tnodes=list(goalanchors)
    ds,ps=dijkstra(graph,indices=snodes,return_predecessors=True);dt,pt=dijkstra(graph,indices=tnodes,return_predecessors=True)
    coordinates=np.stack(np.meshgrid(*axes,indexing='ij'),axis=-1)[free]
    def chain(v,pred,terminal):
        out=[];seen=set()
        while v!=terminal:
            if v<0 or v in seen:return None
            out.append(v);seen.add(v);v=int(pred[v])
        return out
    candidates=[];pair_summaries=[]
    for si,snode in enumerate(snodes):
        for ti,tnode in enumerate(tnodes):
            sa=anchors[sourceanchors[snode]];ta=anchors[goalanchors[tnode]];pref=sa['prefix_length_mm']+ta['prefix_length_mm']
            valid=np.flatnonzero(np.isfinite(ds[si])&np.isfinite(dt[ti]));order=valid[np.argsort(abs(ds[si,valid]+dt[ti,valid]+pref-452))]
            added=0
            for v in order[:1600]:
                l=chain(int(v),ps[si],snode);r=chain(int(v),pt[ti],tnode)
                if l is None or r is None:continue
                l.append(snode);r.append(tnode)
                if set(l[1:])&set(r[1:]):continue # No retracing a branch as fake slack.
                path=list(reversed(l))+r[1:]
                if len(path)<3:continue
                points=coordinates[path];directions=np.diff(points,axis=0);bends=int(np.sum(np.any(directions[1:]!=directions[:-1],axis=1)))
                sd=np.array(sa['prefix_parts'][-1]['end'])-sa['prefix_parts'][-1]['start'];td=np.array(ta['prefix_parts'][-1]['start'])-ta['prefix_parts'][-1]['end']
                cos0=float(np.dot(sd,directions[0])/(np.linalg.norm(sd)*np.linalg.norm(directions[0])));cos1=float(np.dot(td,directions[-1])/(np.linalg.norm(td)*np.linalg.norm(directions[-1])))
                total=float(ds[si,v]+dt[ti,v]+pref);score=abs(total-452)+bends*.15+(2-cos0-cos1)*12
                candidates.append((score,int(v),path,bends,sourceanchors[snode],goalanchors[tnode],total,cos0,cos1));added+=1
                if added>=6:break
            pair_summaries.append(dict(source_anchor_index=sourceanchors[snode],goal_anchor_index=goalanchors[tnode],graph_shortest_total_mm=float(ds[si,tnode]+pref),non_retracing_candidates=added))
    result=dict(status='ATLAS_GUIDE_PENDING_CURVATURE_AND_EXACT_GEOMETRY' if candidates else 'NO_GUIDE_FROM_CURRENT_COARSE_SCREEN_NOT_INFEASIBILITY',
        selected=False,N01_complete=False,physical_pass=False,graph_nodes=n,graph_edges=len(cost),
        sampled_clear_source_anchors=len(sourceanchors),sampled_clear_goal_anchors=len(goalanchors),
        anchors=anchors,pairwise_source_goal_allocation=pair_summaries,
        non_retracing_guide_candidates=len(candidates),guide=None,guides=[],
        source_sha256={q.relative_to(ROOT).as_posix():sha(q) for q in (src,f,sourcefile,Path(__file__),Path(__file__).with_name('feline_tangent_routes.py'))},
        holds=['Grid has right-angle corners: NOT a bend-radius-qualified cable',
            'Coarse prefix screen excludes first6mm own-plug neighbourhood: exact ALL-neighbour check still required',
            'Sampled field cannot certify solid interiors, full123middles, roots, tools or continuous motion',
            'Both factory prefix lengths/whole452 must be solved together in smooth geometry, no changed selected cable'])
    if candidates:
        ranked=sorted(candidates,key=lambda r:r[0]);chosen=ranked[:30]
        if '--representatives' in sys.argv:
            pairs=set()
            for c in ranked:
                pair=(c[4],c[5])
                if pair in pairs:continue
                pairs.add(pair)
                if c not in chosen:chosen.append(c)
            result['one_representative_per_registered_pair_retained']=True
        for score,v,path,bends,si,ti,total,cos0,cos1 in chosen:
            points=coordinates[path];compact=[points[0].tolist()]
            for i in range(1,len(points)-1):
                if np.any(points[i]-points[i-1]!=points[i+1]-points[i]):compact.append(points[i].tolist())
            compact.append(points[-1].tolist())
            result['guides'].append(dict(points_mm=compact,all_grid_points_mm=points.tolist(),source_anchor_index=si,
                goal_anchor_index=ti,graph_total_including_factory_prefixes_mm=total,bends=bends,score=score,
                source_tangent_cosine=cos0,goal_tangent_cosine=cos1,
                grid_registration_links_not_exactly_qualified=True,no_repeat_grid_node=len(path)==len(set(path)),
                not_a_selected_or_radius_qualified_cable=True))
        result['guide']=result['guides'][0]
    if prior:result['previous_planning_receipt']=dict(source_sha256=prior['source_sha256'],worker_seconds=prior['worker_seconds'],reason='Keep EVERY registered pair before curvature fit, not only globally cheapest30. Prior80f838f3 snapshot remains Git history; no new component pose')
    result['worker_seconds']=round(time.monotonic()-tick,3);dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(status=result['status'],nodes=n,source=len(sourceanchors),goal=len(goalanchors),guides=len(candidates),seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':main()
