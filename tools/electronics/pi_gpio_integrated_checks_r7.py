"""OE end restraint moved onto north straight, clear of populated PCB."""
import pi_gpio_integrated_checks_r5 as P
G=P.G
G.OUT=G.ROOT/'hardware/electronics/full-cat/pi-gpio-integrated-r7'
G.ROUTES=G.ROOT/'hardware/electronics/full-cat/pi-wiring-complete-r11'
G.ENDS[2]=(95.54,41,153.25)
if __name__=='__main__':G.main()
