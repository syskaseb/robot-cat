"""One candidate shared source-retention tree, before native details.

Roots are inside actual retained printed material, not envelope centres.
Three same-parent replacements; no holes/cuts in historical source masters.
Case retention/S0 top mounting and whole W5 selection remain separate gates.
"""
import json,math
from pathlib import Path
import FreeCAD as A
from loom_land_port import box
from plan_axial_source_supports import arm_box
from check_main_p0_placement import SavedShapes
from plan_current_harness_interfaces import ROOT,BASE,OUT,SHA


def saddle(g):
    r=g['project_insulation_radius_mm'];t=.381;w=1.6764
    n=A.Vector(*g['normal']);z=A.Vector(*g['axis']);y=z.cross(n)
    assert abs(n.dot(z))<1e-7 and abs(y.Length-1)<1e-7
    m=A.Matrix()
    for col,v in enumerate((n,y,z),1):
        for row,a in enumerate(v,1):setattr(m,'A'+str(row)+str(col),a)
    m.A14,m.A24,m.A34=g['centre_world_mm']
    #3mm axial cradle fits the proven short insulated lands; a thin lacing
    # band is not a nine-mm clamping bridge and keeps its physical-fit gate.
    sign=-1 if g['bound_ends'][0] in ('P_SYS.1','S0.in') else 1
    foot=[r+.5,-2,1.4,r+4.5,2,4.5] if sign==1 else [r+.5,-2,-4.5,r+4.5,2,-1.4]
    pads=[[r+.5,-2,-1.5,r+4.5,2,1.5],foot]
    outer=[-r-.2-t-.15,-r-.2-t-.15,-w/2-.15,r+4.5+t+.15,r+.2+t+.15,w/2+.15]
    inner=[-r-.2+.15,-r-.2+.15,-w,r+4.5-.15,r+.2-.15,w]
    body=box(pads[0]).fuse(box(foot)).cut(box(outer).cut(box(inner))).removeSplitter()
    band=box([-r-.2-t,-r-.2-t,-w/2,r+4.5+t,r+.2+t,w/2]).cut(
              box([-r-.2,-r-.2,-w,r+4.5,r+.2,w]))
    knot=[r+4.5+t,-1,-1.5,r+7.5+t,1,.5]
    band=band.fuse(box(knot)).removeSplitter()
    for s in (body,band):s.Placement=A.Placement(m)*s.Placement
    # Root BEHIND the lacing plane. A mid-plane root would run through
    # its own lacing wall; allocate this before the common material gate.
    p=A.Placement(m).multVec(A.Vector(r+3,0,3*sign))
    return dict(body=body,band=band,root_tip_mm=list(p),
                recipe=dict(pads=[dict(bounds_mm=v) for v in pads],ring_cut=dict(outer=outer,inner=inner),
                    local_to_world=list(m.A),knot=knot,project_lacing_blank_mm=150,
                    land_mm=g['land_mm'],actual_retention_verified=False))


