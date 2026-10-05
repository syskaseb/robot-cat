"""One four-block upper ground allocation with all sixteen attached exits.

Keep central facing plan and bank; move the four leg ground connectors as a
single carrier-mounted family above the crowded bank inputs. Four body boxes
are conservative purchased reservations, not native printed support geometry.
"""
from datetime import datetime,timezone
from pathlib import Path
import json,re
from servo_fuse_inputs_r1 import save,sha
from w5_ground_joint_layout_r4 import ROOT,attached_ends
from w5_ground_joint_layout_r1 import BLOCKS
from w5_ground_network_plan import profile
from w5_s1_source_layout_r2 import CentreLine
from w5_s1_source_layout_r1 import add,mul

OUT=ROOT/'hardware/electronics/full-cat/w5-leg-ground-upper-rail-r1'

def layout():
    graph=ROOT/'hardware/electronics/power-platform/wiring-p0.json'
    rows=[]; bodies={}
    for block in ('FL_G','FR_G','RL_G','RR_G'):
        front=block.startswith('F');side=1 if block[1]=='L' else -1
        cx=-65 if front else 115;cy=side*72;u=-1 if front else 1
        bodies[block]=[cx-9.5,cy-15,165,cx+9.5,cy+15,174]
        for row in attached_ends(json.loads(graph.read_text(encoding='utf-8'))):
            if not row['end'].startswith(block+'.'):continue
            label=int(row['end'].split('.')[-1]);idx=BLOCKS[block]['labels'].index(label)
            row['point_mm']=[cx+u*9.5,cy+(idx-2)*6,169.5]
            row['outward_axis']=[u,0,0]
            c=CentreLine(row['point_mm'],row['outward_axis']);c.line(add(c.p,mul(c.t,6)))
            c.arc([0,0,1],radius=profile(row['wire'])['radius_mm']);c.line(add(c.p,mul(c.t,6)))
            rows.append(dict(**row,edges=c.edges,tip=c.p,tangent=c.t))
    assert len(rows)==16
    return bodies,rows

def main():
    import FreeCAD as A,Part
    from w5_ground_entries_r1 import owners,RECEIVED
    from w5_exact_separation import separated
    begin=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists()
    bodies,rows=layout();fixed,pins=owners(A,Part,json.loads(RECEIVED.read_text(encoding='utf-8')))
    graph=ROOT/'hardware/electronics/power-platform/wiring-p0.json'
    affected={r['wire'] for r in attached_ends(json.loads(graph.read_text(encoding='utf-8')))}
    omitted=[]
    for k in list(fixed):
        if k.startswith(('ReceivedD/','ReceivedV/','R53BUS/G2shared/')) or k in {n+'_NEW_BODY' for n in bodies} or any(re.search(r'(?<![A-Za-z0-9])'+re.escape(w)+r'(?![A-Za-z0-9])',k) for w in affected):
            omitted.append(k);del fixed[k]
    central=ROOT/'hardware/electronics/full-cat/w5-central-ground-routes-r2'
    for wire in ('W001','W003'):
        p=central/(wire+'_WORLD.brep');fixed['NEW/'+wire]=Part.read(str(p));pins.append(p)
    p=ROOT/'hardware/electronics/full-cat/w5-ground-facing-plan-r1/W061_BRIDGE_WORLD.brep'
    fixed['NEW/W061']=Part.read(str(p));pins.append(p)
    built={}; files=[];hits=[];native=[];errors=[]
    for name,b in bodies.items():built[name+'_BODY']=Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
    for row in rows:
        parts=[]
        for e in row['edges']:
            edge=Part.makeLine(A.Vector(*e['start']),A.Vector(*e['end'])) if e['kind']=='line' else Part.Arc(A.Vector(*e['start']),A.Vector(*e['mid']),A.Vector(*e['end'])).toShape()
            section=Part.Wire([Part.makeCircle(profile(row['wire'])['OD_mm']/2,edge.valueAt(edge.FirstParameter),edge.tangentAt(edge.FirstParameter))])
            parts.append(Part.Wire([edge]).makePipeShell([section],True,False))
        built[row['end']]=Part.makeCompound(parts)
    printed={'SourceDeck','SourceCarrier','SourceCover','SourcePlatform','SourceBankLeft','BankRight','SourceWestHood','SourceEastHood'}
    for idx,(key,shape) in enumerate(built.items()):
        for owner,other in [*fixed.items(),*list(built.items())[:idx]]:
            if owner==key.split('.')[0]+'_BODY' or not shape.BoundBox.intersect(other.BoundBox):continue
            if owner in printed:
                native.append(dict(candidate=key,owner=owner,bounds_overlap_only=True));continue
            try:
                vol=sum(a.common(b).Volume for a in shape.Solids for b in other.Solids if a.BoundBox.intersect(b.BoundBox) and not separated(a,b))
                if vol>1e-6:hits.append(dict(candidate=key,owner=owner,volume_mm3=vol))
            except Exception as e:errors.append(dict(candidate=key,owner=owner,error=str(e)))
        p=OUT/(key.replace('.','_')+'_WORLD.brep');shape.exportBrep(str(p));files.append(p)
    finish=datetime.now(timezone.utc)
    pins.extend((Path(__file__),graph,RECEIVED,ROOT/'tools/electronics/w5_ground_network_plan.py',ROOT/'tools/electronics/w5_ground_joint_layout_r1.py',ROOT/'tools/electronics/w5_ground_joint_layout_r4.py'))
    save(OUT/'checks.json',dict(status='FOUR_UPPER_BLOCKS_AND_16_EXITS_UNSELECTED',bodies=bodies,ends=rows,
        hits=hits,errors=errors,native_changes_pending=native,replacement_obligations=omitted,
        native_rail_ready=False,full_routes_ready=False,selected=False,W5_complete=False,physical_pass=False,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in dict.fromkeys(pins)},files={p.relative_to(ROOT).as_posix():sha(p) for p in files},
        started_utc=begin.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-begin).total_seconds()))
    print('UPPER_RAIL',len(hits),len(errors),len(native),flush=True)

if __name__=='__main__':main()
