"""Shorten unused lower posts; reuse the57 unchanged clear R3 pairs.

No routing or placement search. Four posts now end at the raised beam base.
Exact installed-cache input bodies qualify the only two previous contacts.
Subtraction cannot introduce contacts; native/hardware/motion remain open.
"""
from pathlib import Path
from datetime import datetime,timezone
import json
from servo_fuse_inputs_r1 import sha,save
from w5_loom_common_layout import ROOT,BASE

PRIOR=BASE/'w5-loom-common-layout-r3';OUT=BASE/'w5-loom-frames-received-r1'
CACHE=BASE/'w5-installed-r52/owners.json'


def main():
    import FreeCAD as A,Part
    start=datetime.now(timezone.utc);assert not (OUT/'checks.json').exists()
    receipt=PRIOR/'checks.json';r=json.loads(receipt.read_text(encoding='utf-8'))
    wanted={'InputR4/release_0.0_W027_DESIGN','InputR4/release_0.0_W038_DESIGN'}
    assert r['pairs']==59 and len(r['hits'])==2 and not r['errors']
    assert {h['owner'] for h in r['hits']}==wanted
    assert all(sha(ROOT/k)==v for k,v in {**r['source_sha256'],**r['files']}.items())
    cache=json.loads(CACHE.read_text(encoding='utf-8'));cache_geometry=CACHE.parent/cache['geometry']
    for p in (CACHE,cache_geometry):assert sha(p)==r['source_sha256'][p.relative_to(ROOT).as_posix()]
    assert sha(cache_geometry)==cache['geometry_sha256']
    cached=Part.read(str(cache_geometry)).childShapes();owners={x['key']:cached[x['child_index']] for x in cache['rows'] if x['key'] in wanted}
    assert set(owners)==wanted
    source=PRIOR/'FOUR_FRAMES_AND_LANDINGS_PROPOSED_WORLD.brep'
    names=r['proposal_roles'];parts=dict(zip(names,Part.read(str(source)).childShapes()))
    blueprint_path=PRIOR/'plan.json';bp=json.loads(blueprint_path.read_text(encoding='utf-8'))
    coupled_path=PRIOR/'coupled-blueprint.json';cp=json.loads(coupled_path.read_text(encoding='utf-8'))
    assert cp['trunk_and_branch_z_mm']==[84.2,90.2]
    OUT.mkdir(parents=True,exist_ok=True);modified={};volume_checks={};trim_specs={}
    for leg,group in bp['blueprints'].items():
        key=leg+'FixedFrame';shape=parts[key];b=group['raw_boxes']['Post']
        assert b[2]==77 and b[5]==101
        trim=[*b[:2],77,*b[3:5],84.2]
        tool=Part.makeBox(*(trim[i+3]-trim[i] for i in range(3)),A.Vector(*trim[:3]))
        q=shape.cut(tool);assert q.isValid() and len(q.Solids)==1,key
        assert not (q.check(True) or []),key
        assert 0<shape.Volume-q.Volume<1000,key
        parts[key]=q;modified[key]=q;trim_specs[key]=trim
        group['raw_boxes']['Post'][2]=84.2
        volume_checks[key]=dict(before_mm3=shape.Volume,after_mm3=q.Volume,solid_count=1,BOP_errors=0,
                               new_post_base_mm=84.2,beam_base_mm=84.2)
        print('RECEIVED_FIXED_FRAME',key,'single_solid_BOP0',flush=True)
    pairs=[]
    for h in r['hits']:
        common=modified[h['proposal']].common(owners[h['owner']]);v=common.Volume
        assert v<1e-6,(h['proposal'],h['owner'],v)
        pairs.append(dict(proposal=h['proposal'],owner=h['owner'],actual_common_mm3=v,
                          prior_common_mm3=h['mm3'],source='unchanged installed R52 actual body'))
    bp.update(lower_unused_post_trims=trim_specs,coupled_correction=cp,
              changed_input_pairs=pairs,static_fixed_layout_received=True,
              native_complete=False,selected=False,W1_complete=False,W5_complete=False,physical_pass=False)
    geometry=OUT/'FOUR_FRAMES_AND_LANDINGS_RECEIVED_WORLD.brep'
    Part.makeCompound([parts[n] for n in names]).exportBrep(str(geometry))
    save(OUT/'native-blueprint.json',bp)
    finish=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='FOUR_FIXED_FRAMES_AND_LANDINGS_STATIC_RECEIVED_NATIVE_PENDING',
        input_changed_pairs=pairs,reused_clear_pair_count=57,modified_parts=volume_checks,
        receipt_scope='Four fixed frames/landings and R3 passive hood passage only; not all cat or moving range.',
        all_received_pairs_clear=True,material_subtraction_only=True,actual_Deck_joins_mm3=r['actual_Deck_join_mm3'],
        proposal_roles=names,native_complete=False,fasteners_tools_ties_moving_grips_pending=True,
        selected=False,W1_complete=False,W5_complete=False,physical_pass=False,
        started_utc=start.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-start).total_seconds(),
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in [Path(__file__),receipt,source,blueprint_path,coupled_path,CACHE,cache_geometry]},
        files={p.relative_to(ROOT).as_posix():sha(p) for p in [geometry,OUT/'native-blueprint.json']}))


if __name__=='__main__':main()
