"""Shared four-root vertical domains from ALL actual material/wires.

Project complete port/band and whole three-core breakout boxes onto actual
clipped obstacle material. These conservative domains can reject a reservation,
not prove a contact or geometric impossibility. A chosen domain still needs
constant-length flex, actual paths/arms and the full material gate.
"""
import itertools
import copy
import json
import math
import time
from pathlib import Path
import FreeCAD as A
import Part
from support_entry_port import build
from whole_current_body_material import load
from oblique_source_fans import fan
from planar_round_flex import merge,intersect
import current_body_fanout_material as M
P=M.P
DOMAIN=[[-70.,-8.]]


def subtract(intervals,blocked):
    for lo,hi in merge(blocked):
        updated=[]
        for a,b in intervals:
            if hi<a or lo>b:updated.append([a,b]);continue
            if lo>a:updated.append([a,min(b,lo)])
            if hi<b:updated.append([max(a,hi),b])
        intervals=updated
    return intervals


def run(math_name='body-low-hip-rail-exit-plan.json',result_name='body-fixed-port-vertical-space.json'):
    tick=time.monotonic();until=tick+240
    assert Path(math_name).name==math_name and Path(result_name).name==result_name
    mf=P.OUT/math_name;plan=json.loads(mf.read_text())
    for n,h in plan['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    rf=P.OUT/'body-rail-hip-retention-plan.json';ret=json.loads(rf.read_text())
    pf=P.OUT/'body-rail-hip-ports.json';ports=json.loads(pf.read_text())
    targets,wires,pins=load()
    # Four obsolete fixed port/arm owners are replaced only by proven retained
    # native-parent/sibling subsets, not dropped globally.
    subsetfile=P.OUT/'body-low-hip-retention-plan.json';subset=json.loads(subsetfile.read_text())
    archive=P.ROOT/subset['archive'];assert P.SHA(archive)==subset['archive_sha256']
    import zipfile
    with zipfile.ZipFile(archive) as z:
        idx=json.loads(z.read('index.json'))
        for row in subset['retained']:
            item=next(r for r in idx if r['name']=='Retained_'+row['owner'])
            q=Part.Shape();q.importBrepFromString(z.read(item['file']).decode());assert q.isValid()
            original=targets[row['owner']+'/0/0'];assert q.copy().cut(original.copy()).Volume<1e-5
            targets[row['owner']+'/0/0']=q
    for row in ret['changed']:assert targets.pop(row['band']+'/0/0') is not None
    changed_looms={r['loom'] for r in plan['hips']}
    wires={n:q for n,q in wires.items() if not any(n.startswith('leg/'+loom+'/') for loom in changed_looms)}
    ff=P.OUT/'leg-source-near-member-plan.json';family=json.loads(ff.read_text())
    af=P.ROOT/'hardware/simulation/p0/e6-leg-compatibility.json';axes=json.loads(af.read_text())['axes']
    for source in family['routes']:
        if source['loom'] not in changed_looms:continue
        for h in (-15,0,15):wires[f'factory-source/{source["loom"]}/{h}']=(P.wire(M.B.moved_parts(source['source_parts'],source['source'],h,0,axes)),3)
    bf=P.OUT/'body-fanout-layout.json'
    for n,row in json.loads(bf.read_text())['routes'].items():wires['qualified-body/'+n]=(P.wire(row['parts']),1)
    obstacles=[(n,s,0) for n,s in targets.items()]+[(n,s,r) for n,(s,r) in wires.items()]
    bounds={n:(s.BoundBox.XMin,s.BoundBox.YMin,s.BoundBox.ZMin,s.BoundBox.XMax,s.BoundBox.YMax,s.BoundBox.ZMax) for n,s,r in obstacles}
    projected={};queries=0;results=[];previous_seconds=0
    report=P.OUT/result_name
    if report.exists():
        previous=json.loads(report.read_text())
        assert previous['status'].startswith(('PARTIAL_','ALLOCATION_INCOMPLETE_')),'Receive existing complete result instead of rerunning'
        for n,h in previous['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
        results=previous['domains'];queries=previous['projection_queries'];previous_seconds=previous.get('cumulative_worker_seconds',previous['worker_seconds'])
    def blocks(template,root_z):
        nonlocal queries
        bb=template.BoundBox;blocked=[];records=[]
        zlo,zhi=bb.ZMin-root_z,bb.ZMax-root_z
        for name,s,radius in obstacles:
            a,b,c,x,y,z=bounds[name];margin=radius+.25
            if x<bb.XMin-margin or a>bb.XMax+margin or y<bb.YMin-margin or b>bb.YMax+margin:continue
            if z<DOMAIN[0][0]+zlo-margin or c>DOMAIN[0][1]+zhi+margin:continue
            key=(name,bb.XMin-margin,bb.YMin-margin,bb.XMax+margin,bb.YMax+margin,
                 DOMAIN[0][0]+zlo-margin,DOMAIN[0][1]+zhi+margin)
            if key not in projected:
                assert time.monotonic()<until,'Bounded240s allocation exhausted; no impossibility verdict'
                prism=P.box([key[1],key[2],key[5],key[3],key[4],key[6]])
                q=s.copy().common(prism.copy());queries+=1
                assert q.isNull() or q.isValid(),name
                projected[key]=None if q.isNull() or (q.Volume<1e-8 and q.Length<1e-8) else [q.BoundBox.ZMin,q.BoundBox.ZMax]
            interval=projected[key]
            if interval is None:continue
            lo,hi=interval[0]-zhi-margin,interval[1]-zlo+margin
            blocked.append([lo,hi]);records.append(dict(target=name,blocked_root_Z_mm=[lo,hi]))
        return blocked,records
    def save(status):
        result=dict(status=status,domains=results,projection_queries=queries,projection_cache_size=len(projected),
            root_search_domain_mm=DOMAIN,material_instances=len(targets),wire_instances=len(wires),
            source_sha256={**pins,**{f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in (mf,rf,pf,subsetfile,archive,ff,af,bf,Path(__file__),Path(__file__).with_name('oblique_source_fans.py'))}},
            worker_seconds=round(time.monotonic()-tick,3),cumulative_worker_seconds=round(previous_seconds+time.monotonic()-tick,3),selected=False,W5_complete=False,physical_pass=False,
            scope='Conservative whole printedport/band andthreecore breakout boxes vs actualmaterial/centreline clipped into expandedXYprisms, all sampled motion poses. No direct bboxcollision verdict. New sourceflexes/terminalarms/completepaths still OPEN; source root below geometry alone is not acceptance.')
        report.write_text(json.dumps(result,indent=2)+'\n');return result
    try:
        for row in plan['hips']:
            loom=row['loom']
            if sum(r['loom']==loom for r in results)==4:continue
            fixed=copy.deepcopy(next(r for r in ret['changed'] if r['land']['loom']==loom))
            segment=row['fixed_lands'][0]['parts'][0]
            fixed['land'].update(start_world_mm=segment['start'],end_world_mm=segment['end'],
                centre_world_mm=[(a+b)/2 for a,b in zip(segment['start'],segment['end'])],
                axis=row['fixed_tangent_world'])
            port=next(r for g in ports['groups'] if g['id']==fixed['owner'] for r in g['ports'] if r['land_id']==fixed['land']['id'])
            profile=build(fixed['land'],port);zroot=row['fixed_anchor_world_mm'][2]
            blocked=[];witnesses=[]
            for shape in (profile['body'],profile['band']):
                intervals,records=blocks(shape,zroot);blocked+=intervals;witnesses+=records
            for direction in ([1,0,0],[-1,0,0],[0,1,0],[0,-1,0]):
                if any(r['loom']==loom and r['direction']==direction for r in results):continue
                allblocked=list(blocked);allrecords=list(witnesses)
                for core in fan(row,direction):
                    # Expanded actualcurve bounds reserve the whole insulated
                    # core, not an unthickened centreline.
                    curve=P.wire(core['parts']);bb=curve.BoundBox
                    shape=P.box([bb.XMin-1.25,bb.YMin-1.25,bb.ZMin-1.25,bb.XMax+1.25,bb.YMax+1.25,bb.ZMax+1.25])
                    intervals,records=blocks(shape,zroot);allblocked+=intervals;allrecords+=records
                allowed=subtract(DOMAIN,allblocked)
                results.append(dict(loom=loom,direction=direction,allowed_root_Z_mm=allowed,blocked=allrecords))
                save('PARTIAL_ALL_MATERIAL_FIXED_PORT_DOMAIN_ALLOCATION')
            print('fixedport domains',loom,'queries',queries,'seconds',round(time.monotonic()-tick,3),flush=True)
    except (AssertionError,ValueError) as e:
        result=save('ALLOCATION_INCOMPLETE_NO_GEOMETRIC_IMPOSSIBILITY_VERDICT');result['error']=str(e)
        report.write_text(json.dumps(result,indent=2)+'\n');print(str(e),flush=True);return
    domains={r['loom']:[s for s in results if s['loom']==r['loom']] for r in plan['hips']};choices=[]
    for combination in itertools.product(*domains.values()):
        common=DOMAIN
        for row in combination:common=intersect(common,row['allowed_root_Z_mm'])
        for lo,hi in common:
            z=math.floor(hi-1)
            if z>=lo+1:choices.append(dict(root_Z_mm=z,allowed_interval_mm=[lo,hi],directions=[dict(loom=r['loom'],direction=r['direction']) for r in combination]))
    result=save('SHARED_FIXED_PORT_DOMAINS_READY_FLEX_AND_ARMS_OPEN' if choices else 'CONSERVATIVE_DOMAINS_UNRESOLVED_ACTUAL_SECTIONS_REQUIRED_NOT_IMPOSSIBLE')
    result['shared_choices']=sorted(choices,key=lambda r:r['root_Z_mm'],reverse=True)
    report.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],choices=len(choices),best=choices[:1],queries=queries,worker_seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--math-plan',default='body-low-hip-rail-exit-plan.json');parser.add_argument('--output',default='body-fixed-port-vertical-space.json')
    args=parser.parse_args();run(args.math_plan,args.output)
