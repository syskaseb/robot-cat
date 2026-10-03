"""One complete open-sided tray with a rear independent support bridge.

R1/R2 service openings removed the old raised connection. Replace that
connection with a3mm west bridge under the wire/terminal level, not with an
unprintable loose tray or a discarded solid. Keep all installed wires/ties
when checking the added bridge. Two exact nonzero embeds must join it to
both main bank and tray. No additional print, tie or screw.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_rr_output_service_native_r2.py')
wrapper=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert wrapper.rstrip().endswith(tail)
ns=dict(__file__=str(parent),__name__='definition_only')
exec(compile(wrapper.rstrip()[:-len(tail)],str(parent),'exec'),ns)
code=ns['code'].replace('servo-fuse-rr-output-service-native-r2','servo-fuse-rr-output-service-native-r3')
code=code.replace("    previous=ROOT/", "    pin(ROOT/'tools/electronics/servo_fuse_rr_output_service_native_r2.py')\n    pin(ROOT/'hardware/electronics/full-cat/servo-fuse-rr-output-service-native-r2/failure.json')\n    previous=ROOT/",1)
code=code.replace("            lo=hit['bounds_mm'][:3];hi=hit['bounds_mm'][3:]", "            lo=hit['bounds_mm'][:3];hi=hit['bounds_mm'][3:]\n            if k==2:lo[2]=117.5 # remove the obsolete disconnected strip too")
code=code.replace("f=d.addObject('Part::Cut','RROutputServiceFinished')", "f=d.addObject('Part::Cut','RRServiceOpeningsCut')")
at=code.index("        print('RR_SERVICE_NATIVE_RECOMPUTE'")
code=code[:at]+'''        cut=f
        bridge=d.addObject('Part::Box','RRTrayWestSupportBridge')
        bridge.Length=3;bridge.Width=13.7;bridge.Height=2.4
        bridge.Placement.Base=A.Vector(-70.2,-103.5,109.35)
        d.recompute()
        assert cut.Shape.isValid() and len(cut.Shape.Solids)==2
        embeds=[bridge.Shape.common(s).Volume for s in cut.Shape.Solids]
        assert all(v>1e-5 for v in embeds),embeds
        # Exact CURRENT installed owner set; intentional own-parent union
        # only. Check added material, not unchanged pair combinations.
        owner_source=ROOT/'tools/electronics/servo_fuse_rr_clip_approach_r1.py';pin(owner_source)
        ownercode=owner_source.read_text(encoding='utf-8')
        ownercode=ownercode[:ownercode.index('    # These boxes are exactly')]
        ownercode=ownercode.replace('servo-fuse-rr-clip-approach-r1','servo-fuse-rr-service-bridge-owner-load-r3')
        ownercode+='    return owners,pins,final\\n'
        ctx=dict(__file__=str(owner_source),__name__='load_only')
        exec(compile(ownercode,str(owner_source),'exec'),ctx)
        owners,ownerpins,_=ctx['main']();pins.update(ownerpins)
        bridge_hits=[];bridge_errors=[];bridge_pairs=0
        for key,s in owners.items():
            if key=='Bank/RightClipAccessFinished_WORLD':continue
            if not bridge.Shape.BoundBox.intersect(s.BoundBox):continue
            bridge_pairs+=1
            try:
                c=bridge.Shape.common(s)
                if c.Volume>1e-5:
                    bridge_hits.append(dict(owner=key,mm3=c.Volume))
                    c.exportBrep(str(OUT/f'BRIDGE_HIT_{len(bridge_hits)}.brep'))
            except Exception as e:bridge_errors.append(dict(owner=key,error=str(e)))
        save(OUT/'bridge-preflight.json',dict(embeds_mm3=embeds,pairs=bridge_pairs,hits=bridge_hits,errors=bridge_errors))
        print('RR_BRIDGE_PREFLIGHT',embeds,bridge_pairs,len(bridge_hits),flush=True)
        if bridge_hits or bridge_errors:return
        f=d.addObject('Part::MultiFuse','RROutputServiceFinished');f.Shapes=[cut,bridge];f.Refine=False
''' +code[at:]
code=code.replace('before=q.common(f.Base.Shape).Volume','before=q.common(d.RearOutputStationsFinished.Shape).Volume')
code=code.replace("retained_material=retained)","retained_material=retained,bridge_embeds_mm3=embeds,bridge_contact_pairs=bridge_pairs,bridge_hits=bridge_hits)")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
