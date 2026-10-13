"""Checkpoint the existing material gate without changing its geometry/checks.

One worker, immutable hashed BReps, frequent exact-pair receipts, and a live
operation/timing record. A partial run never qualifies the whole support set.
"""
import hashlib,json,time,os
from pathlib import Path
import FreeCAD as A
import Part
import build_remaining_loom_supports as G

P=G.P
CACHE=P.OUT/'remaining-support-cache'
TICK=time.monotonic()
ALLOCATE=G.allocation
PAIRS=G.B.PairReceipts

def write(path,data):
    tmp=path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    os.replace(tmp,path)

def digest(data):
    return hashlib.sha256(json.dumps(data,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def fingerprint(s):
    return hashlib.sha256(s.exportBrepToString().encode()).hexdigest()

def cached_allocation(paths,retention,roots,parents):
    CACHE.mkdir(exist_ok=True)
    merged=({},{},{},{},[])
    for group in roots['groups']:
        name=group['id'];parent=parents.get(group.get('preserved_owner'))
        contract=dict(group=group,paths=next(g for g in paths['groups'] if g['id']==name),
            retention=next(g for g in retention['groups'] if g['id']==name),
            parent_sha256=fingerprint(parent) if parent else None,
            source_sha256={n:P.SHA(Path(G.__file__).with_name(n)) for n in
                ('build_remaining_loom_supports.py','support_entry_port.py','loom_land_port.py','compact_loom_land_port.py')})
        folder=CACHE/digest(contract);receipt=folder/'manifest.json'
        started=time.monotonic()
        write(CACHE/'activity.json',dict(operation='allocation',group=name,elapsed_seconds=round(started-TICK,3)))
        if receipt.exists():
            data=json.loads(receipt.read_text());assert data['contract']==contract
            result=({},{},{},{},data['errors'])
            for index,label in ((0,'shapes'),(2,'bands'),(3,'bonds')):
                for key,row in data[label].items():
                    f=folder/row['file'];assert P.SHA(f)==row['sha256']
                    s=Part.Shape();s.read(str(f));assert s.isValid(),key
                    result[index][key]=s
            result[1].update(data['recipes'])
            mode='reused'
        else:
            result=ALLOCATE(paths,retention,dict(roots,groups=[group]),parents)
            folder.mkdir(exist_ok=True)
            data=dict(contract=contract,recipes=result[1],errors=result[4],shapes={},bands={},bonds={})
            for index,label in ((0,'shapes'),(2,'bands'),(3,'bonds')):
                for number,(key,s) in enumerate(result[index].items()):
                    f=folder/(label+str(number)+'.brep');s.exportBrep(str(f))
                    data[label][key]=dict(file=f.name,sha256=P.SHA(f))
            data['build_seconds']=round(time.monotonic()-started,3);write(receipt,data)
            mode='built'
        for i in (0,1,2,3):merged[i].update(result[i])
        merged[4].extend(result[4])
        print('checkpoint allocation',name,mode,round(time.monotonic()-started,3),flush=True)
    return merged

class StreamingPairs(PAIRS):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.slowest=[];self.last_saved=time.monotonic();self.calls=0
        self.last_print=time.monotonic()

    def check(self,s,t,rs=0,rt=0):
        self.calls+=1;start=time.monotonic()
        # Small identity/complexity record is durable BEFORE an OCC call.
        info=dict(operation='exact_pair',call=self.calls,elapsed_seconds=round(start-TICK,3),
            first_faces=len(s.Faces),second_faces=len(t.Faces),first_edges=len(s.Edges),
            second_edges=len(t.Edges),radii=[rs,rt],first_centre=list(s.BoundBox.Center),second_centre=list(t.BoundBox.Center))
        write(CACHE/'activity.json',info)
        answer=super().check(s,t,rs,rt)
        info.update(seconds=round(time.monotonic()-start,4),answer=answer)
        if info['seconds']>.5:self.slowest=sorted(self.slowest+[info],key=lambda r:-r['seconds'])[:12]
        if time.monotonic()-self.last_saved>10 or self.calls%20==0:
            self.save();self.last_saved=time.monotonic()
        if time.monotonic()-self.last_print>30:
            print('exact pair progress',self.calls,'computed',self.computed,'reused',self.reused,'last_seconds',info['seconds'],flush=True)
            self.last_print=time.monotonic()
        return answer

    def save(self):
        # Atomic cache replacement also keeps completed negative results.
        tmp=self.path.with_suffix(self.path.suffix+'.tmp')
        tmp.write_text(json.dumps(dict(checker_sha256=self.revision,records=self.records),separators=(',',':'))+'\n',encoding='utf-8')
        os.replace(tmp,self.path)
        write(CACHE/'timing.json',dict(calls=self.calls,computed=self.computed,reused=self.reused,
            slowest=self.slowest,elapsed_seconds=round(time.monotonic()-TICK,3)))

if __name__=='__main__':
    CACHE.mkdir(exist_ok=True)
    G.allocation=cached_allocation
    G.B.PairReceipts=StreamingPairs
    G.run()
