"""USB remains south of power, with R24-bounded height fans and500mm budget."""
import pi_power_usb_r3 as R
P=R.P
P.OUT=P.ROOT/'hardware/electronics/full-cat/pi-power-usb-r4'
P.USB_SOUTH_FAN=True
if __name__=='__main__':P.main()
