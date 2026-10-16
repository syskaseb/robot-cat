"""One prototype retention set for4MTA and8opposed source connectors.

Fixed source poses/endpoints remain. Independent wire grips carry wire loads.
MTA cases bear on shelves and use150mm cuttable Alpha lacing; WAGO backers
use nominal.5mm case-only adhesive, NEVER as wire strain relief or a claim of
adhesive/clip strength. No unknown board pads are clamped; delivery fit gates.
"""
import math
import FreeCAD as A
import Part
from loom_land_port import box
from current_bank_datums import bounds


def material(targets,allocation,leg_stations):
    parts={};bands={};pads={};rows=[];recipes={}
    strap_x={'FL':-8.,'FR':-69.5,'RL':130.,'RR':136.}
    for leg in ('FL','FR','RL','RR'):
        names=[n for n in targets if n.startswith('MTA/'+leg+'/')];assert len(names)==1
        own=names[0];a,b,z,X,B,Z=bounds(targets[own]);x=(a+X)/2;y=(b+B)/2;side=1 if y>0 else -1
        inward=b-1.2 if side==1 else B+1.2;outward=B+2 if side==1 else b-2
        low,high=sorted((inward,outward));floor=[a-2,low,z-2,X+2,high,z]
        keys=[[a-1.8,low,z-2,a-.3,high,z+1],[X+.3,low,z-2,X+1.8,high,z+1]]
        body=box(floor).multiFuse([box(v) for v in keys]).removeSplitter()
        cx=strap_x[leg];t=.381;w=1.6764
        inner=[cx-w,low,z-2,cx+w,high,Z];outer=[cx-w/2,low-t,z-2-t,cx+w/2,high+t,Z+t]
        band=box(outer).cut(box(inner));head=[cx-1.5,high+t,Z-6,cx+1.5,high+t+3,Z-4] if side==1 else [cx-1.5,low-t-3,Z-6,cx+1.5,low-t,Z-4]
        band=band.fuse(box(head)).removeSplitter()
        assert body.common(band).Volume<1e-5
        perimeter=2*(high-low+Z-(z-2));assert perimeter+50<=150
        key='MTACase_'+leg;parts[key]=body;bands[key]=band
        root=[x+(7 if leg=='FR' else -7),y,z-2]
        recipes[key]=dict(own_case=own,floor_mm=floor,keys_mm=keys,band_outer_mm=outer,band_inner_mm=inner,knot_mm=head,
            case_lacing='AlphaWire802534B',blank_mm=150,project_perimeter_mm=perimeter,knot_allowance_mm=50,
            fit_gate='Current project35x22x16 case envelope, not guaranteed supplier screw/pad/clip dimensions. Unpowered fit/hand supported cap change; cut case lace before opening cap.',root_goal_mm=root)
        rows.append(dict(id=key,body=body,goal=root,half=[2]*3,recipe=recipes[key],kind='MTA_case_shelf'))
    ends={e['id']:e for e in allocation['ends']}
    for wid in ('W026','W037','W041','W042','W044','W045','W052','W053'):
        names=[n for n in targets if n.split('/')[0]==wid+'_Joint'];assert len(names)==1,(wid,names)
        own=names[0];a,b,z,X,B,Z=bounds(targets[own])
        f=ends[wid+'/factory/end']['point_world_mm'];c=ends[wid+'/custom/start']['point_world_mm']
        assert abs(math.dist(f,c)-35.5)<1e-5
        vertical=abs(c[2]-f[2])>30
        if vertical:
            joint=leg_stations['factory_override']['joint'];assert wid=='W026'
            angle=joint['rotation_x_degrees'];assert abs(abs(angle)-90)<1e-6
            # Lever normal+Z rotates into -Y for+90X, and+Y for-90X.
            # Back the OPPOSITE face, never glue over operating levers.
            positive=angle>0
            lo,hi=(B+.5,B+2.5) if positive else (b-2.5,b-.5)
            floor=[a-2,lo,z-2,X+2,hi,Z+2]
            adhesive=[a, B if positive else b-.5,z,X,B+.5 if positive else b,Z]
            keys=[[a-1.8,lo,z-2,a-.3,hi,Z+2],[X+.3,lo,z-2,X+1.8,hi,Z+2]]
            root=[(a+X)/2,hi if positive else lo,(z+Z)/2]
        else:
            floor=[a-1.5,b-1.5,z-2.5,X+1.5,B+1.5,z-.5]
            adhesive=[a,b,z-.5,X,B,z]
            # Loose lower locating keys, well BELOW the lever-facing top.
            if X-a>B-b:keys=[[a-1.3,b-1.5,z-2.5,X+1.3,b-.3,z+.5],[a-1.3,B+.3,z-2.5,X+1.3,B+1.3,z+.5]]
            else:keys=[[a-1.3,b-1.5,z-2.5,a-.3,B+1.5,z+.5],[X+.3,b-1.5,z-2.5,X+1.3,B+1.5,z+.5]]
            root=[(a+X)/2,(b+B)/2,z-2.5]
        body=box(floor).multiFuse([box(v) for v in keys]).removeSplitter();key='SourceJoint_'+wid
        parts[key]=body;pads[key]=box(adhesive)
        recipes[key]=dict(own_case=own,floor_mm=floor,keys_mm=keys,adhesive_bounds_mm=adhesive,
            project_adhesive_thickness_mm=.5,lever_face_opposite_backer=True,vertical=vertical,
            adhesive_NOT_wire_restraint=True,root_goal_mm=root,
            fit_gate='Unpowered delivered case/backer/adhesive thickness and retention trial. Source wire ends have separate qualified insulation grips; no grip/adhesive strength assigned.')
        rows.append(dict(id=key,body=body,goal=root,half=[2]*3,recipe=recipes[key],kind='source_joint_case_backer'))
    for n,s in {**parts,**bands,**pads}.items():assert s.isValid() and len(s.Solids)==1 and not s.check(True),n
    assert len(parts)==12 and len(bands)==4 and len(pads)==8
    # Integral replacements, not twelve loose new prints. Assign the three
    # remote couplers to their nearby Frames so Upper remains printable.
    remote={'SourceJoint_W037':'FrontRightFixedCarrier',
            'SourceJoint_W045':'RearLeftFixedCarrier',
            'SourceJoint_W053':'RearRightFixedCarrier'}
    for r in rows:r['owner']=remote.get(r['id'],'UpperCarrier001')
    return dict(parts=parts,bands=bands,adhesive=pads,rows=rows,recipes=recipes,new_case_lacing_blanks=4,
        new_case_lacing_candidate_mm=600,new_separate_prints=0,selected=False,physical_pass=False)
