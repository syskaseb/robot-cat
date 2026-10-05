"""One coupled side frame/strap/cover correction; reuse unchanged R1 pairs.

Received paths and purchased bodies are immutable. Four complete service bays
replace individual cover nibbles. A blueprint of native boxes/cylinders is saved
alongside one role-indexed compound; no opaque replacement print is selected.
"""
from pathlib import Path
from datetime import datetime, timezone
import json
import w5_side_retention_preflight as R
from servo_fuse_inputs_r1 import save, sha

ROOT=R.ROOT; OUT=R.N.BASE/'w5-side-retention-coupled-r1'
PRIOR=R.OUT/'checks.json'


def bounds(s):
    return [getattr(s.BoundBox,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]


def geometry(A,Part,plan):
    raw={}; bands={}; tools={}; blueprint=dict(raw_boxes={},tool_boxes={},grooves={})
    recipes=[]; moved_heads=[]
    def box(b):return Part.makeBox(*(b[i+3]-b[i] for i in range(3)),A.Vector(*b[:3]))
    def add(name,b,kind,placement=None):
        s=box(b)
        if placement:s.Placement=placement.multiply(s.Placement)
        if kind=='raw':raw[name]=s;blueprint['raw_boxes'][name]=bounds(s)
        elif kind=='tool':tools[name]=s;blueprint['tool_boxes'][name]=bounds(s)
        else:bands[name]=s
    for row in plan['anchors']:
        add(row['name'],row['stem_bounds_mm'],'raw')
        if row['foot_bounds_mm']:add(row['name']+'Foot',row['foot_bounds_mm'],'raw')
    for row in plan['blocks']:
        name=row['name'];x0,y0,z,x1,y1,hi=row['bounds_mm']
        front=name.startswith('F') or name.startswith('D_F')
        floor=[x0-6.2 if front else x0-2.5,y0,z-1.8,x1+2.5 if front else x1+6.2,y1,z]
        if y0>0:floor[4]+=2.5
        else:floor[1]-=2.5
        if name.startswith('D_'):
            if y0>0:floor[4]+=.2
            else:floor[1]-=.2
        else:
            if y0>0:floor[1]-=.2
            else:floor[4]+=.2
        # Keep W042's existing protection and tie intact. Bear on the block's
        # footprint, place the Y stop on its free inner side instead.
        if name=='FR_G':floor[1]=-87;floor[4]=-54.5
        add(name+'BearingAndOutletWing',floor,'raw')
        inner=x1 if front else x0
        add(name+'InnerStop',[inner+.3 if front else inner-2.3,(y0+y1)/2-3,z-1.8,
                             inner+2.3 if front else inner-.3,(y0+y1)/2+3,z+2],'raw')
        stop=[(x0+x1)/2-3,y1+.3 if y0>0 else y0-2.3,z-1.8,
              (x0+x1)/2+3,y1+2.3 if y0>0 else y0-.3,z+2]
        if name=='FR_G':stop[1],stop[4]=-56.7,-54.7
        add(name+'OuterYStop',stop,'raw')
        y=row['body_tie_y_mm'];low=z-3
        for suffix,b in (
            ('West',[x0-1.2,y-1.25,low,x0,y+1.25,hi+1.2]),
            ('East',[x1,y-1.25,low,x1+1.2,y+1.25,hi+1.2]),
            ('Top',[x0,y-1.25,hi,x1,y+1.25,hi+1.2]),
            ('Bottom',[x0,y-1.25,low,x1,y+1.25,low+1.2]),
            ('Head',[(x0+x1)/2-2.25,y-2.4,low-3.5,(x0+x1)/2+2.25,y+2.4,low])):
            add(name+suffix,b,'band')
        for suffix,x in (('West',x0-1.2),('East',x1)):
            add(name+suffix+'Slot',[x-.3,y-1.55,140,x+1.5,y+1.55,hi+1.5],'tool')
        add(name+'UnderSlot',[x0-.3,y-1.55,low-.3,x1+.3,y+1.55,low+1.5],'tool')
    block_map={r['name']:r for r in plan['blocks']}
    for row in plan['endpoints']:
        key=row['end'].replace('.','_');point=row['point_mm'];radius=row['OD_mm']/2
        near_thick=any(e['block']==row['block'] and e['OD_mm']/2>1.5 and
                      abs(e['point_mm'][1]-point[1])<6.01 for e in plan['endpoints'])
        station=2 if radius>1.5 else 4.5 if near_thick else 3
        shift=.5 if radius>1.5 else 1 if near_thick else 0
        # A DATA body's side strap and the two adjacent outlet heads overlap
        # axially. One shared rule gives .35mm nominal head/strap clearance.
        if row['block'].startswith('D_') and abs(point[1]-block_map[row['block']]['body_tie_y_mm'])<3.65:
            shift=max(shift,3.8-station);moved_heads.append(key+'Head')
        placement=A.Placement(A.Vector(point[0],point[1],0),
                              A.Rotation(A.Vector(0,0,1),90 if row['axis'][0]<0 else -90))
        floor=175 if row['block'].startswith('D_') else 165
        z=point[2];low=floor-3;seat_floor=floor-1.8;across=radius+.4
        if key=='FR_G_2':low=164;seat_floor=164
        add(key+'Seat',[-radius-1.2,.2,seat_floor,radius+1.2,5.8,z],'raw',placement)
        origin=placement.multVec(A.Vector(0,.2,z));axis=placement.Rotation.multVec(A.Vector(0,1,0))
        tools[key+'Groove']=Part.makeCylinder(radius+.2,5.6,origin,axis)
        blueprint['grooves'][key+'Groove']=dict(base_radius_mm=radius,allowance_mm=.2,
            height_mm=5.6,origin_mm=[origin.x,origin.y,origin.z],axis=[axis.x,axis.y,axis.z])
        for suffix,b in (
            ('Left',[-across-1.2,station-1.25,low,-across,station+1.25,z+radius+1.2]),
            ('Right',[across,station-1.25,low,across+1.2,station+1.25,z+radius+1.2]),
            ('Top',[-across,station-1.25,z+radius,across,station+1.25,z+radius+1.2]),
            ('Bottom',[-across,station-1.25,low,across,station+1.25,low+1.2]),
            ('Head',[-2.4,station+shift-2.25,z+radius+1.2,2.4,station+shift+2.25,z+radius+4.7])):
            add(key+suffix,b,'band',placement)
        for suffix,x in (('Left',-across-1.2),('Right',across)):
            add(key+suffix+'Slot',[x-.3,station-1.55,140,x+1.5,station+1.55,z+radius+1.5],'tool',placement)
        add(key+'UnderSlot',[-across-.3,station-1.55,low-.3,across+.3,station+1.55,low+1.5],'tool',placement)
        recipes.append(dict(row,station_mm=station,head_outward_shift_mm=shift,band_bottom_mm=low))
    supports={}
    for name,s in raw.items():
        candidates=[t for t in tools.values() if s.BoundBox.intersect(t.BoundBox)]
        supports[name]=s.cut(Part.makeCompound(candidates)) if candidates else s
        assert supports[name].isValid(),name
    # The raised FR_G.2 underpass affects only material in this local region.
    old_under=box(blueprint['tool_boxes']['FR_G_2UnderSlot'])
    changed_supports={'FR_GBearingAndOutletWing','FR_GOuterYStop','FR_G_2Seat'}
    for name,s in raw.items():
        if s.BoundBox.intersect(old_under.BoundBox):changed_supports.add(name)
    changed_bands={'FR_G_2Left','FR_G_2Right','FR_G_2Bottom',*moved_heads}
    bays={}
    for leg in ('FL','FR','RL','RR'):
        members=[s for n,s in {**raw,**bands}.items()
                 if n.startswith((leg+'_','D_'+leg,leg+'CarrierTower'))]
        b=[min(bounds(s)[i] for s in members)-.4 for i in range(3)]
        b += [max(bounds(s)[i] for s in members)+.4 for i in range(3,6)]
        bays[leg+'CompleteSideServiceBay']=b
    blueprint.update(cover_bays=bays,endpoints=recipes,changed_supports=sorted(changed_supports),
                     changed_bands=sorted(changed_bands),data_head_correction_count=len(moved_heads))
    assert len(moved_heads)==6,moved_heads
    return supports,bands,tools,blueprint


def main():
    import FreeCAD as A,Part
    from w5_exact_separation import separated
    start=datetime.now(timezone.utc);assert not (OUT/'checks.json').exists()
    prior=json.loads(PRIOR.read_text(encoding='utf-8'));assert not prior['errors']
    pins=[Path(__file__),Path(R.__file__),PRIOR]
    for rel,digest in {**prior['source_sha256'],**prior['files']}.items():
        assert sha(ROOT/rel)==digest,rel;pins.append(ROOT/rel)
    plan=json.loads((R.R.OUT/'plan.json').read_text(encoding='utf-8'))
    supports,bands,tools,blueprint=geometry(A,Part,plan)
    changed=set(blueprint['changed_supports'])|set(blueprint['changed_bands'])
    assert all(h['owner']=='SourceCover' or h['part'] in changed for h in prior['hits']),prior['hits']
    fixed,printed,_,_,_,loaded,_,_=R.S.load(A,Part);pins+=loaded
    central=json.loads(R.N.CENTRAL.read_text(encoding='utf-8'))
    for wire,row in central['routes'].items():
        p=ROOT/row['geometry'];fixed[wire]=Part.read(str(p));pins.append(p)
    for name in ('SourceCarrier','SourceCover','SourceEastHood','SourceWestHood'):
        p=ROOT/'hardware/cad/studies/w5-harness-passages-qualified-r1'/(name+'_CANDIDATE_WORLD.brep')
        printed[name]=Part.read(str(p));pins.append(p)
    p=ROOT/'hardware/cad/studies/w5-central-retention-native-r1/CentralRetentionDeck_CANDIDATE_WORLD.brep'
    printed['SourceDeck']=Part.read(str(p));pins.append(p)
    for name in R.N.OWNER_ALIASES:printed.pop(name,None)
    r4=json.loads((R.R.P.CENTRAL).read_text(encoding='utf-8'))
    for name,rel in r4['world_geometries'].items():
        p=ROOT/rel;fixed['CentralRetention/'+name]=Part.read(str(p));pins.append(p)
    def box(b):return Part.makeBox(*(b[i+3]-b[i] for i in range(3)),A.Vector(*b[:3]))
    original_cover=printed['SourceCover'];cover_tools=Part.makeCompound([box(b) for b in blueprint['cover_bays'].values()])
    cover=original_cover.cut(cover_tools);printed['SourceCover']=cover
    cover_errors=cover.check(True) or []
    OUT.mkdir(parents=True,exist_ok=True)
    shapes={**supports,**bands};names=list(shapes)
    files=[]
    for filename,shape in (('SideRetention_PROPOSED_WORLD.brep',Part.makeCompound(list(shapes.values()))),
                           ('CoverFourSideBays_CANDIDATE_WORLD.brep',cover)):
        p=OUT/filename;shape.exportBrep(str(p));files.append(p)
    p=OUT/'native-blueprint.json';save(p,blueprint);files.append(p)
    hits=[];errors=[];pairs=0;reused=0
    def check(name,s,owner,t):
        nonlocal pairs
        if not s.BoundBox.intersect(t.BoundBox):return
        for a in s.Solids:
            for b in t.Solids:
                if not a.BoundBox.intersect(b.BoundBox):continue
                pairs+=1
                if separated(a,b):continue
                try:
                    c=a.common(b)
                    if c.Volume>1e-6:hits.append(dict(part=name,owner=owner,mm3=c.Volume,bounds_mm=bounds(c)))
                except Exception as e:errors.append(dict(part=name,owner=owner,error=str(e)))
    for name,s in shapes.items():
        for owner,t in {**fixed,**printed}.items():
            if name in supports and owner=='SourceCarrier':continue
            if name in changed or owner=='SourceCover':check(name,s,owner,t)
            else:reused+=1
        if name in bands:
            for owner,t in supports.items():
                if name in changed or owner in changed:check(name,s,owner,t)
        save(OUT/'progress.json',dict(last_part=name,pairs=pairs,hits=hits,errors=errors,
            started_utc=start.isoformat(),updated_utc=datetime.now(timezone.utc).isoformat()))
    suffixes=('West','East','Top','Bottom','Head','Left','Right')
    group=lambda k:next(k[:-len(s)] for s in suffixes if k.endswith(s))
    labels=list(bands)
    for i,name in enumerate(labels):
        for other in labels[:i]:
            if group(name)!=group(other) and (name in changed or other in changed):check(name,bands[name],other,bands[other])
    for row in plan['blocks']:
        name=row['name']+'_CURRENT_RESERVATION';check(name,fixed[name],'SourceCover',cover)
    # Shape connectivity and existing cover attachment continuity remain real
    # gates, not inferred from removing nominal overlapping material.
    valid=cover.isValid() and len(cover.Solids)==1 and not cover_errors
    finish=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='COUPLED_SIDE_CLEAR_NATIVE_PENDING' if valid and not hits and not errors else 'COUPLED_SIDE_REJECTED',
        pairs=pairs,inherited_prior_pairs=prior['pairs'],unchanged_candidate_pairs_reused=reused,
        inherited_scope=PRIOR.relative_to(ROOT).as_posix(),changed_roles=sorted(changed),
        block_count=8,endpoint_count=35,body_ties=8,insulation_ties=35,
        compound_role_order=names,hits=hits,errors=errors,cover_valid=cover.isValid(),
        cover_solids=len(cover.Solids),cover_BOP_errors=cover_errors,
        cover_before_mm3=original_cover.Volume,cover_after_mm3=cover.Volume,
        cover_service_bays=blueprint['cover_bays'],frozen_37_routes=True,
        no_new_screws_or_separate_prints=True,prototype_layout_only=True,
        native_connected_roots_parameter_reopen_pending=True,
        cover_attachment_wall_assembly_motion_stock_pending=True,
        selected=False,W1_complete=False,W5_complete=False,physical_pass=False,
        started_utc=start.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-start).total_seconds(),
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in dict.fromkeys(pins)},
        files={p.relative_to(ROOT).as_posix():sha(p) for p in files}))
    print('COUPLED_SIDE_DONE',pairs,len(hits),len(errors),len(cover.Solids),flush=True)


if __name__=='__main__':main()
