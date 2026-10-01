"""Offset MAIN neck leaves room for full upper tie; park ties align with ring."""
import pi_cable_caddy_r2 as P
C=P.C
C.OUT=C.ROOT/'hardware/electronics/full-cat/pi-cable-caddy-r3'
C.MAIN_NECK_X=89.5;C.COIL_TIE_Y=C.COIL_Y
if __name__=='__main__':C.main()
