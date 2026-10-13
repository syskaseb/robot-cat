"""Complete three-source fixed neck family and its rooted insulation seats.

Receive actual selected source endpoints, retain qualified source preparation,
then allocate separate low fixed lanes and a shared JR receiving interface.
No native edit, selection, electrical approval or physical PASS is implied.
"""
import json,math,time,re
from pathlib import Path
import FreeCAD as A
import Part
import check_fixed_underneck_rounds as C
from open_prototype_head_preflight import flatten,HEAD,SHIFT
H,S,Q=C.H,C.S,C.Q
V=A.Vector
OUT=H.OUT
R=12.6
SOURCES=('XB22','XB23','XS23')

def line(a,b):return Part.makeLine(V(*a),V(*b))

def extend(edges,point):
    a=edges[-1].valueAt(edges[-1].LastParameter);b=V(*point)
    if (a-b).Length>1e-8:edges.append(Part.makeLine(a,b))

def quarter(edges,axis):
    start=edges[-1].valueAt(edges[-1].LastParameter)
    u=edges[-1].tangentAt(edges[-1].LastParameter);v=V(*axis)
    assert abs(u.dot(v))<1e-7
    end=start+(u+v)*R
    mid=start+(u*math.sqrt(.5)+v*(1-math.sqrt(.5)))*R
    edges.append(Part.Arc(start,mid,end).toShape())

def transfer(edges,axis,offset):
    # Reuse the exact project-radius S helper, no sampled cubic.
    import plan_current_head_feeds as F
    parts=[H.T.line(list(edges[-1].valueAt(edges[-1].FirstParameter)),list(edges[-1].valueAt(edges[-1].LastParameter)))]
    F.spatial_shift(parts,axis,offset)
    edges.extend(H.T.wire(parts[1:]).Edges)

def selected_prefixes(old):
    def oldwire(n):return old['wire/head-supply-checkpoint/'+n][0]
    red=oldwire('XB22');ground=oldwire('XB23');signal=oldwire('XS23')
    expected={'XB22':[-60,76.625,97.99],'XB23':[-117,-25.8,123.39378221735],'XS23':[83.97,12.97,79.2]}
    for n,w in zip(SOURCES,(red,ground,signal)):
        assert (w.Edges[0].valueAt(w.Edges[0].FirstParameter)-V(*expected[n])).Length<1e-6,(n,'Changed selected source')
    return {'XB22':[red.Edges[0].copy()], 'XB23':[ground.Edges[0].copy()],
            'XS23':[e.copy() for e in signal.Edges[:8]]}

def routes(old,x,y):
    q=selected_prefixes(old)
    # All selected source grips/formed pad preparation remain on unchanged
    # straight lands. Replace ONLY after those source interfaces.
    q['XB22']=[line([-60,76.625,97.99],[-60,76.625,115.99])]
    quarter(q['XB22'],[-1,0,0]);transfer(q['XB22'],[-1,0,0],[0,1.375,0])
    extend(q['XB22'],[-125,78,128.59]);quarter(q['XB22'],[0,0,-1])
    extend(q['XB22'],[-137.6,78,60.6]);quarter(q['XB22'],[-1,0,0])
    # Whole retained station allocation, not just D_FL: FL_G reachesX-145,
    # Y88.5 and its W025 rises atY84. Ground therefore crosses SOUTH of
    # W025 atY68 and descends WEST of the entire Foundation (Xmin-178).
    # Signal transfers west BEFORE entering either north station. Its
    # descent atX-160/Y88 lies outside BOTH housings and their root bonds.
    quarter(q['XB23'],[0,1,0]);extend(q['XB23'],[-95.4,55.4,123.39378221735])
    quarter(q['XB23'],[-1,0,0]);extend(q['XB23'],[-173,68,123.39378221735])
    quarter(q['XB23'],[0,0,-1]);extend(q['XB23'],[-185.6,68,63.6]);quarter(q['XB23'],[-1,0,0])
    # The complete fixed Bridge reachesY26/Z137 and yaw servoY15.75/Z121.
    # Cross west only beyond BOTH, with a2.0mm jacket-edge margin, while
    # staying south of the north stations. This is the allocated crossing
    # corridorY29..54.2, not a transfer through the servo atY-15..10.2.
    extend(q['XS23'],[-116.6,29,110])
    transfer(q['XS23'],[0,1,0],[-43.4,0,0])
    extend(q['XS23'],[-160,75.4,110]);quarter(q['XS23'],[0,0,-1])
    extend(q['XS23'],[-160,88,57.6]);quarter(q['XS23'],[-1,0,0])
    # North lanes are10mm apart for actual band/head access. The front
    # columns are10mm apart as well; only the final9mm lands converge.
    allocation={'XB23':dict(north=68,left=-247,z=51,dx=-2.54,seat_x=-216),
                'XB22':dict(north=78,left=-227,z=48,dx=0,seat_x=-169),
                'XS23':dict(north=88,left=-237,z=45,dx=2.54,seat_x=-187)}
    for n,a in allocation.items():
        e=q[n];north,left,z=a['north'],a['left'],a['z'];endx=x+a['dx']
        assert (e[-1].valueAt(e[-1].LastParameter)-V(e[-1].valueAt(e[-1].LastParameter).x,north,z)).Length<1e-6
        extend(e,[left+R,north,z]);quarter(e,[0,-1,0])
        extend(e,[left,y-9,z]);quarter(e,[1,0,0])
        extend(e,[endx-R,y-9-R,z]);quarter(e,[0,0,1])
        extend(e,[endx,y-9-R,80-R]);quarter(e,[0,1,0])
        extend(e,[endx,y,80])
    return q,allocation

