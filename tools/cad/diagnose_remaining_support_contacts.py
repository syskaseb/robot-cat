"""Localize received new-support contacts; no geometry changes or new gate."""
import json,time
from pathlib import Path
import FreeCAD as A
import Part
import build_remaining_loom_supports as G
P=G.P

def run():
    tick=time.monotonic();file=P.OUT/'remaining-support-material.json'
    received=json.loads(file.read_text());paths=json.loads((P.OUT/'remaining-support-final-paths.json').read_text())
    axes=json.loads((P.ROOT/'hardware/simulation/p0/e6-leg-compatibility.json').read_text())['axes']
    cache={}
    for f in (P.OUT/'remaining-support-cache').glob('*/manifest.json'):
        d=json.loads(f.read_text());name=d['contract']['group']['id']
        current=next((r for r in paths['groups'] if r['id']==name),None)
        if current==d['contract']['paths']:
            assert name not in cache,'Ambiguous candidate cache'
            cache[name]=(f,d)
    rows=[];seen=set()
    for contact in received['contacts']:
        name=contact['group'];other=contact['target'].removeprefix('NewSupport_')
        if not contact['target'].startswith('NewSupport_'):continue
        identity=tuple(sorted(((name,tuple(contact['pose'][:2])),(other,tuple(contact['other_pose'][:2])))))
        if identity in seen:continue
        seen.add(identity)
        def actual(key,pose):
            f,d=cache[key];r=d['shapes'][key];bf=f.parent/r['file'];assert P.SHA(bf)==r['sha256']
            s=Part.Shape();s.read(str(bf));owner=d['contract']['group']['owner_stage']
            t=A.Placement() if owner=='Body' else G.transform(axes,owner.split('_')[1],*pose[:2],owner.split('_')[2])
            return G.moved(s,t),t,d['recipes'][key]
        s,st,sr=actual(name,contact['pose']);t,tt,tr=actual(other,contact['other_pose'])
        start=time.monotonic();w=s.common(t);duration=time.monotonic()-start
        assert w.isValid(),(name,'Invalid full-part witness')
        # The gate checks added material. Full-part localization can also
        # expose an inherited-parent interface; never label that identical.
        same=abs(w.Volume-contact['volume_mm3'])<1e-4
        fragments=[]
        for key,recipe,transform in ((name,sr,st),(other,tr,tt)):
            hits=[]
            for pad in recipe['pads']:
                p=G.moved(G.oriented(pad['bounds_mm'],pad.get('placement')),transform)
                if not p.BoundBox.intersect(w.BoundBox):continue
                c=p.common(w)
                if not c.isNull() and c.Volume>1e-6:hits.append(dict(name=pad['name'],bounds_mm=pad['bounds_mm'],witness_overlap_mm3=c.Volume))
            fragments.append(dict(group=key,pads=hits))
        b=w.BoundBox
        rows.append(dict(received_contact=contact,full_part_volume_mm3=w.Volume,
            matches_received_added_material_volume=same,
            exact_common_seconds=round(duration,4),witness_bounds_mm=[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax],fragments=fragments))
    result=dict(status='RECEIVED_CONTACT_DIAGNOSIS_NO_REDESIGN',contacts=rows,
        received_gate_sha256=P.SHA(file),worker_seconds=round(time.monotonic()-tick,3),
        geometry_changed=False,acceptance=False,physical_pass=False)
    (P.OUT/'remaining-support-contact-diagnosis.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)
if __name__=='__main__':run()
