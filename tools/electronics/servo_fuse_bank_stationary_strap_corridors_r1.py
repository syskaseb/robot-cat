"""One common bottom-open service fringe for fixed MTA/cage straps.

Do not relocate wires or silently remove fixed tie heads from the owner set.
Use complete small strap bounds over the whole100mm relative withdrawal,
then preserve four washer-bearing regions and every part as one solid.
These are preflight shapes; editable native counterparts are still required.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-bank-stationary-strap-corridors-r1'

def receive():
    p=ROOT/'tools/electronics/servo_fuse_bank_fixed_rr_lift_r6.py'
    ns=dict(__file__=str(p),__name__='current_released_owner_definition')
    exec(compile(p.read_text(encoding='utf-8'),str(p),'exec'),ns)
    code=ns['code'];code=code[:code.index("    save(OUT/'owner-census.json'")]
    code=code.replace('servo-fuse-bank-fixed-rr-lift-r6','servo-fuse-bank-stationary-strap-corridors-r1')+'    return owners,module,pins\n'
    ctx=dict(__file__=str(p),__name__='owner_receive_only')
    exec(compile(code,str(p),'exec'),ctx)
    owners,module,pins=ctx['main']();pins[p.relative_to(ROOT).as_posix()]=sha(p)
    return owners,module,pins

def main():
    import FreeCAD as A
    import Part
    start=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists()
    print('STRAP_CORRIDORS_LOAD_CURRENT',flush=True)
    owners,module,pins=receive()
    def bounds(s):return [getattr(s.BoundBox,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]
    def box(b):return Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
    parts={k:v for k,v in module.items() if k in ('BankRight','BankLeft','Cover')}
    allowance=.25;rows=[];tools={k:[] for k in parts};checked=[]
    for key,s in owners.items():
        if not (key.startswith(('BodyTie/','FRNewTie/','CurrentRear/')) and 'Tie' in key):continue
        b=bounds(s);checked.append(key)
        for tag,part in parts.items():
            low=min(part.BoundBox.ZMin-.1,b[2]-100-allowance)
            tb=[b[0]-allowance,b[1]-allowance,low,b[3]+allowance,b[4]+allowance,b[5]+allowance]
            tool=box(tb)
            if not tool.BoundBox.intersect(part.BoundBox):continue
            hit=part.common(tool).Volume
            if hit<=1e-5:continue
            tools[tag].append(tool)
            rows.append(dict(part=tag,owner=key,source_bounds_mm=b,tool_mm=tb,removed_preunion_mm3=hit,
                continuous_relative_translation_mm=100,includes_bounded_whole_strap=True))
            print('STRAP_SERVICE_CORRIDOR',tag,key,hit,flush=True)
    assert any(r['owner']=='CurrentRear/RLHousingTieHead_DESIGN' and r['part']=='BankLeft' for r in rows)
    changed={};counts={};bearing=[]
    axes=[(-60,-108.5),(128,-92.5),(-63,92.5),(128,92.5)]
    for tag,part in parts.items():
        if tools[tag]:
            union=tools[tag][0].multiFuse(tools[tag][1:]) if len(tools[tag])>1 else tools[tag][0]
            union.exportBrep(str(OUT/(tag+'_SERVICE_TOOL.brep')))
            changed[tag]=part.cut(union)
        else:changed[tag]=part.copy()
        q=changed[tag];strict=q.check(True) or []
        counts[tag]=dict(valid=q.isValid(),solids=len(q.Solids),strict_BOP_errors=[str(v) for v in strict],
            removed_mm3=part.Volume-q.Volume,bounds_mm=bounds(q))
        q.exportBrep(str(OUT/(tag+'_CANDIDATE.brep')))
        if tag!='Cover':
            for x,y in axes:
                ring=Part.makeCylinder(2.5,4,A.Vector(x,y,109)).cut(Part.makeCylinder(1.2,4.1,A.Vector(x,y,108.95)))
                before=ring.common(part).Volume
                if before<1e-5:continue
                after=ring.common(q).Volume
                bearing.append(dict(part=tag,xy_mm=[x,y],before_mm3=before,after_mm3=after,preserved=abs(after-before)<1e-5))
    good=all(r['valid'] and r['solids']==1 and not r['strict_BOP_errors'] for r in counts.values()) and all(r['preserved'] for r in bearing)
    end=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='COMMON_STRAP_SERVICE_FRINGE_PREFLIGHT_CLEAR_NATIVE_OPEN' if good else 'COMMON_STRAP_SERVICE_FRINGE_REJECTED_STRUCTURE',
        selected=False,physical_pass=False,W5_complete=False,allowance_mm=allowance,checked_fixed_strap_pieces=checked,
        corridor_boxes=rows,part_counts=counts,bearing_checks=bearing,mounts_preserved=all(r['preserved'] for r in bearing),
        routes_unchanged=True,ties_unchanged=True,added_parts=0,whole_module_release_qualified=False,
        source_sha256=pins,script_sha256=sha(Path(__file__)),started_utc=start.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-start).total_seconds()))
    print('STRAP_CORRIDORS_RESULT',json.dumps(dict(good=good,tools=len(rows),counts=counts,bearing=bearing)),flush=True)

if __name__=='__main__':main()
