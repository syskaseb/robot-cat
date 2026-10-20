"""Change the single blocked F0 plate crossing to an external-side gallery.

Keep F0, XT60, positive full factory lead and negative prefix from the received
rear-gap hypothesis. Whole POST fits BETWEEN P0 outer49.34 and foundation
flange bottom30.52; rotate its service face outwardsX, not into the frame.
"""
import itertools,json,math,zipfile
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from plan_feline_battery_f0_joint import path,pose
from plan_feline_n01_shared import pipe
from receive_feline_source_joint import receive


def construction(parts,ends):
    source=OUT/'n01-BAT-F0-rear-gap-joint.json';r=json.loads(source.read_text())
    assert r['status']=='SHARED_SOURCE_REJECTED_NO_DETAIL' and r['failures']==['W076_factory|Print_P0_BATTERY_PLATE_R4']
    for p,h in r['source_sha256'].items():assert sha(ROOT/p)==h,p
    assert sha(ROOT/r['bundle'])==r['bundle_sha256']
    actors={};raws={}
    with zipfile.ZipFile(ROOT/r['bundle']) as z:
        for n,row in r['geometry'].items():
            raw=z.read(row['entry']);assert __import__('hashlib').sha256(raw).hexdigest()==row['sha256']
            s=Part.Shape();s.importBrepFromString(raw.decode());actors[n]=s;raws[n]=raw
    names={'F0':'Ref_Material_F0_CP2_0_0','XT60':'Ref_Material_XT60_CP2_0_0','POST':'Ref_Material_PostF0Splice_CP2_0_0'}
    p=A.Vector(*r['current_nominal_datums']['F0_out']);u=A.Vector(2**-.5,2**-.5,0);v=A.Vector(-2**-.5,2**-.5,0)
    R=12.4;angle=math.pi/4
    at=lambda a:p+u*(R*math.sin(a))+v*(R*(1-math.cos(a)))
    q=at(angle);rows=[dict(kind='arc',start=list(p),mid=list(at(angle/2)),end=list(q),R_mm=R)]
    # Rise OUTSIDE the whole side web, not through the battery plate.
    # POST top29.25 leaves1.27 below source foundation-flange30.52.
    postY=56.1;postZ=10.25
    lowerY=postY-R;straight=lowerY-q.y;assert straight>0
    more=path(list(q),[0,1,0],[('line',straight),('turn',[0,0,1]),('line',postZ-(p.z+R))],R)
    rows.extend(more['parts']);post1=A.Vector(*more['end'])
    rotation=A.Rotation(A.Vector(0,0,1),90)*A.Rotation(A.Vector(1,0,0),90)
    centre=post1-A.Vector(1.5,0,-9.5)
    actors[names['POST']],tf=pose(parts[names['POST']],[143.000000762939,-35,42],rotation,list(centre))
    assert (tf.multVec(A.Vector(*ends['W076/retained0/end']['point_mm']))-post1).Length<1e-5
    post2=tf.multVec(A.Vector(*ends['W076/retained1/start']['point_mm']))
    recipes=dict(r['recipes']);recipes['W076_factory']=dict(parts=rows,length_mm=R*angle+more['length_mm'],minimum_R_mm=R)
    recipes['W076_custom_prefix']=path(list(post2),[0,0,-1],[('turn',[-1,0,0]),('line',9)],25.2)
    for n in ('W076_factory','W076_custom_prefix'):actors[n]=pipe(recipes[n]['parts'],1.55 if n.endswith('factory') else 2.1)
    assert recipes['W076_factory']['length_mm']+21<=84.5 # extra5mm provisional supply allowance; not a supplier tolerance claim
    mouths={frozenset((names['F0'],n)) for n in ('W075_factory','W076_factory')}
    mouths.update(frozenset((names['XT60'],n)) for n in ('W075_factory','W001_ground_prefix'))
    mouths.update(frozenset((names['POST'],n)) for n in ('W076_factory','W076_custom_prefix'))
    own={}
    for a,b in itertools.combinations(actors,2):
        s,t=actors[a],actors[b];minimum=0. if frozenset((a,b)) in mouths else 1.25
        gap=s.distToShape(t)[0];c=s.common(t);assert c.isNull() or c.isValid()
        own[a+'|'+b]=dict(ok=gap>=minimum-1e-6 and c.Volume<1e-5,gap_mm=gap,minimum_mm=minimum,common_mm3=c.Volume,exact_own_mouth=frozenset((a,b)) in mouths)
    datums=dict(r['current_nominal_datums'],POST1=list(post1),POST2=list(post2))
    changed={names['POST'],'W076_factory','W076_custom_prefix'};inherited=set(actors)-changed
    return actors,recipes,own,names,datums,dict(unchanged_existing_body_names=sorted(inherited),
        unchanged_source_geometry_loaded_from_pinned_archive=True,
        inherited_static_proof=dict(path=source.relative_to(ROOT).as_posix(),sha256=sha(source),bundle=r['bundle'],bundle_sha256=r['bundle_sha256'],
            actors=sorted(inherited),all_previous_fixed_checks_for_inherited_actors_positive=True),
        source_plate_crossing_changed_to_outside_side_web=True,project_supply_allowance5mm_NOT_supplier_tolerance=True,
        no_new_connector_cut_or_purchase=True)


if __name__=='__main__':receive(construction,Path(__file__),'n01-BAT-F0-side-gallery.json')