def geometry():
    f=OUT/'remaining-source-retention-plan.json';plan=json.loads(f.read_text())
    for n,h in plan['source_sha256'].items():assert SHA(ROOT/n)==h,n
    assert plan['status']=='REMAINING_SOURCE_SHARED_LANDS_ROOTS_AND_MATERIAL_GATE_OPEN'
    groups=list(plan['groups']);sf=OUT/'source-receiving-plan.json';source=json.loads(sf.read_text())
    # ALL occupied receiving ports, not only the remaining W066 land.
    for wid,port,r in [('W067','2',2.1),('W068','3',2.1),('W043','5',2)]:
        p=source['P_SYS']['ports'][port]
        groups.append(dict(id=wid+'_P_SYS',wire=wid,bound_ends=['P_SYS.'+port],segment=0,
            centre_world_mm=[p[0],p[1]+1.5,p[2]],axis=[0,1,0],normal=[0,0,-1],
            land_mm=3,project_insulation_radius_mm=r,assembly_group='SOURCE_RECEIVING_CARRIER'))
    assert len(groups)==13
    reader=SavedShapes();neck=BASE/'head-mount-checkpoint/HeadNeckCurrent.FCStd'
    upper=OUT/'upper-fixed-feed-supports/UpperFixedFeedSupportsCurrent.FCStd'
    parents={'RightRiser':reader.shape(neck,'RightRiser'),'LeftRiser':reader.shape(neck,'LeftRiser'),
             'UpperCarrier001':reader.shape(upper,'UpperCarrierFixedFeedsCurrent')}
    anchors={'RightRiser':[-100,-25,55],'LeftRiser':[-100,25,55],'UpperCarrier001':[84,40,146.5]}
    for n,p in anchors.items():
        q=box([a-1 for a in p]+[a+1 for a in p])
        assert abs(parents[n].common(q).Volume-8)<1e-6,('No actual retained anchor',n,p)
    recipes={};components={};trees={n:[] for n in parents};paths={n:[] for n in parents}
    def arm(owner,points,half=(2,2,2)):
        paths[owner].append(dict(points_mm=points,half_widths_mm=list(half)))
        for a,b in zip(points,points[1:]):trees[owner].append(arm_box(a,b,list(half)))
    # The outside x-100 descent would enter the front leg's moving bay.
    # Cross over the retained P0 mount top61, then descend INBOARD atx-60.
    arm('RightRiser',[anchors['RightRiser'],[-100,-25,63.25],[-60,-25,63.25],
        [-60,-66,63.25],[-60,-66,18],[45.5,-66,18]])
    arm('LeftRiser',[anchors['LeftRiser'],[-100,31,55],[-112,31,55],[-112,31,74],[-112,43.19319767883137,74]])
    # Cross BELOW the existing MTA factory bend, not its Z151.4 slab.
    arm('UpperCarrier001',[anchors['UpperCarrier001'],[84,40,143.5],[33.125,40,143.5],
        [33.125,85.5,143.5],[33.125,85.5,51.4],[13.09555285409,85.5,48.4],
        [13.09555285409,54.59195868431,48.4]])
    arm('UpperCarrier001',[[33.125,40,143.5],[33.125,40,154.4]])
    # Bearing strips under P_SYS; keeping an open middle, not a large sheet.
    for x in (15.5,47.5):
        trees['UpperCarrier001'].append(box([x-2,36.8,152.9,x+2,64,155.9]))
        arm('UpperCarrier001',[[33.125,40,154.4],[x,40,154.4]])
    # F_PI floor rails leave its downward lead and R6 bend open.
    for x in (10,28):
        trees['UpperCarrier001'].append(box([x-2,74.5,94.9,x+2,96.5,97.9]))
        arm('UpperCarrier001',[[33.125,85.5,96.4],[x,85.5,96.4]],(1.4,2,1.4))
    for g in groups:
        q=saddle(g);gid=g['id'];components['SourceLacing/'+gid]=q['band']
        owner={'LOWER_SOURCE_CARRIAGE':'RightRiser','S0_SOURCE_MOUNT':'LeftRiser',
               'SOURCE_RECEIVING_CARRIER':'UpperCarrier001'}[g['assembly_group']]
        tip=q['root_tip_mm'];trees[owner].append(q['body'])
        if owner=='RightRiser':arm(owner,[[tip[0],-66,18],[tip[0],-66,tip[2]],tip],(1.4,2,1.4))
        elif owner=='LeftRiser':arm(owner,[[-112,tip[1],74],[-112,tip[1],tip[2]],tip])
        elif g['wire'] in ('W066','W067','W068','W043') and g['bound_ends'][0].startswith('P_SYS.'):
            arm(owner,[[33.125,40,154.4],[tip[0],40,154.4],[tip[0],tip[1],154.4],tip],(1.4,2,1.4))
        elif g['wire']=='W078':
            arm(owner,[[33.125,85.5,96.4],[33.125,tip[1],96.4],[33.125,tip[1],tip[2]],tip],(1.4,2,1.4))
        elif g['wire']=='W077':arm(owner,[[28,85.5,96.4],tip],(1.4,2,1.4))
        else:arm(owner,[[13.09555285409,54.59195868431,48.4],tip],(1.4,2,1.4))
        recipes[gid]=dict(g,owner=owner,saddle=q['recipe'])
    for owner,shapes in trees.items():
        components['SourceStructure/'+owner]=shapes[0].multiFuse(shapes[1:]).removeSplitter()
    pins={f,sf,neck,upper,Path(__file__),Path(__file__).with_name('plan_axial_source_supports.py')}
    return dict(components=components,parents=parents,anchors=anchors,recipes=recipes,paths=paths,
                source_sha256={p.relative_to(ROOT).as_posix():SHA(p) for p in pins},
                selected=False,W5_complete=False,physical_pass=False)
