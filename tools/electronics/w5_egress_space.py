"""Bounded joint egress-space survey before another complete routing layout.

Four orthogonal bend planes per connected cage, one fixed straight grip and
catalogue/provisional radius. No position search, selected path or native part.
Old affected wires/mounts remain explicit replacement obligations.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, re
from servo_fuse_inputs_r1 import save, sha
from w5_ground_network_plan import profile
from w5_ground_joint_layout_r4 import attached_ends, ROOT
from w5_s1_source_layout_r2 import CentreLine
from w5_s1_source_layout_r1 import add, mul

OUT=ROOT/'hardware/electronics/full-cat/w5-space-plan-inputs-r1'

def main():
    import FreeCAD as A, Part
    from w5_ground_entries_r1 import owners, RECEIVED
    from w5_exact_separation import separated
    begin=datetime.now(timezone.utc)
    target=OUT/'egress.json'; assert not target.exists()
    graph_path=ROOT/'hardware/electronics/power-platform/wiring-p0.json'
    ends=attached_ends(json.loads(graph_path.read_text(encoding='utf-8')))
    fixed,pins=owners(A,Part,json.loads(RECEIVED.read_text(encoding='utf-8')))
    affected={r['wire'] for r in ends}
    obligations={}
    for k in list(fixed):
        if k.startswith(('ReceivedD/','ReceivedV/')) or any(re.search(r'(?<![A-Za-z0-9])'+re.escape(w)+r'(?![A-Za-z0-9])',k) for w in affected):
            obligations[k]='Complete changed wire/mount must be supplied and checked jointly'
            del fixed[k]
    printed={'SourceDeck','SourceCarrier','SourceCover','SourcePlatform','SourceBankLeft','BankRight','SourceWestHood','SourceEastHood'}
    results=[]; errors=[]; count=0
    for row in ends:
        u=row['outward_axis']; sideways=[-u[1],u[0],0]
        options=[]
        for name,n in [('up',[0,0,1]),('down',[0,0,-1]),('left',sideways),('right',mul(sideways,-1))]:
            p=profile(row['wire']); c=CentreLine(row['point_mm'],u)
            c.line(add(c.p,mul(c.t,6))); c.arc(n,radius=p['radius_mm']); c.line(add(c.p,mul(c.t,6)))
            bits=[]
            for edge in c.edges:
                e=Part.makeLine(A.Vector(*edge['start']),A.Vector(*edge['end'])) if edge['kind']=='line' else Part.Arc(A.Vector(*edge['start']),A.Vector(*edge['mid']),A.Vector(*edge['end'])).toShape()
                section=Part.Wire([Part.makeCircle(p['OD_mm']/2,e.valueAt(e.FirstParameter),e.tangentAt(e.FirstParameter))])
                bits.append(Part.Wire([e]).makePipeShell([section],True,False))
            shape=Part.makeCompound(bits); hits=[]; changes=[]
            for owner,obstacle in fixed.items():
                if owner==row['end'].split('.')[0]+'_NEW_BODY': continue
                if not shape.BoundBox.intersect(obstacle.BoundBox):continue
                if owner in printed:
                    changes.append(dict(owner=owner,bounds_overlap_only=True,exact_native_check_pending=True))
                    continue
                try:
                    volume=0
                    for a in shape.Solids:
                        for b in obstacle.Solids:
                            if a.BoundBox.intersect(b.BoundBox) and not separated(a,b):
                                volume+=a.common(b).Volume
                    if volume>1e-6:
                        hits.append(dict(owner=owner,volume_mm3=volume))
                except Exception as exc:errors.append(dict(end=row['end'],option=name,owner=owner,error=str(exc)))
            options.append(dict(direction=name,edges=c.edges,tip_mm=c.p,tangent=c.t,
                radius_mm=p['radius_mm'],insulated_grip_mm=6,fixed_contacts=hits,printed_changes=changes))
            count+=1
        results.append(dict(wire=row['wire'],end=row['end'],options=options))
        save(OUT/'egress-progress.json',dict(ends_done=len(results),options_checked=count,errors=errors))
        print('EGRESS',row['end'],row['wire'],[(x['direction'],len(x['fixed_contacts'])) for x in options],flush=True)
    finish=datetime.now(timezone.utc)
    pins.extend((graph_path,RECEIVED,Path(__file__),ROOT/'tools/electronics/w5_ground_network_plan.py',ROOT/'tools/electronics/w5_ground_joint_layout_r4.py'))
    save(target,dict(status='EGRESS_CONSTRAINTS_ONLY_FULL_JOINT_PATHS_AND_GRIPS_OPEN',rows=results,
        replacement_obligations=obligations,errors=errors,mutual_egress_checks_complete=False,
        route_cad_selected=False,W5_complete=False,physical_pass=False,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in dict.fromkeys(pins)},
        started_utc=begin.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-begin).total_seconds()))
    print('EGRESS_COMPLETE',len(results),len(errors),flush=True)

if __name__=='__main__':main()
