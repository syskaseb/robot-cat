"""One N01 support for E2 and its two already-received independent grips.

The carrier is installed before the bank/upper equipment. No detailed N03
fastener design or assertion of a fully assembled N08 service path here.
"""
import FreeCAD as A
import Part


def construct(scene):
    tray=Part.makeBox(38,14.5,2,A.Vector(78.25,-7.25,42))
    # Actual P0 Feature106 reaches39.52, not the general38.52 plane.
    # Its foreign1.25 reserve requires Z>=40.77: choose the shared41 plane.
    # End below the own washer rim; its bearing annulus remains unchanged.
    bridge=Part.makeBox(6,14.8,2,A.Vector(97,6,41))
    arm=Part.makeBox(9,3,2,A.Vector(115.25,1,42))
    posts=[]
    # Extend the REAL planar bottom footprints, not a point guessed from the
    # curved pad's bounding box. The complete existing nylon gets a channel.
    for side in ('module','source'):
        pad=scene['JPWMGrip:'+side+':pad']
        bottom=[f for f in pad.Faces if type(f.Surface).__name__=='Plane'
                and abs(f.CenterOfMass.z-pad.BoundBox.ZMin)<1e-6]
        assert len(bottom)==1,(side,len(bottom))
        # Embed into the pad by .5 for a robust integral Boolean joint.
        # Its exterior is still exactly the existing pad, never extra wire
        # intrusion: the embedded material lies inside that same printed pad.
        foot=bottom[0].copy();foot.translate(A.Vector(0,0,.5))
        post=foot.extrude(A.Vector(0,0,-4.425))
        bandbox=scene['JPWMGrip:'+side+':band'].BoundBox
        channel=Part.makeBox(bandbox.XLength+.4,bandbox.YLength+.4,
                             bandbox.ZLength+.4,A.Vector(bandbox.XMin-.2,bandbox.YMin-.2,bandbox.ZMin-.2))
        posts.append(post.cut(channel))
    base=tray.multiFuse([bridge,arm,*posts])
    for y in (5.85,-8):
        base=base.cut(Part.makeBox(3,2.15,4,A.Vector(100.5,y,41)))
    assert base.isValid() and len(base.Solids)==1
    outer=Part.makeBox(2.5,14.4,16.4,A.Vector(100.75,-7.2,40.8))
    inner=Part.makeBox(4,12,14,A.Vector(100,-6,42))
    band=outer.cut(inner)
    head=Part.makeBox(5.3,4.3,5,A.Vector(99.35,7.2,50))
    assert band.fuse(head).isValid() and len(band.fuse(head).Solids)==1
    joints={}
    for n in ('JPWMGrip:module:pad','JPWMGrip:source:pad','U1Carrier:Rear:Base'):
        joint=base.common(scene[n]).Volume
        assert joint>0,(n,joint)
        joints[n]=joint
    whole=base.multiFuse([scene[n] for n in joints])
    assert whole.isValid() and len(whole.Solids)==1
    return {'E2Tray:Base':base,'E2Tray:Band':band,'E2Tray:Head':head},dict(
        status='CONSTRUCTIVE_SHARED_E2_TRAY_NOT_YET_RECEIVED',
        joints_mm3=joints,case_fixed_centre_mm=[102,0,50],
        case_band_full_stock_mm=dict(width=2.5,thickness=1.2,head=[5.3,4.3,5]),
        independent_wire_grips_unchanged=True,
        installed_before_bank_and_upper_equipment=True,
        detailed_manufacture_N03_and_service_N08_not_claimed=True,
        N01_complete=False,physical_pass=False)
