"""Refine only the hollow Deck's misleading whole-owner bounding box.

Reuse R1's723 pinned owners, no repeat full-owner read. Deck boundary boxes
plus outside-centre screening are conservative; exact Deck distance qualifies
only returned static body candidates. These are not mounted/routed selections.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,math,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-main-space-plan-r2'


def main():
    import FreeCAD as A
    import Part
    started=datetime.now(timezone.utc)
    OUT.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists()
    source=ROOT/'hardware/electronics/full-cat/servo-fuse-main-space-plan-r1/owners.json'
    data=json.loads(source.read_text(encoding='utf-8'))
    pins=dict(data['source_sha256']);pins[source.relative_to(ROOT).as_posix()]=sha(source)
    for rel,h in pins.items():assert sha(ROOT/rel)==h,rel
    deckpath=ROOT/'hardware/cad/studies/servo-fuse-parent-feed-grips-native-r2/Deck_WORLD.brep'
    deck=Part.read(str(deckpath))
    boxes=[(row['id'],row['bounds_mm']) for row in data['owners'] if row['id']!='RetainedDeck']
    def bounds(s):return [getattr(s.BoundBox,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]
    faces=[bounds(f) for f in deck.Faces]
    def intersects(a,b,c=.8):return all(a[i]<b[i+3]+c and a[i+3]>b[i]-c for i in range(3))
    orientations=[('axis_X_upright',[35,16,22]),('axis_X_rolled',[35,22,16]),
                  ('axis_Y_upright',[16,35,22]),('axis_Y_rolled',[22,35,16])]
    candidates=[]
    for label,size in orientations:
        for x in range(-74,119,4):
            for y in range(-84,85,4):
                for bottom in (110,114,118,122):
                    b=[x-size[0]/2,y-size[1]/2,bottom,x+size[0]/2,y+size[1]/2,bottom+size[2]]
                    if b[0]<-94 or b[3]>136 or b[1]<-100 or b[4]>100 or b[5]>139:continue
                    if any(intersects(b,bb) for _,bb in boxes):continue
                    if any(intersects(b,bb) for bb in faces):continue
                    centre=[x,y,bottom+size[2]/2]
                    if deck.isInside(A.Vector(*centre),1e-7,True):continue
                    candidates.append(dict(orientation=label,centre_mm=centre,dimensions_mm=size,bounds_mm=b))
        print('SPACE_ORIENTATION_DONE',label,len(candidates),flush=True)
    exact={};ranked={}
    for leg,x,y in [('FL',-82.5,49.5),('FR',-82.5,-49.5),('RL',25.5,49.5),('RR',25.5,-49.5)]:
        rows=[]
        for row in candidates:
            if row['centre_mm'][1]*y<=0:continue
            b=row['bounds_mm'];axis=0 if row['orientation'].startswith('axis_X') else 1
            for face in (b[axis],b[axis+3]):
                port=list(row['centre_mm']);port[axis]=face
                distance=math.dist(port,[x,y,113.5])
                if distance+21>100:continue
                rows.append(dict(**row,output_face_mm=port,straight_line_lower_bound_mm=distance))
        rows.sort(key=lambda r:r['straight_line_lower_bound_mm'])
        approved=[]
        for row in rows:
            key=tuple(row['bounds_mm'])
            if key not in exact:
                b=row['bounds_mm'];s=Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
                exact[key]=s.distToShape(deck)[0]
            if exact[key]<.8-1e-6:continue
            row.update(exact_Deck_distance_mm=exact[key],other_owner_bbox_clearance_mm=.8,
                source_output_routes_verified=False,native_mount_verified=False,
                cover_may_need_change=intersects(row['bounds_mm'],data['cover_bounds_mm']))
            approved.append(row)
            if len(approved)==24:break
        ranked[leg]=approved
        print('EXACT_DECK_STATIC_CANDIDATES',leg,len(approved),flush=True)
    ended=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='STATIC_BODY_ROOM_FOUND' if all(ranked.values()) else 'SCREEN_INSUFFICIENT_NOT_A_SPACE_BLOCKER',
        selected=False,physical_pass=False,W5_complete=False,candidates_total=len(candidates),
        ranked_by_leg=ranked,Deck_boundary_boxes=len(faces),
        limits=['Bodies only: no four-body combination, installed mounting, both full feed routes or removal proof.',
            'Absence of conservative candidates does not prove no design space.',
            '35x16x22mm MTA enclosure is a recorded project assumption, not delivered measurement.'],
        started_utc=started.isoformat(),finished_utc=ended.isoformat(),
        worker_wall_seconds=(ended-started).total_seconds(),source_sha256=pins,script_sha256=sha(Path(__file__))))
    print(json.dumps(dict(candidates=len(candidates),ranked={k:len(v) for k,v in ranked.items()})),flush=True)


if __name__=='__main__':main()
