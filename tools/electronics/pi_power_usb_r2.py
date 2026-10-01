"""Raised Pi, smooth power height transitions above old P0 mount."""
import pi_power_usb_r1 as P
P.OUT=P.ROOT/'hardware/electronics/full-cat/pi-power-usb-r2'
P.PI_RISE=7;P.POWER_FAN=True
P.GPIO_FOLDER='pi-gpio-integrated-r10';P.GPIO_ROUTES='pi-wiring-complete-r13';P.BUS_FOLDER='pi-bus-mount-r3'
if __name__=='__main__':P.main()
