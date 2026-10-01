"""Raised Pi mount clears reserved power boot and original M5 tray screw."""
import pi_wiring_complete_r12 as P
M=P.M
M.OUT=M.ROOT/'hardware/electronics/full-cat/pi-wiring-complete-r13'
M.PI_RISE=7;M.FAN_HEIGHT=41;M.FANNED_LOW=120.7
def portals(owners):
    meta=P.P.portals(owners)
    for x in (-15.5,42.5):
        for y in (-24.5,24.5):
            post=M.Part.makeCylinder(3,7,M.A.Vector(x,y,45)).cut(M.Part.makeCylinder(1.45,9,M.A.Vector(x,y,44)))
            owners['PiTray18']=owners['PiTray18'].fuse(post)
    assert owners['PiTray18'].isValid() and len(owners['PiTray18'].Solids)==1
    owners['PiTray18'].exportBrep(str(M.OUT/'PiTray_DESIGN.brep'))
    meta.update(Pi_mount_rise_mm=7,Pi_screws='4 M2.5x16 replace4M2.5x8; original nuts/pockets and washers retained',
        fan_curvature_bound_mm=41**2/(6*27.55),native_final_pending=True,new_stls=0)
    return meta
M.PORTAL_BUILDER=portals
if __name__=='__main__':M.main()
