"""Whole flat kits: source box, every fan, common channelled clamp and root.

Boxes are planning volumes; source-case box equivalence is checked against
the pinned valid source model's volume. Clamp exterior includes both halves,
one complete band/head, and a connected lower-frame branch. Not native CAD.
"""
import itertools
import math
import json
from pathlib import Path
import numpy as np


def box_points(lo,hi,step=2):
    lo=np.array(lo,float);hi=np.array(hi,float);assert np.all(hi>lo)
    axes=[np.linspace(a,b,max(1,math.ceil((b-a)/step))+1) for a,b in zip(lo,hi)]
    chunks=[]
    for i in range(3):
        j,k=[n for n in range(3) if n!=i]
        for bound in (lo[i],hi[i]):
            q=np.zeros((len(axes[j])*len(axes[k]),3));q[:,i]=bound
            q[:,[j,k]]=np.array(list(itertools.product(axes[j],axes[k])))
            chunks.append(q)
    return np.unique(np.vstack(chunks),axis=0)


def box_gap(a,b):
    return float(np.linalg.norm(np.maximum(0,np.maximum(a[0]-b[1],b[0]-a[1]))))


def to_box(points,bounds):
    return np.linalg.norm(np.maximum(0,np.maximum(bounds[0]-points,points-bounds[1])),axis=1)


def shared_rail_bounds():
    """Second whole frame family: BELOW seats, OUTBOARD of preserved P0.

    Whole carrier ends at the retained P0 structural side datum X127, not
    cosmetic tail station158. Domains whose complete pier misses the finite
    rail are invalid; connections to actual clamp kits remain a separate HOLD.
    """
    return [np.array([[-126,54 if side>0 else -60,34.7],
                      [127,60 if side>0 else -54,37.7]]) for side in (-1,1)]


