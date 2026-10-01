"""Shift 3V3 insulation restraint onto its straight north segment, before OE fan."""
import pi_gpio_integrated_checks_r7 as P
G=P.G
G.OUT=G.ROOT/'hardware/electronics/full-cat/pi-gpio-integrated-r8'
G.ENDS[0]=(91.54,33,151.5)
if __name__=='__main__':G.main()
