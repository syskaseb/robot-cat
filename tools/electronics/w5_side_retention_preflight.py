"""ONE complete side-frame/band preflight, before changing native Carrier.

Freeze routes and block datums. Plan crowded thick/thin outlet stations and
heads together, then check only added material against the received assembly.
Save one role-indexed compound, not a separate file for every small shape.
"""
from datetime import datetime, timezone
from pathlib import Path
import json
import w5_side_retention_anchors as R
import w5_received_central_scope as S
from servo_fuse_inputs_r1 import save, sha

N=R.P.N;ROOT=N.ROOT;OUT=N.BASE/'w5-side-retention-preflight-r1'
CENTRAL_NATIVE=N.BASE/'w5-central-retention-native-r1/checks.json'


def proposed(A,Part,plan):
    raw={};bands={};cutters={};recipes=[]
    def box(b):return Part.makeBox(*(b[i+3]-b[i] for i in range(3)),A.Vector(*b[:3]))
    for row in plan['anchors']:
        raw[row['name']]=box(row['stem_bounds_mm'])
        if row['foot_bounds_mm']:raw[row['name']+'Foot']=box(row['foot_bounds_mm'])
    for row in plan['blocks']:
        name=row['name'];x0,y0,z,x1,y1,hi=row['bounds_mm']
        front=name.startswith('F') or name.startswith('D_F');u=-1 if front else 1
        floor=[x0-6.2 if front else x0-2.5,y0,z-1.8,x1+2.5 if front else x1+6.2,y1,z]
        # Bearing material also owns both lateral stops; no floating stops.
        if y0>0:floor[4]+=2.5
        else:floor[1]-=2.5
        # Overlap the inter-level tower by0.2mm, not a coincident seam.
        if name.startswith('D_'):
            if y0>0:floor[4]+=.2
            else:floor[1]-=.2
        else:
            if y0>0:floor[1]-=.2
            else:floor[4]+=.2
        raw[name+'BearingAndOutletWing']=box(floor)
        inner=x1 if front else x0
        raw[name+'InnerStop']=box([inner+.3 if front else inner-2.3,(y0+y1)/2-3,z-1.8,
                                  inner+2.3 if front else inner-.3,(y0+y1)/2+3,z+2])
        raw[name+'OuterYStop']=box([(x0+x1)/2-3,y1+.3 if y0>0 else y0-2.3,z-1.8,
                                   (x0+x1)/2+3,y1+2.3 if y0>0 else y0-.3,z+2])
        y=row['body_tie_y_mm'];low=z-3
        bands[name+'West']=box([x0-1.2,y-1.25,low,x0,y+1.25,hi+1.2])
        bands[name+'East']=box([x1,y-1.25,low,x1+1.2,y+1.25,hi+1.2])
        bands[name+'Top']=box([x0,y-1.25,hi,x1,y+1.25,hi+1.2])
        bands[name+'Bottom']=box([x0,y-1.25,low,x1,y+1.25,low+1.2])
        bands[name+'Head']=box([(x0+x1)/2-2.25,y-2.4,low-3.5,(x0+x1)/2+2.25,y+2.4,low])
        for suffix,x in (('West',x0-1.2),('East',x1)):
            cutters[name+suffix+'Slot']=box([x-.3,y-1.55,140,x+1.5,y+1.55,hi+1.5])
        cutters[name+'UnderSlot']=box([x0-.3,y-1.55,low-.3,x1+.3,y+1.55,low+1.5])
    for row in plan['endpoints']:
        key=row['end'].replace('.','_');origin=row['point_mm'];radius=row['OD_mm']/2
        thick=radius>1.5
        near_thick=any(e['block']==row['block'] and e['OD_mm']/2>1.5 and
                       abs(e['point_mm'][1]-origin[1])<6.01 for e in plan['endpoints'])
        # Six-mm ground pitch: stagger thick/thin bands by2.5mm and place
        # thin heads outside the thick band's axial span BEFORE any BOP.
        station=2 if thick else 4.5 if near_thick else 3
        head_shift=.5 if thick else 1 if near_thick else 0
        angle=90 if row['axis'][0]<0 else -90
        transform=A.Placement(A.Vector(origin[0],origin[1],0),A.Rotation(A.Vector(0,0,1),angle))
        def local(b):
            s=box(b);s.Placement=transform.multiply(s.Placement);return s
        floor=165 if not row['block'].startswith('D_') else 175
        z=origin[2];low=floor-3;across=radius+.4
        seat=local([-radius-1.2,.2,floor-1.8,radius+1.2,5.8,z])
        groove=Part.makeCylinder(radius+.2,5.6,A.Vector(0,.2,z),A.Vector(0,1,0))
        groove.Placement=transform.multiply(groove.Placement)
        raw[key+'Seat']=seat;cutters[key+'Groove']=groove
        for suffix,b in (
            ('Left',[-across-1.2,station-1.25,low,-across,station+1.25,z+radius+1.2]),
            ('Right',[across,station-1.25,low,across+1.2,station+1.25,z+radius+1.2]),
            ('Top',[-across,station-1.25,z+radius,across,station+1.25,z+radius+1.2]),
            ('Bottom',[-across,station-1.25,low,across,station+1.25,low+1.2]),
            ('Head',[-2.4,station+head_shift-2.25,z+radius+1.2,2.4,station+head_shift+2.25,z+radius+4.7])):
            bands[key+suffix]=local(b)
        for suffix,x in (('Left',-across-1.2),('Right',across)):
            cutters[key+suffix+'Slot']=local([x-.3,station-1.55,140,x+1.5,station+1.55,z+radius+1.5])
        cutters[key+'UnderSlot']=local([-across-.3,station-1.55,low-.3,across+.3,station+1.55,low+1.5])
        recipes.append(dict(row,station_mm=station,head_outward_shift_mm=head_shift))
    supports={}
    for label,s in raw.items():
        tools=[t for t in cutters.values() if s.BoundBox.intersect(t.BoundBox)]
        supports[label]=s.cut(Part.makeCompound(tools)) if tools else s
        assert s.isValid() and supports[label].isValid(),label
    return supports,bands,cutters,recipes


