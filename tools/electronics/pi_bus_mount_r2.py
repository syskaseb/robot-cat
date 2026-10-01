"""Both north ears avoid Pi power plug at south-left ear."""
import pi_bus_mount_r1 as B
B.OUT=B.ROOT/'hardware/electronics/full-cat/pi-bus-mount-r2'
B.BODY_AXES=[(-12,36),(61,36)]
B.BASE_BOXES=[[-68,0,49,-23,33,52],[-68,33,47,66,39,50],[-26,0,47,-23,36,52]]
if __name__=='__main__':B.main()