def strap(x,y,bottom,top,halfwidth,head_side=1):
    outer=H.T.box([x-halfwidth-1.2,y-1.25,bottom-1.2,x+halfwidth+1.2,y+1.25,top+1.2])
    inner=H.T.box([x-halfwidth,y-1.35,bottom,x+halfwidth,y+1.35,top])
    band=outer.cut(inner)
    head=H.T.box([x-3,y+head_side*3-3,top+1.2,x+3,y+head_side*3+3,top+6.2])
    return band.fuse(head).removeSplitter()

def support(fork,carrier,x,jry):
    roots,meta=C.rooted_parts(fork,carrier,x,jry,80)
    fp=V(*meta['fixed_host_point_mm'])
    pads={'LowerStem':[fp.x-3,fp.y-4,37,fp.x+3,fp.y+4,80.2],
          'FrontRootRail':[-251,fp.y-4,37,fp.x+3,fp.y+4,40],
          'FrontNorthSpine':[-251,fp.y-4,37,-248,92,40],
          'NorthBranch':[-251,64,37,-160,92,40],
          'ReceiverSourceSpine':[x-3,jry-39,72,x+3,jry-25,75],
          'ReceiverSourceSeat':[x-5,jry-39,75,x+5,jry-30.5,78.95],
          'FactorySeatTongue':[x-3,jry,72,x+3,jry+10,79.1]}
    bands={}
    north={'XB23':(68,51,-216),'XB22':(78,48,-169),'XS23':(88,45,-187)}
    for n,(yy,z,sx) in north.items():
        # Real frame beneath each intact-jacket seat, no glue-as-relief.
        pads[n+'NorthSeat']=[sx-5,yy-1.25,40,sx+5,yy+1.25,z-1.05]
        # North wire runs along X: its band is in YZ, not XZ. An axial
        # XZ band cuts two transverse slots and isolates the seat centre.
        b=strap(0,0,40,z+1.25,1.25)
        b.rotate(V(0,0,0),V(0,0,1),90);b.translate(V(sx,yy,0))
        bands[n+'NorthBand']=b
        # Front wire runs along Y, so the unrotated XZ loop is correct.
        xx={'XB23':-247,'XB22':-227,'XS23':-237}[n]
        # Root approaches the band axially, as on the north seats. A
        # transverse arm through the closed side of the band is impossible.
        pads[n+'FrontArm']=[-251,-9.25,37,xx+1.25,-6.75,40]
        pads[n+'FrontSeat']=[xx-1.25,-8,40,xx+1.25,4,z-1.05]
        bands[n+'FrontBand']=strap(xx,0,37,z+1.25,1.25)
    bands['SourceLandBand']=strap(x,jry-34.5,75,81.25,3.85,head_side=-1)
    bands['FactoryLandBand']=strap(x,jry+4.5,75,81.1,1.95)
    fixed=S.fuse([roots['FixedJRSeat']]+[H.T.box(v) for v in pads.values()])
    # A strap may touch the intended jacket but never cut the load path.
    assert len(fixed.Solids)==1,('Shared pads disconnected before any band cut',
        [dict(bounds=H.bb(s),volume=s.Volume) for s in fixed.Solids])
    # Include the JR-retention band after adding receiving lands as well;
    # additions must not refill the earlier qualified strap passage.
    for n,b in {**bands,'FixedJRBand':roots['FixedJRBand']}.items():
        fixed=fixed.cut(b).removeSplitter()
        assert len(fixed.Solids)==1,('Band severs support',n,
            [dict(bounds=H.bb(s),volume=s.Volume) for s in fixed.Solids])
    fixed=fixed.removeSplitter()
    assert fixed.isValid() and len(fixed.Solids)==1,('Whole fixed feed support disconnected',len(fixed.Solids))
    union=carrier.fuse(fixed).removeSplitter()
    assert union.isValid() and len(union.Solids)==1,'No continuous whole support-to-host union'
    roots['FixedJRSeat']=fixed;roots.update(bands)
    meta.update(shared_feed_pads=pads,new_band_count=len(bands)+2,
        rooted_union_valid=True,rooted_union_solids=len(union.Solids),
        receiver_cavity_pitch_mm=2.54,receiver_cavity_pin_view_provisional=True,
        factory_last9_flat_profile_mm=[3.5,1.8],factory_land_contact='flat widthX/heightZ nominal receiving land; delivered twist/pressure gate',
        source_grip='Three straight9mm intact lands on common seat, one cuttable band independent of JR retention',
        phase2='Delivered JR cavity/flat cable orientation, band pressure, PETG rigidity/creep, labels and supported manual movement before power')
    return roots,meta

