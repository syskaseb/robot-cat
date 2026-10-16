"""Read-only selected STL topology and printer-volume preflight, stdlib only."""
import json,math,re,struct,time
from array import array
from collections import defaultdict
from pathlib import Path
from plan_current_harness_interfaces import ROOT,BASE,SHA
from current_work_guard import check


def triangles(raw):
    if len(raw)>=84:
        n=struct.unpack_from('<I',raw,80)[0]
        if len(raw)==84+50*n:
            for i in range(n):
                v=struct.unpack_from('<12f',raw,84+50*i)
                yield (v[3:6],v[6:9],v[9:12])
            return
    text=raw.decode('ascii');v=[tuple(map(float,m)) for m in re.findall(r'\bvertex\s+([-+\deE.]+)\s+([-+\deE.]+)\s+([-+\deE.]+)',text)]
    assert v and len(v)%3==0,'Malformed ASCII STL'
    for i in range(0,len(v),3):yield tuple(v[i:i+3])


def inspect(raw):
    lo=[math.inf]*3;hi=[-math.inf]*3;edges={};parent=array('i');degenerate=0
    def find(i):
        while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
        return i
    count=0
    for tri in triangles(raw):
        parent.append(count)
        points=[tuple(round(x,6) for x in p) for p in tri]
        if len(set(points))<3:degenerate+=1
        for p in tri:
            assert all(math.isfinite(x) for x in p)
            lo=[min(x,y) for x,y in zip(lo,p)];hi=[max(x,y) for x,y in zip(hi,p)]
        for a,b in zip(points,points[1:]+points[:1]):
            key=(a,b) if a<b else (b,a)
            if key in edges:
                n,first=edges[key];edges[key]=(n+1,first);aa,bb=find(count),find(first)
                if aa!=bb:parent[aa]=bb
            else:edges[key]=(1,count)
        count+=1
    assert count>0
    boundary=sum(n==1 for n,_ in edges.values());nonmanifold=sum(n>2 for n,_ in edges.values())
    components=len({find(i) for i in range(count)})
    return dict(facets=count,size_mm=[b-a for a,b in zip(lo,hi)],boundary_edges=boundary,nonmanifold_edges=nonmanifold,
        degenerate_vertex_triangles=degenerate,components=components,closed=not boundary and not nonmanifold and not degenerate)


def fit(size,brim=5):
    return size[0]+2*brim<=256 and size[1]+2*brim<=256 and size[2]<=256


def run():
    check();tick=time.monotonic();file=BASE/'phase1-print-set.json';p=json.loads(file.read_text());rows=[];errors=[]
    for r in p['prints']:
        check();f=ROOT/r['path'];assert SHA(f)==r['sha256']
        q=inspect(f.read_bytes());q.update(identity=r['identity'],path=r['path'],sha256=r['sha256'],quantity=r['quantity'],
            brim_each_mm=5,orientation='Exported STL axes, Z up; no slicer/profile/physical strength approval',fits_with_5mm_brim=fit(q['size_mm']))
        if not q['closed'] or q['components']!=1 or not q['fits_with_5mm_brim']:errors.append(r['identity'])
        rows.append(q)
        if len(rows)%10==0:print('STL preflight',len(rows),'of',len(p['prints']),'unresolved',len(errors),flush=True)
    result=dict(status='ALL_SELECTED_PRINT_STLS_CLOSED_SINGLE_COMPONENT_FIT256' if not errors else 'SELECTED_PRINT_STL_PREFLIGHT_OPEN',
        rows=rows,errors=errors,source_sha256={file.relative_to(ROOT).as_posix():SHA(file),Path(__file__).relative_to(ROOT).as_posix():SHA(Path(__file__))},
        worker_seconds=round(time.monotonic()-tick,3),geometry_changed=False,K1_complete=False,physical_pass=False,
        limitations='Float STL topology with1micrometre vertex identity. Not BRep certification, wall/load/slicer/physical fit approval.')
    (BASE/'phase1-print-preflight.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(parts=len(rows),errors=errors,seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':run()
