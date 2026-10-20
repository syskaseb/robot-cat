"""Keep the whole source gallery; turn custom wire away from RL_G and F0.

Whole output, not a tie-head clock. An inward+rearward direction lies between
the F0 diagonal face and rear belly-footX108.5; retain the same R25.2/full9.
"""
import hashlib,itertools,json,math,zipfile
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from plan_feline_battery_f0_joint import path
from plan_feline_n01_shared import pipe
from receive_feline_source_joint import receive


def construction(parts,ends):
    source=OUT/'n01-BAT-F0-side-gallery.json';r=json.loads(source.read_text())
    assert r['status']=='SHARED_SOURCE_REJECTED_NO_DETAIL' and r['failures']==['W076_custom_prefix|Station:RL_G:wire:RL_G.4']
    for p,h in r['source_sha256'].items():assert sha(ROOT/p)==h,p
    assert sha(ROOT/r['bundle'])==r['bundle_sha256']
    actors={}
    with zipfile.ZipFile(ROOT/r['bundle']) as z:
        for n,row in r['geometry'].items():
            raw=z.read(row['entry']);assert hashlib.sha256(raw).hexdigest()==row['sha256']
            s=Part.Shape();s.importBrepFromString(raw.decode());actors[n]=s
    names={'F0':'Ref_Material_F0_CP2_0_0','XT60':'Ref_Material_XT60_CP2_0_0','POST':'Ref_Material_PostF0Splice_CP2_0_0'}
    p=r['current_nominal_datums']['POST2'];R=25.2;grip=9.;radius=2.1;margin=1.25
    # A sufficient endpoint domain, not an assertion about an untested whole
    # wire. Actual full F0/foot/world pairs are still received below.
    maxsin=(108.5-radius-margin-p[0])/(R+grip)
    maximum=math.degrees(math.asin(maxsin));angle=30.
    assert 0<angle<maximum
    d=[math.sin(math.radians(angle)),-math.cos(math.radians(angle)),0]
    recipes=dict(r['recipes']);recipes['W076_custom_prefix']=path(p,[0,0,-1],[('turn',d),('line',grip)],R)
    actors['W076_custom_prefix']=pipe(recipes['W076_custom_prefix']['parts'],radius)
    mouths={frozenset((names['F0'],n)) for n in ('W075_factory','W076_factory')}
    mouths.update(frozenset((names['XT60'],n)) for n in ('W075_factory','W001_ground_prefix'))
    mouths.update(frozenset((names['POST'],n)) for n in ('W076_factory','W076_custom_prefix'))
    own={}
    for a,b in itertools.combinations(actors,2):
        s,t=actors[a],actors[b];minimum=0. if frozenset((a,b)) in mouths else margin
        gap=s.distToShape(t)[0];c=s.common(t);assert c.isNull() or c.isValid()
        own[a+'|'+b]=dict(ok=gap>=minimum-1e-6 and c.Volume<1e-5,gap_mm=gap,minimum_mm=minimum,common_mm3=c.Volume,exact_own_mouth=frozenset((a,b)) in mouths)
    inherited=set(actors)-{'W076_custom_prefix'}
    return actors,recipes,own,names,r['current_nominal_datums'],dict(unchanged_existing_body_names=sorted(inherited),
        inherited_static_proof=dict(path=source.relative_to(ROOT).as_posix(),sha256=sha(source),bundle=r['bundle'],bundle_sha256=r['bundle_sha256'],
            checked_actor_names=sorted(inherited-{names['F0']}),unchanged_base_F0_not_a_new_clearance_claim=True),
        changed_actor_names=['W076_custom_prefix'],custom_exit_clock=dict(degrees_from_inwardY_toward_rearX=angle,
            endpoint_rear_foot_sufficient_maximum_deg=maximum,domain_NOT_whole_wire_acceptance=True),
        independent_earlier9mm_arc_grip_needed_not_last9mm_over_FHAC=True)


if __name__=='__main__':receive(construction,Path(__file__),'n01-BAT-F0-inward-exit.json')
