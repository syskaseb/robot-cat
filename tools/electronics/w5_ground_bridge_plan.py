"""A facing central ground pair with a short straight bridge.

G2 rotates in its unchanged body envelope. G1 logical .3/.5 exchange only
their physical cages on the same common ground block. Native mounts open.
"""
from datetime import datetime, timezone
import json, re
from pathlib import Path
from servo_fuse_inputs_r1 import save, sha
from w5_ground_joint_layout_r4 import ROOT, ports as received_ports, attached_ends
from w5_ground_network_plan import profile
from w5_s1_source_layout_r2 import CentreLine
from w5_s1_source_layout_r1 import add, mul

OUT=ROOT/'hardware/electronics/full-cat/w5-ground-facing-plan-r1'

def ports():
    p=received_ports()
    for name,row in p.items():
        if name.startswith('G2.'):
            x,y,z=row['point_mm'];row['point_mm']=[222-x,11-y,z];row['outward_axis']=[-1,0,0]
    p['G1.3'],p['G1.5']=p['G1.5'],p['G1.3']
    assert p['G1.5']['point_mm'][1:]==p['G2.1']['point_mm'][1:]
    return p

def main():
    import FreeCAD as A, Part
    from w5_ground_entries_r1 import owners,RECEIVED
    from w5_exact_separation import separated
    begin=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists()
    graph=ROOT/'hardware/electronics/power-platform/wiring-p0.json'
    ends=attached_ends(json.loads(graph.read_text(encoding='utf-8')));datums=ports()
    fixed,pins=owners(A,Part,json.loads(RECEIVED.read_text(encoding='utf-8')))
    obligations={}; affected={r['wire'] for r in ends}
    for key in list(fixed):
        if key.startswith(('ReceivedD/','ReceivedV/','R53BUS/G2shared/')) or any(re.search(r'(?<![A-Za-z0-9])'+re.escape(w)+r'(?![A-Za-z0-9])',key) for w in affected):
            obligations[key]='Whole affected interface requires replacement and final verification'
            del fixed[key]
    results=[]; errors=[]
    printed={'SourceDeck','SourceCarrier','SourceCover','SourcePlatform','SourceBankLeft','BankRight','SourceWestHood','SourceEastHood'}
    def check(label,shape,own_blocks=()):
        hits=[];changes=[]
        for owner,other in fixed.items():
            if owner in own_blocks or not shape.BoundBox.intersect(other.BoundBox):continue
            if owner in printed:
                changes.append(dict(owner=owner,bounds_overlap_only=True));continue
            try:
                vol=sum(a.common(b).Volume for a in shape.Solids for b in other.Solids
                    if a.BoundBox.intersect(b.BoundBox) and not separated(a,b))
                if vol>1e-6:hits.append(dict(owner=owner,volume_mm3=vol))
            except Exception as e: errors.append(dict(label=label,owner=owner,error=str(e)))
        return dict(label=label,contacts=hits,native_changes_pending=changes)
    a=A.Vector(*datums['G1.5']['point_mm']);b=A.Vector(*datums['G2.1']['point_mm'])
    bridge=Part.makeCylinder(2.1,(b-a).Length,a,(b-a))
    bridge.exportBrep(str(OUT/'W061_BRIDGE_WORLD.brep'))
    results.append(dict(**check('W061_straight_bridge',bridge,('G1_NEW_BODY','G2_NEW_BODY')),
        external_length_mm=(b-a).Length,strip_allowance_mm=25,trial_blank_mm=80,
        selected=False,start=list(a),end=list(b)))
    for row in ends:
        if row['end'] not in ('G1.3','G2.2','G2.3','G2.4','G2.5'):continue
        p=datums[row['end']];u=p['outward_axis'];side=[-u[1],u[0],0];radius=profile(row['wire'])['radius_mm']
        for direction,n in [('up',[0,0,1]),('down',[0,0,-1]),('left',side),('right',mul(side,-1))]:
            c=CentreLine(p['point_mm'],u);c.line(add(c.p,mul(u,6)));c.arc(n,radius=radius);c.line(add(c.p,mul(c.t,6)))
            parts=[]
            for e in c.edges:
                edge=Part.makeLine(A.Vector(*e['start']),A.Vector(*e['end'])) if e['kind']=='line' else Part.Arc(A.Vector(*e['start']),A.Vector(*e['mid']),A.Vector(*e['end'])).toShape()
                section=Part.Wire([Part.makeCircle(profile(row['wire'])['OD_mm']/2,edge.valueAt(edge.FirstParameter),edge.tangentAt(edge.FirstParameter))])
                parts.append(Part.Wire([edge]).makePipeShell([section],True,False))
            shape=Part.makeCompound(parts)
            q=check(row['end']+'/'+direction,shape,(row['end'].split('.')[0]+'_NEW_BODY',))
            bridge_vol=sum(s.common(bridge).Volume for s in shape.Solids if s.BoundBox.intersect(bridge.BoundBox))
            if bridge_vol>1e-6:q['contacts'].append(dict(owner='NEW_W061',volume_mm3=bridge_vol))
            q.update(wire=row['wire'],end=row['end'],direction=direction,edges=c.edges,tip=c.p,tangent=c.t)
            results.append(q)
            print('FACING',q['label'],len(q['contacts']),flush=True)
    finish=datetime.now(timezone.utc)
    pins.extend((Path(__file__),graph,RECEIVED,ROOT/'tools/electronics/w5_ground_joint_layout_r4.py',ROOT/'tools/electronics/w5_ground_network_plan.py'))
    save(OUT/'checks.json',dict(status='FACING_PAIR_PLAN_NOT_SELECTED',ports=datums,results=results,errors=errors,
        mapping_changes={'G1':'exchange physical cages of logical .3 and .5, same potential','G2':'rotate180 about111/5.5; same envelope'},
        replacement_obligations=obligations,all_mutual_prefixes_checked=False,full_routes_ready=False,
        native_mounts_ready=False,selected=False,W5_complete=False,physical_pass=False,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in dict.fromkeys(pins)},
        files={str((OUT/'W061_BRIDGE_WORLD.brep').relative_to(ROOT)):sha(OUT/'W061_BRIDGE_WORLD.brep')},
        started_utc=begin.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-begin).total_seconds()))

if __name__=='__main__':main()
