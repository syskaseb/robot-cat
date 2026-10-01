"""Parallel final power bend with3.2mm radial spacing, no crossing red/black."""
import pi_power_usb_r2 as R
P=R.P
P.OUT=P.ROOT/'hardware/electronics/full-cat/pi-power-usb-r3'
P.CONCENTRIC_RETURN=True
if __name__=='__main__':P.main()
