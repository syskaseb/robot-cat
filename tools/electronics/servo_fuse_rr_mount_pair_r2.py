"""Whole fourth-mount redesign, not another shift of its screw alone.

R1 wide foot/flat shoulder intersected two actual TE-OUT ends, the lower
input loop, RR housing tie and Cover. Keep the outboard Y datum but replace
the entire foot/post/washer footprint by the gap between the two TE ends;
fork the Deck shoulder around fixed ties. Tools/lift use the explicit
holder/terminal release stage, never the still-installed holder boxes.
"""
from pathlib import Path

parent = Path(__file__).with_name('servo_fuse_rr_mount_pair_r1.py')
code = parent.read_text(encoding='utf-8')


def replace(old, new):
    global code
    assert old in code, old[:100]
    code = code.replace(old, new)


replace('servo-fuse-rr-mount-pair-r1', 'servo-fuse-rr-mount-pair-r2')
replace("    pins[loader.relative_to(ROOT).as_posix()] = sha(loader)",
        "    pins[loader.relative_to(ROOT).as_posix()] = sha(loader)\n    pins['tools/electronics/servo_fuse_rr_mount_pair_r1.py'] = sha(ROOT/'tools/electronics/servo_fuse_rr_mount_pair_r1.py')")
replace("    foot = oldfoot.copy(); foot.translate(A.Vector(0, shift, 0))\n    post = oldpost.copy(); post.translate(A.Vector(0, shift, 0))\n    axis = [-63., -108.5]",
        "    foot = box([-63., -113., 109., -51., -105., 113.])\n    post = oldpost.copy(); post.translate(A.Vector(3, shift, 0))\n    axis = [-60., -108.5]")
replace("    ledge_bounds = [-73., -117., 105., -48., -92., 109.]\n    ledge = box(ledge_bounds).cut(hole)",
        "    ledge_bounds = [-63.5, -114., 105., -50.5, -93., 109.]\n    fork_boxes = [[-63.5,-114.,105.,-50.5,-103.,109.],[-63.5,-106.,105.,-61.5,-93.,109.],[-53.,-106.,105.,-50.5,-93.,109.]]\n    ledge = box(fork_boxes[0]).multiFuse([box(b) for b in fork_boxes[1:]]).cut(hole)\n    fork_embed = [box(b).common(deck).Volume for b in fork_boxes[1:]]\n    assert all(v>1e-5 for v in fork_embed),fork_embed")
replace("NutTool=cyl(x,y,nut_z-20,3.5,20).cut(cyl(x,y,nut_z-20.1,1.1,20.2)))",
        "NutTool=cyl(x,y,nut_z-4,3.5,4).cut(cyl(x,y,nut_z-4.1,1.1,4.2)))")
replace("    for name,s in tools.items():\n        for key,t in dict(owners,**module,DeckLedge=ledge).items(): check('tool_access',name,s,key,t)",
        """    released = dict(owners)
    removed=[];parked=[];inputs=[]
    for key in list(released):
        ident=key.rsplit('/',1)[-1]
        if ident.startswith('F_') and (ident.endswith('_ATO_DESIGN') or (ident.endswith('_DESIGN') and ident.count('_')==2)):
            removed.append(key);del released[key]
        elif ident.startswith('F_') and ident.endswith(('_IN_DESIGN','_OUT_DESIGN')):
            released[key]=load('hardware/electronics/full-cat/servo-fuse-bank-service-r3/'+ident+'_PARKED.brep');parked.append(key)
        elif 'release_0.0_W' in key:
            rel=next(r for r in pins if r.endswith(ident+'.brep'))
            released[key]=load(rel.replace('release_0.0_','release_1.0_'));inputs.append(key)
    assert len(removed)==24 and len(parked)==24 and len(inputs)==12,(removed,parked,inputs)
    for name,s in tools.items():
        for key,t in dict(released,**module,DeckLedge=ledge).items(): check('tool_access_AFTER_holder_terminal_release',name,s,key,t)""")
replace("        for key,t in owners.items(): check('continuous_changed_mount_100mm',name,sweep,key,t)",
        "        for key,t in released.items(): check('continuous_changed_mount_100mm',name,sweep,key,t)")
replace("actual_parent_embed_mm3=embedded,washer_bearing_missing_mm3=bearing_missing,",
        "actual_parent_embed_mm3=embedded,full_fork_embeds_mm3=fork_embed,fork_boxes_mm=fork_boxes,washer_bearing_missing_mm3=bearing_missing,\n        released_holder_ATO_count=24,parked_TE_count=24,released_input_count=12,tool_order='Release24TE/remove12mini+12ATO before unbolting4bank mounts; short4mm nut access below,28mm Allen above.',")
exec(compile(code, str(Path(__file__).resolve()), 'exec'))
