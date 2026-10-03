"""Whole bottom-open insulation clamp: open rib AND seat, cinch upwards.

R1 opened the rib but the unchanged flat seat still trapped the fixed wire.
R2 retains two side anchor feet and adds a small upper bearing bridge. The
same twelve T18I loops cinch the insulation UP to that bridge, then are cut
before bank withdrawal. No additional loose print, tie, fastener or wire.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_output_rib_exits_native_r1.py')
code=parent.read_text(encoding='utf-8')
def replace(old,new):
    global code
    assert old in code,old[:100]
    code=code.replace(old,new)
replace('servo-fuse-output-rib-exits-native-r1','servo-fuse-output-rib-exits-native-r2')
replace('    pins={}','    pins={}\n    pins[parent.relative_to(ROOT).as_posix()]=sha(parent)')
replace('before[tag]=base.Shape.copy();tools=[]','before[tag]=base.Shape.copy();tools=[];roofs=[];ties=[]')
replace('rb=rib.Shape.BoundBox;hb=hole.Shape.BoundBox','rb=rib.Shape.BoundBox;hb=hole.Shape.BoundBox;seat=datum.getObject(ident+\'Seat\').Shape.BoundBox')
replace('q.Length=diam;q.Width=rb.YLength+.2;q.Height=cz-rb.ZMin+.1','q.Length=diam;q.Width=seat.YLength+.2;q.Height=cz-rb.ZMin+.1')
replace('cx-diam/2,rb.YMin-.1,rb.ZMin-.1','cx-diam/2,seat.YMin-.1,rb.ZMin-.1')
replace('                tools.append(q)', '''                tools.append(q)
                def boxobj(name,b):
                    o=d.addObject('Part::Box',name);o.Length=b[3]-b[0];o.Width=b[4]-b[1];o.Height=b[5]-b[2]
                    o.Placement.Base=A.Vector(*b[:3]);return o
                roof=boxobj(ident+'UpperBearingBridge',[cx-6,seat.YMin,cz+1.2,cx+6,seat.YMax,cz+2.7]);roofs.append(roof)
                side=1 if seat.YMin>0 else -1
                sy0,sy1=sorted((side*137,side*140));ty0,ty1=sorted((side*137.25,side*139.75))
                for i,dx in enumerate((-3.5,3.5)):
                    tools.append(boxobj(ident+'UpperCinchSlot'+str(i),[cx+dx-1,sy0,rb.ZMin-.2,cx+dx+1,sy1,cz+3.9]))
                tb=[[cx+dx-.6,ty0,cz-2.4,cx+dx+.6,ty1,cz+3.9] for dx in (-3.5,3.5)]
                tb += [[cx-4.1,ty0,cz-2.4,cx+4.1,ty1,cz-1.2],[cx-4.1,ty0,cz+2.7,cx+4.1,ty1,cz+3.9]]
                tb += [[cx+4.1,ty0,cz+2.7,cx+8.6,ty0+4.8,cz+6.2]]
                tieparts=[Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3])) for b in tb]
                ties.append((ident,Part.makeCompound(tieparts)))
                ties[-1][1].exportBrep(str(OUT/(ident+'_UPWARD_TIE_DESIGN.brep')))
                roof.Shape.exportBrep(str(OUT/(ident+'_ROOF_STOCK.brep')))
                planned=2*(7+5.1)+15;assert planned<145
''')
# Recompute boxes before exports; a freshly created Part::Box has no Shape yet.
replace("                ties[-1][1].exportBrep", "                d.recompute()\n                ties[-1][1].exportBrep")
replace('upper_arch_retained=True,local_one_solid=True)', '''upper_arch_retained=True,local_one_solid=True,
                    bearing_roof_bounds_mm=bounds(roof.Shape),cinch_direction='UPWARD_TO_UPPER_BRIDGE',
                    tie_type='same T18I111-02370,12 replacements not additional installed loops',
                    tie_band_bounds_mm=tb,PROJECT_loop_and_insertion_mm=planned,
                    nominal_insulation_OD_mm=2.4,physical_grip_qualified=False)''')
replace('final.Base=link;final.Tool=compound;final.Refine=False;finals[tag]=final', '''stock=d.addObject('Part::MultiFuse',tag+'UpperClampStock');stock.Shapes=[link]+roofs;stock.Refine=False
            final.Base=stock;final.Tool=compound;final.Refine=False;finals[tag]=final''')
replace('            assert s.Volume<before[tag].Volume','            assert abs(s.Volume-before[tag].Volume)>1e-5')
replace('removed_bridge_mm3=before[tag].Volume-s.Volume','net_material_delta_mm3=s.Volume-before[tag].Volume')
replace("status='TWELVE_DOWNWARD_OUTPUT_EXITS_NATIVE_COMPLETE_MODULE_SERVICE_OPEN'", "status='TWELVE_DOWNWARD_CLAMPS_NATIVE_COMPLETE_INSTALLED_FIT_AND_SERVICE_OPEN'")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
