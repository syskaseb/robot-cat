"""Four body straps using the existing eight native Deck slots.

Use the accepted current closed blocks, not another positioning search.
Ports are operated on the bench before crossing wires are dressed; common
bank removal leaves the16conductors and closed20ports untouched. This does
not claim in-situ lever/finger access or physical WAGO retention strength.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,sys,math
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-p-wago-retention-r1'

def main():
    import FreeCAD as A
    import Part
    from servo_fuse_bank_current_owner_receive import receive
    start=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists()
    owners,module,pins=receive(released=False)
    def read(rel):p=ROOT/rel;pins[rel]=sha(p);return json.loads(p.read_text(encoding='utf-8'))
    mapping=read('hardware/electronics/full-cat/servo-fuse-wago-map-r1/interface.json')
    native=read('hardware/cad/studies/open-deck-p0/plate-r1/checks.json')
    q=read('hardware/manufacturing/one-batch-prototype-r51/one-order-quantities.json')
    sku=next(r for r in q['lines'] if r['id']=='tie:111-02370')
    assert sku['dimensions_mm']==dict(length=145,width=2.5,thickness=1.2,head_length=4.8,head_width=4.5,height_H=3.5)
    holes={r['id']:r for r in native['wago_ties']}
    allowners={**owners,**module};changed={};rows=[];hits=[];errors=[];pairs=0;lever_pairs=0
    def box(b):return Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
    def bounds(s):return [getattr(s.BoundBox,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]
    for block in mapping['blocks']:
        ident=block['id'];x,y,z=block['center_mm'];sy=holes[ident]['slot_centers_xy_mm'][0][1]
        slots=[[h[0]+21,h[1]] for h in holes[ident]['slot_centers_xy_mm']]
        assert slots==[[x-16.5,sy],[x+16.5,sy]],(ident,slots)
        target=owners[ident+'_design'];b=bounds(target)
        assert all(abs(a-c)<1e-5 for a,c in zip(b,[x-15,y-9.5,109,x+15,y+9.5,118]))
        tie={};tie['Bottom']=box([x-16.5,sy-1.25,103.8,x+16.5,sy+1.25,105])
        tie['Top']=box([x-15.6,sy-1.25,118,x+15.6,sy+1.25,119.2])
        for sign,label in [(-1,'Left'),(1,'Right')]:
            xb=x+sign*16.5;xt=x+sign*15.6
            pts=[A.Vector(xb-.6,sy-1.25,103.8),A.Vector(xb+.6,sy-1.25,103.8),
                 A.Vector(xt+.6,sy-1.25,119.2),A.Vector(xt-.6,sy-1.25,119.2)]
            tie[label]=Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(A.Vector(0,2.5,0))
        tie['Head']=box([x-18,sy-2.25,119.2,x-13.2,sy+2.25,122.7])
        length=2*31.8+2*math.hypot(15.4,.9)
        assert length+15<145
        for tag,s in tie.items():
            label=ident+'_'+tag;changed[label]=s;s.exportBrep(str(OUT/(label+'_DESIGN.brep')))
            assert s.isValid() and len(s.Solids)==1
            for owner,t in allowners.items():
                if not s.BoundBox.intersect(t.BoundBox):continue
                pairs+=1
                try:
                    c=s.common(t)
                    if c.Volume>1e-5:
                        hits.append(dict(part=label,owner=owner,mm3=c.Volume,bounds_mm=bounds(c)))
                        c.exportBrep(str(OUT/('HIT_'+str(len(hits))+'.brep')))
                except Exception as exc:errors.append(dict(part=label,owner=owner,error=str(exc)))
        # Only qualify the new strap versus the established PROJECT sector;
        # never erase the previous whole installed lever/access conflicts.
        side=1 if y>0 else -1
        local_lever=[]
        for port in block['ports']:
            pivot=A.Vector(port['entry_mm'][0]-2.5,y-side*4,117.2)
            def point(a):return pivot+A.Vector(0,side*14*math.cos(a),14*math.sin(a))
            sector=Part.Face(Part.Wire([Part.makeLine(pivot,point(0)),Part.Arc(point(0),point(math.radians(55)),point(math.radians(110))).toShape(),Part.makeLine(point(math.radians(110)),pivot)])).extrude(A.Vector(5,0,0))
            for tag,s in tie.items():
                if not sector.BoundBox.intersect(s.BoundBox):continue
                lever_pairs+=1;c=sector.common(s)
                if c.Volume>1e-5:local_lever.append(dict(port=port['project_slot'],part=tag,mm3=c.Volume))
        rows.append(dict(id=ident,sku='111-02370',straps=1,native_slots_world_xy_mm=slots,
            plane_y_mm=sy,centreline_upper_bound_mm=length,insertion_reserve_ASSUMED_mm=15,
            native_Deck_slots_unchanged=True,provisional_lever_to_new_strap_hits=local_lever,
            assembly='Prewire all four occupied ports on loose block; fifthNC stays empty. Close levers, position on Deck, thread/tighten this body strap, then dress fixed feeds and input fans. Do not open levers through crossing installed wires.',
            bank_removal='Keep block strap and all four wires connected; cut only24TE insulation ties and use accepted lower input release. No WAGO lever operation in that bank-removal recipe.'))
        print('P_WAGO_NATIVE_SLOT_STRAP',ident,len(hits),len(local_lever),flush=True)
    # Changed straps may not intersect each other either.
    labels=list(changed)
    for i,name in enumerate(labels):
        for other in labels[i+1:]:
            if name.rsplit('_',1)[0]==other.rsplit('_',1)[0]:continue # intentional same physical loop/head joints
            s,t=changed[name],changed[other]
            if s.BoundBox.intersect(t.BoundBox):
                pairs+=1;c=s.common(t)
                if c.Volume>1e-5:hits.append(dict(part=name,owner=other,mm3=c.Volume,bounds_mm=bounds(c)))
    end=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='P_WAGO_NATIVE_EXISTING_SLOTS_RETENTION_CLEAR_BENCH_ORDER' if not hits and not errors and not any(r['provisional_lever_to_new_strap_hits'] for r in rows) else 'P_WAGO_RETENTION_REJECTED',
        selected=False,physical_pass=False,W5_complete=False,blocks=rows,ports=20,conductors=16,NC=4,
        hits=hits,errors=errors,pairs=pairs,lever_to_new_strap_pairs=lever_pairs,
        added_prints=0,added_fasteners=0,body_straps_installed=4,native_grip_slots=8,
        retained_fixed_lower_feed_grips=4,retained_bank_insulation_grips=24,
        whole_installed_lever_access_qualified=False,hinge_dimensions_measured=False,
        previous_installed_sector_conflicts_preserved='servo-fuse-wago-access-r2/checks.json',
        source_sha256=pins,script_sha256=sha(Path(__file__)),started_utc=start.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-start).total_seconds()))
    print('P_WAGO_RETENTION_RESULT',json.dumps(dict(hits=len(hits),errors=len(errors),body_straps=4)),flush=True)

if __name__=='__main__':main()
