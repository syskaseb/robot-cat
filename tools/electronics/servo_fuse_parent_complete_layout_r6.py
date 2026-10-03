"""Prepare corrected end details and batch new native booleans on the SAME layout.

Do not run while R5 is active. R5 witnesses remain immutable; no previously
rejected outboard/carrier geometry is retried. This fixes analytical issues
in FR height/strip representation and avoids24 serial expensive Deck cuts.
"""
from pathlib import Path
base=Path(__file__).with_name('servo_fuse_parent_complete_layout_r5.py')
code=base.read_text(encoding='utf-8')


def replace(old,new):
    global code
    assert code.count(old)==1,old[:80]
    code=code.replace(old,new)


code=code.replace('servo-fuse-parent-complete-layout-r5','servo-fuse-parent-complete-layout-r6')
replace('owners,extra,_=layout.current_owners(); pins.update(extra)', '''# Reuse exact retained source recipe, replacing only the redundant
    # coincident-tail Boolean with equality of serialized current BREP.
    # A differing serialization fails loudly; no retained obstacle is hidden.
    import types
    helper=ROOT/'tools/electronics/servo_fuse_side_bank_r10.py'
    helper_ns={'__file__':str(helper),'__name__':'layout_definition_only'}
    loader=helper.read_text(encoding='utf-8').rsplit('exec(compile',1)[0]
    exec(compile(loader,str(helper),'exec'),helper_ns)
    owner_code=helper_ns['code']
    old_check='        assert a.cut(b).Volume+b.cut(a).Volume<1e-5'
    new_check="""        from tempfile import TemporaryDirectory
        with TemporaryDirectory(prefix='robot-cat-retained-tail-') as td:
            pa=Path(td)/'a.brep';pb=Path(td)/'b.brep'
            a.exportBrep(str(pa));b.exportBrep(str(pb))
            assert sha(pa)==sha(pb), 'Retained tail copies differ; do not hide a changed obstacle'
        print('RETAINED_TAIL_IDENTICAL_SERIALIZATION',flush=True)"""
    assert owner_code.count(old_check)==1
    owner_code=owner_code.replace(old_check,new_check)
    cached=types.ModuleType('servo_fuse_same_retained_owners');cached.__file__=str(helper)
    exec(compile(owner_code,str(helper),'exec'),cached.__dict__)
    pin(helper);pin(ROOT/'tools/electronics/servo_fuse_side_bank_r8.py')
    owners,extra,_=cached.current_owners();pins.update(extra)''')
replace("assert not (OUT/'checks.json').exists(), 'Preserve completed evidence'",
    "assert not (OUT/'checks.json').exists(), 'Preserve completed evidence'\n    previous_result=ROOT/'hardware/electronics/full-cat/servo-fuse-parent-complete-layout-r5/checks.json'\n    if not previous_result.exists(): previous_result=previous_result.with_name('aborted-worker.json')\n    assert previous_result.exists(), 'Receive or stop own R5 worker first; do not duplicate'")
replace('    V = A.Vector',
    "    V = A.Vector\n    pin(previous_result)\n    pin(ROOT/'tools/electronics/servo_fuse_parent_complete_layout_r5.py')\n    pin(ROOT/'hardware/electronics/full-cat/pi-interface-final-r2/suppliers.json')")
replace("path,tube=r.shape(od,tangent); routes[name]=tube; changed[name]=tube",
    "path,tube=r.shape(od,tangent); routes[name]=tube; changed[name]=tube\n        trim=9 if name in ('W045','W053') else 10")
# Preserve output geometry;100mm is provisional and9mm is an explicit trim
# allowance, not a supplied-length measurement or a claimed tolerance margin.
code=code.replace('strip_allowance_mm=strip,trim_reserve_mm=10,','strip_allowance_mm=strip,trim_reserve_mm=trim,')
code=code.replace('math.ceil((path.Length+strip+10)/10)*10','math.ceil((path.Length+strip+trim)/10)*10')
replace('r.line([right+6,cy,cz]); r.arc(X,-Y,20); r.line([25,-60,cz])',
    'r.line([right+6,cy,cz]); r.arc(X,-Y,20); r.shift(-Y,Z*5,20); r.line([25,-40,127.5])')
replace("changed[leg+'_221412']=box([21.75,-60,118.5,34.75,-41.7,126.65])",
    "changed[leg+'_221412']=box([21.75,-40,123.5,34.75,-21.7,131.65])")
replace('e.line([56.7,-100,cz]); e.arc(-X,V(0,1,0),25.2); e.line([31.5,-60,cz])',
    'e.line([56.7,-100,cz]); e.arc(-X,V(0,1,0),25.2); e.shift(V(0,1,0),Z*5,25.2); e.line([31.5,-40,127.5])')
