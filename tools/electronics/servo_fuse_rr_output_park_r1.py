"""Coupled RR housing withdrawal/parking, without stretching either wire.

With BOTH cages open, slide the connector12mm west: the11mm bare ends
leave its east-facing mouths while all insulated wire routes stay fixed.
Carry the electrically free housing in a west service pocket of the same
bank, held by one replacement/spare tie. Test floor, matching casing, full
slide and parked housing/tie jointly before exporting any changed CAD.
These are prototype motion allowances, not measured cage/latch mechanics.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,math,sys,re
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-rr-output-park-r1'

def main():
    import FreeCAD as A
    import Part
    start=datetime.now(timezone.utc)
    loader=ROOT/'tools/electronics/servo_fuse_rr_clip_approach_r1.py'
    code=loader.read_text(encoding='utf-8');code=code[:code.index('    # These boxes are exactly')]
    code=code.replace('servo-fuse-rr-clip-approach-r1','servo-fuse-rr-output-park-r1')+'    return owners,pins,final\n'
    ns=dict(__file__=str(loader),__name__='owner_only');exec(compile(code,str(loader),'exec'),ns)
    original,pins,_=ns['main']();pins[loader.relative_to(ROOT).as_posix()]=sha(loader)
    def load(p):pins[p.relative_to(ROOT).as_posix()]=sha(p);return Part.read(str(p))
    def read(p):pins[p.relative_to(ROOT).as_posix()]=sha(p);return json.loads(p.read_text(encoding='utf-8'))
    def box(b):return Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
    def bounds(s):return [getattr(s.BoundBox,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]
    service=read(ROOT/'hardware/electronics/full-cat/servo-fuse-rr-output-service-receive-r6/checks.json')
    assert not service['hits'] and not service['errors']
    for row in service['exports']:
        gp=ROOT/row['file'];pins[gp.relative_to(ROOT).as_posix()]=sha(gp)
        tag='BankRight' if row['final']=='RROutputServiceFinished' else 'Cover'
        key='Bank/RightClipAccessFinished_WORLD' if tag=='BankRight' else 'ModifiableCover'
        original[key]=load(gp.parent/(tag+'_WORLD.brep'))
    floor_b=[-80,-97.8,109.35,-65,-84.2,111.75]
    stop_b=[-70,-95.2,111.75,-67.3,-86.65,114.95]
    cover_b=[-80.2,-111,109.15,-48.6,-84,130.2]
    floor=box(floor_b);stop=box(stop_b);cover_tool=box(cover_b)
    # One service-only spare tie, not an additional installed circuit restraint.
    x=-75.5;ya=-96.2;yb=-85.65;za=107.85;zt=124.75
    tie_boxes=[[x-1.25,ya,za,x+1.25,yb,za+1.2],[x-1.25,ya,za,x+1.25,ya+1.2,zt+1.2],
               [x-1.25,yb-1.2,za,x+1.25,yb,zt+1.2],[x-1.25,ya,zt,x+1.25,yb,zt+1.2],
               [x-2.25,ya-4.8,zt-3.5,x+2.25,ya,zt]]
    ties=[box(b) for b in tie_boxes]
    slot_boxes=[[b[0]-.15,b[1]-.15,b[2]-.15,b[3]+.15,b[4]+.15,b[5]+.15] for b in tie_boxes]
    slot_tools=[box(b) for b in slot_boxes];slot=slot_tools[0].multiFuse(slot_tools[1:])
    bank=original['Bank/RightClipAccessFinished_WORLD'].cut(stop).fuse(floor).cut(slot)
    cover=original['ModifiableCover'].cut(cover_tool)
    assert bank.isValid() and len(bank.Solids)==1 and cover.isValid() and len(cover.Solids)==1
    owners=dict(original);owners['Bank/RightClipAccessFinished_WORLD']=bank;owners['ModifiableCover']=cover
    cage=owners.pop('W053/221412');removed=[]
    for key in list(owners):
        if key.startswith('CurrentRear/RR') or re.fullmatch(r'R11/F_(FL|FR|RL|RR)[123]_(ATO_)?DESIGN',key):
            removed.append(key);del owners[key]
    assert len(removed)==39 # 24bodies/ATOs, 15faces of3released straps
    park=cage.copy();park.translate(A.Vector(-12,0,0));b=bounds(cage)
    slide=box([b[0]-12,b[1],b[2],b[3],b[4],b[5]])
    hits=[];errors=[];pairs=0
    def check(phase,name,s,key,t):
        nonlocal pairs
        if not s.BoundBox.intersect(t.BoundBox):return
        pairs+=1
        try:
            c=s.common(t)
            if c.Volume>1e-5:
                hits.append(dict(phase=phase,part=name,owner=key,mm3=c.Volume,bounds_mm=bounds(c)))
                c.exportBrep(str(OUT/f'HIT_{len(hits)}.brep'))
        except Exception as e:errors.append(dict(phase=phase,part=name,owner=key,error=str(e)))
    # Static added stock must fit normal installed assembly, not just service.
    for key,t in original.items():
        if key=='Bank/RightClipAccessFinished_WORLD':continue # native own union
        if key=='ModifiableCover':t=cover
        check('installed_added_floor','RRServiceFloor',floor,key,t)
    for key,t in owners.items():check('housing_withdrawal','RRHousingSlide12',slide,key,t)
    for k,s in enumerate(ties):
        for key,t in owners.items():check('service_only_tie',f'RRPARK{k}',s,key,t)
        check('service_only_tie',f'RRPARK{k}',s,'parkedHousing',park)
    # Nominal wire-to-mouth clearance: stripped lengths11mm versus12mm
    # connector displacement; unchanged insulated ends remain atX=-49.
    assert abs(cage.BoundBox.XMax+49)<1e-6 and abs(park.BoundBox.XMax+61)<1e-6
    for n,s in [('BankRight',bank),('Cover',cover),('HousingSlide',slide),('HousingParked',park),('NewFloor',floor)]:s.exportBrep(str(OUT/(n+'_DESIGN.brep')))
    for k,s in enumerate(ties):s.exportBrep(str(OUT/f'ParkingTie{k}_DESIGN.brep'))
    for k,s in enumerate(slot_tools):s.exportBrep(str(OUT/f'ParkingSlot{k}_TOOL.brep'))
    save(OUT/'checks.json',dict(status='RR_PARK_COUPLED_CONFLICTS' if hits or errors else 'RR_PARK_COUPLED_PREFLIGHT_CLEAR_NATIVE_PENDING',
        selected=False,physical_pass=False,W5_complete=False,hits=hits,errors=errors,pairs=pairs,
        floor_bounds_mm=floor_b,stop_opening_mm=stop_b,cover_opening_mm=cover_b,slot_boxes_mm=slot_boxes,
        withdrawal_mm=12,supplier_strip_mm=11,axial_free_gap_mm=1,wire_paths_changed=False,
        part_ownership='FreedRRhousing carried by right bank in temporary service pocket; both wires stay stationary.',
        removed_before_slide=removed,service_tie=dict(SKU='111-02370',installed_normal=0,required_spare_for_removal=1,
            PROJECT_length_with_insertion_mm=2*((yb-ya)+(zt-za))+15,head_bounds_mm=tie_boxes[-1]),
        sequence='Battery absent; remove12ATOs/mini holders, cut3RRstraps, open both outward cages with PROJECT90degree lever allowance. Slide housing west12mm off stationary11mm bare ends; hold in service pocket with1spareT18I before common bank+Cover lift.',
        actual_cage_action_qualified=False,common_bank_lift_qualified=False,
        source_sha256=pins,script_sha256=sha(Path(__file__)),started_utc=start.isoformat(),finished_utc=datetime.now(timezone.utc).isoformat(),
        worker_wall_seconds=(datetime.now(timezone.utc)-start).total_seconds()))
    print('RR_PARK_PREFLIGHT',json.dumps(dict(pairs=pairs,hits=hits,errors=errors)),flush=True)
if __name__=='__main__':main()
