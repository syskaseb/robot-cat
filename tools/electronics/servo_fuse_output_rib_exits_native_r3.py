"""Replace complete lower seat with an upper keeper, on ALL12 output exits.

Unlike R2, no old lower saddle remains to trap the wire or cinch band. A
small upper bridge retains the wire by the same T18I loop, cinched upwards.
All overlapping native cutters are UNIONED before the cut, not compounded.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_output_rib_exits_native_r2.py')
wrapper=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert wrapper.rstrip().endswith(tail)
ns=dict(__file__=str(parent),__name__='rib_r2_definition_only')
exec(compile(wrapper.rstrip()[:-len(tail)],str(parent),'exec'),ns)
code=ns['code']
def replace(old,new):
    global code
    assert old in code,old[:100]
    code=code.replace(old,new)
replace('servo-fuse-output-rib-exits-native-r2','servo-fuse-output-rib-exits-native-r3')
replace('    pins={}',"    pins={}\n    pins['tools/electronics/servo_fuse_output_rib_exits_native_r1.py']=sha(ROOT/'tools/electronics/servo_fuse_output_rib_exits_native_r1.py')")
replace('q.Length=diam;q.Width=seat.YLength+.2;', 'diam=seat.XLength+.2\n                q.Length=diam;q.Width=seat.YLength+.2;')
replace("                    tools.append(boxobj(ident+'UpperCinchSlot'+str(i),[cx+dx-1,sy0,rb.ZMin-.2,cx+dx+1,sy1,cz+3.9]))", """                    slot=boxobj(ident+'UpperCinchSlot'+str(i),[cx+dx-1,sy0,rb.ZMin-.2,cx+dx+1,sy1,cz+3.9])
                    slot.setExpression('Length','2 mm + OutputExitParameters.ExtraWidth')
                    slot.setExpression('Placement.Base.x',f'{cx+dx-1} mm - OutputExitParameters.ExtraWidth/2')
                    tools.append(slot)""")
replace('assert min(legs)>=2.19 and cz+float(hole.Radius)<rb.ZMax','assert cz+float(hole.Radius)<rb.ZMax')
replace('retained_leg_widths_mm=legs,','retained_upper_rib_web_width_mm=rb.XLength,')
replace("compound=d.addObject('Part::Compound',tag+'ExitTools');compound.Links=tools", "compound=d.addObject('Part::MultiFuse',tag+'ExitTools');compound.Shapes=tools;compound.Refine=False")
replace('s=final.Shape.copy();assert s.isValid() and len(s.Solids)==1 and not s.check(True)', """s=final.Shape.copy();strict=s.check(True) or []
            if not s.isValid() or len(s.Solids)!=1 or strict:
                s.exportBrep(str(OUT/(tag+'_REJECTED.brep')))
                save(OUT/'fault.json',dict(tag=tag,valid=s.isValid(),solids=len(s.Solids),BOP_errors=[str(x) for x in strict]))
            assert s.isValid() and len(s.Solids)==1 and not strict""")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
