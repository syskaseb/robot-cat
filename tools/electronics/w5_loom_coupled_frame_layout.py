"""One complete lower frame/landing/hood correction from the received map.

Do NOT sever the rail with a tie or hood contact pocket. All four trunks and
branches pass above the fixed input-tie envelope; one defined passive hood
passage receives the RL rail. Landings/foot toes receive the complete remaining
R2 contact reliefs together. No received cable moves. Native/selection pending.
"""
from pathlib import Path
import json
from servo_fuse_inputs_r1 import sha
from w5_loom_common_layout import ROOT,BASE

PRIOR=BASE/'w5-loom-common-layout-r2/checks.json'


def main():
    r=json.loads(PRIOR.read_text(encoding='utf-8'));assert not r['errors'] and len(r['hits'])==15
    source_file=Path(__file__).with_name('w5_loom_common_layout.py')
    received_file=Path(__file__).with_name('w5_loom_outboard_layout.py')
    assert all(sha(ROOT/k)==v for k,v in {**r['source_sha256'],**r['files']}.items())
    code=received_file.read_text(encoding='utf-8')
    # Reuse the exact received geometric definitions, not a changed parent.
    start=code.index('    changes={');end=code.index('\n    for old,new',start)
    ctx={};exec(code[start:end].strip(),ctx);changes=ctx['changes']
    source=source_file.read_text(encoding='utf-8')
    for old,new in changes.items():
        assert source.count(old)==1;source=source.replace(old,new)
    source=source.replace("OUT=BASE/'w5-loom-common-layout-r2'","OUT=BASE/'w5-loom-common-layout-r3'")
    source=source.replace("ry-4,77,max(post_x,xext)+4,ry+4,83]","ry-4,84.2,max(post_x,xext)+4,ry+4,90.2]")
    source=source.replace("min(ry,outer_y)-4,77,xext+4,max(ry,outer_y)+4,83]","min(ry,outer_y)-4,84.2,xext+4,max(ry,outer_y)+4,90.2]")
    source=source.replace("y-4,77,max(xext,x)+4,y+4,83]","y-4,84.2,max(xext,x)+4,y+4,90.2]")
    assert source.count('84.2')==3 and source.count('90.2')==3
    # Material-only reliefs cannot introduce new contacts. Do not relief a
    # trunk into separate solids: actual input ties are bypassed above instead.
    old="        proposals[leg+'FixedFrame']=frame"
    new="""        landing_reliefs=[];foot_reliefs=[]
        for hit in _received['hits']:
            if hit['proposal']==leg+'DeckLanding' or (hit['proposal']==leg+'FixedFrame' and '/F_'+leg+'1_OUT_DESIGN' in hit['owner']):
                b=hit['bounds_mm'];expanded=[v-.5 for v in b[:3]]+[v+.5 for v in b[3:]]
                item=box(expanded)
                (landing_reliefs if hit['proposal'].endswith('DeckLanding') else foot_reliefs).append(item)
                _relief_specs.setdefault(hit['proposal'],[]).append(dict(owner=hit['owner'],bounds_mm=expanded))
        if landing_reliefs:proposals[leg+'DeckLanding']=pad.cut(Part.makeCompound(landing_reliefs))
        joins[leg]=proposals[leg+'DeckLanding'].common(deck).Volume
        assert joins[leg]>1 and len(proposals[leg+'DeckLanding'].Solids)==1,('Lost integral pad material',leg)
        if foot_reliefs:frame=frame.cut(Part.makeCompound(foot_reliefs))
        assert frame.isValid() and len(frame.Solids)==1,('Severed frame',leg)
        proposals[leg+'FixedFrame']=frame"""
    assert source.count(old)==1;source=source.replace(old,new)
    marker="    rows=read(CORRIDORS)['routes'];"
    replacement="""    hood=printed['SourceEastHood']
    hood_tool=Part.makeBox(3.4,9,7,A.Vector(191.1,102.5,83.7))
    hood_cut=hood.cut(hood_tool)
    assert hood_cut.isValid() and len(hood_cut.Solids)==1,'RL hood passage severed owner'
    printed['SourceEastHood']=hood_cut
    hood_path=OUT/'EastHood_RL_FRAME_PASSAGE_UNSELECTED_WORLD.brep';hood_cut.exportBrep(str(hood_path))
    save(OUT/'coupled-blueprint.json',dict(hood_tool_box_mm=[191.1,102.5,83.7,194.5,111.5,90.7],
        trunk_and_branch_z_mm=[84.2,90.2],relief_specs=_relief_specs,native_pending=True,selected=False,physical_pass=False))
    rows=read(CORRIDORS)['routes'];"""
    assert source.count(marker)==1;source=source.replace(marker,replacement)
    source=source.replace("pins.extend([Path(__file__),_base_source,_prior_proof,CORRIDORS,BEARING,SIDE,N.CENTRAL])",
        "pins.extend([Path(__file__),_base_source,_receiver_source,_prior_proof,CORRIDORS,BEARING,SIDE,N.CENTRAL])")
    source=source.replace("files={q.relative_to(ROOT).as_posix():sha(q) for q in [p,OUT/'plan.json']}",
        "files={q.relative_to(ROOT).as_posix():sha(q) for q in [p,OUT/'plan.json',hood_path,OUT/'coupled-blueprint.json']}")
    source=source.replace("    names=list(proposals);p=", "    save(OUT/'coupled-blueprint.json',dict(hood_tool_box_mm=[191.1,102.5,83.7,194.5,111.5,90.7],trunk_and_branch_z_mm=[84.2,90.2],relief_specs=_relief_specs,native_pending=True,selected=False,physical_pass=False))\n    names=list(proposals);p=")
    ctx=dict(__file__=str(Path(__file__).resolve()),__name__='coupled_frame_receive',_received=r,
             _base_source=source_file,_receiver_source=received_file,_prior_proof=PRIOR,_relief_specs={})
    exec(compile(source,str(source_file),'exec'),ctx);ctx['main']()


if __name__=='__main__':main()