def build(station,family,side,departure,centre_x=0):
    pitch,depth,height=station['flat_dimensions_pitch_departure_thickness_mm']
    source=station['source_part_record'];volume=pitch*depth*height
    assert source['valid'] and source['solids']==1 and abs(source['volume_mm3']-volume)<1e-5
    assert family in station['row_families'] and side in (-1,1) and departure in (-1,1)
    if station['fixed_identity_pose']:
        centre=np.array(station['source_world_centre_mm']);side=1;departure=-1
        # Current P_SYS pitch points-Y and departure-X; keep all original
        # coordinates, not the other rows' source-centre recipe.
        pitchsign=-1
    else:
        # Derive wire planes from whole clamp+band budget, not case alone.
        rmax=max(p['radius_mm'] for p in station['ports'])
        z=min(52-1.25-rmax-2-1.2,52-1.25-height/2) if family=='outer' else 48.5
        centre=np.array([centre_x,side*(62.5 if family=='outer' else 19.5),z])
        h=float(np.cross(station['source_pitch_axis'],station['source_departure_axis'])[2])
        assert abs(abs(h)-1)<1e-7
        pitchsign=int(-h*departure) # Preserve source+Z/leverUP, including +Y mouths.
    d=np.array([departure,0,0.]);b=np.array([0,0,1.]) if family=='outer' else np.array([0,side,0.])
    commonR=station['shared_fan_R_mm'];first=9
    activeYs=[(centre[1]+pitchsign*p['local_pitch_departure_thickness_mm'][0],
               max(12.4,p['minimum_project_R_mm'])) for p in station['ports'] if not p['protected_whole_route_reuse']]
    commonY=max(side*y+r for y,r in activeYs) if family=='inner' else None
    boxes=[];wires=[];clouds=[];radii=[];types=[]
    def addbox(name,lo,hi,kind):
        bounds=np.sort(np.array([lo,hi],float),axis=0)
        p=box_points(*bounds);boxes.append(dict(name=name,bounds=bounds,kind=kind))
        clouds.append(p);radii.append(np.zeros(len(p)));types.append(np.full(len(p),kind))
    casebounds=np.array([centre-[depth/2,pitch/2,height/2],centre+[depth/2,pitch/2,height/2]])
    addbox('source_case',*casebounds,0)
    portrows=[];reused=[]
    for port in station['ports']:
        port=dict(port)
        if port['protected_whole_route_reuse']:
            path=Path(__file__).resolve().parents[2]/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/n01-central-spine-power-plan-r4.json'
            source=next(r for r in json.loads(path.read_text())['routes'] if r['wire']=='W043')
            assert source['parts'][-1]['length_mm']>=9 and source['radius_mm']==1.7
            port['radius_mm']=source['radius_mm']
        lp,ld,lz=port['local_pitch_departure_thickness_mm'];assert abs(lz)<1e-5
        q=centre+np.array([departure*ld,pitchsign*lp,lz])
        portrows.append(dict(port,q=q))
        if port['protected_whole_route_reuse']:
            assert np.allclose(q,source['parts'][-1]['end']) and np.allclose(d,[-1,0,0])
            reused.append(dict(wire=port['wire'],points=np.linspace(q,q+d*9,10),radius=port['radius_mm'],
                point_mm=q.tolist(),departure_axis=d.tolist(),grip_length_mm=9,
                source_straight_length_mm=source['parts'][-1]['length_mm'],not_new_wire_geometry=True))
            continue
        R=commonY-side*q[1] if family=='inner' else commonR
        assert R>=port['minimum_project_R_mm']-1e-7
        a=q+d*first;angles=np.linspace(0,math.pi/2,math.ceil(R*math.pi/2)+1)
        arc=a+R*np.sin(angles)[:,None]*d+R*(1-np.cos(angles))[:,None]*b
        end=arc[-1];p=np.vstack((np.linspace(q,a,10),arc,np.linspace(end,end+b*9,10)))
        wires.append(dict(wire=port['wire'],endpoint=port['endpoint'],points=p,radius=port['radius_mm'],
            point_mm=q.tolist(),departure_axis=d.tolist(),bend_unit=b.tolist(),R_mm=R,
            first_mm=first,before_arc_grip_line_mm=[q.tolist(),a.tolist()],
            after_arc_end_mm=(end+b*9).tolist()))
        clouds.append(p);radii.append(np.full(len(p),port['radius_mm']));types.append(np.ones(len(p),dtype=int))
    active=portrows # Replacement owns ALL occupied jackets, including existingW043.
    assert active
    qx=active[0]['q'][0];z=centre[2];rmax=max(r['radius_mm'] for r in active)
    ymin=min(r['q'][1]-r['radius_mm'] for r in active)-2
    ymax=max(r['q'][1]+r['radius_mm'] for r in active)+2
    xs=sorted((qx,qx+departure*9));cap=np.array([[xs[0],ymin,z-rmax-2],[xs[1],ymax,z+rmax+2]])
    addbox('common_channelled_cap_exterior',*cap,4)
    # Exterior rounded-rectangle band budget. Interior is the cap, not an
    # additional filled block. Only the four boundary strips are material.
    mid=qx+departure*4.5;bx=[mid-1.25,mid+1.25]
    for name,lo,hi in (
        ('band_lowY',[bx[0],ymin-1.2,cap[0,2]-1.2],[bx[1],ymin,cap[1,2]+1.2]),
        ('band_highY',[bx[0],ymax,cap[0,2]-1.2],[bx[1],ymax+1.2,cap[1,2]+1.2]),
        ('band_lowZ',[bx[0],ymin,cap[0,2]-1.2],[bx[1],ymax,cap[0,2]]),
        ('band_highZ',[bx[0],ymin,cap[1,2]],[bx[1],ymax,cap[1,2]+1.2])):
        addbox(name,lo,hi,2)
    if family=='outer' or station['fixed_identity_pose']:
        head=np.array([mid,ymin-1.2-3 if side>0 else ymax+1.2+3,z])
    else:head=np.array([mid,(ymin+ymax)/2,cap[1,2]+1.2+3])
    addbox('one_common_band_head',head-3,head+3,2)
    # Shared carrier: seat/floor and a back-side return around (not through)
    # the purchased case. Roots may fuse with other roots, never with wires.
    ylo,yhi=casebounds[:,1];bottom=casebounds[0,2]
    back=centre[0]-departure*depth/2;backlo,backhi=sorted((back-departure*4.25,back-departure*1.25))
    floorlo=min(backlo,casebounds[0,0],xs[0]);floorhi=max(backhi,casebounds[1,0],xs[1])
    if family=='outer':
        seatnear=side*(49.3396+1.25)
        yy=sorted((seatnear,side*(abs(centre[1])+pitch/2)))
        addbox('outer_low_bearing_floor',[floorlo,yy[0],bottom-2],[floorhi,yy[1],bottom],3)
        yy=sorted((side*54,side*60));x=centre[0]-departure*depth/4
        addbox('outer_vertical_pier_to_low_rail',[x-3,yy[0],34.7],[x+3,yy[1],bottom],3)
    else:
        addbox('inner_bearing_floor',[floorlo,ylo,bottom-2],[floorhi,yhi,bottom],3)
        edge=side*(abs(centre[1])+pitch/2);yy=sorted((edge,side*60))
        if yy[1]-yy[0]>1e-5:
            addbox('inner_return_to_shared_rail',[backlo,yy[0],min(bottom-2,39.77)],
                   [backhi,yy[1],max(bottom,42.77)],3)
        yy=sorted((side*54,side*60))
        addbox('inner_vertical_pier_to_low_rail',[backlo,yy[0],34.7],[backhi,yy[1],max(bottom,42.77)],3)
    addbox('independent_clamp_root',[xs[0],ymin,bottom-2],
           [xs[1],ymax,cap[0,2]],3)
    p=np.vstack(clouds);rr=np.concatenate(radii);tt=np.concatenate(types)
    bounds=np.array([(p-rr[:,None]).min(0),(p+rr[:,None]).max(0)])
    return dict(ref=station['ref'],family=family,side=side,departure_X=departure,centre_mm=centre.tolist(),
        fixed_identity=station['fixed_identity_pose'],pitch_Y_sign=pitchsign,
        source_lever_UP_preserved_from_actual_handedness=True,first_mm=first,
        R_mm=max(w['R_mm'] for w in wires),inner_concentric_full_fan=(family=='inner'),
        points=p,radii=rr,types=tt,bounds=bounds,boxes=boxes,wires=wires,reused_jacket_lands=reused,
        frame_family='STRUCTURAL_END_BOUNDED_LOW_CARRIER_COMPLETE_OWNERS',
        tie_wrap_rectangular_upper_bound_mm=2*((ymax-ymin)+(cap[1,2]-cap[0,2]))+10,
        all_caps_channel_all_owned_jackets=True,actual_band_length_fit_not_verified=True)


