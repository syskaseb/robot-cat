"""One open-prototype bank: two panels, four removable flange bars, four feet.

Retain current purchased12-holder/24-TE datums, NOT the old outer cassette.
Panel apertures are inherited PROTOTYPE fit assumptions, not catalogue data.
Installed service, four parent roots, native CAD and stock remain mandatory.
"""
import math
import FreeCAD as A
import Part
from loom_land_port import box


def geometry():
    prints={};feet={};hardware={};tools={};access={};sweeps={};jaws={};rows=[];fasteners=[]
    for side,y,centres,owners in [
        ('L',58,[-53,-23,7,37,67,97],['FrontLeftFixedCarrier','RearLeftFixedCarrier']),
        ('R',-58,[-53,-21,11,43,75,107],['FrontRightFixedCarrier','RearRightFixedCarrier'])]:
        lo,hi=centres[0]-24,centres[-1]+24
        panel=box([lo,y-13.5,122,hi,y+13.5,124])
        for i,x in enumerate(centres,1):
            # Historical R47 prototype aperture, rotated to current28x15 flange.
            # Delivered fit may replace this panel; no latch motion is invented.
            panel=panel.cut(box([x-11.1,y-5.65,121,x+11.1,y+5.65,125]))
            access[f'ATO_{side}{i}']=box([x-14,y-13,144.8,x+14,y+13,189.8])
            sweeps[f'F_{side}{i}_CP2_ATO']=box([x-9.55,y-2.55,126,x+9.55,y+2.55,179.8])
            for sign in (-1,1):
                jaws[f'F_{side}{i}_CP2_ATO/{sign}']=box([x-10.55,y+(-5.55 if sign==-1 else 2.55),137,
                    x+10.55,y+(-2.55 if sign==-1 else 5.55),184])
            rows.append(dict(id=f'F_{side}{i}_CP2',centre_xy_mm=[x,y],
                flange_top_z_mm=126,panel_top_z_mm=124,nominal_flange_mm=[28,15,2],
                aperture_mm=[22.2,11.3],aperture_supplier_verified=False,
                strategy='Flange bears on panel; two removable outboard bars oppose extraction. No reliance on unknown snap-clip actuation.',
                provisional='Housing/body/TE engagement and panel aperture require delivered fit coupon; preserved current nominal datums are not measured mating dimensions.'))
        bars={sign:box([lo,y+(5.5 if sign==1 else -13.5),126,
                           hi,y+(13.5 if sign==1 else -5.5),129]) for sign in (-1,1)}
        for end,x,owner in [('Front',centres[0]-20,owners[0]),('Rear',centres[-1]+20,owners[1])]:
            foot=box([x-5,y-14,118,x+5,y+14,122])
            for sign in (-1,1):
                yy=y+sign*9;name=side+end+('North' if sign==1 else 'South')
                bore=Part.makeCylinder(1.7,18,A.Vector(x,yy,116))
                panel=panel.cut(bore);bars[sign]=bars[sign].cut(bore);foot=foot.cut(bore)
                poly=[A.Vector(x+3.35*math.cos(k*math.pi/3),yy+3.35*math.sin(k*math.pi/3),117.9) for k in range(7)]
                pocket=Part.Face(Part.makePolygon(poly)).extrude(A.Vector(0,0,2.7));foot=foot.cut(pocket)
                # Nominal M3 hardware envelopes, not an exact vendor SKU claim.
                shaft=Part.makeCylinder(1.5,12,A.Vector(x,yy,117.5))
                head=Part.makeCylinder(2.75,3,A.Vector(x,yy,129.5))
                washer=Part.makeCylinder(3.5,.5,A.Vector(x,yy,129)).cut(Part.makeCylinder(1.6,.5,A.Vector(x,yy,129)))
                hexpoly=[A.Vector(x+3.175*math.cos(k*math.pi/3),yy+3.175*math.sin(k*math.pi/3),118) for k in range(7)]
                nut=Part.Face(Part.makePolygon(hexpoly)).extrude(A.Vector(0,0,2.4)).cut(Part.makeCylinder(1.5,2.4,A.Vector(x,yy,118)))
                hardware[name+'/M3x12']=shaft.fuse(head).removeSplitter()
                hardware[name+'/washer']=washer;hardware[name+'/nut']=nut
                tools[name+'/LkeyShaft']=Part.makeCylinder(1.5,20,A.Vector(x,yy,132.5))
                # A removable hex key approaches from the row's outboard side.
                tools[name+'/LkeyHandle']=Part.makeCylinder(1.5,40,A.Vector(x,yy,152.5),A.Vector(0,1 if side=='L' else -1,0))
                fasteners.append(dict(id=name,axis_xy_mm=[x,yy],screw='M3x12',washer=1,nut=1,
                    shaft_tip_z_mm=117.5,nut_bottom_z_mm=118,tip_past_nut_mm=.5,
                    stack='Head/washer -> removable bar -> panel at end outside holders -> integral Frame foot/nut pocket',
                    assembly='Fit captive nut before parent installation. Support bank, loosen from above with nominalOD3 Lkey; no powered work.'))
            foot=foot.removeSplitter()
            assert foot.isValid() and len(foot.Solids)==1 and not foot.check(True)
            feet[side+end]=dict(shape=foot,owner=owner,root_goal_mm=[x,y,116],
                root_beam_half_widths_mm=[4,4,4],parent_path=None,
                scope='Structural bank pilot, distinct from1.4mm wire arms. Full root/bearing/strength gate OPEN.')
        panel=panel.removeSplitter();prints['Bank'+side+'Panel']=panel
        for sign,b in bars.items():prints['Bank'+side+('North' if sign==1 else 'South')+'Retainer']=b.removeSplitter()
    for n,s in prints.items():
        assert s.isValid() and len(s.Solids)==1 and not s.check(True),n
        b=s.BoundBox;assert max(b.XLength+10,b.YLength+10,b.ZLength)<256
    return dict(prints=prints,feet=feet,hardware=hardware,tools=tools,ATO_access=access,ATO_sweeps=sweeps,ATO_jaws=jaws,
        recipe=dict(holders=rows,fasteners=fasteners,new_separate_prints=6,
            integrated_parent_feet=4,nominal_hardware={'M3x12':8,'M3nut':8,'M3washer':8},
            panel_aperture_basis='servo_fuse_side_bank_r4.py prototype11.3x22.2 rotated90deg; NOT a manufacturer cutout tolerance. Current28x15x2 flange from0300330 reference.',
            shared_layout='Two rows remainY+/-58, flange top126 and all24TE/current wires unchanged. Panels122..124, bars126..129 outsideY+/-5.5 from each row. No old outer BankLeft/Right/Deck/Cover or cosmetic shell.',
            routine_ATO_design_basis='Nominal19.1x5.1x18.8 fuse,35mm UP withdrawal. Two project3mm jaw envelopes21.1wide grip aboveZ137 and translate35mm; NOT manufacturer tool dimensions, measured engagement or complete commercial pliers geometry. Coarse28x26x45 budget is advisory, not proof of physical collision. Delivered fuse/tool fit remains phase2 gate.',
            assembly=['Install four rooted parent feet with captive nuts before electronics/looms.',
                      'Prepare12 holders and24 TE assemblies on bench; dry-fit replaceable panels to delivered housings.',
                      'Place panels on feet, seat flanges, fit two outboard bars per row using8 nominalM3x12 stacks.',
                      'Route through current passages and lace insulation independently; case retention bars never clamp wire or lever.',
                      'Routine ATO replacement is from above with WAGO retained; prove installed tool/pull reservations against full current scene.',
                      'Deep repair: disconnect sources, support bank, reverse wiring and panel/bar installation. No independent old cover or whole-cassette lift assumed.'],
            open=['Exact shared material/tool/ATO checks with full36/19/25 and all55 saddle choices',
                  'Four actual parent roots/load paths; static/dynamic mechanical sizing K2',
                  'Native parameter/reopen/exports, hardware stock and delivered unpowered fit'],
            selected=False,W5_complete=False,M4_complete=False,physical_pass=False))