def prepare():
    selected=json.loads((OUT/'fixed-underneck-rounds-plan.json').read_text());x,z=selected['fixed_receiver_XZ_mm'];jry=selected['fixed_receiver_Y_mm']
    assert selected['status']=='ROUNDED_FACTORY_SHARED_SPACE_MATH_CLEAR_MATERIAL_OPEN'
    for n,h in selected['source_sha256'].items():assert S.SHA(H.ROOT/n)==h,('Stale factory plan',n)
    _,old,archive=S.scene();r=H.P.SavedShapes();head=H.head(r)
    fork=flatten(r,HEAD,'HeadNoseInsertUnit')['Fork'][0];fork.translate(SHIFT)
    fork=fork.cut(H.T.box([-195,20.5,152.25,-180,32,154.65]))
    feeds,allocation=routes(old,x,jry-30)
    # Reject a reversed/too-short corner leg BEFORE constructing support
    # Booleans. Geometry continuity is a planning input, not a late test.
    for n,es in feeds.items():
        for a,b in zip(es,es[1:]):
            assert (a.valueAt(a.LastParameter)-b.valueAt(b.FirstParameter)).Length<1e-6,n
            assert a.tangentAt(a.LastParameter).dot(b.tangentAt(b.FirstParameter))>1-1e-6,(n,'Reversed or discontinuous tangent')
    roots,meta=support(fork,head['YawCarrier'],x,jry)
    return selected,feeds,roots,meta,fork,r,allocation,archive

def run():
    tick=time.monotonic();p,feeds,roots,meta,fork,reader,allocation,archive=prepare()
    report=dict(status='SHARED_FIXED_HEAD_FEEDS_PLAN_ONLY',selected=False,physical_pass=False,
        W2_complete=False,W3_complete=False,allocation=allocation,rooted_support=meta,
        lengths_mm={},mutual=[],continuity=[],min_radius_mm={},bands=len(roots)-2,
        retains=['Selected three actual sources and source preparation/grips','F_HP factory output and lap sleeve','All yaw source feeds','Uncut250 pitch factory','P0/E6/bankR47/15drives/MG92B'],
        remains=['Whole new feeds/roots/bands with head/body and current wires','Full factory self-clearance and support contacts','Native editable assembly/param/reopen/closed exports/stock/selection'],
        source_sha256={**reader.hashes,archive.relative_to(H.ROOT).as_posix():S.SHA(archive),
          **{Path(f).relative_to(H.ROOT).as_posix():S.SHA(Path(f)) for f in (__file__,C.__file__)}})
    for n,es in feeds.items():
        w=Part.Wire(es);assert w.isValid();report['lengths_mm'][n]=w.Length
        rr=[]
        for e in es:
            if not isinstance(e.Curve,Part.Line):rr.append(e.Curve.Radius)
        report['min_radius_mm'][n]=min(rr);assert min(rr)>=R-1e-6,n
        for a,b in zip(es,es[1:]):
            gap=(a.valueAt(a.LastParameter)-b.valueAt(b.FirstParameter)).Length
            dot=a.tangentAt(a.LastParameter).dot(b.tangentAt(b.FirstParameter))
            assert gap<1e-6 and dot>1-1e-6,(n,gap,dot)
        assert abs(es[-1].Length-9)<1e-6,n
        w.exportBrep(str(OUT/(n+'_FixedNeckFeed.brep')))
    for i,n in enumerate(SOURCES):
        for m in SOURCES[i+1:]:
            d,witness,_=Part.Wire(feeds[n]).distToShape(Part.Wire(feeds[m]))
            report['mutual'].append(dict(a=n,b=m,distance_mm=d,clear=d>=2.1-1e-4,
                witness=[[list(v) for v in pair] for pair in witness[:1]]))
    if not all(q['clear'] for q in report['mutual']):report['status']='REJECTED_FIXED_HEAD_FEEDS_MUTUAL'
    report['worker_seconds']=round(time.monotonic()-tick,3)
    H.save('fixed-head-feed-interface-plan.json',report)
    print(json.dumps({k:report[k] for k in ('status','lengths_mm','min_radius_mm','mutual','worker_seconds')}),flush=True)

if __name__=='__main__':run()
