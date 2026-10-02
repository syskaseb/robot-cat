"""Bounded W036 correction after explicit R1 fuse/P_FRONT conflicts."""
import body_ground_front_return_r1 as B
B.OUT=B.ROOT/"hardware/electronics/full-cat/body-ground-front-return-r2"
B.SPEC=("G1.4",[66,11,113.5],1,"FR_G.1",[-33,-30.5,113.5],1,128.5,88)
if __name__=="__main__": B.main()
