"""Changed twelve case retainers against the retained operating assembly.

No parking pose is installed. Actual shared geometry accepts contacts; bounding
boxes merely reject distant pairs. Anchor probes accept only exact containment.
"""
import argparse,itertools,json,time,subprocess
from pathlib import Path
import FreeCAD as A
from bank_upper_retained_context import prepare,P
from current_source_retention_context import C
from plan_axial_source_supports import arm_box
from current_work_guard import check


def anchor_candidates(scene):
    result={'UpperCarrier001':[[-56,-22,120],[-56,-22,80],[-56,-22,74.5],
        [80,20,74.5],[120,20,74.5],[80,-20,74.5],[120,-20,74.5]]}
    for r in scene['frame_anchor_metadata']['groups']:
        if min(r['arm_half_widths_world_mm'])<2:continue
        points=[]
        for path in r['paths']:
            for a,b in zip(path['points_mm'],path['points_mm'][1:]):
                points.extend([a,[(x+y)/2 for x,y in zip(a,b)],b])
        result[r['name']]=points
    return {o:list(dict.fromkeys(tuple(p) for p in points)) for o,points in result.items()}


def run(reuse_anchors=None):
    check();tick=time.monotonic();scene=prepare();targets=scene['targets'];wires=scene['wires']
    bounds=C.ImmutableBounds();cache=C.AtomicMaterial(P.OUT/'source-case-retention-pairs.json',bounds.near)
    rows=[];anchors={};errors=[];checks=0
    pins=dict(scene['pins']);pins[Path(__file__).relative_to(P.ROOT).as_posix()]=P.SHA(Path(__file__))
    def save():
        p=dict(status='SOURCE_CASE_OPERATING_PREFLIGHT',parts=rows,anchors=anchors,errors=errors,checks=checks,
            computed_pairs=cache.computed,reused_pairs=cache.reused,worker_seconds=round(time.monotonic()-tick,3),
            source_sha256=pins,selected=False,W5_complete=False,physical_pass=False)
        f=P.OUT/'source-case-retention-space.json';tmp=f.with_suffix('.tmp')
        tmp.write_text(json.dumps(p,indent=2)+'\n');tmp.replace(f);cache.save()
    def hit(a,b,r=0):
        nonlocal checks
        if not bounds.near(a,b,r+.0001):return None
        if r and not b.Solids and len(b.Edges)>1:
            return next((v for e in b.Edges if (v:=hit(a,e,r))),None)
        check();checks+=1;gap,volume=cache.check(a,b,0,r)
        if volume>1e-5 or (r and gap<r-1e-6):return dict(volume_mm3=volume,gap_mm=gap,required_mm=r)
    if reuse_anchors:
        rel=(P.OUT/'source-case-retention-space.json').relative_to(P.ROOT).as_posix()
        old=json.loads(subprocess.check_output(['git','show',reuse_anchors+':'+rel],cwd=P.ROOT))
        assert not old['errors']
        native={n:h for n,h in scene['pins'].items() if n.endswith('.FCStd')}
        assert native and all(old['source_sha256'].get(n)==h for n,h in native.items())
        for n in ('body36-receiver-support-reservations','current-body-native-composition','local-source-retention-native/manifest'):
            f=P.OUT/(n+'.json');key=f.relative_to(P.ROOT).as_posix();assert old['source_sha256'][key]==P.SHA(f)
        anchors.update(old['anchors']);print('inherited exact unchanged native anchors',reuse_anchors,flush=True)
    save()
    for owner,points in ({} if reuse_anchors else anchor_candidates(scene)).items():
        if owner not in scene['parents']:continue
        parent=scene['parents'][owner];anchors[owner]=[]
        for point in points:
            check()
            if not all(parent.isInside(A.Vector(*[x+2*d for x,d in zip(point,sign)]),1e-7,True)
                       for sign in itertools.product((-1,1),repeat=3)):continue
            outside=arm_box(point,point,[2]*3).cut(parent.copy()).Volume
            if outside<1e-5:anchors[owner].append(dict(point_mm=point,outside_mm3=outside))
            save()
        print('case load anchors',owner,len(anchors[owner]),flush=True)
    cases=scene['cases'];ownership={r['id']:r['owner'] for r in cases['rows']}
    for kind,items in [('SourceCase',cases['parts']),('SourceCaseBand',cases['bands']),('SourceCaseAdhesive',cases['adhesive'])]:
        for name,s in items.items():
            full=kind+'/'+name;row=dict(part=full,owner=ownership[name],contacts=[],parent_unions=[]);rows.append(row)
            for n,t in targets.items():
                if n==full or not t.Solids:continue
                v=hit(s,t)
                if not v:continue
                if kind=='SourceCase' and n in scene['owned'][ownership[name]]:
                    row['parent_unions'].append(dict(obstacle=n,**v));continue
                row['contacts'].append(dict(obstacle=n,**v))
            for n,(w,r) in wires.items():
                if (v:=hit(s,w,r+.25)):row['contacts'].append(dict(obstacle=n,**v))
            save();print('source case',full,'contacts',len(row['contacts']),'pairs',checks,flush=True)
    save()


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--reuse-anchors');run(parser.parse_args().reuse_anchors)