def compatible(a,b):
    if box_gap(a['bounds'],b['bounds'])>=1.25:return True
    for x in a['boxes']:
        for y in b['boxes']:
            if x['kind']==y['kind']==3:continue # Same printed common carrier.
            if {x['kind'],y['kind']}=={0,3}:
                root=x if x['kind']==3 else y;case=y if y['kind']==0 else x
                if root['bounds'][1,2]<=case['bounds'][0,2]+1e-6:continue
            if box_gap(x['bounds'],y['bounds'])<1.25-1e-5:return False
    for group,other in ((a,b),(b,a)):
        for wire in group['wires']:
            for box in other['boxes']:
                if float(np.min(to_box(wire['points'],box['bounds'])))-wire['radius']<1.25-1e-5:return False
    from scipy.spatial import cKDTree
    for x in a['wires']:
        for y in b['wires']:
            if float(cKDTree(x['points']).query(y['points'],workers=1)[0].min())<x['radius']+y['radius']+.2-1e-5:return False
    return True


def compact(m):
    return {k:v for k,v in m.items() if k not in ('points','radii','types','bounds','boxes','wires','reused_jacket_lands')}


def self_wire_gap(m):
    from scipy.spatial import cKDTree
    margins=[]
    for a,b in itertools.combinations(m['wires']+m.get('reused_jacket_lands',[]),2):
        d=float(cKDTree(a['points']).query(b['points'],workers=1)[0].min())
        margins.append(d-a['radius']-b['radius']-.2)
    return min(margins,default=1e6)


def pier_supported(m):
    rail=shared_rail_bounds()[0 if m['side']<0 else 1]
    piers=[r for r in m['boxes'] if 'vertical_pier_to_low_rail' in r['name']]
    assert len(piers)==1
    # Positive volume, not corner/edge contact; still not a whole load proof.
    return bool(np.all(np.minimum(piers[0]['bounds'][1],rail[1])-
                       np.maximum(piers[0]['bounds'][0],rail[0])>1e-5))