replace('mouth_datums_mm=[[25,-60,122.5],[31.5,-60,122.5]]',
    'mouth_datums_mm=[[25,-40,127.5],[31.5,-40,127.5]]')
replace('r.line([right+6,cy,cz]); r.arc(X,-Y,21.2); r.line([135.2,side*33,cz])',
    'r.line([right+6,cy,cz]); r.arc(X,-Y,21.2); r.line([135.2,side*44,cz])')
replace('e.line([110,source_y,cz]); e.arc(X,Y,25.2); e.line([135.2,side*47,cz])',
    'e.line([110,source_y,cz]); e.arc(X,Y,25.2); e.line([135.2,side*36,cz])')
replace('sleeve=Part.makeCylinder(4.5,26,V(135.2,side*27,cz),Y)',
    """sleeve=Part.makeCylinder(4.5,26,V(135.2,side*27,cz),Y).cut(
                Part.makeCylinder(2.5,26.2,V(135.2,side*26.9,cz),Y))
            # Distinct bare conductors and metal overlap, not two insulated
            # cylinders occupying one another. Equivalent solid4mm2 Cu is a
            # clearance model, NOT measured strand deformation.
            for suffix,dx in [('BareFactory',1.15),('BareExtension',-1.15)]:
                changed[leg+'_'+suffix]=Part.makeCylinder(math.sqrt(4/math.pi),8,V(135.2+dx,side*36,cz),Y)
            changed[leg+'_SolderCore']=Part.makeCylinder(2.4,8,V(135.2,side*36,cz),Y)""")
replace("existing_shrink='Botland5375 assortment13mm'",
    "existing_shrink='TE5053142077 RNF-100-3/8-0-STK, selected6m stock, expanded9.5/recovered4.8mm;52mm blanks+52mm trialspares candidate, no extra package'")
replace('Slide13mm sleeve first;8mm opposing bare copper lap',
    'Slide selected TE3/8 sleeve first;8mm opposing bare copper lap')
replace('shrink13mm_blank_mm=52','shrink_TE3_8_blank_mm=52')
start=code.index('        for leg,b in seats:')
end=code.index("        previous.Label='Four integral main fuse saddles (UNSELECTED)'",start)
code=code[:start]+'''        pads=[]; slots=[]
        print('NATIVE_BATCH_START',flush=True)
        for leg,b in seats:
            pad=d.addObject('Part::Box',leg+'MainPad');pad.Length=b[3]-b[0];pad.Width=b[4]-b[1];pad.Height=b[5]-b[2];pad.Placement.Base=V(*b[:3])
            pad.setExpression('Height','MainHolderParameters.PadHeight');pads.append(pad)
            sgn=1 if leg.endswith('L') else -1
            cx=-18.5 if leg.startswith('F') else 90.5
            for j,x in enumerate((cx-9,cx+9)):
                for k,ya in enumerate((78.3,95.5)):
                    low,high=sorted((sgn*ya,sgn*(ya+1.2)))
                    tool=d.addObject('Part::Box',leg+'TieSlot'+str(j)+str(k));tool.Length=2.9;tool.Width=1.6;tool.Height=8
                    tool.Placement.Base=V(x-1.45,low-.2,104);slots.append(tool)
                low,high=sorted((sgn*79.5,sgn*95.5))
                tool=d.addObject('Part::Box',leg+'UnderTie'+str(j));tool.Length=2.9;tool.Width=high-low;tool.Height=1.7
                tool.Placement.Base=V(x-1.45,low,107.4);slots.append(tool)
        fused=d.addObject('Part::MultiFuse','AllFourMainSeats');fused.Shapes=[previous]+pads;fused.Refine=True
        tools=d.addObject('Part::Compound','AllMainTiePassTools');tools.Links=slots
        previous=d.addObject('Part::Cut','MainTiePassFinished');previous.Base=fused;previous.Tool=tools;previous.Refine=True
''' + code[end:]
replace("par.PadHeight=2.9;d.recompute();probe=previous.Shape.Volume;assert probe>volume",
    "print('NATIVE_INITIAL_RECOMPUTE_FINISHED',flush=True)\n        par.PadHeight=2.9;d.recompute();probe=previous.Shape.Volume;assert probe>volume\n        print('NATIVE_PARAMETER_PROBE_FINISHED',flush=True)")
replace("for n in (w+'_factory',w+'_extension'):intended.add(frozenset((leg+'_splice_insulation',n)))\n        intended.add(frozenset((w+'_factory',w+'_extension')))",
    "for suffix in ('BareFactory','BareExtension'):intended.add(frozenset((leg+'_'+suffix,leg+'_SolderCore')))\n        # No insulated-wire overlap waiver in corrected R6.")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
