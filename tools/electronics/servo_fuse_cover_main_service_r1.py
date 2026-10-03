"""One bottom-open Cover service layout for all retained main feeds/straps.

Conservative rectangular service space is an explicit design allowance, not
a claimed contact witness. Preserve the old Cover, exact wires and mounts.
Reject any disconnected result; do not pick a largest fragment.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_cover_rr_fixed_service_r1.py')
code=parent.read_text(encoding='utf-8')
def replace(old,new):
    global code
    assert old in code,old[:100]
    code=code.replace(old,new)
replace('servo-fuse-cover-rr-fixed-service-r1','servo-fuse-cover-main-service-r1')
replace("fail=read('hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r7/checks.json')", "fail=read('hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r8/checks.json')")
replace("fail['hits'][0]['owner']=='CandidateDeck'", "fail['hits'][0]['owner']=='W045/extension'")
replace("native=read('hardware/electronics/full-cat/servo-fuse-fr-source-fixed-deck-native-r2/checks.json')", "native=read('hardware/electronics/full-cat/servo-fuse-cover-rr-fixed-service-r1/checks.json')")
replace("dest=CAD/'CoverRRFixedService.FCStd'", "dest=CAD/'CoverMainService.FCStd'")
begin=code.index("        parent=d.getObject(row['final']);b=list(outline)")
end=code.index("        print('COVER_RR_OPEN_BOTTOM_RECOMPUTE'",begin)
code=code[:begin]+'''        parent=d.getObject(row['final'])
        # Read the completed R8 recipe without rerunning its collision loop.
        lp=ROOT/'tools/electronics/servo_fuse_bank_fixed_rr_lift_r8.py'
        scope=dict(__file__=str(lp),__name__='definition_only')
        raw=lp.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
        assert raw.rstrip().endswith(tail)
        exec(compile(raw.rstrip()[:-len(tail)],str(lp),'exec'),scope)
        ownerscode=scope['code'];ownerscode=ownerscode[:ownerscode.index("    save(OUT/'owner-census.json'")]+"    return owners,module,pins\\n"
        ownerscode=ownerscode.replace("    assert not (OUT/'checks.json').exists(),'Preserve result'",'    # Read-only current owner receipt.')
        marker="    ns=dict(__file__=str(loader),__name__='owners_only');"
        assert marker in ownerscode
        ownerscode=ownerscode.replace(marker,"    code=code.replace(\\\"    assert not (out / 'checks.json').exists(), 'Preserve completed results'\\\",'    # Read-only owner receipt.')\\n"+marker)
        ctx=dict(__file__=str(lp),__name__='read_only_owners')
        exec(compile(ownerscode,str(lp),'exec'),ctx)
        owners,module,ownerpins=ctx['main']();pins.update(ownerpins);pins[lp.relative_to(ROOT).as_posix()]=sha(lp)
        chosen={k:s for k,s in owners.items() if
            (k.startswith(('RLSource/','RRSource/','RetainedFeed/','AcceptedFR/','W045/','W053/'))
             and 'Bare' not in k and 'Solder' not in k and 'Sleeve' not in k)
            or k.startswith(('FRTie/','RLTie/','RRTie/','PWagoTie/'))}
        p=d.addObject('App::VarSet','MainFeedServiceParameters');p.addProperty('App::PropertyLength','Allowance');p.Allowance=.3
        tools=[];b=[];covered=[]
        bottom=parent.Shape.BoundBox.ZMin-.1
        for index,(key,s) in enumerate(chosen.items()):
            q=s.BoundBox
            if q.ZMax<=bottom:continue
            dims=[q.XLength,q.YLength,q.ZMax-bottom]
            if any(v<=0 for v in dims):continue
            tool=d.addObject('Part::Box','MainServicePassage'+str(index))
            tool.addProperty('App::PropertyString','RetainedOwner');tool.RetainedOwner=key
            for prop,val in zip(('Length','Width','Height'),dims):
                tool.setExpression(prop,f'{val} mm + 2*MainFeedServiceParameters.Allowance')
            for axis,val in zip(('x','y','z'),(q.XMin,q.YMin,bottom)):
                tool.setExpression('Placement.Base.'+axis,f'{val} mm - MainFeedServiceParameters.Allowance')
            tools.append(tool);covered.append(key);b.append([q.XMin-.3,q.YMin-.3,bottom-.3,q.XMax+.3,q.YMax+.3,q.ZMax+.3])
        assert len(tools)>20
        compound=d.addObject('Part::Compound','MainServicePassageTools');compound.Links=tools
        final=d.addObject('Part::Cut','CoverMainServiceFinished');final.Base=parent;final.Tool=compound;final.Refine=False
'''+code[end:]
replace("p.Allowance=.4;d.recompute();vp=final.Shape.Volume", "p.Allowance=.4;d.recompute();vp=final.Shape.Volume")
replace("existing_upper_window_preserved=True,added_parts=0,assembly_ties_cut=33,", "existing_upper_window_preserved=True,added_parts=0,assembly_ties_cut=33,covered_stationary_owners=covered,allowance_basis='Conservative whole-owner rectangles for downward service; not measured contact bounds',")
replace("status='NATIVE_COVER_RR_FULL_BOTTOM_SERVICE_COMPLETE_SHARED_REMOVAL_OPEN'", "status='NATIVE_COVER_MAIN_FEED_BOTTOM_SERVICE_COMPLETE_SHARED_REMOVAL_OPEN'")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
