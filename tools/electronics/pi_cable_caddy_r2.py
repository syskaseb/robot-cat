"""MAIN post connects to real Deck plane105; park clears rerouted USB."""
import pi_cable_caddy_r1 as C
C.OUT=C.ROOT/'hardware/electronics/full-cat/pi-cable-caddy-r2'
C.POWER_FOLDER='pi-power-usb-r4';C.MAIN_POST_TOP=108;C.COIL_Y=-69
if __name__=='__main__':C.main()
