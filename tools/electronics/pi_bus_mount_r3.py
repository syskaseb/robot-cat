"""2mm north beam reuses existing M5 ear nuts/washers, M3x10 for added2mm."""
import pi_bus_mount_r2 as P
B=P.B
B.OUT=B.ROOT/'hardware/electronics/full-cat/pi-bus-mount-r3'
B.BASE_BOXES=[[-68,0,49,-23,33,52],[-68,33,47,66,39,49],[-26,0,47,-23,36,52]]
B.TRAY_PATH='hardware/electronics/full-cat/pi-wiring-complete-r13/PiTray_DESIGN.brep'
if __name__=='__main__':B.main()