def main():
    import FreeCAD as A,Part
    from w5_exact_separation import separated
    start=datetime.now(timezone.utc)
    assert not (OUT/'checks.json').exists()
    # Native Deck must already be received, not duplicated or assumed done.
    native=json.loads(CENTRAL_NATIVE.read_text(encoding='utf-8'))
    assert native['status']=='CENTRAL_RETENTION_NATIVE_PARAMETER_EXPORT_REOPEN_COMPLETE'
    plan_path=R.OUT/'plan.json';plan=json.loads(plan_path.read_text(encoding='utf-8'))
    assert plan['all_anchors_have_actual_material_join'] and plan['all_straights_match']
    pins=[Path(__file__),plan_path,CENTRAL_NATIVE]
    for receipt in (plan,native):
        for rel,digest in {**receipt['source_sha256'],**receipt.get('files',{})}.items():
            assert sha(ROOT/rel)==digest,rel;pins.append(ROOT/rel)
    fixed,printed,_,_,_,loaded,_,_=S.load(A,Part);pins+=loaded
    central=json.loads(N.CENTRAL.read_text(encoding='utf-8'))
    for wire,row in central['routes'].items():
        p=ROOT/row['geometry'];fixed[wire]=Part.read(str(p));pins.append(p)
    for owner in ('SourceCarrier','SourceCover','SourceEastHood','SourceWestHood'):
        p=ROOT/'hardware/cad/studies/w5-harness-passages-qualified-r1'/(owner+'_CANDIDATE_WORLD.brep')
        printed[owner]=Part.read(str(p));pins.append(p)
    p=ROOT/'hardware/cad/studies/w5-central-retention-native-r1/CentralRetentionDeck_CANDIDATE_WORLD.brep'
    printed['SourceDeck']=Part.read(str(p));pins.append(p)
    for label in N.OWNER_ALIASES:printed.pop(label,None)
    r4_path=R.P.CENTRAL;r4=json.loads(r4_path.read_text(encoding='utf-8'))
    for label,rel in r4['world_geometries'].items():
        p=ROOT/rel;fixed['CentralRetention/'+label]=Part.read(str(p));pins.append(p)
    supports,bands,tools,recipes=proposed(A,Part,plan)
    OUT.mkdir(parents=True,exist_ok=True)
    shapes={**supports,**bands};names=list(shapes)
    p=OUT/'SideRetention_PROPOSED_WORLD.brep'
    Part.makeCompound([shapes[k] for k in names]).exportBrep(str(p))
    geometry_pin={p.relative_to(ROOT).as_posix():sha(p)}
    hits=[];errors=[];pairs=0;joins={}
    def check(label,s,owner,t):
        nonlocal pairs
        if not s.BoundBox.intersect(t.BoundBox):return
        for a in s.Solids:
            for b in t.Solids:
                if not a.BoundBox.intersect(b.BoundBox):continue
                pairs+=1
                if separated(a,b):continue
                try:
                    common=a.common(b)
                    if common.Volume>1e-6:
                        hits.append(dict(part=label,owner=owner,mm3=common.Volume,
                            bounds_mm=[getattr(common.BoundBox,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]))
                except Exception as e:errors.append(dict(part=label,owner=owner,error=str(e)))
    for label,s in shapes.items():
        for owner,t in {**fixed,**printed}.items():
            if label in supports and owner=='SourceCarrier':
                joins[label]=s.common(t).Volume
                continue # Deliberate union with its own physical parent only.
            check(label,s,owner,t)
        if label in bands:
            for owner,t in supports.items():check(label,s,owner,t)
        save(OUT/'progress.json',dict(last_part=label,pairs=pairs,hits=hits,errors=errors,
            started_utc=start.isoformat(),updated_utc=datetime.now(timezone.utc).isoformat()))
        print('SIDE_RETENTION_PREFLIGHT',label,len(hits),len(errors),flush=True)
    suffixes=('West','East','Top','Bottom','Head','Left','Right')
    group=lambda k:next(k[:-len(s)] for s in suffixes if k.endswith(s))
    labels=list(bands)
    for i,label in enumerate(labels):
        for other in labels[:i]:
            if group(label)!=group(other):check(label,bands[label],other,bands[other])
    # The elevated bodies are not exempt from their new physical parents.
    # Earlier path receipts did not qualify side-body/printed-frame assembly.
    for row in plan['blocks']:
        owner=row['name']+'_CURRENT_RESERVATION'
        assert owner in fixed,owner
        for name,t in printed.items():check(owner,fixed[owner],name,t)
    tie=json.loads(R.P.TIE.read_text(encoding='utf-8'))
    body_loops={r['name']:2*(r['bounds_mm'][3]-r['bounds_mm'][0]+r['bounds_mm'][5]-r['floor_mm']+3)+4.8
                for r in plan['blocks']}
    assert all(v+tie['head_length_mm']+20<tie['length_mm'] for v in body_loops.values())
    finish=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='WHOLE_SIDE_PREFLIGHT_REJECTED' if hits or errors else 'WHOLE_SIDE_PREFLIGHT_CLEAR_NATIVE_PENDING',
        endpoints=recipes,block_count=8,endpoint_count=35,proposed_body_ties=8,proposed_insulation_ties=35,
        support_role_count=len(supports),band_piece_count=len(bands),tool_count=len(tools),
        compound_role_order=names,geometry_single_file=True,hits=hits,errors=errors,pairs=pairs,
        support_parent_overlap_mm3=joins,all_raw_anchors_inherited=True,
        body_loop_mm=body_loops,minimum_pull_tail_allowance_mm=20,
        side_body_printed_scope_checked=True,
        joint_plan_before_native_changes=True,no_routes_retraced=True,
        whole_native_connected_roots_pending=True,lever_assembly_motion_stock_pending=True,
        selected=False,W1_complete=False,W5_complete=False,physical_pass=False,
        started_utc=start.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-start).total_seconds(),
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in dict.fromkeys(pins)},files=geometry_pin))


if __name__=='__main__':main()
