"""OE and3V3 restraints at clear straight sections."""
import pi_gpio_integrated_checks_r8 as P
G=P.G
G.OUT=G.ROOT/'hardware/electronics/full-cat/pi-gpio-integrated-r9'
G.ROUTES=G.ROOT/'hardware/electronics/full-cat/pi-wiring-complete-r12'
G.ENDS[2]=(97.54,41,153.25)
if __name__=='__main__':G.main()
