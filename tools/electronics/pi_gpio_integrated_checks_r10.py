"""Raised Pi fan, retained clear six restraint positions."""
import pi_gpio_integrated_checks_r9 as P
G=P.G
G.OUT=G.ROOT/'hardware/electronics/full-cat/pi-gpio-integrated-r10'
G.ROUTES=G.ROOT/'hardware/electronics/full-cat/pi-wiring-complete-r13'
if __name__=='__main__':G.main()
